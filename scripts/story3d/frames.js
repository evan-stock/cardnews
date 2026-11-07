// 사용: node frames.js page.html outdir [fps] [dur] [times(쉼표)]
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const [page, out, fps = '30', dur = '10', only] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(__dirname, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0, async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 720, height: 1280 } }); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/${page}`); await p.waitForFunction('window.ready===true', null, { timeout: 60000 });
  const times = only ? only.split(',').map(Number) : [...Array(Math.round(+fps * +dur)).keys()].map(i => i / +fps);
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) { await p.evaluate(t => window.renderFrame(t), times[i]);
    await p.screenshot({ path: path.join(out, only ? `peek_${times[i]}.png` : String(i).padStart(4, '0') + '.png') });
    if (i % 30 === 0) console.log('frame', i, ((Date.now() - t0) / 1000).toFixed(0) + 's'); }
  await b.close(); srv.close(); });
