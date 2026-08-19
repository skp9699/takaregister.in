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
hi-89s   93.1s total   line starts 0.4 · 8.7 · 15.0 · 22.1 · 25.4 · 28.9 · 37.8
                                   42.1 · 47.9 · 54.6 · 65.7 · 70.5 · 77.1 · 80.1 · 86.9
hi-36s   41.0s total   line starts 0.4 · 6.7 · 14.8 · 19.1 · 25.8 · 30.6 · 35.9
```

**The long cut measures 93.1s here, 3s past Meta's 90s Reels cap.** Left
untrimmed on the customer's instruction. Most commercial Hindi TTS reads faster
than this in-house Kokoro build, so a different generator may land under on its
own; if it does not, the cut posts as a feed video rather than a Reel.

Two lines were added after the first pass and are why it grew:

- **line 3, the karigar question.** Yarn sitting with a job weaver is the
  hardest quantity to know and the easiest to lose, so it goes ahead of the
  godown question. Line 4 then drops the repeated "yarn".
- **line 10, shortage and excess.** 600 kilo went out where 500 should have;
  950 metres came back where 1000 should have. At 10.6s it is the longest beat
  in the script, which suits an analysis screen that has to fill in.

`WhatsApp` is deliberately Latin inside the Devanagari file — व्हाट्सएप gets
phonemised as Hindi syllables and comes out wrong. Numerals are safe as digits:
"500 किलो" and "पाँच सौ किलो" synthesise to the same 3.63s, so they are being
expanded rather than skipped.

The short cut is 41s rather than 36s because its one concrete question has to
name both trades. Asking only "kitna kilo yarn pada hai" speaks to weavers and
says nothing to a fabric trader who buys no yarn at all, so line 2 asks about
taake as well and line 4 names all three units — kilo, taake, metre. Those four
seconds buy half the audience.

Scene tables and subtitle cues live in `../reel.html` under `T.hi89` / `T.hi36`
and get re-cut to whatever the new timings turn out to be.
