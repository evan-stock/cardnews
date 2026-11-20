"""20261120-xiref: 참고 @algosave 게시물('다카이치가 중국에 받은 대우', 10장) 구성을 그대로 따라 오늘의쓸모 디자인으로.
사진은 SBS D리포트 화면(박힌 자막·로고 잘라냄)만 사용. 참고 게시물의 사진·댓글은 쓰지 않음. 따옴표는 SBS가 전한 일본 외무성 간부 발언만.
"""
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



def sbs(n, box=(40, 95, 1130, 568)):  # SBS 1280x720: 위 로고·아래 박힌 자막 잘라냄
    return op(n).crop(box)
def stack(imgs, h):
    g = 14; hh = (h - g * (len(imgs) - 1)) // len(imgs)
    im = Image.new("RGB", (940, h), (10, 10, 12)); y = 0
    for a in imgs: im.paste(fit(a, 940, hh, (.5, .5)), (0, y)); y += hh + g
    return im
def side(imgs, h, labels):
    g = 10; ww = (940 - g * (len(imgs) - 1)) // len(imgs)
    im = Image.new("RGB", (940, h), (10, 10, 12)); x = 0
    for a in imgs: im.paste(fit(a, ww, h, (.5, .5)), (x, 0)); x += ww + g
    return tagged(im, [(14 + k * (ww + g), h - 64, t, c) for k, (t, c) in enumerate(labels)])
def tagged(im, labels):
    d = ImageDraw.Draw(im); f = F("ExtraBold", 30)
    for (x, y, t, col) in labels:
        w = d.textlength(t, font=f); d.rounded_rectangle((x, y, x + w + 28, y + 50), 10, fill=col); d.text((x + 14, y + 25), t, font=f, fill=(0, 0, 0) if col == YE else FG, anchor="lm")
    return im
def ring(im, box, width=8):
    d = ImageDraw.Draw(im); d.ellipse(box, outline=YE, width=width); return im
RED = (214, 52, 52)
# 2 일본 전용기 + 계단 비교(일본·미국·한국)
frame(("일본 총리 전용기 도착", "계단부터 '비교'됐다"),
      stack([sbs("y_0.5.png"), side([sbs("y_0.5.png", (420, 160, 900, 568)), sbs("y_26.0.png", (330, 40, 790, 568)), sbs("y_35.0.png", (300, 95, 900, 568))], 400,
                                    [("일본", RED), ("미국", YE), ("한국", YE)])], 760),
      "온라인에선 '계단 높이' 차이도 화제", "영상: SBS D리포트").save(O / "c02.jpg", quality=93)
# 3 영접 인사
frame(("다카이치를 맞은 사람은", "'5년 전 퇴직한' 외교관"), stack([sbs("y_16.5.png"), sbs("y_18.5.png")], 760),
      "영접 담당 대사, 고위 지도자 아니었다", "일본 언론 보도 · 영상: SBS D리포트").save(O / "c03.jpg", quality=93)
# 4 트럼프는 시진핑이 직접
frame(("반면 트럼프는", "시진핑이 '직접' 마중"), tagged(stack([sbs("y_21.5.png"), sbs("y_24.5.png")], 760), [(16, 16, "트럼프", YE)]),
      "차에서 내려 공항까지 직접 나왔다", "영상: SBS D리포트").save(O / "c04.jpg", quality=93)
# 5 한국은 환영 인파
frame(("한국 대통령 도착 땐", "'환영 인파'에 군악대"), tagged(stack([sbs("y_32.5.png"), sbs("y_38.5.png")], 760), [(16, 16, "한국", YE)]),
      "전용기 앞까지 빼곡한 환영 행렬", "영상: SBS D리포트").save(O / "c05.jpg", quality=93)
# 6 한국 vs 일본
frame(("같은 공항, 같은 APEC", "'환영 인파' vs '10명 남짓'"), side([sbs("y_38.5.png", (300, 95, 900, 568)), sbs("y_9.5.png", (300, 95, 900, 568))], 640, [("한국", YE), ("일본", RED)]),
      "일본 외무성 간부 \"외교상 최소한의 예의도 없어\"", "SBS 보도 · 일본 쪽은 꽃도 음악도 없었다(일본 언론)").save(O / "c06.jpg", quality=93)
# 7 만찬 악수
frame(("만찬장에선", "말 건네도 '대답 없이'"), fit(sbs("y_80.8.png"), 940, 444),
      "악수만 하고 대화는 없었다", "중화권 매체 보도 · 영상: SBS D리포트").save(O / "c07.jpg", quality=93)
# 8 혼자 입장
frame(("만찬장 입장도", "'혼자' 걸어 들어왔다"), fit(sbs("y_77.6.png"), 940, 700, (.5, .3)),
      "웃으며 들어왔지만", "영상: SBS D리포트").save(O / "c08.jpg", quality=93)
# 9 기념촬영 뒷줄
g = op("y_42.5.png").crop((0, 100, 1280, 640)); ring(g, (980, 60, 1130, 430))
frame(("기념촬영 자리는", "'뒷줄 구석'으로 마무리"), fit(g, 940, 520, (.5, .5)),
      "다카이치, 뒷줄 오른쪽 배치", "SBS 보도 · 영상: SBS D리포트").save(O / "c09.jpg", quality=93)
# 표지: 기념촬영(시진핑 앞줄, 다카이치 뒷줄 노란 동그라미) 위쪽 크게 + 아래 어두운 제목 자리
cv = Image.new("RGB", (W, H), (10, 10, 12))
top = op("y_42.5.png").crop((400, 110, 1150, 650)); ring(top, (590, 50, 740, 420), 10)
top = top.resize((W, round(top.height * W / top.width)), Image.LANCZOS)
cv.paste(top.filter(ImageFilter.GaussianBlur(30)).resize((W, H)), (0, 0)); cv.paste(top, (0, 0))
cv.save(O / "cover_bg.jpg", quality=95)
print("ok")
