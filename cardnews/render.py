"""카드뉴스 메이커 앱과 같은 디자인으로 1080x1350 JPEG 렌더링."""
import base64
import os

from playwright.sync_api import sync_playwright

from .common import CFG, ROOT

TEMPLATE = ROOT / "templates" / "renderer.html"


def _data_url(path):
    ext = "png" if path.lower().endswith(".png") else "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(open(path, "rb").read()).decode()


def render(slides, outdir, sty=None, col=None):
    os.makedirs(outdir, exist_ok=True)
    payload = {
        "sty": sty or CFG["style"]["sty"], "col": CFG["style"]["col"] if col is None else col,
        "ch": CFG["brand"]["channel_name"], "hd": CFG["brand"]["handle"],
        "slides": [{"t": s["t"], "b": s["b"], "sub": s.get("sub", ""), "img": _data_url(s["image"]) if s.get("image") else None} for s in slides],
    }
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(TEMPLATE.as_uri())
        pg.evaluate("async()=>{try{await Promise.all(['400','700','900'].map(w=>document.fonts.load(w+' 40px \"Noto Sans KR\"')).concat([document.fonts.load('400 40px \"Black Han Sans\"')]))}catch(e){}}")
        pg.evaluate("""async(x)=>{
          st.sty=x.sty; st.col=x.col; $('ch').value=x.ch; $('hd').value=x.hd;
          S=[];
          for(const s of x.slides){const o={t:s.t,b:s.b,sub:s.sub||''};
            if(s.img){const im=new Image();await new Promise((r,j)=>{im.onload=r;im.onerror=r;im.src=s.img});if(im.naturalWidth)o.img=im}
            S.push(o)}
          const txt=x.slides.map(s=>(s.t||'')+(s.b||'')).join('')+'팔로우하고 먼저 받아보세요오늘의쓸모';
          try{await Promise.all([document.fonts.load('400 100px "Black Han Sans"',txt)].concat(['400','700','900'].map(w=>document.fonts.load(w+' 40px "Noto Sans KR"',txt))))}catch(e){}
          if(PROF&&!PROF.complete)await new Promise(r=>{PROF.onload=r;setTimeout(r,2000)});
        }""", payload)
        for i in range(len(slides)):
            url = pg.evaluate("(i)=>{const cv=document.createElement('canvas');draw(cv,i);return cv.toDataURL('image/jpeg',0.92)}", i)
            fp = os.path.join(outdir, f"{i + 1:02d}.jpg")
            open(fp, "wb").write(base64.b64decode(url.split(",", 1)[1]))
            files.append(fp)
        b.close()
    if errs:
        raise RuntimeError("렌더링 오류: " + "; ".join(errs))
    return files
