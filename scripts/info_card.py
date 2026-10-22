"""정보형 카드(한눈에 보기) 1080x1350 생성기. 디자인 v2 색·글꼴 그대로.
사용: python scripts/info_card.py spec.json out_dir
spec: [{"name":"info1","sub":"한눈에 보기","t":"제목","kind":"rows|steps|checks",
        "items":[["라벨","값",hl]] 또는 ["문장",...], "note":"※ 각주"}]
값/문장 안 '작은따옴표'는 노랑 강조.
"""
import json, sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent
W, H, P = 1080, 1350, 90
BG, FG, MU, YE, LN = (12, 12, 14), (255, 255, 255), (165, 165, 172), (255, 216, 77), (52, 52, 58)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich(d, x, y, text, font, base, anchor="ls"):
    parts = re.split(r"(['‘’][^'‘’]*['‘’])", text)
    for p in parts:
        if not p:
            continue
        hl = p[0] in "'‘’"
        p = p.strip("'‘’") if hl else p
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor=anchor)
        x += d.textlength(p, font=font)
    return x


def card(c, out):
    im = Image.new("RGB", (W, H), BG)
    if BGIMG:  # 표지 사진을 흐리고 아주 어둡게 깔기
        from PIL import ImageFilter, ImageEnhance
        b = Image.open(BGIMG).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(18))
        b = ImageEnhance.Brightness(b).enhance(DIM)
        im = Image.blend(im, b, 1.0)
    d = ImageDraw.Draw(im)
    y = 170
    d.text((P, y), c["sub"], font=F("SemiBold", 36), fill=YE, anchor="ls")
    y += 40
    for line in c["t"].split("\n"):
        y += 92
        rich(d, P, y, line, F("Black", 80), FG)
    y += 70
    d.line((P, y, W - P, y), fill=LN, width=3)
    k = c.get("kind", "rows")
    if k == "rows":
        n = len(c["items"]); gap = min(150, (H - 300 - y) // n)
        for lab, val, *hl in c["items"]:
            y += gap
            d.text((P, y - 8), lab, font=F("Medium", 36), fill=MU, anchor="ls")
            vf = F("Black", 58)
            val_main, _, small = val.partition("|")
            x = rich(d, 360, y, f"'{val_main}'" if hl and hl[0] else val_main, vf, FG)
            if small:
                d.text((360, y + 46), small, font=F("Medium", 30), fill=MU, anchor="ls")
            d.line((P, y + (78 if small else 42), W - P, y + (78 if small else 42)), fill=LN, width=1)
            if small:
                y += 36
    elif k == "steps":
        n = len(c["items"]); gap = min(200, (H - 260 - y) // n)
        top = y + 90
        for i, (when, what) in enumerate(c["items"]):
            yy = top + i * gap
            last = i == n - 1
            col = YE if last else FG
            d.ellipse((P, yy - 14, P + 28, yy + 14), fill=col)
            if not last:
                d.line((P + 14, yy + 18, P + 14, yy + gap - 18), fill=LN, width=4)
            d.text((P + 60, yy - 22), when, font=F("SemiBold", 32), fill=YE if last else MU, anchor="ls")
            for j, ln in enumerate(what.split("\n")):
                rich(d, P + 60, yy + 34 + j * 58, ln, F("Black", 48), col)
    elif k == "checks":
        n = len(c["items"]); gap = min(215, (H - 280 - y) // n)
        for i, it in enumerate(c["items"]):
            yy = y + 110 + i * gap
            d.rounded_rectangle((P, yy - 44, P + 52, yy + 8), 12, fill=YE)
            d.line((P + 12, yy - 18, P + 23, yy - 6, P + 41, yy - 32), fill=BG, width=7)
            lines = it.split("\n")
            rich(d, P + 82, yy, lines[0], F("Black", 50), FG)
            for j, ln in enumerate(lines[1:], 1):
                d.text((P + 82, yy + 18 + j * 46), ln, font=F("Medium", 34), fill=MU, anchor="ls")
    if c.get("note"):
        d.text((P, H - 150), c["note"], font=F("Medium", 30), fill=MU, anchor="ls")
    logo = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")
    h = 40; w = int(logo.width * h / logo.height)
    logo = logo.resize((w, h), Image.LANCZOS)
    a = logo.split()[3].point(lambda v: int(v * .75)); logo.putalpha(a)
    im.paste(logo, ((W - w) // 2, H - 62 - h), logo)
    im.save(out, quality=95)


BGIMG, DIM = None, .15
if __name__ == "__main__":
    if len(sys.argv) > 3:
        BGIMG = sys.argv[3]; DIM = float(sys.argv[4]) if len(sys.argv) > 4 else .15
    spec = json.loads(Path(sys.argv[1]).read_text())
    od = Path(sys.argv[2]); od.mkdir(parents=True, exist_ok=True)
    for c in spec:
        card(c, od / f"{c['name']}.jpg")
        print(od / f"{c['name']}.jpg")
