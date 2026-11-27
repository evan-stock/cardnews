"""(복사) (복사본): 김민석 민주당 대표 조희대 대법원장 탄핵 5당 연대 공식 제안 → 신장식 \"지나치게 추상적\"·절차 합의 역제안(경향·데일리안 11.25). 본문 기사 캡처, 마무리 장 없음."""
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
    p = photo; dy = max(0, (1130 - (300 + p.height + 170)) // 2 - 60)  # 짧은 캡처는 묶음을 세로 가운데로
    rich_center(d, 168 + dy, top[0], F("Medium", 46), FG); rich_center(d, 236 + dy, top[1], F("Black", 54), FG)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300 + dy), m)
    d = ImageDraw.Draw(im); y = 300 + dy + p.height + 92
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





def cap(src, box=None):
    im = op(src)
    if box: im = im.crop(box)
    return im.resize((940, round(im.height * 940 / im.width)), Image.LANCZOS)
OUT = D
def vf(t, c=(.62,.5)):
    return fit(op(f"f{t}.jpg"), 940, 690, c).filter(ImageFilter.UnsharpMask(2, 50, 2))
S = "메가스터디 2028 수능 수학 커리큘럼 가이드 영상(원본 자막)"
frame(("현우진, 강의 영상에서", "\"수능이 '종말' 보는 것 같다\""), vf("2"),
      "\"부정한 사람들이 있었다는 거잖아\"", S).save(O / "c03.jpg", quality=93)
frame(("\"예를 들어 집에 바퀴벌레가 한 마리 보여\"", "\"집에 '한 마리'일 것 같아?\""), vf("8.6"),
      "드러난 건 일부일 수 있다는 말", S).save(O / "c02.jpg", quality=93)
frame(("\"시험은 점점 어려워지는데\"", "\"통계치가 '이상해'\""), vf("24"),
      "\"분포가 후진국, 앞뒤로 쏠려 있어\"", S).save(O / "c04.jpg", quality=93)
frame(("\"앞에 쏠려 있다는 건\"", "\"그런 '집단'이 있을 수도\""), vf("32"),
      "\"너무 괘씸하다\"", S).save(O / "c05.jpg", quality=93)
frame(("수능 이틀 전 '연기'까지 요구했던 그", "\"카르마는 '오차'가 없다\""), vf("36.5"),
      "\"무력감 갖지 말자\"", "11.17 인스타그램 글에도 같은 말 · 메가스터디 영상").save(O / "c06.jpg", quality=93)
print("ok")
