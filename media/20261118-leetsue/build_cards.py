"""20261118-leetsue: 리트 만점자 현직 변호사 형사고발(관악경찰서) + 시대인재 계약 해지. 실명·개명 전 이름 쓰지 않음.
표지 lay one(사진 꽉 채움, 테두리 없음) + 2~4장 검은 바탕 틀(taxyoung-c·jinwoo-ow와 같은 frame) + CTA. 따옴표는 기사 속 고발인 실제 발언만."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

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


def panel(rows, w=940, h=600):
    p = Image.new("RGB", (w, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = (h - 80) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 50 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198))
        x = 56
        for s in re.split(r"('[^']*')", v):
            if not s: continue
            hl = s.startswith("'"); s = s.strip("'")
            d.text((x, y + 44), s, font=F("Black", 42), fill=YE if hl else FG); x += d.textlength(s, font=F("Black", 42))
    return p


op = lambda n: Image.open(O / n).convert("RGB")
sh = lambda im: im.filter(ImageFilter.UnsharpMask(2, 60, 2))
fit = lambda im, w, h, c=(.5, .5): sh(ImageOps.fit(im, (w, h), Image.LANCZOS, centering=c))

# 표지: 사진을 화면에 꽉(테두리 없이)
fit(op("press01.jpg"), W, H, (.42, .3)).save(O / "cover_bg.jpg", quality=95)
frame(("18일 서울 관악경찰서", "현직 변호사들 '고발장' 제출"), fit(op("press03.jpg"), 940, 590),
      "공무집행방해·업무방해·공문서 변조 등", "리트뿐 아니라 지난해 수능까지 수사 요청").save(O / "c02.jpg", quality=93)
frame(("고발인 방민우 변호사", "\"강제수사로 확보할 자료가 '많다'\""),
      panel([("수사 요구", "'금융거래 내역'까지 확인해야"), ("확인할 것", "부정행위 물품을 '샀는지'"), ("고발 대상", "올해 리트 + 지난해 '수능'")]),
      "고발 단계, 혐의는 수사로 확인", "경향신문·이데일리(11.18)").save(O / "c03.jpg", quality=93)
frame(("수능 직전 '생명과학Ⅱ 과외' 의혹에", "입시업체도 '계약 해지'"), fit(op("press02.jpg"), 940, 534, (.5, .4)),
      "시대인재, '브레인코치' 계약 해지", "본인은 AI 사용 부인 · 19일 수능 국어 생중계 예고").save(O / "c04.jpg", quality=93)
print("ok")
