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




frame(("중앙일보가 확인한 다섯 줄 메모", "\"몸과 정신이 '무너졌다'\""),
      panel([("첫 문장", "\"며칠새 몸과 정신이 '무너졌다'\""),
             ("이어서", "\"'아무것도' 할 수 없다\""),
             ("공개 검증을 두고", "\"가려 했지만 마지막은 '혼자이고 싶다'\""),
             ("마지막 문장", "\"이 글도 '조롱'을 당하겠지\"")], h=640),
      "부정행위 의혹에 대한 '언급은 없었다'", "중앙일보(11.21) · 일부 표현 줄임").save(O / "c02.jpg", quality=93)
desk = op("press01.jpg")
frame(("끝내 비어 있던 자리", "공개 검증장엔 '오지 않았다'"), fit(desk, 940, 560),
      "경찰 \"사망에도 '수사 계속'\"", "사진: 공개 검증장(중앙일보 장진영 기자)").save(O / "c03.jpg", quality=93)
fit(op("press01.jpg"), W, H, (.5, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
# 2026.11.21 추가: 한국경제·연합뉴스 '탈출하게 도와달라'(사망 이틀 전 행적)
frame(("숨지기 이틀 전, 집주인에게", "\"'탈출'하게 도와달라\""),
      panel([("11월 17일", "취재진 피해 건물 나갈 방법 '집주인에게 문의'"),
             ("같은 날 오후", "건물 나서다 '취재진과 마주쳐'"),
             ("본인 답변", "\"목요일에 말씀드릴 것, '실력'으로 보여드릴 수 있다\""),
             ("11월 19일 새벽", "자취방 들러 짐 일부 챙겨 '다시 나가'")], h=640),
      "그날 아침 공개 검증엔 '나타나지 않았다'", "한국경제·연합뉴스(11.21)").save(O / "c01.jpg", quality=93)
