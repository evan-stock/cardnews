"""20261123-gampy: 감정평가사 6개월 동차 합격 수기 논란(감평냥이) — 수기 비공개·볼펜심 4개 → 강사 수사 의뢰 예고 → 본인 해명(189명 중 150등).
본문: 실제 기사 화면 캡처(아시아경제·JTBC/네이트). eren/build_cards.py 복사."""
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




def cap(src, box, h):
    im = op(src).crop(box); return im.resize((round(im.width * h / im.height), h), Image.LANCZOS) if im.width * h / im.height <= 940 else im.resize((940, round(im.height * 940 / im.width)), Image.LANCZOS)
frame(("6개월 만에 감정평가사 1·2차 합격", "그런데 '합격 수기'가 사라졌다"), cap("asiae.jpg", (0, 290, 860, 868), 600),
      "답안지 5권도 안 채우고 '볼펜심 4개'", "아시아경제(11.17) · 하루 9시간 공부, 마라톤·가족여행도 병행").save(O / "c02.jpg", quality=93)
frame(("시험 강사가 나섰다", "\"6개월, 나는 '안 믿는다'\""), cap("nate_susa.jpg", (0, 0, 860, 560), 600),
      "\"국가기관에 의한 '강제수사' 필요\"", "윤철신 스터디파이터 대표 · JTBC(11.18)").save(O / "c03.jpg", quality=93)
frame(("합격자 본인 해명", "\"189명 중 '150등'…부정 아냐\""), cap("nate_haemyeong.jpg", (0, 0, 860, 520), 560),
      "\"수사 요청에도 '성실히' 임하겠다\"", "JTBC(11.19) · 부정행위 여부는 확인되지 않았습니다").save(O / "c04.jpg", quality=93)
ImageOps.fit(op("asiae.jpg").crop((0, 4720, 820, 5330)), (W, H), Image.LANCZOS).save(O / "cover_bg.jpg", quality=95)
print("ok")
