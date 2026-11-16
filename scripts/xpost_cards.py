"""20261106-chipshock: X 게시물 재구성 카드(안사리 원글, 머스크·안사리 주고받기) + 종가 카드. 1080x1350, 디자인 v2 색·글꼴.
사용: python scripts/xpost_cards.py media/20261106-chipshock/cand
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

R = Path(__file__).resolve().parent.parent
W, H, P = 1080, 1350, 90
BG, FG, MU, YE, LN, BOX = (12, 12, 14), (255, 255, 255), (150, 156, 164), (255, 216, 77), (56, 58, 64), (24, 25, 28)
BLUE = (77, 148, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            t = (line + " " + word).strip()
            if d.textlength(t, font=font) <= maxw:
                line = t
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def rich(d, x, y, text, font):
    import re
    for p in re.split(r"('[^']*')", text):
        if not p:
            continue
        hl = p.startswith("'")
        p = p.strip("'") if hl else p
        d.text((x, y), p, font=font, fill=YE if hl else FG)
        x += d.textlength(p, font=font)


def base(bg_path=None):
    if bg_path:
        im = ImageOps.fit(Image.open(bg_path).convert("RGB"), (W, H))
        im = Image.blend(im.filter(ImageFilter.GaussianBlur(30)), Image.new("RGB", (W, H), (0, 0, 0)), 0.86)
    else:
        im = Image.new("RGB", (W, H), BG)
    return im


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")
    h = 40
    lg = lg.resize((round(lg.width * h / lg.height), h), Image.LANCZOS)
    a = lg.split()[3].point(lambda v: int(v * 0.85))
    lg.putalpha(a)
    im.paste(lg, ((W - lg.width) // 2, H - 78), lg)


def head(d, sub, title, y=110):
    d.text((P, y), sub, font=F("SemiBold", 32), fill=YE)
    y += 58
    for ln in title.split("\n"):
        rich(d, P, y, ln, F("Black", 60))
        y += 76
    return y + 14


def avatar(im, d, x, y, initials, col):
    r = 34
    d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=col)
    f = F("Black", 26)
    tw = d.textlength(initials, font=f)
    d.text((x + r - tw / 2, y + r - 16), initials, font=f, fill=(255, 255, 255))


def post_box(im, d, y, name, handle, initials, col, en, ko, meta, en_size=40):
    x0, x1 = P, W - P
    inner = x1 - x0 - 72
    fen, fko = F("SemiBold", en_size), F("Medium", 34)
    en_l = wrap(d, en, fen, inner)
    ko_l = wrap(d, ko, fko, inner)
    h = 36 + 68 + 30 + len(en_l) * int(en_size * 1.32) + 26 + 2 + 26 + len(ko_l) * 48 + (60 if meta else 10) + 20
    d.rounded_rectangle((x0, y, x1, y + h), 28, fill=BOX, outline=LN, width=3)
    cx, cy = x0 + 36, y + 36
    avatar(im, d, cx, cy, initials, col)
    d.text((cx + 88, cy + 4), name, font=F("Black", 30), fill=FG)
    d.text((cx + 88, cy + 42), handle, font=F("Medium", 26), fill=MU)
    d.text((x1 - 36 - 26, cy + 14), "𝕏", font=F("Black", 30), fill=FG) if False else None
    ty = cy + 68 + 30
    for ln in en_l:
        d.text((cx, ty), ln, font=fen, fill=FG)
        ty += int(en_size * 1.32)
    ty += 26
    d.line((cx, ty, x1 - 36, ty), fill=LN, width=2)
    ty += 26
    for ln in ko_l:
        rich(d, cx, ty, ln, fko)
        ty += 48
    if meta:
        ty += 14
        d.text((cx, ty), meta, font=F("Medium", 26), fill=MU)
    return y + h


def card_ansari(out_dir):
    im = base()
    d = ImageDraw.Draw(im)
    y = head(d, "11월 4일(현지) · 미 하원의원 X 게시물", "선거 이긴 다음 날,\n'1순위'로 꼽은 것")
    y = post_box(im, d, y + 10, "Yassamin Ansari", "@RepYassAnsari · 민주당, 애리조나", "YA", (52, 92, 170),
                 "Top of the Democratic agenda on day 1 needs to be a pause on advanced AI development, "
                 "regulation of this out of control industry, and a ban on artificial superintelligence.",
                 "민주당이 첫날 할 일 1순위는 '고급 AI 개발 중단', 통제 불능인 이 업계에 대한 규제, "
                 "그리고 '초지능 금지'여야 합니다.",
                 "조회 1,700만 회 이상 (11월 6일 기준)", en_size=38)
    d.text((P, y + 24), "X 게시물 내용을 옮겨 구성 · 번역 오늘의쓸모", font=F("Medium", 24), fill=MU)
    y += 110
    d.text((P, y), "누구길래?", font=F("SemiBold", 32), fill=YE)
    y += 56
    for ln in ["야사민 안사리, 34세. 애리조나 3선거구.", "미 하원 '첫 이란계 민주당 의원'이자 최연소 여성 의원.",
               "이번 중간선거에서 '재선'에 성공했습니다."]:
        rich(d, P, y, ln, F("Medium", 34))
        y += 52
    logo(im)
    im.save(out_dir / "x_ansari.jpg", quality=93)


def card_musk(out_dir):
    im = base()
    d = ImageDraw.Draw(im)
    y = head(d, "머스크의 반응", "머스크 '\"멋진 신세계군\"'\n안사리 \"곧 봅시다\"", y=150)
    y = post_box(im, d, y + 4, "Elon Musk", "@elonmusk · 안사리 글 인용", "EM", (60, 60, 66),
                 "It's a Brave New World", "'\"멋진 신세계군\"' — 헉슬리의 디스토피아 소설 제목",
                 None, en_size=44)
    y = post_box(im, d, y + 28, "Yassamin Ansari", "@RepYassAnsari · 머스크 글 인용", "YA", (52, 92, 170),
                 "See you soon.", "'\"곧 봅시다.\"'", "조회 78만 회 이상", en_size=44)
    d.text((P, y + 24), "X 게시물 내용을 옮겨 구성 · 번역 오늘의쓸모", font=F("Medium", 24), fill=MU)
    logo(im)
    im.save(out_dir / "x_musk.jpg", quality=93)


def card_stocks(out_dir):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = 150
    for name, price, pct in [("삼성전자", "188,700원", "▼ 6.35%"), ("SK하이닉스", "1,132,000원", "▼ 10.44%")]:
        d.text((P, y), name, font=F("SemiBold", 40), fill=MU)
        d.text((P, y + 56), price, font=F("Black", 104), fill=FG)
        d.text((P, y + 182), pct, font=F("Black", 58), fill=BLUE)
        y += 300
    d.text((P, y - 20), "11월 6일 종가 · 한국거래소", font=F("Medium", 30), fill=MU)
    im.save(out_dir / "stocks_close.jpg", quality=93)


if __name__ == "__main__":
    o = Path(sys.argv[1])
    card_ansari(o)
    card_musk(o)
    card_stocks(o)
