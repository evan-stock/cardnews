"""20261122-choiresign: 최교진 교육부 장관 사의 표명(11.22, 교육부 대변인실 입장문). 근거: 연합뉴스 1보·서울신문 속보(11.22), 국회 교육위 발언(11.16)·TF 회의 전 발언(11.20)·수험생연대·국민의힘 사퇴 촉구(11.21~22), 교육부 111건 발표."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




fit(op(O / "cover_src.jpg"), W, H, (.28, .2)).save(O / "cover_bg.jpg", quality=95)

# 2장 사의 표명
frame(("22일, 교육부 대변인실 입장문", "\"수능 '책임 통감'\""),
      fit(op(O / "press01.jpg"), 940, 560, (.45, .4)),
      "준비 부족 비판에 '책임' 인정", "시험 직전 잇단 변화로 혼란 · 사표 수리 여부는 아직").save(O / "c02.jpg", quality=93)

# 3장 일주일 타임라인
frame(("수능 앞뒤 일주일", "사의까지 '6일'"),
      panel([("11월 16일 국회", "\"AI 커닝 100%? '못 할 것 같다'\""),
             ("11월 19일 수능", "전자기기 부정행위 '111건' 적발"),
             ("11월 20일", "\"사퇴하라고 하면 '해야죠'\""),
             ("11월 21일", "수험생연대·국민의힘 '사퇴 촉구'"),
             ("11월 22일", "결국 '사의 표명'")], h=680),
      "'나이' 발언 논란에서 사퇴까지", "연합뉴스·뉴스1·MBC·한국경제 보도").save(O / "c03.jpg", quality=93)

# 4장 남은 숙제
frame(("장관은 물러나도", "'숙제'는 남았다"),
      panel([("적발 111건", "재난문자 54 · 신호탐지 52 · 실제 사용 '5'"),
             ("사후 추적", "와이파이·블루투스 신호 '분석 수사'"),
             ("신고 포상금", "부정행위 1건당 '최소 1억'"),
             ("시험 제도", "대통령 \"국가시험 '전면 개편'\"")], h=640),
      "다음 장관의 '첫 과제'", "교육부·국무총리·대통령 발표(11.19~21)").save(O / "c04.jpg", quality=93)
print("ok")
