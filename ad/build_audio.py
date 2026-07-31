#!/usr/bin/env python3
"""
Builds the ad's audio track: voiceover (espeak-ng) + a quiet music bed, mixed
and muxed onto the silent render.

Each line in voiceover.txt declares the second it must start on and how long it
may run. espeak is re-run at a faster words-per-minute until the clip fits its
slot, so the narration stays locked to the animation even if the copy changes.

  python3 build_audio.py [--voice en-gb-x-rp] [--lang en]
"""
import os, re, subprocess, sys, wave, shutil, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")
SILENT = os.path.join(BUILD, "takaregister-ad-silent.mp4")

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="en-gb-x-rp")
ap.add_argument("--script", default=os.path.join(HERE, "voiceover.txt"))
ap.add_argument("--out", default=os.path.join(BUILD, "takaregister-ad.mp4"))
ap.add_argument("--duration", type=float, default=58.0)
A = ap.parse_args()

os.makedirs(BUILD, exist_ok=True)
TMP = os.path.join(BUILD, "vo")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd[:6])}...\n{r.stderr[-1500:]}")
    return r


def wav_len(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


# ---- parse script -----------------------------------------------------------
lines = []
for raw in open(A.script, encoding="utf-8"):
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        continue
    start, cap, text = (p.strip() for p in raw.split("|", 2))
    lines.append((float(start), float(cap), text))
print(f"{len(lines)} narration lines")

# ---- synthesise each line, shrinking until it fits its slot ------------------
clips = []
for i, (start, cap, text) in enumerate(lines):
    raw = f"{TMP}/raw{i}.wav"
    wpm, dur = 142, None
    for _ in range(16):
        run(["espeak-ng", "-v", A.voice, "-s", str(wpm), "-p", "36", "-g", "4",
             "-w", raw, text])
        dur = wav_len(raw)
        # the pitch-down pass below stretches the clip by 1/0.90
        if dur / 0.90 <= cap:
            break
        wpm += 8
    fitted = dur / 0.90
    flag = "" if fitted <= cap else "  << OVERRUNS"
    print(f"  {i+1}. t={start:5.2f}s  cap={cap:4.1f}s  got={fitted:4.1f}s  {wpm}wpm{flag}")

    # Warm the voice up: drop the sample rate to pull pitch and formants down,
    # restore tempo, then band-limit and even out the level.
    out = f"{TMP}/vo{i}.wav"
    run([FFMPEG, "-y", "-i", raw, "-af",
         "asetrate=22050*0.90,aresample=48000,atempo=1/0.90,"
         "highpass=f=95,lowpass=f=7600,"
         "acompressor=threshold=-20dB:ratio=3:attack=8:release=180,"
         "aecho=0.85:0.9:38:0.06,"
         "volume=2.4",
         "-ar", "48000", "-ac", "1", out])
    clips.append((start, out))

# ---- music bed: slow drone, well under the voice ----------------------------
bed = os.path.join(BUILD, "bed.wav")
D = A.duration
run([FFMPEG, "-y",
     "-f", "lavfi", "-i", f"sine=frequency=55:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=82.41:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=110:duration={D}:sample_rate=48000",
     "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={D}:sample_rate=48000",
     "-filter_complex",
     "[0:a]volume=0.55[a];[1:a]volume=0.30[b];[2:a]volume=0.20[c];[3:a]volume=0.10[d];"
     "[a][b][c][d]amix=inputs=4:normalize=0[m];"
     # slow swell, lift under the brand reveal and the sign-off
     f"[m]tremolo=f=0.22:d=0.28,lowpass=f=420,"
     f"volume='0.30*(1-exp(-t/2.2))*(1+0.5*exp(-((t-14.6)/2.4)^2)+0.6*exp(-((t-55.2)/2.6)^2))':eval=frame,"
     f"afade=t=out:st={D-3.2}:d=3.2[out]",
     "-map", "[out]", "-ar", "48000", "-ac", "1", "-t", str(D), bed])

# ---- mix voice over bed -----------------------------------------------------
mix = os.path.join(BUILD, "audio.wav")
inputs, filt, tags = ["-i", bed], [], ["[0:a]"]
for n, (start, path) in enumerate(clips, start=1):
    inputs += ["-i", path]
    filt.append(f"[{n}:a]adelay={int(start*1000)}|{int(start*1000)}[v{n}]")
    tags.append(f"[v{n}]")
filt.append("".join(tags) + f"amix=inputs={len(clips)+1}:normalize=0:dropout_transition=0[mx]")
# duck the bed a little whenever the voice is present, then normalise
filt.append("[mx]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]")
run([FFMPEG, "-y"] + inputs + ["-filter_complex", ";".join(filt),
     "-map", "[out]", "-ar", "48000", "-ac", "2", "-t", str(D), mix])

# ---- mux onto the silent render --------------------------------------------
if not os.path.exists(SILENT):
    sys.exit(f"missing {SILENT} — run render.js first")
run([FFMPEG, "-y", "-i", SILENT, "-i", mix,
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", A.out])

mb = os.path.getsize(A.out) / 1048576
print(f"\nwrote {A.out}  ({mb:.2f} MB)")
