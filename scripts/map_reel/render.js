// 사용: node render.js frames <fps>  |  node render.js shots 1.0,4.5,...
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const mode = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve('index.html'));
  await p.waitForFunction('window.ready===true');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const dur = await p.evaluate('SCENES.dur');
  if (mode === 'shots') {
    fs.mkdirSync('shots', { recursive: true });
    for (const t of process.argv[3].split(',').map(Number)) {
      await p.evaluate(t => render(t), t);
      await p.screenshot({ path: `shots/t${t.toFixed(2)}.jpg`, type: 'jpeg', quality: 80 });
    }
  } else {
    const fps = +(process.argv[3] || 30);
    fs.mkdirSync('frames', { recursive: true });
    const n = Math.round(dur * fps);
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => render(t), i / fps);
      await p.screenshot({ path: `frames/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
      if (i % 100 === 0) console.log(i, '/', n);
    }
  }
  await b.close();
})();
