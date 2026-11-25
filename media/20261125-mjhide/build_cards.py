"""20261125-mjhide: 2027 수능 가채점 만점자 최소 3명, AI 부정행위 의혹 분위기에 신원 공개 거부(베리타스알파 11.23·위키트리 11.24). 본문 기사 캡처, 마무리 장 없음.\n틀: 20261124-jensengta/build_cards.py."""
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
frame(("2027 수능 가채점 만점자 '최소 3명'", "그런데 아무도 '공개' 안 한다"), cap("wiki.jpg", (0, 0, 860, 925), 640),
      "만점 알려지는 순간 '의혹' 표적", "위키트리(11.24)").save(O / "c02.jpg", quality=93)
frame(("입시 매체도 올해는 '비공개'", "\"만점자 '잠재적 범죄자' 취급\""), cap("veritas.jpg", (0, 460, 860, 1000), 540),
      "매년 하던 '출신고·인터뷰' 보도 중단", "베리타스알파(11.23)").save(O / "c03.jpg", quality=93)
frame(("시험 전엔 안경·단추 검사", "시험 뒤엔 1년 전 '시험지'까지"), cap("veritas.jpg", (0, 3000, 860, 3950), 640),
      "성적 밝히는 순간 '나도 의심'받는다", "베리타스알파(11.23)").save(O / "c04.jpg", quality=93)
# 2026.11.25 사용자 지시: 표지 자료화면 교체 — 시험장 창문 너머 수험생 뒷모습(뉴스1·위키트리), 얼굴 안 보임
ImageOps.fit(op("press08.jpg"), (W, H), Image.LANCZOS, centering=(.5, .5)).filter(ImageFilter.UnsharpMask(2, 40, 2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
