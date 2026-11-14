"""20261114-sonyeon: 행시(5급 공채) 행정직 수석·최연소 김재겸의 '소년등과 일불행' 소감. 세무사 수석 논란과 대비.
표지 = 검은 바탕 틀(frame, kress에서 복사) + 증명사진·한자 구절 패널. 2장 = lay one CTA(배경 cta_bg)."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
HJ = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=1)  # TC


def rich_center(d, y, text, font, base, cx=W / 2):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = cx - tw / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, p, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


PW, PH = 940, 760
def dark_books(alpha=0.22):
    b = ImageOps.fit(Image.open(O / "press03.jpg").convert("RGB"), (PW, PH), Image.LANCZOS)
    return b.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * alpha))

# 1장 표지: 왼쪽 증명사진 + 오른쪽 이력(답은 숨김)
panel = dark_books()
por = Image.open(O / "press01.jpg").convert("RGB")
pw = round(por.width * PH / por.height)
por = por.resize((pw, PH), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2)).crop((60, 0, pw - 52, PH))
panel.paste(por, (0, 0))
pd = ImageDraw.Draw(panel); rx = por.width + (PW - por.width) / 2
rows = [("2005년생", "Black", 60, FG), ("만 21세", "Medium", 40, (200, 200, 206)), ("", None, 0, None),
        ("행정직", "Medium", 40, (200, 200, 206)), ("수석", "Black", 76, YE), ("+", "Medium", 40, (200, 200, 206)),
        ("최연소", "Black", 76, YE), ("", None, 0, None), ("서울대 철학과 3학년", "Medium", 32, (170, 170, 178))]
y = 120
for t, w, sz, c in rows:
    if not t: y += 34; continue
    if w == "Black" and sz > 60: y += 30
    pd.text((rx, y), t, font=F(w, sz), fill=c, anchor="ms"); y += sz + 26
frame(("세무사 수석이 '논란'으로 시끄러운 사이", "행시 수석·최연소의 '한마디'"), panel,
      "최연소 소감 묻자 꺼낸 '옛말' 한 줄", sub="2026 5급 공채(옛 행정고시) 김재겸 씨").save(O / "c01.jpg", quality=95)

# 2장 본문: 한자 구절 공개
panel = dark_books(0.3); pd = ImageDraw.Draw(panel)
fs = 112; cx = PW / 2
for ci, (col, color) in enumerate(zip([("少", "年", "登", "高", "科"), ("一", "不", "幸")], [FG, YE])):
    x = cx + (90 if ci == 0 else -90); y0 = 40 if ci == 0 else 40 + fs * 1.12
    for i, ch in enumerate(col):
        pd.text((x, y0 + i * fs * 1.12), ch, font=HJ(fs), fill=color, anchor="mt")
pd.text((cx, PH - 52), "소년등고과 일불행 · 북송 유학자 정자", font=F("SemiBold", 32), fill=(215, 215, 222), anchor="ms")
frame(("최연소 소감을 묻자 꺼낸 말", "어린 나이 급제가 '첫째 불행'"), panel,
      "\"최연소로서 무언가를 하기보다\"", sub="국민 공복의 일인으로서 끊임없이 노력하겠다는 다짐").save(O / "c02.jpg", quality=95)

# CTA 배경: 수험 때 쌓아둔 책(법률저널)
ImageOps.fit(Image.open(O / "press03.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.5, .35)).save(O / "cta_bg.jpg", quality=95)
print("ok")

# 최종 표지(사용자 선택 2026.11.14 19:38): 증명사진 + 한자 세로쓰기(한글 독음·출처 줄 없음)
panel = dark_books()
por = Image.open(O / "press01.jpg").convert("RGB")
pw = round(por.width * PH / por.height)
por = por.resize((pw, PH), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2)).crop((60, 0, pw - 52, PH))
panel.paste(por, (0, 0))
pd = ImageDraw.Draw(panel); rx = por.width + (PW - por.width) / 2
fs = 92; step = fs * 1.15; y0 = (PH - (4 * step + fs * 1.1)) / 2
for ci, (col, color) in enumerate(zip([("少", "年", "登", "高", "科"), ("一", "不", "幸")], [FG, YE])):
    x = rx + (52 if ci == 0 else -52); ys = y0 if ci == 0 else y0 + step
    for i, ch in enumerate(col):
        pd.text((x, ys + i * step), ch, font=HJ(fs), fill=color, anchor="mt")
frame(("세무사 수석이 '논란'으로 시끄러운 사이", "행시 수석·최연소의 '한마디'"), panel,
      "어린 나이 급제는 '첫째 불행'이다", sub="05년생 김재겸(21) · 5급 공채 행정직 수석 · 서울대 철학과").save(O / "c01final.jpg", quality=95)
print("final ok")

# 표지 사진(우리 lay one 표지에 넣을 1080x1350): 증명사진 + 한자 세로쓰기, 글자 없음
CW, CH = 1080, 1350
bg = ImageOps.fit(Image.open(O / "press03.jpg").convert("RGB"), (CW, CH), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.2))
por = Image.open(O / "press01.jpg").convert("RGB")
ph = 1080; pw = round(por.width * ph / por.height)
por = por.resize((pw, ph), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2))
por = por.crop(((pw - 640) // 2 - 10, 0, (pw - 640) // 2 + 630, ph))
bg.paste(por, (0, 0))
dd = ImageDraw.Draw(bg); rx = 640 + (CW - 640) / 2
fs = 112; step = fs * 1.15; y0 = 110
for ci, (col, color) in enumerate(zip([("少", "年", "登", "高", "科"), ("一", "不", "幸")], [FG, YE])):
    x = rx + (64 if ci == 0 else -64); ys = y0 if ci == 0 else y0 + step
    for i, ch in enumerate(col):
        dd.text((x, ys + i * step), ch, font=HJ(fs), fill=color, anchor="mt")
bg.save(O / "cover_photo.jpg", quality=95)
print("cover_photo ok")
