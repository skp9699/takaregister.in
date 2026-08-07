#!/usr/bin/env python3
"""
Builds a single self-contained page holding every ad image, for saving to a
phone. Mobile browsers will not reliably download a file from a chat
attachment, but they will always save an image you press and hold — so the
PNGs are embedded as data URIs rather than linked.

The output is generated, not source: it is the tracked PNGs base64-encoded,
which is why build/ad-artwork.html is gitignored. Re-run this after changing
any creative.

  python3 build_artwork_page.py
"""
import base64, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
OUT = os.path.join(B, "ad-artwork.html")

# (heading, strapline, brand key, [(file, format, dimensions, where it goes)])
GROUPS = [
    ("Taka Register", "From yarn to finished fabrics", "tr", [
        ("image-ad-feed.png",   "Feed",   "4:5 · 1080×1350", "Facebook & Instagram feed"),
        ("image-ad-square.png", "Square", "1:1 · 1080×1080", "WhatsApp ads, safest against cropping"),
        ("image-ad-story.png",  "Story",  "9:16 · 1080×1920", "Stories & Reels placement")]),
    ("Vyora — price", "Your Tally books, for less than half", "vy", [
        ("vyora-ad-feed.png",   "Feed",   "4:5 · 1080×1350", "Lead card of the carousel"),
        ("vyora-ad-square.png", "Square", "1:1 · 1080×1080", "WhatsApp ads"),
        ("vyora-ad-story.png",  "Story",  "9:16 · 1080×1920", "Stories & Reels")]),
    ("Vyora — collections", "He says thirty days. He takes forty-seven.", "vy", [
        ("vyora-coll-feed.png",   "Feed",   "4:5 · 1080×1350", "Second card of the carousel"),
        ("vyora-coll-square.png", "Square", "1:1 · 1080×1080", "WhatsApp ads"),
        ("vyora-coll-story.png",  "Story",  "9:16 · 1080×1920", "Stories & Reels")]),
]


def uri(name):
    with open(os.path.join(B, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


sections = []
for title, strap, kind, items in GROUPS:
    cards = []
    for fn, label, dims, use in items:
        kb = round(os.path.getsize(os.path.join(B, fn)) / 1024)
        cards.append(f'''      <figure class="shot {kind}">
        <img src="{uri(fn)}" alt="{html.escape(title)} — {label}" loading="lazy">
        <figcaption>
          <span class="fmt">{label}</span>
          <span class="dim">{dims}</span>
          <span class="use">{html.escape(use)}</span>
          <span class="wt">{kb} KB</span>
        </figcaption>
      </figure>''')
    sections.append(f'''    <section class="grp {kind}">
      <header class="grphd">
        <h2>{html.escape(title)}</h2>
        <p>{html.escape(strap)}</p>
      </header>
{chr(10).join(cards)}
    </section>''')

FONTS = open(os.path.join(B, "fonts.css")).read()

# Theme tokens are defined three times on purpose: bare :root for light, the
# prefers-color-scheme block for viewers who never chose (guarded so an explicit
# light choice still wins), and the [data-theme] stamp so a toggle wins too.
page = f'''<title>Ad artwork — TakaRegister &amp; Vyora</title>
<style>
{FONTS}
:root{{
  --ground:#f2f0ea; --panel:#ffffff; --edge:#ddd8cc;
  --ink:#141d2b; --ink-soft:#5c6472; --ink-faint:#8a8f9c;
  --taka:#0f1f38; --vyora:#3531a0;
  --hint-bg:#fdf6e2; --hint-edge:#e3cf92; --hint-ink:#6d5716;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --ground:#12151c; --panel:#1a1e27; --edge:#2c323e;
    --ink:#eef0f4; --ink-soft:#a3aab8; --ink-faint:#767d8b;
    --taka:#d8c98f; --vyora:#9a95ff;
    --hint-bg:#241f10; --hint-edge:#4d411f; --hint-ink:#e0cd94;
  }}
}}
:root[data-theme="dark"]{{
  --ground:#12151c; --panel:#1a1e27; --edge:#2c323e;
  --ink:#eef0f4; --ink-soft:#a3aab8; --ink-faint:#767d8b;
  --taka:#d8c98f; --vyora:#9a95ff;
  --hint-bg:#241f10; --hint-edge:#4d411f; --hint-ink:#e0cd94;
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:'DM Sans',system-ui,sans-serif;line-height:1.55;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:560px;margin:0 auto;padding:28px 18px 64px;
  display:flex;flex-direction:column;gap:34px}}
h1{{font-family:'Playfair Display',Georgia,serif;font-weight:900;
  font-size:clamp(26px,7vw,34px);line-height:1.12;margin:0 0 6px;text-wrap:balance}}
.lede{{color:var(--ink-soft);margin:0;font-size:15px}}
.hint{{display:flex;gap:10px;align-items:flex-start;
  background:var(--hint-bg);border:1px solid var(--hint-edge);color:var(--hint-ink);
  border-radius:10px;padding:12px 14px;font-size:14px;margin-top:18px}}
.hint svg{{flex:0 0 auto;width:18px;height:18px;stroke:currentColor;fill:none;
  stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;margin-top:1px}}
.grp{{display:flex;flex-direction:column;gap:16px}}
.grphd{{border-left:3px solid var(--taka);padding-left:12px}}
.grp.vy .grphd{{border-left-color:var(--vyora)}}
.grphd h2{{font-family:'Playfair Display',Georgia,serif;font-weight:900;
  font-size:20px;margin:0;letter-spacing:-.01em;color:var(--taka)}}
.grp.vy .grphd h2{{color:var(--vyora)}}
.grphd p{{margin:2px 0 0;font-size:13.5px;color:var(--ink-soft)}}
.shot{{margin:0;background:var(--panel);border:1px solid var(--edge);
  border-radius:12px;overflow:hidden}}
.shot img{{display:block;width:100%;height:auto;border-bottom:1px solid var(--edge)}}
figcaption{{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px;padding:11px 13px}}
.fmt{{font-weight:700;font-size:14px;color:var(--ink)}}
.dim{{font-size:12px;color:var(--ink-soft);font-variant-numeric:tabular-nums}}
.use{{flex-basis:100%;font-size:12.5px;color:var(--ink-faint)}}
.wt{{margin-left:auto;font-size:11.5px;color:var(--ink-faint);font-variant-numeric:tabular-nums}}
footer{{border-top:1px solid var(--edge);padding-top:16px;
  font-size:12.5px;color:var(--ink-faint)}}
</style>

<div class="wrap">
  <header>
    <h1>Ad artwork</h1>
    <p class="lede">Nine images, ready to upload — three campaigns in three sizes each.</p>
    <div class="hint">
      <svg viewBox="0 0 24 24"><path d="M12 3v12"/><path d="m7 11 5 5 5-5"/><path d="M4 20h16"/></svg>
      <span><strong>On a phone:</strong> press and hold an image, then choose Save or Download. On a computer, right-click and Save image as.</span>
    </div>
  </header>

{chr(10).join(sections)}

  <footer>All artwork 1080px wide, PNG. Sample figures and party names are illustrative — swap them for real ones before publishing.</footer>
</div>
'''

with open(OUT, "w") as f:
    f.write(page)
print(f"wrote {OUT}  ({os.path.getsize(OUT)/1048576:.2f} MB)")
