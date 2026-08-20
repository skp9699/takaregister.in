#!/usr/bin/env python3
"""
Reads the line boundaries out of a finished voiceover.

Silence detection alone is not enough: the read breathes mid-sentence, so there
are always more gaps than lines. This picks which gaps are line breaks by
choosing the set that makes the pace most even across the whole script — a
greedy nearest-gap snap once put a ten-word line at 0.169 sec/word, which is
not a speed anyone reads at.

  python3 derive_timing.py assets/vo-hi-final.mp3
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")

audio = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/assets/vo-hi-final.mp3"
script = sys.argv[2] if len(sys.argv) > 2 else f"{HERE}/voiceover/hi-89s-devanagari.txt"

lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip() and not l.startswith("#")]
w = [len(l.split()) for l in lines]
N, TOT = len(lines), sum(w)

probe = subprocess.run([FFMPEG, "-i", audio, "-af", "silencedetect=noise=-34dB:d=0.16",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
DUR = None
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe)
if m:
    DUR = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
gaps = sorted(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", probe)],
                  [float(x) for x in re.findall(r"silence_end: ([\d.]+)", probe)]))
if not gaps:
    sys.exit("no silences found — check the noise floor")

# speech runs from the first sound to the last
T0 = round(gaps[0][1], 2) if gaps[0][0] < 0.35 else 0.30
T1 = gaps[-1][0] if DUR and gaps[-1][1] > DUR - 0.6 else (DUR or gaps[-1][1])
RATE = (T1 - T0) / TOT

INF = float("inf")
G = len(gaps)
def cost(dur, words):
    lo, hi = words * RATE * 0.55, words * RATE * 1.9
    if dur < lo or dur > hi:
        return INF
    return (dur - words * RATE) ** 2
dp = [[INF] * G for _ in range(N - 1)]
bk = [[-1] * G for _ in range(N - 1)]
for j in range(G):
    dp[0][j] = cost(gaps[j][0] - T0, w[0])
for i in range(1, N - 1):
    for j in range(i, G):
        best, bj = INF, -1
        for k in range(i - 1, j):
            if dp[i - 1][k] == INF:
                continue
            d = gaps[j][0] - gaps[k][1]
            if d <= 0.15:
                continue
            cc = cost(d, w[i])
            if cc == INF:
                continue
            c = dp[i - 1][k] + cc
            if c < best:
                best, bj = c, k
        dp[i][j], bk[i][j] = best, bj
best, bj = INF, -1
for j in range(N - 2, G):
    if dp[N - 2][j] == INF:
        continue
    d = T1 - gaps[j][1]
    if d <= 0.15:
        continue
    cc = cost(d, w[N - 1])
    if cc == INF:
        continue
    c = dp[N - 2][j] + cc
    if c < best:
        best, bj = c, j
if bj < 0:
    sys.exit("could not fit the script to the audio — is this the right script?")

chain, i, j = [], N - 2, bj
while i >= 0:
    chain.append(j); j = bk[i][j]; i -= 1
chain.reverse()

starts = [T0] + [round(gaps[j][1], 2) for j in chain]
ends = [round(gaps[j][0], 2) for j in chain] + [round(T1, 2)]

print(f"\n  {os.path.basename(audio)}  {DUR:.2f}s  ·  {N} lines  ·  {G} gaps detected\n")
print(f"  {'#':>3} {'start':>7} {'end':>7} {'runs':>6} {'wds':>4} {'s/wd':>6}  line")
sp = []
for i, (s, e) in enumerate(zip(starts, ends)):
    r = (e - s) / w[i]; sp.append(r)
    flag = "" if 0.20 <= r <= 0.48 else "   <-- check"
    print(f"  {i+1:>3} {s:7.2f} {e:7.2f} {e-s:6.2f} {w[i]:4} {r:6.3f}  {lines[i][:32]}{flag}")
print(f"\n  sec/word  min {min(sp):.3f}  max {max(sp):.3f}  mean {sum(sp)/len(sp):.3f}")

json.dump({"starts": starts, "ends": ends, "dur": round(DUR, 2)},
          open(f"{SCRATCH}/timing.json", "w"))
print(f"  wrote timing.json")
