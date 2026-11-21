"""20261121-ljmmin: 이 대통령 엑스 '최대 1억 아니라 최소 1억'(11.21) vs 권익위 '최대 1억'(11.19). 헤럴드경제·세계일보·연합(11.21)."""
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


def cap(name, box, w=940, maxh=760):
    im = Image.open(O / name).convert("RGB").crop(box)
    h = round(im.height * w / im.width)
    if h > maxh: im = im.crop((0, 0, im.width, round(maxh * im.width / w))); h = maxh
    return im.resize((w, h), Image.LANCZOS)


frame(("11월 21일 오후, 대통령 엑스", "\"최대 1억이 아니라 '최소 1억'\""),
      cap("xembed_clean.png", (0, 0, 1290, 850)),
      "부정행위자 '수만큼' 더 얹어 준다", "이재명 대통령 X 게시물 캡처(11.21)").save(O / "c02.jpg", quality=93)
frame(("그런데 이틀 전 정부 공식 발표는", "신고 포상금 '최대 1억'"),
      cap("segye_clean.png", (0, 0, 1290, 750)),
      "응시자격 정지 처분이 나와야 '지급'", "국민권익위원회 발표 · 세계일보(11.19)").save(O / "c03.jpg", quality=93)
frame(("부처가 발표한 기준을", "대통령이 엑스로 '직접 정정'"),
      cap("herald_clean.png", (0, 0, 1290, 710)),
      "공식 발표 '상한'과 대통령 '최소액'이 엇갈렸다", "헤럴드경제 기사 캡처(11.21)").save(O / "c04.jpg", quality=93)
p = Image.open(O / "p1.jpg").convert("RGB")
ImageOps.fit(p.crop((60, 0, 900, 941)), (W, H), Image.LANCZOS, centering=(.45, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
