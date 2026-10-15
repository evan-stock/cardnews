"""카드뉴스 메이커 앱과 같은 디자인으로 1080x1350 JPEG 렌더링."""
import base64
import os

from playwright.sync_api import sync_playwright

from .common import CFG, ROOT

TEMPLATE = ROOT / "templates" / "renderer.html"


def _prep(path):
    """카드(1080x1350)를 꽉 채우려면 1.4배 넘게 키워야 하는 사진은
    가로 폭에 맞춰 위쪽에 놓고 빈 곳은 같은 사진을 흐리게 채운다(덜 확대돼 덜 흐림)."""
    from PIL import Image, ImageFilter
    W, H = 1080, 1350
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        return path
    s = max(W / im.width, H / im.height)
    if s <= 1.4:
        return path
    if im.width / im.height <= 1.0 and s <= 2.2:
        # 세로에 가까운 사진은 꽉 채우는 게 낫다(살짝 선명하게만)
        out = path.rsplit(".", 1)[0] + "_sharp.jpg"
        im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=3)).save(out, quality=95)
        return out
    bg = im.resize((int(im.width * s) + 1, int(im.height * s) + 1)).filter(ImageFilter.GaussianBlur(45))
    x, y = (bg.width - W) // 2, (bg.height - H) // 2
    bg = Image.blend(bg.crop((x, y, x + W, y + H)), Image.new("RGB", (W, H), (0, 0, 0)), 0.35)
    r = min(W / im.width, 860 / im.height)
    fg = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    fg = fg.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    bg.paste(fg, ((W - fg.width) // 2, 70))
    out = path.rsplit(".", 1)[0] + "_fit.jpg"
    bg.save(out, quality=93)
    return out


def _data_url(path):
    ext = "png" if path.lower().endswith(".png") else "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(open(path, "rb").read()).decode()


def render(slides, outdir, sty=None, col=None, overlays=()):
    """overlays: 영상 장의 인덱스들. 그 장은 사진 없이 글자·그라데이션만 담은 투명 PNG(NN_overlay.png)도 만든다."""
    os.makedirs(outdir, exist_ok=True)
    payload = {
        "sty": sty or CFG["style"]["sty"], "col": CFG["style"]["col"] if col is None else col,
        "ch": CFG["brand"]["channel_name"], "hd": CFG["brand"]["handle"],
        "slides": [{"t": s["t"], "b": s["b"], "sub": s.get("sub", ""), "img": _data_url(_prep(s["image"])) if s.get("image") else None} for s in slides],
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
        for i in overlays:
            url = pg.evaluate("(i)=>{const s=S[i],keep=s.img;s.img=null;s.clear=true;const cv=document.createElement('canvas');draw(cv,i);s.img=keep;s.clear=false;return cv.toDataURL('image/png')}", i)
            open(os.path.join(outdir, f"{i + 1:02d}_overlay.png"), "wb").write(base64.b64decode(url.split(",", 1)[1]))
        b.close()
    if errs:
        raise RuntimeError("렌더링 오류: " + "; ".join(errs))
    return files
