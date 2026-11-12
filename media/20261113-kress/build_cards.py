"""20261113-kress: 참고 게시물(@peakon.mag DfpWK1dn2Lr) 구성 — 표지(말풍선) → 사임 사실+사진 → 임시 CEO 크레스 → 머스크 X → 팔로우.
2~4장은 검은 바탕 '위 문구 + 가운데 사진 + 아래 노란 한 줄' 틀로 직접 그림. 표지 배경에도 말풍선을 그려 둠."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
PEN = lambda s: ImageFont.truetype(str(R / "assets/fonts/HiMelody-Regular.ttf"), s)


def bubble(im, cx, cy, text, w=380, h=170, tail="bl", fs=50):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    tx = {"bl": (x0 + w * .28, y1 - 10, x0 + w * .12, y1 + 60, x0 + w * .42, y1 - 18),
          "br": (x1 - w * .28, y1 - 10, x1 - w * .12, y1 + 60, x1 - w * .42, y1 - 18)}[tail]
    d.polygon([(tx[0], tx[1]), (tx[2], tx[3]), (tx[4], tx[5])], fill="white", outline="black")
    d.ellipse((x0, y0, x1, y1), fill="white", outline="black", width=4)
    d.polygon([(tx[0], tx[1] - 6), (tx[2] + 4, tx[3] - 8), (tx[4], tx[5] - 4)], fill="white")
    lines = text.split("\n"); lh = fs + 6; y = cy - lh * len(lines) / 2 + fs * .5
    for ln in lines:
        d.text((cx, y), ln, font=PEN(fs), fill="black", anchor="mm"); y += lh


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


def frame(top, photo, bottom, sub=None, focus=(.5, .5), bub=None, ph=760):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    pw = 940; p = fit(photo, pw, ph, focus) if isinstance(photo, (str, Path)) else photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    if bub: bubble(im, *bub)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


# 표지 배경: 젠슨 황(IBTimes) 세로로 + 말풍선
c = fit(O / "press02.jpg", 1080, 1350, (.52, .3)); bubble(c, 790, 640, "믿기지가...\n않는군...", 360, 160, "bl", 52)
c.save(O / "cover_bg.jpg", quality=95)
# CTA 배경
fit(O / "press02.jpg", 1080, 1350, (.52, .3)).save(O / "cta_bg.jpg", quality=95)

frame(("11월 12일 젠슨 황이", "엔비디아 CEO·이사직 '즉시 사임'"), O / "alice.jpg",
      "와... 와... 믿기지가 않는다", sub="불륜 인정 나흘 만에 (사진: 젠슨 황과 앨리스 황)", focus=(.5, .4),
      bub=(270, 920, "이게 말이\n되냐고요", 320, 150, "br", 48)).save(O / "c02.jpg", quality=95)

frame(("갑자기 비어버린 엔비디아 수장 자리엔", "'콜레트 크레스' CFO가 임시 CEO로"), O / "press01.jpg",
      "정식 후임 정해질 때까지 CFO와 겸직", sub="2013년 입사 · 마이크로소프트 13년 · 시스코 CFO 출신 (59세)",
      focus=(.5, .22), bub=(300, 420, "제가 잠시\n맡겠습니다", 340, 160, "br", 50)).save(O / "c03.jpg", quality=95)

# 4장: 머스크·젠슨 합성(사용자 AI 이미지) 위 + 실제 X 캡처 아래
top = fit(O / "musk_ai.jpg", 940, 320, (.5, .2)); xc = Image.open(O / "x_cap.png").convert("RGB")
xc = xc.resize((940, round(xc.height * 940 / xc.width)), Image.LANCZOS)
combo = Image.new("RGB", (940, 320 + 14 + xc.height), (10, 10, 12)); combo.paste(top, (0, 0)); combo.paste(xc, (0, 334))
frame(("하루 전엔 머스크가", "\"젠슨 모시면 '영광'\""), combo, "\"일론, 젠슨 좀 데려가 줘\" → \"그럼 영광이지\"",
      sub="X @zerohedge · @elonmusk (11월 12일)", bub=(560, 520, "이거 ㄹㅇ\n되나", 250, 120, "bl", 44)).save(O / "c04.jpg", quality=95)
print("ok")
