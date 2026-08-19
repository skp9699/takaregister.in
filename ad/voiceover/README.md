# Reel voiceover scripts

The customer's own Hinglish script, with five changes applied. Two cuts of the
same script — one for the page, one for paid.

| file | lines | for |
|---|---|---|
| `hi-89s-*.txt` | 15 | organic post. Meta Reels caps at 90s, so this has to stay under it |
| `hi-36s-*.txt` | 7 | paid placement, where views drop off long before 90s |

Each cut is written twice. Same words both times — only the script differs:

- **`-hinglish.txt`** — as written. Use with a multilingual generator that
  takes romanised Hindi (ElevenLabs multilingual, Play.ht, Murf).
- **`-devanagari.txt`** — same sentences in Devanagari. Use with anything
  driving a Hindi-only voice: those run a Hindi phonemiser, which reads Latin
  text as letters rather than words and produces nonsense.

Lines are separated by blank lines. One line is one visual beat in the reel, so
keep the breaks — don't paste it in as a single paragraph.

## The five changes

Everything else is untouched.

| was | is | why |
|---|---|---|
| "garment office" | "kapde ke kaam" | garment means apparel and stitching. The buyers are weavers and fabric traders — a Bhiwandi weaver reads "garment" and assumes it isn't for him |
| "Munim ji se koi chhoti galti toh nahi ho rahi?" | "Galti kisi se bhi ho sakti hai, jab saara hisaab sirf kaagaz par ho" | the munim is often a twenty-year man, and frequently the person asked to evaluate the software. Blame the arrangement, not him |
| "hum customize kar denge" | "hum sunte hain, aur agle update mein jodne ki poori koshish karte hain" | matches what was actually promised — consideration in the next update, not bespoke development on demand |
| "neeche diye gaye link par click karein" | "WhatsApp par message kijiye" | a Reel has no clickable link in frame, and WhatsApp is the CTA used everywhere else |
| — | 89s and 36s cuts | the original ran ~89s spoken. Fine organically, too long behind money |

## Timing

The video is cut to the voice, not the other way round. Once the audio exists,
what's needed back is the **start time of each line**. Lengths measured on the
in-house Kokoro build, for reference only — a different generator will differ:

```
hi-89s   88.4s total   line starts 0.4 · 9.1 · 15.6 · 22.6 · 26.2 · 31.6 · 36.9
                                   41.3 · 49.1 · 56.0 · 62.3 · 68.9 · 72.0 · 76.5 · 82.5
hi-36s   38.3s total   line starts 0.4 · 6.7 · 12.4 · 16.7 · 22.1 · 27.8 · 33.1
```

Scene tables and subtitle cues live in `../reel.html` under `T.hi89` / `T.hi36`
and get re-cut to whatever the new timings turn out to be.
