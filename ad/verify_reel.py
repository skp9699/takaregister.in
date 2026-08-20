#!/usr/bin/env python3
"""
Checks that the encoded MP4 shows what the page shows.

A page that renders correctly is not the same thing as a video that plays
correctly. Two ffmpeg processes once wrote the same output path at the same
time; the file passed a single-frame check at 77s and was mangled for its first
eighteen seconds. This samples every beat instead of one, and compares each
frame against a reference rendered from the page at the same timestamp.

  python3 verify_reel.py build/takaregister-reel-split-en.mp4 split-en
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageChops, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"
FFMPEG = os.environ.get("FFMPEG_PATH", f"{SCRATCH}/node_modules/ffmpeg-static/ffmpeg")
TMP = f"{SCRATCH}/verify"

mp4 = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/build/takaregister-reel-split-en.mp4"
variant = sys.argv[2] if len(sys.argv) > 2 else "split-en"

page = open(f"{HERE}/reel2.html", encoding="utf-8").read()
beats = json.loads(re.search(r"const BEATS=(\[.*?\]);\n", page, re.S).group(1))
dur = float(re.search(r"const DUR=([\d.]+);", page).group(1))

# sample each beat where it has settled, away from the crossfades at either end
times = [round(b["s"] + b["d"] * 0.62, 2) for b in beats]
os.makedirs(TMP, exist_ok=True)

node = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch({{ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--disable-gpu','--hide-scrollbars','--disable-lcd-text','--force-color-profile=srgb'] }});
  const p = await b.newPage({{ viewport:{{width:540,height:960}}, deviceScaleFactor:2 }});
  await p.goto('file://{HERE}/reel2.html?render=1&v={variant}',{{waitUntil:'load'}});
  await p.evaluate(()=>document.fonts.ready); await p.evaluate(()=>window.__imagesReady);
  for (const t of {json.dumps(times)}) {{
    await p.evaluate(x=>window.renderAt(x), t);
    await p.screenshot({{ path:`{TMP}/ref-${{t}}.png` }});
  }}
  await b.close();
}})();
"""
open(f"{TMP}/ref.js", "w").write(node)
r = subprocess.run(["node", f"{TMP}/ref.js"], capture_output=True, text=True,
                   env={**os.environ, "NODE_PATH": f"{SCRATCH}/node_modules"})
if r.returncode:
    sys.exit(f"reference render failed:\n{r.stderr[-1200:]}")

print(f"\n  {os.path.basename(mp4)}  vs  reel2.html?v={variant}   ({dur}s, {len(beats)} beats)\n")
print(f"  {'beat':>4} {'t':>7}  {'diff':>6}   verdict")
bad, prev = 0, None
for i, (t, b) in enumerate(zip(times, beats)):
    got = f"{TMP}/got-{t}.png"
    subprocess.run([FFMPEG, "-y", "-ss", str(t), "-i", mp4, "-frames:v", "1", got],
                   capture_output=True)
    if not os.path.exists(got):
        print(f"  {i+1:>4} {t:7.2f}       -   NO FRAME"); bad += 1; continue
    a = Image.open(f"{TMP}/ref-{t}.png").convert("RGB")
    c = Image.open(got).convert("RGB").resize(a.size)
    diff = ImageStat.Stat(ImageChops.difference(a, c)).mean
    d = sum(diff) / 3
    # h.264 at crf 20 moves a few levels; a wrong or frozen frame moves dozens
    ok = d < 6.0
    same_as_prev = prev is not None and ImageStat.Stat(
        ImageChops.difference(Image.open(prev).convert("RGB"), c)).mean[0] < 0.8
    note = "ok" if ok else f"MISMATCH — not the frame the page draws"
    if same_as_prev:
        note += "  · identical to previous beat (frozen)"
    if not ok or same_as_prev:
        bad += 1
    print(f"  {i+1:>4} {t:7.2f}  {d:6.2f}   {note}")
    prev = got

print(f"\n  {'all beats match the page' if not bad else f'{bad} beat(s) wrong — do not ship this file'}")
sys.exit(1 if bad else 0)
