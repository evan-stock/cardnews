"""20261117-taxyoung-c: 세무사 63회 최연소 합격자, 세무냥이 불똥 — AI 의심 저격받고 책 캐리어로 증명, 성적 '722명 중 518등·겨우 과락 면해'까지 공개.
화면: MBC 뉴스데스크 보도 영상(X @itwillbe_sage 경유, cardnews media/20261117-taxyoung2). 박힌 자막·수어 화면은 잘라냄. 따옴표는 영상 속 실제 발언.
"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


def fit(name, w=940, h=700, c=(.5, .5), crop=None):
    im = Image.open(O / name).convert("RGB")
    if crop: im = im.crop(crop)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=c)
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))






fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda n: Image.open(O / n).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p



V = R / "media/20261117-taxyoung2/video/v1.mp4"
for t in (5, 12, 17, 31):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(V), "-frames:v", "1", str(O / f"f{t}.png")], check=True)
sh = lambda im: im.filter(ImageFilter.UnsharpMask(2, 70, 2))
frame(("최연소 합격자라는 이유로", "\"너도 'AI'냐\" 저격"), sh(fit(op("f5.png").crop((300, 90, 1040, 430)), 940, 600)),
      "\"여자친구 인스타 아이디까지 '태그'\"", "\"생각보다 심각하구나…\" (안호준 씨)").save(O / "c02.jpg", quality=93)
frame(("결백을 보여주려고", "공부한 책 '캐리어'째 들고 왔다"), sh(fit(op("f17.png").crop((150, 70, 960, 460)), 940, 600)),
      "\"총 몇 권?\" \"'세지 않아봐서' 모르겠어요\"", "학원 별명은 '지박령'(동료 수강생)").save(O / "c03.jpg", quality=93)
frame(("그래서 공개된 성적", "722명 중 '518등'"), sh(fit(op("f31.png").crop((160, 70, 960, 470)), 940, 600)),
      "한 과목은 '겨우' 과락 면했다", "AI 안경 썼다면 더 안정적으로 붙었을 거라는 것").save(O / "c04.jpg", quality=93)
sh(fit(op("f12.png").crop((300, 0, 680, 470)), W, H, (.5, .3))).save(O / "cover_bg.jpg", quality=95)
print("ok")
