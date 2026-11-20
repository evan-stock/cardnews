"""20261120-distrust: 세무냥이 사태가 남긴 불신(세무사 최연소·미트냥이·감평냥이 해명, 냥이 리스트). 리트냥이 제외(사용자 지시). 개인정보 가림."""
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

op = lambda n: Image.open(O / n).convert("RGB")


def cap(name, box, blur=(), mark=(), w=940, maxh=760):
    im = op(name)
    for b in blur:  # 이름·생년월일 등 가리기(원본 좌표)
        im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(14)), b[:2])
    im = im.crop(box)
    if mark:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
        for m in mark: dd.rectangle(m, fill=(255, 216, 77, 90))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    h = round(im.height * w / im.width)
    if h > maxh: im = im.crop((0, 0, im.width, round(maxh * im.width / w))); h = maxh
    return im.resize((w, h), Image.LANCZOS)


def stack(a, b, gap=16):
    im = Image.new("RGB", (940, a.height + gap + b.height), (10, 10, 12)); im.paste(a, (0, 0)); im.paste(b, (0, a.height + gap)); return im


# 미트냥이 1: 6년 준비 + 성적표
frame(("MDEET 전국 1등 '미트냥이'", "\"1년 아니라 '6년' 준비했다\""),
      stack(cap("m6.jpg", (0, 0, 1080, 245)), cap("m6.jpg", (15, 280, 630, 560), blur=[(115, 400, 450, 436), (25, 400, 112, 436)], maxh=420)),
      "130.5 → 124.4 → 140.9점, 성적표 전부 '공개'", "본인 해명문 캡처(X @HMGOD111652 · 11.20)").save(O / "c04.jpg", quality=93)
# 미트냥이 2: 해명문 쓴 이유
frame(("그가 해명문을 쓴 이유", "\"가족들까지 '상처'받아서\""),
      stack(cap("m9.jpg", (15, 780, 1075, 1060), mark=[(0, 0, 1060, 95)]), cap("m1.jpg", (0, 0, 910, 512), maxh=470)),
      "\"결코 어떤 시험도 부정한 방법으로 치지 않았다\"", "본인 해명문 캡처 / 아래: '1년' 오해가 시작된 강의 영상 · 11.20").save(O / "c05.jpg", quality=93)
# 감평냥이
frame(("'6개월 합격' 감평냥이도", "학력·성적·공부 사진까지 '공개'"),
      stack(cap("g5.jpg", (40, 1030, 920, 1200), mark=[(0, 0, 880, 170)]), cap("g8.jpg", (69, 900, 872, 1460), maxh=440)),
      "\"서울대 석사, '6개월' 표현은 부적절했다\"", "본인 2차 해명문 캡처 · 11.19").save(O / "c06.jpg", quality=93)
print("ok")
