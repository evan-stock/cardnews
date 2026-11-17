"""20261117-leetint: 리트 만점자 17일 밤 자택 앞 인터뷰(중앙일보 단독·한국일보) — AI 부정행위 전면 부인, "차라리 수사 받겠다".
따옴표는 기사에 실린 실제 발언만. 실명 안 씀. 표지 사진: 나무위키 프로필(사용자 제공, jinwoo-ow와 같은 사진)."""
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



frame(("17일 밤 자택 앞에서 만난 리트 만점자", "의혹 '전면 부인'"),
      panel([("리트·수능에서 AI 한 번도 안 썼나", "\"'그렇다'\""), ("수사 이야기가 나오자", "\"차라리 '수사를 받겠다'\""), ("과외 때 실력 부족 의혹엔", "\"수능일인 '목요일'에 다 밝혀질 것\"")], h=560),
      "\"실력으로 '얼마든지' 보여드릴 수 있다\"", "중앙일보·한국일보(11.17)").save(O / "c02.jpg", quality=93)
frame(("시험지 의혹엔 이렇게 답했다", "'확률 희박'은 인정"),
      panel([("25~29번 답 고친 흔적", "\"고민하다 답을 '고른' 거다\""), ("우연일 가능성", "\"확률이 희박하다는 건 '인정한다'\""), ("시험지에 적힌 숫자 '33'", "\"다음 날 '전화통화' 하다 끄적인 것\"")], h=560),
      "스토킹 폭로자엔 '법적 대응' 고려", "부정행위는 아직 확인된 사실이 아닙니다").save(O / "c03.jpg", quality=93)
fit(op("lee_photo.jpg"), W, H, (.5, .2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
