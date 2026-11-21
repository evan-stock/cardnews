"""20261121-leetnews: 리트 만점자 유서 메모(중앙일보 단독 11.21). 자살보도 권고기준: 방법·장소 묘사 없음, 상담전화 109 표기. leetpara/build_cards.py 복사."""
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




# 2026.11.21 사용자 지시: 본문은 실제 기사 캡처(제목 + 해당 문단)
def cap(src, parts):
    im = op(src); ims = [im.crop(b) for b in parts]
    out = Image.new("RGB", (860, sum(i.height for i in ims) + 30 * (len(ims) - 1)), (255, 255, 255))
    y = 0
    for i in ims: out.paste(i, (0, y)); y += i.height + 30
    return out.resize((940, round(out.height * 940 / 860)), Image.LANCZOS)
frame(("숨지기 이틀 전, 집주인에게", "\"'탈출'하게 도와달라\""), cap("hk.jpg", [(0, 370, 860, 560), (0, 5560, 860, 5940)]),
      "취재진 피해 건물 나갈 방법을 '물었다'", "한국경제(11.21) 기사 화면").save(O / "c01.jpg", quality=93)
frame(("중앙일보가 확인한 다섯 줄 메모", "\"이 글도 '조롱'을 당하겠지\""), cap("jaj.jpg", [(0, 262, 860, 430), (0, 2040, 860, 2440)]),
      "부정행위 의혹에 대한 '언급은 없었다'", "중앙일보(11.21) 기사 화면").save(O / "c02.jpg", quality=93)
fit(op("press01.jpg"), W, H, (.5, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
