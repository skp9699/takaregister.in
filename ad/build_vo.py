#!/usr/bin/env python3
"""
Voice-first narration builder.

Unlike build_audio.py (which squeezes lines into fixed scene slots), this reads
each line at a natural pace and reports where it lands. The printed timeline is
the spec the video gets cut to — voice first, animation second.

  python3 build_vo.py --script script-en.txt --voice en-gb-x-rp+Andrea --out build/vo-en.mp3
  python3 build_vo.py --script script-hi.txt --voice hi+Andrea         --out build/vo-hi.mp3 --warm 0.94
"""
import argparse, os, shutil, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")

ap = argparse.ArgumentParser()
ap.add_argument("--script", required=True)
ap.add_argument("--voice", default="en-gb-x-rp+Andrea")
ap.add_argument("--out", required=True)
ap.add_argument("--wpm", type=int, default=150, help="natural reading pace")
ap.add_argument("--pitch", type=int, default=52)
ap.add_argument("--warm", type=float, default=0.96,
                help="<1 drops pitch and formants; keep near 1 for a female read")
ap.add_argument("--bed", type=float, default=0.20, help="music bed level, 0 to disable")
ap.add_argument("--stems", action="store_true", help="also keep the dry voice-only track")
A = ap.parse_args()

OUT = os.path.abspath(A.out)
TMP = os.path.join(os.path.dirname(OUT), "vo_" + os.path.basename(A.script).split(".")[0])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd[:5])}...\n{r.stderr[-1500:]}")
    return r


def wav_len(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


# ---- read script ------------------------------------------------------------
lines = []
for raw in open(A.script, encoding="utf-8"):
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        continue
    gap, text = raw.split("|", 1)
    lines.append((float(gap.strip()), text.strip()))

# ---- synthesise each line at one steady pace --------------------------------
clips, t, timeline = [], 0.0, []
for i, (gap, text) in enumerate(lines):
    raw = f"{TMP}/raw{i}.wav"
    run(["espeak-ng", "-v", A.voice, "-s", str(A.wpm), "-p", str(A.pitch), "-g", "3",
         "-w", raw, text])
    dry = f"{TMP}/vo{i}.wav"
    run([FFMPEG, "-y", "-i", raw, "-af",
         f"asetrate=22050*{A.warm},aresample=48000,atempo=1/{A.warm},"
         "highpass=f=100,lowpass=f=8200,"
         "acompressor=threshold=-20dB:ratio=3:attack=8:release=180,"
         "aecho=0.85:0.9:34:0.05,volume=2.2",
         "-ar", "48000", "-ac", "1", dry])
    d = wav_len(dry)
    t += gap
    timeline.append((i + 1, t, d, text))
    clips.append((t, dry))
    t += d

TOTAL = t + 1.2
print(f"\n  #   starts    runs   line")
for n, start, d, text in timeline:
    print(f"  {n:2}  {start:6.2f}s  {d:5.2f}s  {text[:58]}{'…' if len(text) > 58 else ''}")
print(f"\n  total narration: {TOTAL:.1f}s")

# ---- music bed --------------------------------------------------------------
inputs, filt, tags = [], [], []
if A.bed > 0:
    bed = f"{TMP}/bed.wav"
    run([FFMPEG, "-y",
         "-f", "lavfi", "-i", f"sine=frequency=55:duration={TOTAL}:sample_rate=48000",
         "-f", "lavfi", "-i", f"sine=frequency=82.41:duration={TOTAL}:sample_rate=48000",
         "-f", "lavfi", "-i", f"sine=frequency=110:duration={TOTAL}:sample_rate=48000",
         "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={TOTAL}:sample_rate=48000",
         "-filter_complex",
         "[0:a]volume=0.55[a];[1:a]volume=0.30[b];[2:a]volume=0.20[c];[3:a]volume=0.10[d];"
         "[a][b][c][d]amix=inputs=4:normalize=0[m];"
         f"[m]tremolo=f=0.22:d=0.28,lowpass=f=420,"
         f"volume='{A.bed}*(1-exp(-t/2.2))':eval=frame,"
         f"afade=t=out:st={TOTAL-3.0}:d=3.0[o]",
         "-map", "[o]", "-ar", "48000", "-ac", "1", "-t", str(TOTAL), bed])
    inputs += ["-i", bed]
    tags.append("[0:a]")

base = len(tags)
for n, (start, path) in enumerate(clips):
    idx = base + n
    inputs += ["-i", path]
    filt.append(f"[{idx}:a]adelay={int(start*1000)}|{int(start*1000)}[v{n}]")
    tags.append(f"[v{n}]")
filt.append("".join(tags) + f"amix=inputs={len(tags)}:normalize=0:dropout_transition=0[mx]")
filt.append("[mx]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[o]")

run([FFMPEG, "-y"] + inputs + ["-filter_complex", ";".join(filt),
     "-map", "[o]", "-t", str(TOTAL), "-c:a", "libmp3lame", "-b:a", "192k", OUT])

if A.stems:
    dry_out = OUT.rsplit(".", 1)[0] + "-dry.mp3"
    di, df, dt = [], [], []
    for n, (start, path) in enumerate(clips):
        di += ["-i", path]
        df.append(f"[{n}:a]adelay={int(start*1000)}|{int(start*1000)}[v{n}]")
        dt.append(f"[v{n}]")
    df.append("".join(dt) + f"amix=inputs={len(clips)}:normalize=0:dropout_transition=0,"
                            "loudnorm=I=-15:TP=-1.5:LRA=11[o]")
    run([FFMPEG, "-y"] + di + ["-filter_complex", ";".join(df),
         "-map", "[o]", "-t", str(TOTAL), "-c:a", "libmp3lame", "-b:a", "192k", dry_out])
    print(f"  dry stem: {dry_out}")

print(f"\nwrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
