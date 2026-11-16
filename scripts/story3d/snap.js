// 사용: node snap.js page.html out.png W H  → page 의 window.render() 를 부르고 화면을 찍는다
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const [page, out, W = '1800', H = '1200'] = process.argv.slice(2);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.wav': 'audio/wav' };
const srv = http.createServer((q, r) => { const f = path.join(__dirname, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0, async () => {
  const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: +W, height: +H } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('page:', m.text()); });
  await p.goto(`http://localhost:${port}/${page}`); await p.waitForFunction('window.ready===true', null, { timeout: 30000 });
  console.log(await p.evaluate(() => window.render()));
  await p.screenshot({ path: out }); await b.close(); srv.close();
});
