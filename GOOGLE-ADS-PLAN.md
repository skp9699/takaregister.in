# Google Ads — ₹20,000 credit plan

Working plan for spending the ₹20,000 Google Ads promotional credit.
Interactive version (with copy buttons for the keyword/copy blocks):
https://claude.ai/code/artifact/6a4a28ca-3e7c-4ec3-955f-2dfa056c8f0e

## Verdict

Advertise **Vyora**, at ~85% of budget. Taka Register gets a small
exact-match-only campaign (₹100–150/day) as a cheap option, not a real channel.

## What the credit actually is

Spend-matched, not free money: spend ₹20,000 of your own money within 60 days
of applying the code, then Google credits ₹20,000. Real budget is ₹40,000 over
roughly three months. **Confirm the exact terms in Billing → Promotions** — they
vary by offer.

Underspending the threshold forfeits the credit entirely. A powerloom-only
campaign would not find ₹20,000 of relevant clicks in 60 days.

## Blockers to fix before spending

1. **No tracking on the site.** `index.html` has no GA4, no Google Ads tag, no
   conversion tracking. Conversions that need to fire: WhatsApp click
   (`wa.me/917820986133`), email click, and each of the four download buttons
   (Vyora Windows/Android, Taka Windows/Android). Without this, Smart Bidding
   cannot optimise and we learn nothing about which keyword produced a customer.
2. **Account is in Smart Campaign mode.** Switch to Expert Mode before finishing
   setup — Smart Campaigns give no match-type control and no real negative
   keyword management.
3. **Auto-generated ad copy is wrong.** "Software Development Company" / "Your
   Local Software Company" / "Competent Software Developers" position us as a
   dev agency. Expensive keywords, wrong audience. Delete.

## Why Vyora over Taka Register

| | Vyora | Taka Register |
|---|---|---|
| Who's searching | Any Tally user in India | A few thousand mills in three towns |
| Proof of demand | Biz Analyst has 500k+ installs; many Tally partners resell "Tally on Mobile" | No vendor ad market exists for powerloom ERP |
| Do they search Google | Yes | No — they ask a neighbour, accountant or loom agent |
| Can absorb ₹650/day | Yes, on tight keywords | No; Google would broaden into junk to spend it |

At ~₹650/day and ₹15–40 CPC we get 20–40 clicks/day total. Split two ways,
neither product reaches the ~100 clicks per keyword theme needed for the data to
mean anything. Concentration is the whole game at this budget.

## Business-specific notes

- **Turn off the call button.** Support hours are Mon–Sat 3–8 PM. A missed call
  is a lost lead; a WhatsApp message waits. If the call button stays, schedule
  the call asset to 3–8 PM only.
- **"Tally" is a trademark.** Fine as a keyword under Google's India policy;
  can be restricted in ad text if Tally Solutions has filed a complaint. If ads
  get disapproved, use the trademark-free headline swaps and keep "Tally" in
  keywords only. Keep describing Vyora as a companion app; never imply official
  affiliation.

## 60-day pacing

| When | Daily | Focus |
|---|---|---|
| Week 0 | ₹0 | Tracking, Expert Mode, `/vyora` landing page, delete bad copy |
| Weeks 1–2 | ₹350 | Vyora only. Phrase+Exact. Manual CPC / Max Clicks ₹25 cap. Maharashtra + Gujarat. Search terms report every 2 days. |
| Weeks 3–4 | ₹400 | Pause keywords with 40+ clicks and 0 conversions. Launch Taka exact-match at ₹100/day. Expand geo only if CPL holds. |
| Weeks 5–8 | ₹450 | Cross ₹20,000 ~day 55, confirm credit posts. At 30+ conversions switch to Maximise Conversions, then tCPA. |
| Credit period | ₹700 | Scale winners only. Add remarketing for `/vyora` non-converters. |

Do **not** start on Maximise Conversions — there is no conversion history for it
to work from.

## Vyora keywords

High intent (phrase + exact):

