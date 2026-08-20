#!/usr/bin/env node
/**
 * Fit check. Meta's UI eats the top 14% and bottom 35% of a 9:16 frame, so all
 * readable content has to live inside .safe (499px tall). This walks each scene
 * of a cut at its midpoint and reports the lowest content pixel against that
 * bound — cheaper than rendering 2,652 frames and squinting at them.
 *
 *   node check-reel.js --v hi89
 */
const { chromium } = require('playwright');
const path = require('path');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > -1 ? process.argv[i+1] : d; };

const V = arg('v', 'hi89');
const SRC = arg('page', /^(screens|type|split|mixed)(-en)?$/.test(V) ? 'reel2.html' : 'reel.html');
const PAGE = 'file://' + path.join(__dirname, SRC) + '?render=1&v=' + V;

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--disable-lcd-text', '--hide-scrollbars', '--disable-gpu'] });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.__imagesReady || Promise.resolve());

  const rows = await page.evaluate(() => {
    const band = document.querySelector('.safe').getBoundingClientRect();
    const out = [];
    for (const [id, s, d] of window.__SC) {
      // Sample once the entries have settled. At the midpoint a card can still
      // be sliding in, which reads as an overflow that never appears on screen.
      window.renderAt(s + d * 0.88);
      const sc = document.getElementById(id);
      let top = Infinity, bot = -Infinity;          // all ink, for the safe band
      let tl = Infinity, tr = -Infinity;            // text only, for side clipping
      // An element inside an overflow:hidden box is clipped to it, so its own
      // rect lies about where ink lands — a 900px screenshot inside a 320px
      // window is not a 900px overflow. The clipping box is measured instead.
      const clipped = el => {
        for (let p = el.parentElement; p && p !== sc; p = p.parentElement)
          if (getComputedStyle(p).overflow !== 'visible') return true;
        return false;
      };
      for (const el of sc.querySelectorAll('*')) {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || +cs.opacity < 0.02) continue;
        if (clipped(el)) continue;
        const b = el.getBoundingClientRect();
        if (b.width && b.height) { top = Math.min(top, b.top); bot = Math.max(bot, b.bottom); }
        for (const n of el.childNodes) {
          if (n.nodeType !== 3 || !n.textContent.trim()) continue;
          const rg = document.createRange(); rg.selectNodeContents(n);
          for (const r of rg.getClientRects()) {
            if (!r.width || !r.height) continue;
            tl = Math.min(tl, r.left); tr = Math.max(tr, r.right);
          }
        }
      }
      out.push({ id, dur: +d.toFixed(2),
                 top: Math.round(top - band.top), bottom: Math.round(bot - band.top),
                 left: Math.round(tl), right: Math.round(tr) });
    }
    // subtitles are their own layer, outside .safe's box but inside the band
    const cues = window.__CUES;
    let widest = 0, widestText = '';
    for (const c of cues) {
      window.renderAt((c[0] + c[1]) / 2);
      const w = document.getElementById('subt').getBoundingClientRect().width;
      if (w > widest) { widest = w; widestText = c[2]; }
    }
    return { out, band: Math.round(band.height), widest: Math.round(widest), widestText };
  });

  const H = rows.band;
  console.log(`\n  ${V} · safe band ${H}px tall · stage 540px wide\n`);
  console.log('  scene   dur     top  bottom   text x        fit');
  let bad = 0;
  for (const r of rows.out) {
    // Meta only overlays the top and bottom of a 9:16 reel, never the sides, so
    // the side bound is about text actually running off frame — not margin taste.
    // S1's ledger header sits at x=11 on purpose; that has to pass.
    const okY = r.bottom <= H, okX = r.left >= 8 && r.right <= 532;
    if (!okY || !okX) bad++;
    console.log(`  ${r.id.padEnd(6)} ${String(r.dur).padStart(5)}s  ${String(r.top).padStart(4)}  ${String(r.bottom).padStart(6)}   ${String(r.left).padStart(3)}–${String(r.right).padEnd(3)}   ` +
                `${okY ? 'ok' : `OVERFLOWS by ${r.bottom - H}px`}${okX ? '' : '  X-OVERFLOW'}`);
  }
  console.log(`\n  widest subtitle plate: ${rows.widest}px of 488 available`);
  console.log(`    "${rows.widestText}"`);
  if (rows.widest > 488) { console.log('    ^ WRAPS — shorten this cue'); bad++; }
  console.log(errs.length ? `\n  JS ERRORS:\n${errs.map(e => '    ' + e).join('\n')}` : '\n  no JS errors');
  await browser.close();
  process.exit(bad || errs.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
