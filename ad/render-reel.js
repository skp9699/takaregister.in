#!/usr/bin/env node
/**
 * Renders reel.html to MP4. Frames are driven by renderAt(t) and piped straight
 * into ffmpeg, so nothing touches disk. Pass --nosubs for the caption-free cut.
 *
 *   node render-reel.js --v hi89 --out build/reel-subs-hi89.mp4 [--nosubs]
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'), fs = require('fs');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > -1 ? process.argv[i+1] : d; };
const has = k => process.argv.includes('--' + k);

const FPS = +arg('fps', 30), SCALE = +arg('scale', 2), CRF = +arg('crf', 19);
const OUT = path.resolve(arg('out', path.join(__dirname, 'build', 'reel-silent.mp4')));
const FFMPEG = process.env.FFMPEG_PATH ||
  '/tmp/claude-0/-home-user-takaregister-in/ea668c35-4dd5-5cf7-ab4f-02856e1baa4b/scratchpad/node_modules/ffmpeg-static/ffmpeg';
// variant: en | hi36 | hi89 in reel.html; screens | type | split | mixed in reel2.html
const V = arg('v', arg('lang', 'en') === 'hi' ? 'hi36' : 'en');
const SRC = arg('page', /^(screens|type|split|mixed)$/.test(V) ? 'reel2.html' : 'reel.html');
const PAGE = 'file://' + path.join(__dirname, SRC) + '?render=1&v=' + V +
  (has('nosubs') ? '&nosubs=1' : '');

(async () => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--disable-lcd-text','--force-color-profile=srgb','--hide-scrollbars','--disable-gpu'] });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: SCALE });
  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // screenshots are half the frame in reel2; a frame rendered before they decode
  // is a blank card that no later frame corrects
  await page.evaluate(() => window.__imagesReady || Promise.resolve());
  await page.waitForTimeout(400);

  const DUR = await page.evaluate(() => window.AD_DURATION);
  const TOTAL = Math.round(DUR * FPS);
  console.log(`${V} · ${DUR}s · ${FPS}fps · ${TOTAL} frames · ${540*SCALE}x${960*SCALE}${has('nosubs')?' · no subtitles':' · subtitled'}`);

  const ff = spawn(FFMPEG, ['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-c:v','libx264','-preset','slow','-crf',String(CRF),'-pix_fmt','yuv420p',
    '-movflags','+faststart','-r',String(FPS), OUT], { stdio:['pipe','inherit','pipe'] });
  let err=''; ff.stderr.on('data',d=>err+=d);
  const done = new Promise((res,rej)=>ff.on('close',c=>c===0?res():rej(new Error('ffmpeg '+c+'\n'+err.slice(-2000)))));
  ff.stdin.on('error',()=>{});
  const write = b => ff.stdin.write(b) ? Promise.resolve() : new Promise(r=>ff.stdin.once('drain',r));

  const t0=Date.now();
  for (let f=0; f<TOTAL; f++){
    await page.evaluate(t => window.renderAt(t), f/FPS);
    await write(await page.screenshot({ type:'jpeg', quality:96 }));
    if (f%150===0||f===TOTAL-1) console.log(`  ${f+1}/${TOTAL}  ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await done; await browser.close();
  console.log(`wrote ${OUT} (${(fs.statSync(OUT).size/1048576).toFixed(2)} MB)`);
})().catch(e=>{console.error(e);process.exit(1);});
