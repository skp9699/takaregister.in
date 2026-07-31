#!/usr/bin/env node
/**
 * Offline renderer for ad.html.
 *
 * Drives the page's deterministic renderAt(t) one frame at a time and pipes the
 * screenshots straight into ffmpeg, so a 1700-frame render never touches disk.
 * Frame timing comes from the clock we pass in, not from wall time, so the
 * output is identical no matter how slow the machine is.
 *
 *   node render.js [--fps 30] [--scale 2] [--out out.mp4] [--crf 20]
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const arg = (k, d) => {
  const i = process.argv.indexOf('--' + k);
  return i > -1 ? process.argv[i + 1] : d;
};

const FPS    = +arg('fps', 30);
const SCALE  = +arg('scale', 2);          // 540x960 CSS * 2 = 1080x1920
const CRF    = +arg('crf', 20);
const OUT    = path.resolve(arg('out', path.join(__dirname, 'build', 'takaregister-ad-silent.mp4')));
const FFMPEG = arg('ffmpeg', process.env.FFMPEG_PATH ||
  '/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad/node_modules/ffmpeg-static/ffmpeg');
const PAGE   = 'file://' + path.join(__dirname, 'ad.html') + '?render=1';

(async () => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });

  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--disable-lcd-text', '--force-color-profile=srgb',
           '--hide-scrollbars', '--disable-gpu']
  });
  const page = await browser.newPage({
    viewport: { width: 540, height: 960 },
    deviceScaleFactor: SCALE
  });

  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);           // let the embedded woff2 settle

  const DUR = await page.evaluate(() => window.AD_DURATION);
  const TOTAL = Math.round(DUR * FPS);
  console.log(`duration ${DUR}s · ${FPS}fps · ${TOTAL} frames · ${540 * SCALE}x${960 * SCALE}`);

  const ff = spawn(FFMPEG, [
    '-y',
    '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(CRF),
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-r', String(FPS),
    OUT
  ], { stdio: ['pipe', 'inherit', 'pipe'] });

  let ffErr = '';
  ff.stderr.on('data', d => { ffErr += d.toString(); });
  const done = new Promise((res, rej) =>
    ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c + '\n' + ffErr.slice(-3000)))));
  ff.stdin.on('error', () => {});           // ffmpeg may close first on error

  const write = buf => ff.stdin.write(buf)
    ? Promise.resolve()
    : new Promise(r => ff.stdin.once('drain', r));

  const t0 = Date.now();
  for (let f = 0; f < TOTAL; f++) {
    await page.evaluate(t => window.renderAt(t), f / FPS);
    await write(await page.screenshot({ type: 'jpeg', quality: 96 }));
    if (f % 120 === 0 || f === TOTAL - 1) {
      const pct = ((f + 1) / TOTAL * 100).toFixed(0);
      const el = ((Date.now() - t0) / 1000).toFixed(0);
      console.log(`  ${String(f + 1).padStart(4)}/${TOTAL}  ${pct}%  ${el}s`);
    }
  }

  ff.stdin.end();
  await done;
  await browser.close();

  const mb = (fs.statSync(OUT).size / 1048576).toFixed(2);
  console.log(`\nwrote ${OUT}  (${mb} MB)`);
})().catch(e => { console.error(e); process.exit(1); });
