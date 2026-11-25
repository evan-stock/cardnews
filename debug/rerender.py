"""(임시 2026-11-25) 해외 언론 기사 화면 캡처 → media/20261125-neon/press/"""
import os
from playwright.sync_api import sync_playwright
out = "media/20261125-neon/press"; os.makedirs(out, exist_ok=True)
U = [("ettoday", "https://ai.ettoday.net/news/3277503"), ("udn", "https://tech.udn.com/tech/story/123454/9899342"), ("cnyes", "https://news.cnyes.com/news/id/6670651")]
with sync_playwright() as p:
    b = p.chromium.launch()
    for n, u in U:
        try:
            pg = b.new_page(viewport={"width": 900, "height": 1400}, locale="zh-TW")
            pg.goto(u, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(4000)
            pg.evaluate("""()=>{const h=document.querySelector('h1');if(!h)return;const ps=[...document.querySelectorAll('article p, .story p, #article p, p')].filter(p=>p.innerText.length>40).slice(0,3);
              const k=document.createElement('div');k.style.cssText='background:#fff;padding:28px;width:840px;font-family:sans-serif';
              const lab=document.createElement('div');lab.innerText=location.hostname;lab.style.cssText='color:#c00;font-weight:700;font-size:16px;margin-bottom:10px';k.appendChild(lab);
              const t=h.cloneNode(true);t.style.cssText='font-size:30px;line-height:1.35;margin:0 0 16px;color:#111';k.appendChild(t);
              ps.forEach(p=>{const q=document.createElement('p');q.innerText=p.innerText;q.style.cssText='font-size:19px;line-height:1.7;color:#222';k.appendChild(q)});
              document.body.innerHTML='';document.body.style.background='#fff';document.body.appendChild(k);}""")
            pg.wait_for_timeout(800); pg.locator("body > div").first.screenshot(path=f"{out}/{n}.png")
        except Exception as e: print(n, e)
    b.close()