```
"tally mobile app"
"tally on mobile"
"tally prime mobile app"
"tally erp 9 mobile app"
"tally data on mobile"
"mobile app for tally"
"tally ledger app"
"tally outstanding report mobile"
"view tally on phone"
"tally companion app"
[tally mobile app for android]
[check tally reports on phone]
[see tally data on mobile]
```

Problem-first (cheaper, slower):

```
"how to see tally data on mobile"
"party ledger app"
"outstanding payment app for business"
"check party outstanding on phone"
"item stock report on mobile"
```

Competitor (allowed as keywords, not in ad text):

```
"biz analyst"
"biz analyst app"
"biz analyst alternative"
"tally mobile pro"
```

## Negative keywords — add day one

`tally counter` is the important one: hand-held clickers have far more search
volume than accounting Tally. Without it a real slice of the budget goes to
people shopping for clickers. `tally hall` is a band.

```
tally counter
counter
clicker
tally hall
tally marks
tally meaning
tally definition
tally chart

free
crack
cracked
keygen
torrent
course
tutorial
training
classes
institute
certification
learn
job
jobs
vacancy
salary
resume
internship
tally prime download
tally erp 9 download
gst return
gst filing
software development
software company
app development
developers
hire

accounting software
billing software
invoice software
erp software
inventory software
best accounting software
```

## Vyora ad copy

Headlines (max 30 chars):

```
Tally On Your Phone              19
Your Tally Books, On Mobile      27
See Tally Data Anywhere          23
Party Ledgers On Your Phone      27
Check Outstanding Anytime        25
Know Who Owes You, Instantly     28
Tally Mobile App For India       26
Works Offline. Syncs Later.      27
Your Data Stays In Your Drive    29
No Exports. No Screenshots.      27
Read-Only. Books Stay Safe.      27
Item Stock At A Glance           22
Built In India For Tally Users   30
Free Trial — Start Today         24
Vyora — Tally Companion App      27
```

Descriptions (max 90 chars):

```
A desktop agent mirrors your books to your Drive. Open ledgers and stock on your phone.
Outstanding, party ledgers, item stock and registers — from anywhere, even offline.
Read-only and private. Synced to your own Google Drive, never to our servers.
Made in Bhiwandi. WhatsApp us directly — you reach the people who build it.
```

Trademark-free swaps if "Tally" headlines get disapproved:

```
Your Books On Your Phone         24
Accounting Books On Mobile       26
Ledgers & Outstanding, Live      27
```

Assets — sitelinks: "Download for Android", "Windows Sync Agent", "How It
Works", "Your Data Stays Yours". Callouts: "Works Offline", "Own Google Drive",
"Read-Only & Safe", "WhatsApp Support", "Free Trial". Structured snippet
(Features): Party Ledgers, Outstanding, Item Stock, Sales Register, Purchase
Register.

## Taka Register — ₹100/day, exact match only

Expect it to underspend. That is the design. Never loosen match types to make it
spend its cap.

```
[powerloom software]
[powerloom erp]
[powerloom mill software]
[loom production software]
[weaving mill software]
[textile weaving erp]
[yarn inventory software]
[grey fabric software]
[fabric production software]
[taka register]
```

```
Powerloom Mill ERP
Loom-Wise Production Daily
Yarn, Dyeing & Fabric Stock
TDS Cards & Loom Output
Made In Bhiwandi For Mills
Works Offline On Your PC
Free Trial — WhatsApp Us

Track loom-wise output, yarn, dyeing and fabric at processors. Windows and Android.
Built in Bhiwandi for powerloom mills. Your data stays on your PC and your own Drive.
```

## Landing page

`takaregister.in` is one page whose hero reads "Software built for powerloom
mills." Sending "tally mobile app" traffic there hurts landing-page relevance
(higher CPC) and conversion rate. A dedicated `/vyora` page — Vyora's own
headline, its own screenshots, one WhatsApp CTA, nothing about looms — is the
highest-leverage pre-launch change.

## Caveat

Search-volume claims here are directional, based on the competitive landscape
rather than Keyword Planner data. Run the keyword list through Keyword Planner
for real numbers in your geography before launch.
