"""20261124-jensengta: 젠슨 황 11일 만에 CEO 복귀 → 'GTA6 다 깨고 돌아왔다' 밈(가짜 지메일·링크드인, 엑스 @TrungTPhan 118만 조회).
사실: 11.12 퇴진(사생활 논란 등) → 11.22 이사회 복귀 결정, 11.23 발표·주가 31% 급등(글로벌이코노믹). 본문은 사용자 제공 밈 이미지·엑스 화면 + 기사 캡처.
틀: 20261123-zicokarma/build_cards.py."""
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
frame(("11월 12일 젠슨 황 '퇴진'", "\"GTA6도 안 나왔는데 가버리다니\""), cap("segye.jpg", (0, 0, 860, 880), 640),
      "엔비디아 공지에 달린 '게이머'들 댓글", "세계일보(11.13)").save(O / "c02.jpg", quality=93)
frame(("그리고 11일 만에", "CEO '복귀'·주가 31% 폭등"), cap("genews.jpg", (0, 760, 860, 1300), 540),
      "하루 만에 시총 '1264조원' 늘어", "글로벌이코노믹(11.24)").save(O / "c03.jpg", quality=93)
# 2026.11.24: 반응 좋았던 같은 소재 게시물처럼 표지를 링크드인 밈으로, 지메일 밈은 4장으로
frame(("이사회에 보냈다는 메일까지", "\"GTA6 다 깼어, 이제 '복귀'할게\""), cap("gmail.jpg", (0, 0, 982, 1228), 640),
      "물론 진짜 메일 아니고 '밈'입니다", "엑스에서 퍼진 합성 이미지").save(O / "c04.jpg", quality=93)
li = op("linkedin.jpg").crop((0, 40, 2013, 1620))
bg = Image.new("RGB", (W, H), (10, 10, 12)); lw = W - 80; li = li.resize((lw, round(li.height * lw / li.width)), Image.LANCZOS)
m = Image.new("L", li.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, li.width - 1, li.height - 1), 28, fill=255)
bg.paste(li, (40, 110), m)
d = ImageDraw.Draw(bg); f = F("SemiBold", 30); d.text((W - 50, 70), "엑스에서 퍼진 합성 밈", font=f, fill=(140, 140, 140), anchor="rm")
bg.save(O / "cover_bg.jpg", quality=95)
print("ok")
