"""20261117-check: 수능날 이렇게 검사한다(17일 국무회의·총리 발표 + 정부 후속). 표지·CTA lay one + 2~6장 검은 바탕 틀(frame).
사진: 기사 수집(cand/press07 아시아투데이 총리, press05 세계일보 단추 카메라)."""
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


frame(("한성숙 총리, 17일 국무회의", "\"직을 걸고 '막아야'\""), fit(op("press07.jpg"), 940, 640, (.5, .45)),
      "수능 부정행위 '발본색원'", "의심 사례는 끝까지 추적하겠다").save(O / "c02.jpg", quality=93)
frame(("모레(19일) 시험장에 들어가면", "이렇게 '검사'한다"),
      panel([("스마트기기", "전원 끄고 '전부 수거'"), ("안경·시계", "한 명도 빠짐없이 '전수 점검'"), ("옷깃·소매·단추", "'꼼꼼하게' 살핀다"), ("가방", "시험실 밖 '복도'에 따로 보관")]),
      "평소 쓰던 안경도 '점검 대상'", "17일 국무회의 발표").save(O / "c03.jpg", quality=93)
frame(("이런 걸 잡겠다는 것", "지퍼에 숨긴 '초소형 카메라'"), fit(op("press05.jpg"), 940, 640),
      "맨눈으로는 구분이 어렵다", "사진: 세계일보").save(O / "c04.jpg", quality=93)
frame(("걸리면", "'무관용'"),
      panel([("현장 적발", "시험 '무효' + 응시자격 박탈"), ("응시 제한", "1년 → '3년' 추진"), ("수사", "'고발·수사의뢰'까지"), ("사전 모의", "현장 부정행위와 똑같이 '엄단'")]),
      "끝나고 신고돼도 '같은 처벌'", "교육부·총리 발표(11.16~17)").save(O / "c05.jpg", quality=93)
frame(("정부가 동시에 하는 것", "'비상근무' 돌입"),
      panel([("청와대", "AI 부정행위 '비상대책 TF'"), ("시험장 1,312곳", "스마트안경 '전담 요원' 배치"), ("시험장 주변", "와이파이 관리·감독관 '추가'"), ("네이버·당근", "AI 안경·카메라 '거래 관리'"), ("국가자격시험", "감시 예산 '182억' 증액 추진")], gap=118),
      "그래도 전파 차단은 '안 한다'", "JTBC·연합뉴스(11.17)").save(O / "c06.jpg", quality=93)
cov = fit(op("press05.jpg"), W, H); cov.save(O / "cover_bg.jpg", quality=95)
print("ok")
