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
for t in (5, 9, 17, 31):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(V), "-frames:v", "1", str(O / f"f{t}.png")], check=True)
sh = lambda im: im.filter(ImageFilter.UnsharpMask(2, 70, 2))
# 2026-11-17 다시: 방송 자막이 핵심이라 자막을 살린 원본 장면 그대로(수어 화면 쪽만 살짝 잘라냄)
full = lambda n: sh(fit(op(n).crop((0, 0, 1060, 636)), 940, 564))
frame(("세무냥이 불똥에 공개된 성적", "722명 중 '518등'"), full("f31.png"),
      "한 과목은 '겨우' 과락 면했다", "MBC 뉴스데스크(11.17)").save(O / "c02.jpg", quality=93)
frame(("최연소 합격자라는 이유로", "\"너도 'AI'냐\" 저격"), full("f5.png"),
      "여자친구 인스타 아이디까지 '태그'", "애먼 사람이 의심받았다").save(O / "c03.jpg", quality=93)
frame(("결국 공부한 책을", "'캐리어'째 들고 왔다"), full("f17.png"),
      "학원 별명은 '지박령'", "동료 수강생 인터뷰").save(O / "c04.jpg", quality=93)
sh(fit(op("f9.png").crop((520, 0, 960, 470)), W, H, (.5, .25))).save(O / "cover_bg.jpg", quality=95)
for t in (5, 9, 17, 31): (O / f"f{t}.png").unlink()
print("ok")
