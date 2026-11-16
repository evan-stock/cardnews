"""20261114-gokp: 고경표 음주사고. 표지 lay one + 2~4장 frame + CTA."""
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
    rows = [("오늘(14일) 오후 6시 30분", "MBC '놀면 뭐하니?' 방송", "'95 서울가요제' 출연 예정", True),
            ("11월 21일 (토)", "단독 팬미팅", "서울 성암아트홀 · 오후 2시·6시", False),
            ("11월 29일 (일)", "tvN '보검 매직컬2' 첫 방송", "박보검·이상이와 새 멤버로 합류", False)]
    x0 = 70; ys = [110, 320, 530]
    d.line((x0, ys[0], x0, ys[-1]), fill=(90, 90, 98), width=6)
    for (dt, t, s, hot), y in zip(rows, ys):
        c = YE if hot else (210, 210, 216); r = 20 if hot else 15
        d.ellipse((x0 - r, y - r, x0 + r, y + r), fill=c)
        d.text((x0 + 52, y - 42), dt, font=F("Medium", 32), fill=YE if hot else GR, anchor="ls")
        d.text((x0 + 52, y + 14), t, font=F("Black", 46), fill=YE if hot else FG, anchor="ls")
        d.text((x0 + 52, y + 62), s, font=F("Medium", 32), fill=GR, anchor="ls")
    return g



im = Image.open(O / "press12.jpg").convert("RGB"); im = im.crop((0, 0, im.width, int(im.width * 1350 / 1080)))
im.resize((1080, 1350), Image.LANCZOS).save(O / "cover_bg.jpg", quality=95)

frame(("14일 오전 3시 30분, 마포구 동교동", "만취 운전 중 '청소차' 충돌"), O / "press14.jpg",
      "혈중알코올농도 '면허 취소' 수준", sub="0.08% 이상 · 동승자 없음 · 음주측정 후 귀가 (경찰)",
      ph=600, py=370, focus=(.5, .25)).save(O / "c02.jpg", quality=95)

frame(("소속사 씨엘엔컴퍼니 공식 사과", '"잘못 인정, \'깊이 반성\'"'), O / "press01.jpg",
      '"처분 겸허히 받아들이겠다"', sub='"피해 회복을 비롯해 책임 다하겠다"',
      ph=600, py=370, focus=(.5, .3)).save(O / "c03.jpg", quality=95)

frame(("하필 일정 줄줄이 앞두고", "출연 예능·팬미팅 '비상'"), timeline(),
      "편집·하차 여부는 아직 발표 전", sub="tvN 식스센스: B사이드 · 티빙 대탈출: 도시괴담도 출연",
      ph=640, py=330).save(O / "c04.jpg", quality=95)
print("ok")
