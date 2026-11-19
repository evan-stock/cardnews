"""20261119-leetjail(속보): JTBC(11.19 09:08) 리트 만점자 구치소 수감 재소자 증언·개명 전 이름·생년월일 일치 공갈 판결문. 실명·개명 전 이름 안 씀.
근거: 사용자 제공 JTBC 기사 캡처(제목·요약·첫 문단). 따옴표는 기사에 실린 증언만. sidae/build_cards.py 복사."""
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



cap = op("jtbc.jpg").crop((0, 0, 1179, 590))
for nm in ((598, 178, 835, 262), (40, 178, 250, 262)):  # 제목 속 실명·'[단독]' 가림
    cap.paste(cap.crop(nm).filter(ImageFilter.GaussianBlur(14)), nm[:2])
cap = cap.resize((940, round(590 * 940 / 1179)), Image.LANCZOS)
frame(("JTBC 보도 (11.19)", "리트 만점자 '구치소 수감' 증언"), cap,
      "개명 전 이름·생년월일 '일치' 공갈 판결문", "오늘 저녁 6시 30분 JTBC 뉴스룸 보도 예정").save(O / "c02.jpg", quality=93)
frame(("함께 수감됐다는 재소자", "\"사기로 돈 모아 '학습교재'\""),
      panel([("구치소 동료 증언", "\"사기로 돈 모아 '학습교재' 만든다고 했다\""), ("판결문", "개명 전 이름·생년월일 '일치'"), ("재판 결과", "집행유예 두 달 뒤 '동종 범죄'로 징역형"), ("오늘 공개 풀이", "끝내 '노쇼'")], h=640),
      "본인 측 입장은 아직 확인되지 않았습니다", "JTBC(11.19)").save(O / "c03.jpg", quality=93)
noshow = op("noshow.jpg").crop((0, 0, 1206, 735))
for b in ((470, 120, 830, 180), (0, 575, 1206, 700)):  # 현수막·하단 안내문 속 실명 가림
    noshow.paste(noshow.crop(b).filter(ImageFilter.GaussianBlur(12)), b[:2])
frame(("오늘 예고했던 수능 국어 공개 검증", "결국 '노쇼'"), fit(noshow, 940, 560, (.5, .5)),
      "시험지 배부 때까지 '불참', 검증 무효", "전날부터 휴대전화 꺼져, 주최 측은 경찰에 신변 확인 요청").save(O / "c04.jpg", quality=93)
# 표지: 본인 사진 | 구치소(수용자) 사진 나란히, 꽉 채움
cv = Image.new("RGB", (W, H))
cv.paste(fit(op("lee_photo.jpg"), W // 2, H, (.5, .2)), (0, 0)); cv.paste(fit(op("prison.jpg"), W // 2, H, (.5, .5)), (W // 2, 0))
ImageDraw.Draw(cv).rectangle((W // 2 - 3, 0, W // 2 + 2, H), fill=(10, 10, 12))
cv.save(O / "cover_bg.jpg", quality=95)
print("ok")
