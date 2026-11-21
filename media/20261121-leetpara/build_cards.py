"""20261121-leetpara: 리트 만점자 '단양 패러글라이딩 각성' 일화 거짓 의혹. 본문은 커뮤니티 캡처(나무위키 캡처·처분 정리 이미지, 디시 글).
표지: 인터뷰 사진 + 단양 패러글라이딩(위키미디어 공용 CC BY 4.0) 좌우 페이드. leetaccomp/build_cards.py 복사."""
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




ref = op("ref_full.jpg")  # 참고 게시물(커뮤니티에 돈 캡처)
namu = ref.crop((100, 0, 1340, 380)).resize((940, round(380 * 940 / 1240)), Image.LANCZOS)
frame(("커뮤니티에 퍼진 캡처", "본인이 밝혀온 '각성' 일화"), namu,
      "\"단양에서 '패러글라이딩' 설명 읽고 각성\"", "온라인 커뮤니티 게시글 속 나무위키 캡처").save(O / "c02.jpg", quality=93)
frame(("함께 퍼진 처분 이력", "2022년 9월 '징역 6개월 실형'"),
      panel([("2022년 9월 선고(보도)", "공갈·공갈미수 '징역 6개월 실형'"),
             ("본인이 말한 일화 시기", "2022년 말 '3주 전국일주'"),
             ("다른 보도 속 일화 시기", "2023년 '도보 전국일주'(주간경향)"),
             ("누리꾼 주장", "\"그때는 '수감 중' 아니었나\"")], h=640),
      "2022년 말이면 '수감 기간'과 겹칠 수 있다", "처분 이력은 언론 보도 기준 · 출소 시점 미확인").save(O / "c03.jpg", quality=93)
b3 = op("baek3.jpg"); b3 = b3.resize((940, round(b3.height * 940 / b3.width)), Image.LANCZOS)
frame(("인터뷰에서 직접 말한 각성 순간", "\"이 글에만 '집중할 힘'이 생겼다\""), b3,
      "패러글라이딩 원리 글이 \"'너무 잘' 읽혔다\"", "사진: 유튜브 '지금 백지연' 인터뷰(11.19 공개)").save(O / "c01.jpg", quality=93)
# 표지: 위 백지연 인터뷰 장면, 아래 패러글라이딩, 사이 페이드
iv = op("baek1.jpg"); iv = iv.resize((W, round(iv.height * W / iv.width)), Image.LANCZOS)  # 1080x608
pg = op("para2.jpg").crop((0, 0, 1700, 1000)); PH = 990; pg = pg.resize((round(pg.width * PH / pg.height), PH), Image.LANCZOS)
x0 = (pg.width - W) // 2 + 120; pg = pg.crop((x0, 0, x0 + W, PH))
cv = Image.new("RGB", (W, H)); cv.paste(pg, (0, H - PH)); fade = 230
m = Image.new("L", (W, iv.height), 255); md = ImageDraw.Draw(m)
for y in range(iv.height - fade, iv.height): md.line([(0, y), (W, y)], fill=round(255 * (iv.height - y) / fade))
cv.paste(iv, (0, 0), m); cv.save(O / "cover_bg.jpg", quality=95)
print("ok")
