"""20261120-xicard: 같은 날 시진핑, 트럼프 환대 vs 다카이치 냉대 비교 캐러셀(참고 @algosave 게시물처럼 장면 캡처 비교). sidae/build_cards.py 복사.
장면: SBS D리포트(박힌 자막·로고 잘라냄), Viory(트럼프·시진핑 악수). 사실: SBS·뉴스핌·아주경제·서울신문 11.19~20. 따옴표 없음."""
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



def sbs(n):  # SBS 1280x720: 위 로고·아래 박힌 자막 잘라냄
    return op(n).crop((40, 95, 1130, 612))
def pair(a, b, h=372):
    im = Image.new("RGB", (940, h * 2 + 14), (10, 10, 12))
    im.paste(fit(a, 940, h, (.5, .5)), (0, 0)); im.paste(fit(b, 940, h, (.5, .5)), (0, h + 14))
    return im
def tagged(im, labels):  # 사진 왼쪽 위에 작은 꼬리표
    d = ImageDraw.Draw(im); f = F("ExtraBold", 30)
    for (x, y, t, col) in labels:
        w = d.textlength(t, font=f); d.rounded_rectangle((x, y, x + w + 28, y + 50), 10, fill=col); d.text((x + 14, y + 25), t, font=f, fill=(0, 0, 0) if col == YE else FG, anchor="lm")
    return im
RED = (214, 52, 52)
frame(("트럼프 공항 도착", "시진핑이 '직접' 마중"), tagged(pair(sbs("y_21.5.png"), sbs("y_24.5.png")), [(16, 16, "환대", YE)]),
      "차에서 내려 직접 영접", "영상: SBS D리포트").save(O / "c02.jpg", quality=93)
frame(("같은 날 다카이치 도착", "영접은 '외교부 의전 대사'"), tagged(pair(sbs("y_1.5.png"), sbs("y_16.5.png")), [(16, 16, "냉대", RED)]),
      "의장대 10명 남짓, 꽃도 음악도 없었다", "일본 언론 보도 · 영상: SBS D리포트").save(O / "c03.jpg", quality=93)
frame(("트럼프와는 웃으며 악수", "다카이치와는 '대화 없이'"), tagged(pair(op("v3a.png"), sbs("y_80.8.png")), [(16, 16, "트럼프", YE), (16, 402, "다카이치", RED)]),
      "정상회담도 끝내 무산", "중화권 매체 보도 · 영상: Viory, SBS D리포트").save(O / "c04.jpg", quality=93)
# 표지: 위 트럼프·시진핑 악수(환대) / 아래 다카이치 공항(냉대), 꽉 채움
cv = Image.new("RGB", (W, H))
cv.paste(fit(op("v3a.png"), W, 640, (.5, .45)), (0, 0)); cv.paste(fit(sbs("y_16.5.png"), W, H - 646, (1.0, .3)), (0, 646))
ImageDraw.Draw(cv).rectangle((0, 640, W, 646), fill=(10, 10, 12))
tagged(cv, [(30, 40, "트럼프 · 환대", YE), (30, 676, "다카이치 · 냉대", RED)])
cv.save(O / "cover_bg.jpg", quality=95)
print("ok")
