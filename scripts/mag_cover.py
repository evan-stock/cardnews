"""매거진형 표지 배경 만들기 (2026.10.29, 전쟁 징후 17개 캐러셀에서 검증).

만든 이미지를 media/<id>/cand/<이름>.jpg 로 저장 → 원고 images[0]에 그 이름을 넣고
표지 장은 평소처럼 "lay":"one" + t(얇은 줄\n굵은 줄)로 쓴다. 우리 하단 문구·로고는 렌더러가 얹는다.
→ 이 스크립트는 '사진 처리 + 위쪽 장식'만 하고, 아래 45%는 글자 자리로 비워 둔다.

사용 예:
  python scripts/mag_cover.py duotone  media/X/cand/press01.jpg media/X/cand/mag.jpg --big 17 --tag "WAR SIGNALS"
  python scripts/mag_cover.py cutout   media/X/cand/press01.jpg media/X/cand/mag.jpg --big 17 --tag "WAR SIGNALS" --bg red
  python scripts/mag_cover.py frame    media/X/cand/press01.jpg media/X/cand/mag.jpg
  python scripts/mag_cover.py bignum   media/X/cand/press01.jpg media/X/cand/mag.jpg --big 17 --line1 "개 중" --line2 "2개 켜짐"
  python scripts/mag_cover.py halftone media/X/cand/press01.jpg media/X/cand/mag.jpg --tag "전쟁 징후 체크"
  python scripts/mag_cover.py symbol   media/X/cand/press01.jpg media/X/cand/mag.jpg --tag "NO.17"
  python scripts/mag_cover.py split    media/X/cand/top.jpg     media/X/cand/mag.jpg --second media/X/cand/bottom.jpg
옵션: --fx/--fy(크롭 위치 0~1), --color red|yellow|blue|green(듀오톤 색).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FB = str(ROOT / "assets/fonts/Pretendard-Black.otf")
FM = str(ROOT / "assets/fonts/Pretendard-Medium.otf")
W, H = 1080, 1350
Y = (255, 216, 77)  # 브랜드 노랑
TONES = {"red": ((18, 4, 6), (150, 15, 22), (240, 50, 50)),
         "yellow": ((20, 16, 4), (150, 115, 10), (255, 225, 110)),
         "blue": ((4, 8, 20), (20, 50, 140), (110, 170, 255)),
         "green": ((4, 16, 10), (15, 100, 60), (120, 230, 170))}


def font(path, size):
    return ImageFont.truetype(path, size)


def fill(im, fx=0.5, fy=0.2, w=W, h=H):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = int((im.width - w) * fx), int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def grain(im, a=8):
    n = Image.effect_noise(im.size, 40).convert("L")
    return Image.blend(im.convert("RGB"), Image.merge("RGB", (n, n, n)), a / 255)


def big_number(d, text, tag, x=60, y=40, size=360):
    if text:
        d.text((x, y), text, font=font(FB, size), fill=Y)
    if tag:
        d.text((x + 10, y + int(size * 1.03)), tag, font=font(FB, 40), fill=Y)


def duotone(src, a):
    g = ImageOps.autocontrast(fill(src, a.fx, a.fy).convert("L"), cutoff=2)
    lo, mid, hi = TONES[a.color]
    im = grain(ImageOps.colorize(g, black=lo, mid=mid, white=hi))
    big_number(ImageDraw.Draw(im), a.big, a.tag)
    return im


def cutout(src, a):
    """인물 누끼 + 뒤에 초대형 숫자(머리가 숫자를 가림). rembg 필요: pip install rembg onnxruntime"""
    from rembg import new_session, remove
    cut = remove(src.convert("RGB"), session=new_session("u2net_human_seg")).convert("RGBA")
    bgcol = {"red": (200, 20, 28), "black": (14, 14, 14), "yellow": (240, 200, 60)}.get(a.bg, (14, 14, 14))
    bg = Image.new("RGBA", (W, H), bgcol + (255,))
    d = ImageDraw.Draw(bg)
    if a.big:
        sz = 820  # 글자가 길면(예: -30%) 가로 폭에 맞춰 줄인다
        while sz > 200 and d.textlength(a.big, font=font(FB, sz)) > W - 40:
            sz -= 20
        d.text((W // 2, -60 * sz // 820), a.big, font=font(FB, sz), fill=Y + (255,), anchor="ma")
    if a.tag:
        d.text((70, 70), a.tag, font=font(FB, 38), fill=(255, 255, 255, 255))
    s = 1180 / cut.width
    cut = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
    bg.alpha_composite(cut, ((W - cut.width) // 2, 170))
    return grain(bg, 6)


def frame(src, a):
    im = grain(fill(src, a.fx, a.fy), 5)
    ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=Y, width=44)
    return im


def bignum(src, a):
    bg = Image.new("RGB", (W, H), (14, 14, 14))
    bg.paste(ImageOps.grayscale(fill(src, a.fx, a.fy, W, 540)).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(bg)
    d.text((50, 490), a.big or "", font=font(FB, 330), fill=Y)
    d.text((520, 580), a.line1 or "", font=font(FB, 90), fill=(255, 255, 255))
    d.text((520, 680), a.line2 or "", font=font(FB, 90), fill=(255, 255, 255))
    return bg


def halftone(src, a, cell=9):
    g = ImageOps.autocontrast(ImageOps.grayscale(fill(src, a.fx, a.fy)), cutoff=2)
    sm = g.resize((W // cell, H // cell))
    out = Image.new("L", (W, H), 245)
    d = ImageDraw.Draw(out)
    for yy in range(sm.height):
        for xx in range(sm.width):
            r = (1 - sm.getpixel((xx, yy)) / 255) * cell * 0.69
            if r > 0.4:
                cx, cy = xx * cell + cell / 2, yy * cell + cell / 2
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=20)
    im = out.convert("RGB")
    if a.tag:
        d = ImageDraw.Draw(im)
        f = font(FB, 52)
        tw = d.textlength(a.tag, font=f)
        d.rectangle((60, 90, 100 + tw, 160), fill=Y)
        d.text((80, 96), a.tag, font=f, fill=(15, 15, 15))
    return im


def symbol(src, a):
    """검정 바탕에 상징물 하나(미사일·건물 등)만 크게, 가장자리는 어둠에 녹임."""
    bg = Image.new("RGB", (W, H), (10, 10, 10))
    m = ImageOps.grayscale(fill(src, a.fx, a.fy, 760, 1000))
    m = ImageOps.colorize(m, (10, 10, 10), (255, 235, 180))
    mask = Image.new("L", m.size, 0)
    ImageDraw.Draw(mask).ellipse((-150, -120, m.width + 150, m.height + 40), fill=255)
    bg.paste(m, ((W - m.width) // 2, 40), mask.filter(ImageFilter.GaussianBlur(80)))
    if a.tag:
        ImageDraw.Draw(bg).text((W - 70, 70), a.tag, font=font(FB, 44), fill=Y, anchor="ra")
    return bg


def split(src, a):
    top = ImageOps.grayscale(fill(src, a.fx, a.fy, W, H // 2)).convert("RGB")
    bot = fill(Image.open(a.second).convert("RGB"), 0.5, 0.4, W, H - H // 2)
    im = Image.new("RGB", (W, H))
    im.paste(top, (0, 0))
    im.paste(bot, (0, H // 2))
    ImageDraw.Draw(im).rectangle((0, H // 2 - 4, W, H // 2 + 4), fill=Y)
    return im


STYLES = {f.__name__: f for f in (duotone, cutout, frame, bignum, halftone, symbol, split)}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("style", choices=STYLES)
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--big", default="")
    p.add_argument("--tag", default="")
    p.add_argument("--line1", default="")
    p.add_argument("--line2", default="")
    p.add_argument("--bg", default="black")
    p.add_argument("--color", default="red", choices=TONES)
    p.add_argument("--second")
    p.add_argument("--fx", type=float, default=0.5)
    p.add_argument("--fy", type=float, default=0.15)
    a = p.parse_args()
    STYLES[a.style](Image.open(a.src).convert("RGB"), a).convert("RGB").save(a.out, quality=95)
    print(a.out)
