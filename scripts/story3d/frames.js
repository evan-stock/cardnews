// 사용: node frames.js page.html outdir [fps] [dur] [times(쉼표)]
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const [page, out, fps = '30', dur = '10', only] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(__dirname, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0, async () => {
  // GPU=1 이면 맥 그래픽 칩(Metal)으로 그림(11.21), 아니면 예전처럼 CPU(swiftshader)
  const gpu = process.env.GPU === '1';
  const b = await chromium.launch(gpu ? { channel: 'chromium', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] } : { args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: +(process.env.W || 720), height: +(process.env.H || 1280) }, deviceScaleFactor: +(process.env.DPR || 1) }); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/${page}`); await p.waitForFunction('window.ready===true', null, { timeout: 60000 });
  // RANGE="a-b" 이면 a~b번 장만(여러 갈래로 나눠 동시에 그릴 때), FMT=jpg 면 JPG(빠름)
  const all = [...Array(Math.round(+fps * +dur)).keys()];
  const [ra, rb] = (process.env.RANGE || '').split('-').map(Number);
  const idx = process.env.RANGE ? all.filter(i => i >= ra && i <= rb) : all;
  const times = only ? only.split(',').map(Number) : idx.map(i => i / +fps);
  const jpg = process.env.FMT === 'jpg';
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) { await p.evaluate(t => window.renderFrame(t), times[i]);
    await p.screenshot(jpg ? { path: path.join(out, only ? `peek_${times[i]}.jpg` : String(idx[i]).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 95 } : { path: path.join(out, only ? `peek_${times[i]}.png` : String(idx[i]).padStart(4, '0') + '.png') });
    if (i % 30 === 0) console.log('frame', i, ((Date.now() - t0) / 1000).toFixed(0) + 's'); }
  await b.close(); srv.close(); });
