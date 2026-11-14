"""20261114-faastop: 미국 전역 이륙 중단. 표지 lay one + 2~5장 검은 바탕 frame 틀 + CTA lay one."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255); GR = (190, 190, 198)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def fit(src, w, h, focus=(.5, .5)):
    return ImageOps.fit(Image.open(src).convert("RGB"), (w, h), Image.LANCZOS, centering=focus)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None, focus=(.5, .5), ph=760, py=300):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, py - 132, top[0], F("Medium", 46), FG); rich_center(d, py - 64, top[1], F("Black", 54), FG)
    pw = 940; p = fit(photo, pw, ph, focus) if isinstance(photo, (str, Path)) else photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, py), m)
    d = ImageDraw.Draw(im); y = py + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), GR)
    logo(im); return im


def timeline():
    g = Image.new("RGB", (940, 640), (24, 24, 28)); d = ImageDraw.Draw(g)
    rows = [("9월 21일", "AI 'SMART' 워싱턴서 첫 시범", "같은 날 뉴욕 일대 공항은 통신선 절단으로 마비", False),
            ("11월 10일 (화)", "22개 관제센터 '전부'로 확대", "8억 7500만 달러 · 12년 계약", False),
            ("11월 13일 (금)", "미국 전역 이륙 중단", "항로관제센터 통신 장애", True)]
    x0 = 70; ys = [110, 320, 530]
    d.line((x0, ys[0], x0, ys[-1]), fill=(90, 90, 98), width=6)
    for (dt, t, s, hot), y in zip(rows, ys):
        c = YE if hot else (210, 210, 216); r = 20 if hot else 15
        d.ellipse((x0 - r, y - r, x0 + r, y + r), fill=c)
        d.text((x0 + 52, y - 42), dt, font=F("Medium", 32), fill=YE if hot else GR, anchor="ls")
        tt = t.replace("'", ""); d.text((x0 + 52, y + 14), tt, font=F("Black", 46), fill=YE if hot else FG, anchor="ls")
        d.text((x0 + 52, y + 62), s, font=F("Medium", 32), fill=GR, anchor="ls")
    return g



frame(("AI 관제 확대 사흘 뒤인 13일", "미국 '모든 공항' 이륙 금지"), O / "press01.jpg",
      "지연 1만 편 · 결항 2천 편 넘어", sub="FlightAware 13일 저녁 집계 (하루 전체 기준)",
      ph=600, py=370).save(O / "c02.jpg", quality=95)

frame(("11월 10일 FAA 발표", "AI 'SMART' 관제센터 22곳 '전부'에"), O / "press03.jpg",
      "날씨·항로·인력 데이터 200개로 '경로 추천'", sub="비행기를 직접 조종하진 않고, 관제 쪽에 추천만 (FAA)",
      ph=600, py=370, focus=(.35, .5)).save(O / "c03.jpg", quality=95)

frame(("시범 7주 만에 전국으로", "그리고 '사흘 뒤' 하늘이 멈췄다"), timeline(),
      "관제사 노조·의원들 \"검증 부족, 확대 미뤄라\"", sub="확대 전부터 나온 요구 (노조 \"협의에서 빠졌다\")",
      ph=640, py=330).save(O / "c04.jpg", quality=95)

frame(("개발사 \"SMART와 무관\" · 정부 \"통신 장애\"", "국토안보장관 \"'아무것도' 배제 안 해\""), O / "press08.jpg",
      "원인은 아직 발표 전", sub="CNN \"수사 당국 초기 판단, 사이버 공격은 아닌 듯\"",
      ph=600, py=370).save(O / "c05.jpg", quality=95)
print("ok")
