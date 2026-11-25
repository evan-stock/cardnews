"""(임시 2026-11-25) 마운자로 대마도 기사 캡처 → media/20261125-mounjaro/press/"""
import os, json
from playwright.sync_api import sync_playwright
out = "media/20261125-mounjaro/press"; os.makedirs(out, exist_ok=True)
U = [("inews", "http://inews24.com/view/2030005", "아이뉴스24", ["1시간", "배를 놓", "34만원", "반값"]),
     ("fn", "https://www.fnnews.com/news/202611241738457546", "파이낸셜뉴스", ["12일부터", "3개월분", "30만원", "스시자로"]),
     ("mt", "https://supple.kr/news/cmwucuhz6phyykwp8iaegvhc6", "머니투데이", ["11~16%", "후쿠오카", "올린"])]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for n, u, pub, kws in U:
        try:
            pg = b.new_page(viewport={"width": 900, "height": 1400}, locale="ko-KR")
            pg.goto(u, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(4000)
            data = pg.evaluate("""(kws)=>{const h=(document.querySelector('h1')||document.querySelector('h2')||{}).innerText||document.title;
              const ps=[...document.querySelectorAll('p, div')].filter(e=>e.children.length<3).map(e=>e.innerText.trim()).filter(t=>t.length>30&&t.length<400);
              const uniq=[...new Set(ps)];return {h, ps:uniq.filter(t=>kws.some(k=>t.includes(k))).slice(0,6)}}""", kws)
            res[n] = data
            for k, para in enumerate([data["ps"]]):
                pass
            pg.evaluate("""([d,pub])=>{const k=document.createElement('div');k.style.cssText='background:#fff;padding:28px;width:840px;font-family:sans-serif';
              const l=document.createElement('div');l.innerText=pub+' · 2026.11.24';l.style.cssText='color:#c00;font-weight:700;font-size:16px;margin-bottom:10px';k.appendChild(l);
              const t=document.createElement('div');t.innerText=d.h;t.style.cssText='font-size:30px;font-weight:800;line-height:1.35;margin:0 0 16px;color:#111';k.appendChild(t);
              d.ps.slice(0,4).forEach(x=>{const q=document.createElement('p');q.innerText=x;q.style.cssText='font-size:20px;line-height:1.7;color:#222';k.appendChild(q)});
              document.body.innerHTML='';document.body.style.background='#fff';document.body.appendChild(k);}""", [data, pub])
            pg.wait_for_timeout(500); pg.locator("body > div").first.screenshot(path=f"{out}/{n}.png")
        except Exception as e: print(n, e)
    b.close()
json.dump(res, open(f"{out}/text.json", "w"), ensure_ascii=False, indent=1)
