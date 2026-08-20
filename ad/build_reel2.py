#!/usr/bin/env python3
"""
Generates reel2.html — the 81s Hindi reel, in four treatments.

Everything time-related is derived, never typed: beat bounds come from the
silence analysis of the customer's own voiceover, and subtitle chunks are split
out of the script by word count. Retiming means re-running this, not editing
fifteen numbers by hand.

  python3 build_reel2.py && node render-reel.js --v screens --out build/x.mp4
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad"

TIMING = json.load(open(f"{SCRATCH}/timing.json"))
CROPS = json.load(open(f"{SCRATCH}/crops.json"))
LINES = [l.strip() for l in open(f"{HERE}/voiceover/hi-89s-devanagari.txt", encoding="utf-8") if l.strip()]
HOLD = 3.8                      # seconds the sign-off stays up after the voice ends
DUR = round(TIMING["dur"] + HOLD, 2)

# ── beat table ───────────────────────────────────────────────────────────────
# One beat per spoken line. `img` is the screenshot that carries it; None means
# the beat is built rather than shown, because no asset makes that claim.
BEATS = [
    dict(img=None, t="type",            k="वीवर और फैब्रिक ट्रेडर के लिए", h="कपड़े का पूरा काम<br>नोटबुक में?",  pain=True,
         ke="FOR WEAVERS &amp; FABRIC TRADERS", he="The whole cloth business<br>in notebooks?"),
    dict(img=None, t="type",            k="अगर वो न हों",          h="पूरा हिसाब<br>कहाँ से मिलेगा?",        pain=True,
         ke="IF HE IS AWAY",           he="Where do the<br>books come from?"),
    dict(img="m106_weaver_stock.png",   k="कारीगर के पास",        h="किस कारीगर के पास<br>कितना किलो यार्न?",
         ke="AT THE KARIGAR",          he="Which karigar holds<br>how many kilos?"),
    dict(img="r13_fabric_at_dyer.png",  k="डाइंग में",            h="कितने ताके<br>फंसे हैं?",
         ke="AT THE DYER",             he="How many taka<br>are stuck?"),
    dict(img=None, t="type",            k="जब हिसाब कागज पर हो",  h="छोटी सी चूक,<br>बड़ा नुकसान।",         pain=True,
         ke="WHEN IT IS ALL ON PAPER", he="A small slip,<br>a big loss."),
    dict(img="m103_drawer.png",         k="अब",                   h="हिसाब स्क्रीन पर।",
         ke="NOW",                     he="The books,<br>on a screen."),
    dict(img="screens-2649.png",        k="हर स्टेज",             h="यार्न से फिनिश<br>कपड़े तक।",
         ke="EVERY STAGE",             he="Yarn to<br>finished cloth."),
    dict(img="m102_home_dashboard.png", k="सारा हिसाब एक ही जगह", h="किलो, ताके, मीटर।",
         ke="ALL IN ONE PLACE",        he="Kilos, taka, metres."),
    dict(img=None, t="variance",        k="भेजा और आया",          h="फर्क तुरंत सामने।",
         ke="SENT AND RECEIVED",       he="The gap, at once."),
    dict(img="r03_stock_ageing.png",    k="कितने दिनों से",       h="माल वहीं फंसा<br>पड़ा है।",
         ke="HOW MANY DAYS",           he="Stuck in the<br>same place."),
    dict(img="m130_sync.png",           k="विंडोज और एंड्रॉइड",   h="मोबाइल या<br>कंप्यूटर पर।",
         ke="WINDOWS AND ANDROID",     he="On your phone<br>or computer."),
    dict(img=None, t="tagline",         k="",                     h="स्टॉक सही,<br>तो बिजनेस सही।",
         ke="",                        he="Stock right,<br>business right."),
    dict(img=None, t="type",            k="जो आप कहेंगे",         h="अगले अपडेट में<br>जोड़ने की कोशिश।",
         ke="WHAT YOU ASK FOR",        he="Goes into the<br>next update."),
    dict(img=None, t="cta",             k="",                     h="", ke="", he=""),
]

assert len(LINES) == len(BEATS) == len(TIMING["starts"]), \
    f"{len(LINES)} lines, {len(BEATS)} beats, {len(TIMING['starts'])} timed"

# ── scene bounds: midpoint of each inter-line gap ────────────────────────────
S, E = TIMING["starts"], TIMING["ends"]
bounds = [0.0] + [(E[i] + S[i + 1]) / 2 for i in range(len(BEATS) - 1)] + [DUR]
# the last beat absorbs the hold; every other bound is the voice
for i, b in enumerate(BEATS):
    b["s"] = round(bounds[i], 2)
    b["d"] = round(bounds[i + 1] - bounds[i], 2)
    if b.get("img"):
        meta = CROPS[b["img"]]
        assert not meta.get("text_only"), (
            f'beat {i+1} shows {b["img"]}, which is a statement card with no screen on it. '
            "Under a headline that is two headlines on one frame — give the beat a real "
            "screen or set t='type'.")
        b["crop"] = meta["t"]

# ── subtitles: split each line into glanceable chunks ────────────────────────
# Break on the punctuation the writer already put in; fall back to word count.
# Time is shared out by words, which tracks the read closely enough at this size.
def chunks(text, lo, hi):
    parts = [p.strip() for p in re.split(r'(?<=[,।?—.])\s+', text) if p.strip()]
    # A line with no internal punctuation arrives as one long part — split it on
    # word count too, or it renders as a plate wider than the frame.
    MAXW = 8
    # Never end a plate on a word that governs the next one. "1000 मीटर की" /
    # "जगह 950 मीटर" reads as a fragment; the break belongs before "की जगह".
    HANG = {"की", "के", "का", "से", "में", "पर", "और", "या", "को", "तक", "कि", "जब", "तो",
            # English needs its own list, or a plate ends on "should have. The"
            "the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "for", "from",
            "with", "where", "when", "that", "which", "how", "is", "are", "was", "were",
            "has", "have", "had", "should", "will", "would", "can", "your", "our", "it",
            "this", "these", "no", "not", "one", "so", "as", "by", "up", "out", "into"}
    split = []
    for p in parts:
        ws = p.split()
        if len(ws) <= MAXW:
            split.append(p); continue
        n = -(-len(ws) // MAXW)
        size = -(-len(ws) // n)
        cuts, i = [], 0
        while i < len(ws):
            j = min(i + size, len(ws))
            if j < len(ws):                            # pull the break back off a hanging word
                for back in (0, 1, 2, 3, 4):
                    tok = ws[j - 1 - back].strip("।,?—.").lower()
                    if tok not in HANG and not tok.isdigit():
                        j -= back; break
            cuts.append(" ".join(ws[i:j])); i = j
        split += cuts
    merged = []
    for p in split:
        if merged and len(merged[-1].split()) + len(p.split()) <= MAXW:
            merged[-1] += " " + p
        else:
            merged.append(p)
    out, w = [], [len(m.split()) for m in merged]
    tot, t = sum(w), lo
    for m, n in zip(merged, w):
        dt = (hi - lo) * n / tot
        out.append([round(t, 2), round(t + dt, 2), m])
        t += dt
    return out

CUES = []
for i, line in enumerate(LINES):
    CUES += chunks(line, S[i], E[i])

# The audio stays Hindi; these are what an English-text cut shows while it plays.
# Same 15 bounds, so nothing about the timeline moves.
LINES_EN = [l.strip() for l in open(f"{HERE}/voiceover/hi-89s-english-subs.txt", encoding="utf-8")
            if l.strip() and not l.startswith("#")]
assert len(LINES_EN) == len(LINES), len(LINES_EN)
CUES_EN = []
for i, line in enumerate(LINES_EN):
    CUES_EN += chunks(line, S[i], E[i])

js = lambda o: json.dumps(o, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="hi" id="root">
<head>
<meta charset="utf-8">
<title>Taka Register — Reel</title>
<link rel="stylesheet" href="build/fonts.css">
<link rel="stylesheet" href="build/fonts-hi.css">
<style>
:root{{
  --navy:#0f1f38; --teal:#1a7a6e; --gold:#c9a84c; --gold-dk:#a8862f;
  --paper:#f4f2ec; --ink:#0f1f38; --muted:#6f7787; --line:#e2ddd1;
  --red:#b8483d; --amber:#c9861f;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:540px;height:960px;overflow:hidden;background:#000}}
body{{font-family:'DM Sans','Noto Sans Devanagari',sans-serif;-webkit-font-smoothing:antialiased}}
#stage{{position:relative;width:540px;height:960px;overflow:hidden;background:var(--paper)}}
.warp{{position:absolute;inset:0;
  background:repeating-linear-gradient(90deg,transparent,transparent 22px,rgba(15,31,56,.022) 22px,rgba(15,31,56,.022) 23px)}}

/* Meta covers the top 14% and bottom 35% of a 9:16 frame. Everything that has
   to be read lives between them. */
.safe{{position:absolute;left:0;right:0;top:125px;height:499px}}
.beat{{position:absolute;inset:0;opacity:0;will-change:opacity}}
.ctr{{position:absolute;left:30px;right:30px}}

.kick{{font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--teal);
  text-transform:uppercase;letter-spacing:.02em}}
.head{{font-family:'Playfair Display','Noto Serif Devanagari',serif;font-weight:900;
  color:var(--ink);line-height:1.16;letter-spacing:0}}

/* screenshot, cropped to its densest region and scaled near 1:1 so the type
   inside it survives a phone screen */
.shot{{position:absolute;overflow:hidden;border-radius:10px;
  box-shadow:0 14px 40px rgba(15,31,56,.20);border:1px solid rgba(15,31,56,.10)}}
.shot img{{position:absolute;display:block;image-rendering:auto}}
.bg{{position:absolute;inset:0;overflow:hidden}}
.bg img{{position:absolute;display:block;filter:saturate(.55)}}
.bg::after{{content:'';position:absolute;inset:0;background:rgba(244,242,236,.86)}}
.rail{{position:absolute;left:26px;width:4px;height:74px;border-radius:2px;background:var(--gold)}}
.trule{{position:absolute;left:50%;top:300px;height:4px;border-radius:2px;background:var(--gold);width:0;transform:translateX(-50%)}}

/* ── variance panel: the one claim no screenshot makes ── */
.vp{{position:absolute;left:30px;right:30px;background:#fff;border:1px solid var(--line);
  border-radius:12px;padding:13px 15px;box-shadow:0 4px 16px rgba(15,31,56,.08)}}
.vh{{display:flex;justify-content:space-between;font-size:9.5px;font-weight:700;
  letter-spacing:.10em;color:var(--muted);text-transform:uppercase;
  padding-bottom:8px;border-bottom:1px solid var(--line)}}
.vr{{display:flex;align-items:baseline;justify-content:space-between;padding:16px 0 14px;
  border-bottom:1px dotted #e0dacb}}
.vr:last-child{{border-bottom:0;padding-bottom:2px}}
.vr .lb{{font-size:12px;font-weight:700;color:var(--ink);flex:0 0 62px}}
.vr .cell{{text-align:right;flex:1}}
.vr .cap{{display:block;font-size:9px;color:var(--muted);letter-spacing:.02em}}
.vr .num{{display:block;font-family:'Playfair Display','Noto Serif Devanagari',serif;
  font-size:22px;font-weight:900;color:#3d4757;font-variant-numeric:lining-nums tabular-nums;line-height:1.1}}
.vr .gap{{flex:0 0 84px;text-align:right}}
.vr .gap .num{{font-size:26px}}
.up .gap .num{{color:var(--red)}}
.dn .gap .num{{color:var(--amber)}}
.vfoot{{position:absolute;left:30px;right:30px;display:flex;align-items:center;gap:9px;
  background:rgba(26,122,110,.10);border:1.5px solid rgba(26,122,110,.45);
  border-radius:10px;padding:11px 13px}}
.vfoot svg{{flex:0 0 auto;width:17px;height:17px;stroke:var(--teal);fill:none;stroke-width:2.6;
  stroke-linecap:round;stroke-linejoin:round}}
.vfoot span{{font-size:12.5px;font-weight:700;color:var(--ink)}}

/* ── tagline + sign-off ── */
.tag{{position:absolute;left:30px;right:30px;text-align:center}}
.tag .big{{font-family:'Playfair Display','Noto Serif Devanagari',serif;font-weight:900;
  font-size:42px;line-height:1.16;color:var(--ink)}}
.tag .rule{{height:5px;border-radius:3px;background:var(--gold);margin:20px auto 0;width:0}}
.brand{{position:absolute;left:30px;right:30px;text-align:center;
  font-family:'Playfair Display','Noto Serif Devanagari',serif;font-size:36px;font-weight:900;color:var(--ink)}}
.brand i{{font-style:normal;color:var(--gold-dk)}}
.cta{{position:absolute;left:30px;right:30px;display:flex;align-items:center;justify-content:center;
  background:var(--navy);color:#fff;border-radius:9px;height:50px;font-size:16px;font-weight:700}}
.cta u{{text-decoration:none;color:var(--gold)}}
.sub{{position:absolute;left:30px;right:30px;text-align:center;font-size:13px;color:#3d4757}}
.contact{{position:absolute;left:30px;right:30px;display:flex;flex-direction:column;gap:7px}}
.contact div{{display:flex;align-items:center;gap:9px;font-size:12.5px;color:#3d4757;
  background:rgba(255,255,255,.72);border:1px solid var(--line);border-radius:8px;padding:8px 11px}}
.contact svg{{flex:0 0 auto;width:14px;height:14px;stroke:var(--gold-dk);fill:none;stroke-width:1.9;
  stroke-linecap:round;stroke-linejoin:round}}
.contact b{{font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}}

/* ── subtitles, held inside the safe band ── */
#subs{{position:absolute;left:24px;right:24px;bottom:352px;text-align:center;opacity:0}}
#subs .t{{display:inline-block;background:rgba(15,31,56,.94);color:#fff;
  font-size:15.5px;font-weight:600;line-height:1.36;padding:8px 14px;border-radius:8px;
  box-shadow:0 5px 16px rgba(0,0,0,.22)}}
</style>
</head>
<body>
<div id="stage">
  <div class="warp"></div>
  <div class="bg" id="bg"><img id="bgimg" alt=""></div>
  <div class="safe" id="safe"></div>
  <div id="subs"><span class="t" id="subt"></span></div>
</div>
<script>
const Q=new URLSearchParams(location.search);
// v is style, optionally suffixed -en for the English-text cut. The audio is
// Hindi either way — the suffix only changes what is printed on the frame.
const RAW=Q.get('v')||'screens';
const EN=/-en$/.test(RAW);
const STYLE=RAW.replace(/-en$/,'');          // screens | type | split | mixed
const SUBS_ON=!Q.get('nosubs');
const BEATS={js(BEATS)};
const CUES=EN?{js(CUES_EN)}:{js(CUES)};
const DUR={DUR};
const K=b=>EN?(b.ke!==undefined?b.ke:b.k):b.k;
const H=b=>EN?(b.he!==undefined?b.he:b.h):b.h;
const TXT=EN?{{
  vh:['GOODS','SENT → RECEIVED','GAP'], yarn:'Yarn', cloth:'Cloth',
  sent:'sent', went:'went', came:'came', more:'over', less:'short',
  kg:' kg', m:' m',
  vfoot:'The gap shows up before the payment goes out.',
  brand:'Taka <i>Register</i>', tag:'Fabric stock right. Business right. Better margins.',
  cta:'Free demo &nbsp;·&nbsp; message us on&nbsp;<u>WhatsApp</u>',
  place:'Bhiwandi, Maharashtra',
  foot:'<b style="color:#a8862f">takaregister.in</b> &nbsp;·&nbsp; for weavers &amp; fabric traders · Bhiwandi'
}}:{{
  vh:['माल','भेजा → आया','फर्क'], yarn:'यार्न', cloth:'कपड़ा',
  sent:'भेजा', went:'गया', came:'आया', more:'ज्यादा', less:'कम',
  kg:' किलो', m:' मी',
  vfoot:'फर्क तुरंत सामने — पेमेंट जाने से पहले।',
  brand:'टका <i>रजिस्टर</i>', tag:'फैब्रिक स्टॉक सही। बिजनेस सही। मार्जिन बेहतर।',
  cta:'फ्री डेमो &nbsp;·&nbsp; <u>WhatsApp</u>&nbsp;पर मैसेज कीजिए',
  place:'भिवंडी, महाराष्ट्र',
  foot:'<b style="color:#a8862f">takaregister.in</b> &nbsp;·&nbsp; वीवर और ट्रेडर के लिए · भिवंडी'
}};

const cl=(v,a,b)=>Math.max(a,Math.min(b,v));
const eOut=t=>1-Math.pow(1-cl(t,0,1),3);
const eIO=t=>{{t=cl(t,0,1);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}};
const pr=(x,s,d)=>cl((x-s)/d,0,1);
const $=id=>document.getElementById(id);
const set=(el,o)=>{{for(const k in o) el.style[k]=o[k];}}
const grp=n=>n.toLocaleString('en-IN');

// Which treatment a beat gets. Built beats (variance, tagline, cta) ignore the
// style; picture beats follow it. `mixed` shows the product for anything that
// proves a claim and drops to type for the beats that only accuse.
function treat(b){{
  if(b.t) return b.t;
  if(STYLE==='type') return 'type';
  if(STYLE==='mixed') return b.pain ? 'type' : 'shot';
  return 'shot';
}}

const SAFE_W=540, BAND_H=499;
function shotBox(crop, maxW, maxH){{
  const [,,cw,ch]=crop, s=Math.min(maxW/cw, maxH/ch);
  return {{w:Math.round(cw*s), h:Math.round(ch*s), s}};
}}
function mountShot(el, img, crop, box){{
  const [cx,cy,,]=crop;
  el.style.width=box.w+'px'; el.style.height=box.h+'px';
  const im=el.querySelector('img');
  im.style.width=Math.round(1080*box.s)+'px';
  im.style.left=Math.round(-cx*box.s)+'px';
  im.style.top =Math.round(-cy*box.s)+'px';
}}

const svgTick='<svg viewBox="0 0 24 24"><path d="m5 13 4 4L19 7"/></svg>';
const ICON={{
  ph:'<svg viewBox="0 0 24 24"><path d="M4 5c0 9 6 15 15 15l2-3-4-2-2 2a12 12 0 0 1-6-6l2-2-2-4z"/></svg>',
  web:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18"/></svg>',
  pin:'<svg viewBox="0 0 24 24"><path d="M12 21s7-6 7-11a7 7 0 1 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'
}};

// ── build the DOM once; renderAt only animates ───────────────────────────────
const safe=$('safe');
BEATS.forEach((b,i)=>{{
  const d=document.createElement('div');
  d.className='beat'; d.id='b'+i;
  const tr=treat(b);
  if(tr==='shot'){{
    // `split` gives the words the room and the picture the supporting role;
    // `screens` does the reverse. Same beat, opposite emphasis.
    const wide = STYLE!=='split';
    const box=shotBox(b.crop, wide?480:404, wide?330:276);
    const hx = wide ? 30 : 44, hs = wide ? 25 : 31;
    d.innerHTML=
      (wide?'':`<div class="rail" style="top:26px"></div>`)+
      `<div class="ctr kick" style="top:12px${{wide?'':';left:44px'}}">${{K(b)}}</div>`+
      `<div class="ctr head" style="top:${{hx}}px;font-size:${{hs}}px${{wide?'':';left:44px'}}">${{H(b)}}</div>`+
      `<div class="shot" style="left:${{Math.round((SAFE_W-box.w)/2)}}px;top:${{BAND_H-box.h-64}}px">`+
        `<img src="assets/shortlist/${{b.img}}" alt=""></div>`;
    mountShot(d.querySelector('.shot'), b.img, b.crop, box);
  }} else if(tr==='type'){{
    d.innerHTML=
      (K(b)?`<div class="ctr kick" style="top:138px;text-align:center">${{K(b)}}</div>`:'')+
      `<div class="ctr head" style="top:168px;font-size:44px;text-align:center">${{H(b)}}</div>`+
      `<div class="trule"></div>`;
  }} else if(tr==='variance'){{
    d.innerHTML=
      `<div class="ctr kick" style="top:12px">${{K(b)}}</div>`+
      `<div class="ctr head" style="top:30px;font-size:25px">${{H(b)}}</div>`+
      `<div class="vp" style="top:118px">`+
        `<div class="vh"><span>${{TXT.vh[0]}}</span><span>${{TXT.vh[1]}}</span><span>${{TXT.vh[2]}}</span></div>`+
        `<div class="vr up"><span class="lb">${{TXT.yarn}}</span>`+
          `<span class="cell"><span class="cap">${{TXT.sent}}</span><span class="num" data-n="500" data-u="${{TXT.kg}}">0</span></span>`+
          `<span class="cell"><span class="cap">${{TXT.went}}</span><span class="num" data-n="600" data-u="${{TXT.kg}}">0</span></span>`+
          `<span class="gap"><span class="cap">${{TXT.more}}</span><span class="num" data-n="100" data-p="+">0</span></span></div>`+
        `<div class="vr dn"><span class="lb">${{TXT.cloth}}</span>`+
          `<span class="cell"><span class="cap">${{TXT.sent}}</span><span class="num" data-n="1000" data-u="${{TXT.m}}">0</span></span>`+
          `<span class="cell"><span class="cap">${{TXT.came}}</span><span class="num" data-n="950" data-u="${{TXT.m}}">0</span></span>`+
          `<span class="gap"><span class="cap">${{TXT.less}}</span><span class="num" data-n="50" data-p="−">0</span></span></div>`+
      `</div>`+
      `<div class="vfoot" style="top:334px">${{svgTick}}<span>${{TXT.vfoot}}</span></div>`;
  }} else if(tr==='tagline'){{
    d.innerHTML=`<div class="tag" style="top:170px"><div class="big">${{H(b)}}</div><div class="rule"></div></div>`;
  }} else if(tr==='cta'){{
    const contacts = (STYLE==='split');
    d.innerHTML=
      `<div class="brand" style="top:${{contacts?70:104}}px">${{TXT.brand}}</div>`+
      `<div class="sub" style="top:${{contacts?118:154}}px;font-size:12.5px">${{TXT.tag}}</div>`+
      `<div class="cta" style="top:${{contacts?160:196}}px">${{TXT.cta}}</div>`+
      (contacts
        ? `<div class="contact" style="top:228px">`+
            `<div>${{ICON.ph}}<b>+91 78209 86133</b></div>`+
            `<div>${{ICON.web}}<span>www.takaregister.in</span></div>`+
            `<div>${{ICON.pin}}<span>${{TXT.place}}</span></div>`+
          `</div>`
        : `<div class="sub" style="top:266px;font-size:12px;color:#6f7787">${{TXT.foot}}</div>`);
  }}
  safe.appendChild(d);
}});

// No backdrop in any style. The assets are text graphics; dimmed behind a
// headline they read as a smudge, and their English shows through a Hindi cut.
$('bg').style.display='none';

function renderAt(t){{
  t=cl(t,0,DUR);
  let active=null;
  BEATS.forEach((b,i)=>{{
    const el=$('b'+i), XF=0.34;
    let a=0;
    if(t>=b.s-XF && t<=b.s+b.d+XF)
      a=cl(Math.min(pr(t,b.s-XF*.5,XF), 1-pr(t,b.s+b.d-XF*.5,XF)),0,1);
    el.style.opacity=a;
    el.style.display=a<=0.002?'none':'block';
    if(a>0.002){{ anim(el,b,t-b.s); if(!active||a>0.5) active=b; }}
  }});
  const box=$('subs');
  if(!SUBS_ON){{ box.style.opacity=0; return; }}
  const c=CUES.find(c=>t>=c[0]&&t<c[1]);
  if(c){{ $('subt').textContent=c[2];
          box.style.opacity=Math.min(pr(t,c[0],.13), 1-pr(t,c[1]-.11,.11)); }}
  else box.style.opacity=0;
}}

function anim(el,b,x){{
  const tr=treat(b);
  const k=el.querySelector('.kick'), h=el.querySelector('.head');
  if(k) set(k,{{opacity:eOut(pr(x,.05,.45)),transform:`translateY(${{(1-eOut(pr(x,.05,.45)))*10}}px)`}});
  if(h) set(h,{{opacity:eOut(pr(x,.14,.6)),transform:`translateY(${{(1-eOut(pr(x,.14,.6)))*16}}px)`}});
  if(tr==='shot'){{
    const s=el.querySelector('.shot'), p=pr(x,.34,.75);
    set(s,{{opacity:eOut(p),transform:`translateY(${{(1-eOut(p))*26}}px) scale(${{.975+eOut(p)*.025}})`}});
  }} else if(tr==='type'){{
    const r=el.querySelector('.trule');
    if(r) r.style.width=(eIO(pr(x,.55,.85))*116)+'px';
  }} else if(tr==='variance'){{
    const p=pr(x,.45,.7);
    set(el.querySelector('.vp'),{{opacity:eOut(p),transform:`translateY(${{(1-eOut(p))*18}}px)`}});
    // the two rows count up in turn, so the gap reads as a number and not a word
    el.querySelectorAll('.vr').forEach((row,ri)=>{{
      const g=eIO(pr(x,1.0+ri*.95,1.15));
      set(row,{{opacity:eOut(pr(x,.85+ri*.95,.5))}});
      row.querySelectorAll('.num').forEach(n=>{{
        const v=Math.round(+n.dataset.n*g);
        n.textContent=(n.dataset.p||'')+grp(v)+(n.dataset.u||'');
      }});
    }});
    const f=pr(x,3.3,.6);
    set(el.querySelector('.vfoot'),{{opacity:eOut(f),transform:`translateY(${{(1-eOut(f))*14}}px)`}});
  }} else if(tr==='tagline'){{
    const p=pr(x,.06,.7);
    set(el.querySelector('.tag'),{{opacity:eOut(p),transform:`scale(${{.93+eOut(p)*.07}})`}});
    el.querySelector('.rule').style.width=(eIO(pr(x,.6,.8))*58)+'%';
  }} else if(tr==='cta'){{
    const q=[['.brand',.05],['.sub',.35],['.cta',.6],['.contact',.9],['.sub:last-of-type',.9]];
    el.querySelectorAll('.brand,.sub,.cta,.contact').forEach((n,i)=>{{
      const p=pr(x,.05+i*.26,.6);
      set(n,{{opacity:eOut(p),transform:`translateY(${{(1-eOut(p))*14}}px)`}});
    }});
  }}
}}

window.renderAt=renderAt;
window.AD_DURATION=DUR;
window.__SC=BEATS.map(b=>[('b'+BEATS.indexOf(b)),b.s,b.d]);
window.__CUES=CUES;
window.__imagesReady=Promise.all(
  [...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{{i.onload=i.onerror=r;}})));
document.documentElement.lang = EN ? 'en' : 'hi';
renderAt(0);
if(!location.search.includes('render'))
  window.addEventListener('load',()=>{{const t0=performance.now();
    (function l(n){{const t=(n-t0)/1000;renderAt(t);if(t<DUR)requestAnimationFrame(l);}})(t0);}});
</script>
</body>
</html>
"""

open(f"{HERE}/reel2.html", "w", encoding="utf-8").write(HTML)
print(f"wrote reel2.html  ({len(HTML)/1024:.0f} KB)")
print(f"\n  {'#':>3} {'start':>6} {'dur':>6}  {'treatment':<10} asset")
for i, b in enumerate(BEATS):
    print(f"  {i+1:>3} {b['s']:6.2f} {b['d']:6.2f}  {b.get('t','shot'):<10} {b.get('img') or '—'}")
print(f"\n  {len(CUES)} subtitle cues, total {DUR}s")
