# Taka Register — animated video ad

A 58-second vertical (1080×1920) ad for Taka Register and Vyora, built from the
claims already made on `index.html` and the shipped features in `version.json`.
Everything here is reproducible: `ad.html` is the animation, `render.js` turns it
into video, `build_audio.py` adds narration.

---

## 1. What the ad should say

### A. Open on the problem — don't open on the product

A mill owner scrolling past will not stop for "comprehensive ERP platform". They
stop for a question they can't answer about their own mill. So the ad opens cold
on **"Where is your yarn?"** with three units — twister, dyer, weaver — and a
question mark where the quantity should be.

Then a fast stack of four pains, all of them real and all of them expensive:

| The pain | Why it costs money |
|---|---|
| Bill booked, yarn still in transit | Today's stock shows goods that aren't in the building |
| Yarn moved twister → dyer | Off one unit's book, onto nobody's. It simply disappears |
| Weaver's bill — right or wrong? | Settled by argument, not arithmetic |
| Forty takas at the dyer, since when? | Nobody counts the days, so nobody chases |

### B. The problem-solvers — this is the heart of the ad

Ranked by how sharp and how *felt* the pain is. The first four are the strongest
because each one names a specific failure the trade already recognises.

**1. Yarn stays on the books wherever it goes.** ⭐ *strongest*
Purchase → twisting → dyeing → sizing → weaver, location-wise, in kilos. The
version 1.0.20 fix says exactly why this matters: yarn a twister doubled and sent
on to a dyeing unit used to be credited *only* to the twister, so yarn delivered
anywhere else vanished from stock entirely. Every mill has felt this and blamed
the staff.
> *"Every kilo. Every location."*

**2. Stock that doesn't lie about goods in transit.** ⭐
Park a purchase on **DELIVERY PENDING** when the bill is on file but the yarn
hasn't come in; give it a **DELIVERED ON** date and stock counts it from the day
it lands, not the day the bill was written. One click — *Awaiting Delivery* —
answers "what have I bought that hasn't turned up yet?"
> *"Your stock stops lying."*

**3. Loom-wise production, not a weekly guess.** ⭐
TDS cards, warping registers, output per loom in real time. Which loom earned its
keep this week is a number, not an opinion.

**4. Bills checked to the paisa.** ⭐
The Weaver Bill and Dyeing Bill checkers price the work against your own rates
and formulas. This turns a monthly argument into a monthly reconciliation.

**5. Grey lying at the dyer, aged by the day.**
Grey in Dyeing shows sent − received per challan *with days-out ageing*. Forty
takas sitting nineteen days is dead capital that nobody was counting.

**6. Your Tally books when you're not at the office (Vyora).** ⭐
A desktop agent mirrors Tally to your own Drive; the phone app is a fast
read-only window. Party ledgers, outstanding, item stock, registers — no exports,
no emailed screenshots.

**7. How long each party *actually* takes to pay (Vyora).** ⭐ *most under-sold*
Not just who owes what, but the **average pay cycle** per party, shown next to
the oldest bill due. "He says thirty days, he takes forty-seven" is the kind of
line that sells software on its own, and nobody else in this segment offers it.

**8. It speaks your register's language.**
Every purchase line carries a stable **DB ID** to write beside the entry in the
paper register. It never changes when you edit the bill and is never reused. This
is the point that tells a paper-first business the software respects how they
already work — worth more than any feature list.

### C. Trust — the objection block

For a family business, these three kill the objection before it's raised:

- **On your device, in your own Google Drive. Never on our servers — not one row.**
- **Power cut? Keep working.** Fully offline; syncs when the line is back.
- **A WhatsApp line to the people who built it.** Not a call centre.

### D. Close

Both products named, `takaregister.in`, Windows + Android, and
**Bhiwandi · Ichalkaranji · Erode** — the belt should see itself in the ad.

### Deliberately left out

Cut for time; they slow a 58-second edit and are better on the website:
Roll/Putha, Temp Challans, Sale Register ↔ order linking, Physical Stock counts,
Job Stock Closures, Trader Reports, the configurable sidebar, licensing.

---

## 2. Building it

```bash
node render.js                 # ad.html → build/takaregister-ad-silent.mp4
python3 build_audio.py         # + narration and music bed → build/takaregister-ad.mp4
```

`ad.html` opened in a browser plays the ad live. The animation is driven entirely
by `renderAt(t)`, so the renderer steps a clock rather than recording real time —
a slow machine produces exactly the same frames as a fast one.

Useful flags: `node render.js --fps 30 --scale 2 --crf 20`. For a square or
landscape cut, change the `540×960` stage in `ad.html` and the viewport in
`render.js` together, then re-check the scene offsets.

### Re-timing the narration

`voiceover.txt` is `START | MAX_SECONDS | TEXT`. `START` must match the scene
table (`SC[]`) in `ad.html`. `build_audio.py` re-runs espeak progressively faster
until each line fits its `MAX`, and prints the words-per-minute it settled on —
**anything above about 220 wpm is being rushed**, so shorten the line rather than
let it speed up. Commas beat full stops: a period makes espeak insert a long
pause, which forces the rest of the line to be read faster to compensate.

---

## 3. About the voice track — read this before publishing

The narration is **espeak-ng**, a formant synthesiser. It is correctly timed and
perfectly clear, but it sounds synthetic — it is a **scratch track for approving
the edit**, not a broadcast voice.

Neural voices (Piper) could not be installed here: the model files live on
huggingface.co, which this environment's network policy blocks.

For the published cut, replace the voice and keep everything else:

1. Record the lines in `voiceover.txt` — a human read, or a commercial TTS
   (ElevenLabs, Google Cloud, Azure all have good Indian-English and Hindi voices).
2. Drop the clips into `build/vo/` as `vo0.wav` … `vo8.wav` at 48 kHz mono.
3. Re-run `build_audio.py`; the mix and mux are unchanged.

Keep each recording under the `MAX` in `voiceover.txt` or the narration will run
past its scene.

### Language

This cut is English, matching the website and the app UI. For the belt itself,
Hindi (Bhiwandi), Marathi (Ichalkaranji) and Tamil (Erode) versions would almost
certainly convert better. The pipeline supports it — `build_audio.py --voice hi`
already works — but on-screen text would need a Devanagari or Tamil font embedded
in `build/fonts.css`, replacing the current Latin-only subset.
