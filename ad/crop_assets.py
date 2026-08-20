#!/usr/bin/env python3
"""
Works out which part of each supplied PNG to show.

A reel frame can only hold about a third of a 1080x1920 card at readable size,
so every asset has to be cropped. The first version of this maximised ink inside
a fixed-height window, which sliced straight through lines of type — "Open the
app." lost its top, "on your books." lost its bottom. It looked deliberate
because it was consistently wrong.

This one finds the horizontal whitespace bands between rows of type first, and
only ever cuts along those. A crop can be a little taller or shorter than asked
for, but it can never land mid-line.

  python3 crop_assets.py
"""
import json, glob, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"

# Assets whose own headline must not appear. m102's card reads "The whole mill
# is on one screen" — "mill" is the word the customer struck out early on, so
# the crop starts below it and shows only the device.
FLOOR = {"m102_home_dashboard.png": "device"}

TARGET = {"t": 700, "w": 980}          # tight and wide variants


def profile(im):
    """Ink per row and the horizontal extent of content, against the corner colour."""
    W, H = im.size
    px = im.load()
    bg = px[6, 6]
    ink = lambda c: abs(c[0]-bg[0]) + abs(c[1]-bg[1]) + abs(c[2]-bg[2]) > 40
    step = 3
    xs = list(range(0, W, step))
    rows = [0] * H
    for y in range(0, H, step):
        n = sum(ink(px[x, y]) for x in xs)
        for yy in range(y, min(y + step, H)):
            rows[yy] = n
    cols = [sum(ink(px[x, y]) for y in range(0, H, step * 3)) for x in xs]
    thr = max(cols) * 0.06 if max(cols) else 0
    on = [xs[i] for i, v in enumerate(cols) if v > thr]
    x0, x1 = (min(on), max(on) + step) if on else (0, W)
    return rows, max(0, x0 - 14), min(W, x1 + 14)


def device_top(im):
    """First row of the dark device mock, so a crop can start at the screenshot
    rather than at the card's own headline."""
    W, H = im.size
    px = im.load()
    dark = lambda c: c[0] < 70 and c[1] < 80 and c[2] < 110
    for y in range(0, H, 4):
        if sum(dark(px[x, y]) for x in range(0, W, 4)) > (W / 4) * 0.35:
            return max(0, y - 12)
    return 0


def cut_lines(rows, H):
    """Rows where nothing is printed, collapsed to one candidate per band.
    These are the only places a crop is allowed to begin or end."""
    peak = max(rows) if rows else 0
    quiet = [y for y in range(H) if rows[y] <= peak * 0.02]
    bands, run = [], []
    for y in quiet:
        if run and y == run[-1] + 1:
            run.append(y)
        else:
            if run:
                bands.append(run)
            run = [y]
    if run:
        bands.append(run)
    # a band one pixel tall is noise between two glyphs, not a gap between lines
    cuts = [b[len(b) // 2] for b in bands if len(b) >= 4]
    return sorted(set([0] + cuts + [H]))


def best_crop(path, target, floor=0):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    rows, x0, x1 = profile(im)
    pre = [0]
    for v in rows:
        pre.append(pre[-1] + v)
    cuts = [c for c in cut_lines(rows, H) if c >= floor]
    if len(cuts) < 2:
        return [x0, floor, x1 - x0, min(target, H - floor)]
    lo, hi = int(target * 0.72), int(target * 1.30)
    best, box = -1.0, None
    for i, a in enumerate(cuts):
        for b in cuts[i + 1:]:
            h = b - a
            if h < lo or h > hi:
                continue
            density = (pre[b] - pre[a]) / h            # ink per row, not total
            # prefer heights near the target so the scale stays consistent
            fit = 1.0 - abs(h - target) / target * 0.45
            score = density * fit
            if score > best:
                best, box = score, [x0, a, x1 - x0, h]
    return box or [x0, floor, x1 - x0, min(target, H - floor)]


out = {}
files = sorted(glob.glob(f"{HERE}/assets/shortlist/*.png")) + sorted(glob.glob(f"{HERE}/assets/screens-*.png"))
for p in files:
    n = os.path.basename(p)
    floor = 0
    if FLOOR.get(n) == "device":
        floor = device_top(Image.open(p).convert("RGB"))
    out[n] = {k: best_crop(p, t, floor) for k, t in TARGET.items()}

json.dump(out, open(f"{SCRATCH}/crops.json", "w"))
print(f"{len(out)} assets cropped on whitespace boundaries")
for k in ("m102_home_dashboard.png", "03_promise.png", "m130_sync.png",
          "m106_weaver_stock.png", "screens-2649.png", "r03_stock_ageing.png"):
    if k in out:
        print(f"  {k:28} tight {out[k]['t']}")
