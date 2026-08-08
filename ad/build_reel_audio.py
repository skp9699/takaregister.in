#!/usr/bin/env python3
"""
Builds the reel's audio and muxes it onto the rendered video.

Produces two cuts from one render pair:
  reel-<lang>.mp4            voice only, no captions
  reel-<lang>-music-subs.mp4 voice under a soft bed, captions burnt in

The bed is a sustained pad rather than a loop — at this length a loop's seam is
audible, and the point is to fill silence, not to be noticed. It sits ~20 dB
under the voice and swells only at the brand reveal and the sign-off.

  python3 build_reel_audio.py --lang en
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")

ap = argparse.ArgumentParser()
ap.add_argument("--lang", default="en")
ap.add_argument("--duration", type=float, default=29.5)
ap.add_argument("--bed", type=float, default=0.10,
                help="bed level under the voice; kept very low by request")
ap.add_argument("--swell", default="11.6,26.0", help="seconds where the bed lifts")
A = ap.parse_args()

VO      = f"{BUILD}/vo-{A.lang}-30s-dry.mp3"
V_SUBS  = f"{BUILD}/reel-subs.mp4" if A.lang == "en" else f"{BUILD}/reel-subs-{A.lang}.mp4"
V_PLAIN = V_SUBS   # both cuts are subtitled
D = A.duration


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED ({what}):\n{r.stderr[-1800:]}")


for f in (VO, V_SUBS):
    if not os.path.exists(f):
        sys.exit(f"missing {f} — render the video and build the voice first")

# ---- music bed -------------------------------------------------------------
# A minor pad: root, fifth, octave, plus a little air on top. Slow tremolo and a
# low-pass keep it behind the voice instead of competing with it.
bed = f"{BUILD}/reel-bed-{A.lang}.wav"
s1, s2 = (float(x) for x in A.swell.split(","))
run([FFMPEG, "-y",
     "-f", "lavfi", "-i", f"sine=frequency=55:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=82.41:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=110:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=220:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=880:duration={D}:sample_rate=48000",
     "-filter_complex",
     "[0:a]volume=0.50[a];[1:a]volume=0.26[b];[2:a]volume=0.20[c];"
     "[3:a]volume=0.11[d];[4:a]volume=0.07[e];[5:a]volume=0.012[f];"
     "[a][b][c][d][e][f]amix=inputs=6:normalize=0[m];"
     "[m]tremolo=f=0.18:d=0.22,lowpass=f=560,"
     f"volume='{A.bed}*(1-exp(-t/2.6))"
     f"*(1+0.38*exp(-((t-{s1})/2.2)^2)+0.55*exp(-((t-{s2})/2.4)^2))':eval=frame,"
     f"afade=t=in:st=0:d=1.2,afade=t=out:st={D-2.6}:d=2.6[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", "-t", str(D), bed], "bed")

# ---- voice alone, levelled -------------------------------------------------
voice = f"{BUILD}/reel-voice-{A.lang}.wav"
run([FFMPEG, "-y", "-i", VO,
     # pad to the full render length: amix ends with the last spoken line,
     # and -shortest would otherwise clip the hold on the sign-off
     "-af", "loudnorm=I=-15:TP=-1.5:LRA=11,apad",
     "-ar", "48000", "-ac", "2", "-t", str(D), voice], "voice")

# ---- voice over bed, with the bed ducking under speech ---------------------
mixed = f"{BUILD}/reel-mixed-{A.lang}.wav"
run([FFMPEG, "-y", "-i", voice, "-i", bed, "-filter_complex",
     "[0:a]asplit=2[v][key];"
     "[1:a][key]sidechaincompress=threshold=0.045:ratio=6:attack=12:release=340[duck];"
     "[v][duck]amix=inputs=2:normalize=0[m];"
     "[m]alimiter=limit=0.96,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", "-t", str(D), mixed], "mix")

# ---- mux -------------------------------------------------------------------
out_plain = f"{BUILD}/takaregister-reel-{A.lang}-subs.mp4"
out_full  = f"{BUILD}/takaregister-reel-{A.lang}-subs-music.mp4"
for video, audio, out in ((V_PLAIN, voice, out_plain), (V_SUBS, mixed, out_full)):
    run([FFMPEG, "-y", "-i", video, "-i", audio,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", out], os.path.basename(out))
    print(f"  {os.path.basename(out):44} {os.path.getsize(out)/1048576:5.2f} MB")

for tmp in (bed, voice, mixed):
    os.remove(tmp)
print("\ndone")
