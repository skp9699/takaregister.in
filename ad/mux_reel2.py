#!/usr/bin/env python3
"""
Muxes the customer's final voiceover onto each rendered treatment.

The voice is theirs and finished, so nothing here touches its level or timing —
it is copied on as-is. `--music` adds the soft pad under it for the one cut that
wants a bed; the bed ducks against the voice rather than sitting at a fixed
level, and swells only at the brand beat and the sign-off.

  python3 mux_reel2.py                 all four, voice only
  python3 mux_reel2.py --music screens  also write a bedded cut of that one
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")
VO = os.path.join(HERE, "assets", "vo-hi-final.mp3")
DUR = 81.03
SWELL = (33.5, 68.5, 77.5)          # brand beat, tagline, sign-off

ap = argparse.ArgumentParser()
ap.add_argument("--styles", default="screens,type,split,mixed,screens-en,type-en,split-en,mixed-en")
ap.add_argument("--music", default="", help="also write a bedded cut of this style")
ap.add_argument("--bed", type=float, default=0.62)
A = ap.parse_args()


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED ({what}):\n{r.stderr[-1600:]}")


def bed_wav():
    """A minor pad: root, fifth, octave and a little air. Slow tremolo and a
    low-pass keep it behind the voice instead of competing with it."""
    out = f"{B}/r2-bed.wav"
    sw = "".join(f"+0.40*exp(-((t-{s})/2.3)^2)" for s in SWELL)
    ins = []
    for f in (55, 82.41, 110, 164.81, 220, 880):
        ins += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={DUR}:sample_rate=48000"]
    run([FFMPEG, "-y", *ins,
         "-filter_complex",
         "[0:a]volume=0.50[a];[1:a]volume=0.26[b];[2:a]volume=0.20[c];"
         "[3:a]volume=0.11[d];[4:a]volume=0.07[e];[5:a]volume=0.012[f];"
         "[a][b][c][d][e][f]amix=inputs=6:normalize=0[m];"
         "[m]tremolo=f=0.18:d=0.22,lowpass=f=560,"
         f"volume='{A.bed}*(1-exp(-t/2.6))*(1{sw})':eval=frame,"
         f"afade=t=in:st=0:d=1.4,afade=t=out:st={DUR-3.0}:d=3.0[o]",
         "-map", "[o]", "-ar", "48000", "-ac", "2", "-t", str(DUR), out], "bed")
    return out


for style in A.styles.split(","):
    src = f"{B}/silent-{style}.mp4"
    if not os.path.exists(src):
        print(f"  skip {style} — not rendered"); continue
    out = f"{B}/takaregister-reel-{style}.mp4"
    run([FFMPEG, "-y", "-i", src, "-i", VO,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", out], style)
    print(f"  {os.path.basename(out):40} {os.path.getsize(out)/1048576:5.2f} MB")

if A.music:
    bed = bed_wav()
    mixed = f"{B}/r2-mixed.wav"
    run([FFMPEG, "-y", "-i", VO, "-i", bed, "-filter_complex",
         "[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][key];"
         "[1:a][key]sidechaincompress=threshold=0.10:ratio=3:attack=15:release=420[duck];"
         "[v][duck]amix=inputs=2:normalize=0[m];"
         "[m]alimiter=limit=0.96,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
         "-map", "[o]", "-ar", "48000", "-ac", "2", "-t", str(DUR), mixed], "mix")
    out = f"{B}/takaregister-reel-{A.music}-music.mp4"
    run([FFMPEG, "-y", "-i", f"{B}/silent-{A.music}.mp4", "-i", mixed,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", out], "music mux")
    print(f"  {os.path.basename(out):40} {os.path.getsize(out)/1048576:5.2f} MB")
    for f in (bed, mixed):
        os.remove(f)
