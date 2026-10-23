# 댓글로 키우는 아이 1화 v2 — SVG 캐릭터(life_sprites.py)로 다시 그림 (2026.10.23 '투박하다' 피드백)
# 사용: python3 scripts/story_shorts/anim_life_ep1_v2.py <출력폴더>
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import life_sprites as L
from anim_life_ep1 import W, H, F, YEL, WHT, ease, back, blink

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
V1.OUT = OUT; os.makedirs(OUT, exist_ok=True)
S = L.render_all(os.path.join(OUT, "_sprites"))
INK = (91, 58, 41)

def put(im, key, cx, cy, sc=1.0, rot=0.0):
    sp = S[key]
    if abs(sc - 1) > 1e-3:
        sp = sp.resize((max(1, int(sp.width * sc)), max(1, int(sp.height * sc))), Image.LANCZOS)
    if rot: sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))

def breathe(t, k=0): return 1 + 0.012 * math.sin(t * 3 + k)

def txt(d, x, y, s, size, fill=INK, stroke=0, sfill=INK, anchor="mm"):
    d.text((x, y), s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

def label(d, y, s, size=96, fill=YEL):
    txt(d, W / 2, y, s, size, fill, stroke=9, sfill=INK)

def pill(d, x, y, s, size=50, bg=(255, 255, 255)):
    w = d.textlength(s, font=F(size))
    d.rounded_rectangle((x - w / 2 - 28, y - size * 0.75, x + w / 2 + 28, y + size * 0.75), radius=40, fill=bg, outline=INK, width=5)
    txt(d, x, y + 2, s, size)

def bubble(d, x, y, s, size):
    w = d.textlength(s, font=F(size)); pad = size * 0.5
    box = (x - w / 2 - pad, y - size * 0.8, x + w / 2 + pad, y + size * 0.8)
    d.polygon([(box[0] + 40, box[3] - 6), (box[0] + 90, box[3] - 6), (box[0] + 10, box[3] + 50)], fill=WHT, outline=INK, width=5)
    d.rounded_rectangle(box, radius=int(size * 0.7), fill=WHT, outline=INK, width=6)
    d.line([(box[0] + 44, box[3] - 3), (box[0] + 86, box[3] - 3)], fill=WHT, width=9)
    txt(d, x, y + 3, s, size, (230, 70, 80))

def baby_key(t, expr="happy", seed=0):
    return "baby_blink" if expr != "cry" and blink(t, seed) < 1 else f"baby_{expr}"

def base(key):
    return S[key].copy()

# ---------- 장면 ----------
def s1(t, dur):
    im = base("bg_nursery"); d = ImageDraw.Draw(im)
    for i in range(12):  # 반짝이
        a = (t * 0.7 + i * 0.29) % 1; x = 540 + 420 * math.cos(i * 0.52 + t * 0.3); y = 420 + 300 * math.sin(i * 1.3 + t * 0.25)
        r = 13 * math.sin(a * math.pi); d.polygon([(x, y - r * 2), (x + r, y), (x, y + r * 2), (x - r, y)], fill=(255, 205, 80))
    cry = 0.5 < t < 2.4; k = back(t / 0.5)
    shake = 5 * math.sin(t * 38) if cry else 0
    put(im, baby_key(t, "cry" if cry else "happy"), 540 + shake, 450, 1.12 * k * breathe(t))
    d = ImageDraw.Draw(im)
    if cry: bubble(d, 830, 150, "응애!!", 84)
    a = ease((t - 2.6) / 0.4)
    if a > 0:
        label(d, 1215 + (1 - a) * 80, "D+0 탄생", 120)
        pill(d, W / 2, 1360, "인생 결정권: 여러분", 54)
    return im

def s2(t, dur):
    im = base("bg_nursery"); d = ImageDraw.Draw(im)
    put(im, baby_key(t), 250, 450, 0.78 * breathe(t))
    x0 = 1080 - ease(t / 0.5) * 680
    im.alpha_composite(S["card_birth"], (int(x0 - 20), 150)); d = ImageDraw.Draw(im)
    txt(d, x0 + 290, 218, "출생 카드", 58, WHT, stroke=5)
    for i, (k, v, at) in enumerate((("이름", "김댓글", 0.6), ("키", "50cm", 1.7), ("몸무게", "3.2kg", 2.6))):
        a = back((t - at) / 0.35)
        if a <= 0: continue
        y = 345 + i * 120
        txt(d, x0 + 50, y, k, 52, (150, 125, 110), anchor="lm")
        txt(d, x0 + 530, y, v, int(74 * min(a, 1.15)), INK, anchor="rm")
        d.line([(x0 + 40, y + 52), (x0 + 540, y + 52)], fill=(240, 225, 212), width=4)
    a = ease((t - 0.8) / 0.4)
    if a > 0: label(d, 1240 + (1 - a) * 60, "주인공: 김댓글", 104)
    return im

def s3(t, dur):
    im = base("bg_living"); d = ImageDraw.Draw(im)
    for who, x, at, lab in (("dad", 235, 0.0, "아빠: 회사원"), ("mom", 845, 1.3, "엄마: 분식집 사장")):
        k = back((t - at) / 0.45)
        if k > 0:
            key = f"{who}_blink" if blink(t, 1.1 if who == "dad" else 2.0) < 1 else who
            put(im, key, x, 400, 0.78 * k * breathe(t, x))
            d = ImageDraw.Draw(im)
            if k > 0.9: pill(d, x, 700, lab, 46)
    put(im, baby_key(t, seed=0.6), 540, 560, 0.5 * breathe(t, 2))
    d = ImageDraw.Draw(im)
    if t > 2.6:
        a = back((t - 2.6) / 0.4); bx, by = 160, 1090
        bank = S["card_bank"] if a >= 0.999 else S["card_bank"].resize((int(760 * a) or 1, int(330 * a) or 1))
        im.alpha_composite(bank, (int(540 - bank.width / 2), int(by + 165 - bank.height / 2))); d = ImageDraw.Draw(im)
        if a > 0.9:
            p = ease((t - 2.8) / 2.2); won = int(870000 * p / 1000) * 1000
            txt(d, 540, by + 70, "통장 잔고", 54, WHT, stroke=5)
            txt(d, 540, by + 205, f"{won:,}원", 118, YEL, stroke=8)
    return im

ITEM_X = (210, 540, 870)
ITEMS = (("pencil", "연필", (90, 170, 240)), ("money", "돈", (80, 180, 110)), ("mic", "마이크", (235, 100, 140)))

def s4(t, dur):
    im = base("bg_dol"); d = ImageDraw.Draw(im)
    tk = "tod_blink" if blink(t, 0.4) < 1 else "tod_o"
    put(im, tk, 540, 330, 0.92 * breathe(t))
    # 팔: 아이템 사이를 오가며 고민
    tgt = 1 + math.sin(max(0, t - 0.9) * 2.0) if t < dur - 0.5 else 1
    tx = ITEM_X[0] + (ITEM_X[2] - ITEM_X[0]) * tgt / 2
    sx, sy = 630, 425; ang = math.degrees(math.atan2(-(560 - sy), tx - sx))
    im.alpha_composite(S["table"], (20, 500))
    put(im, "arm", sx + 95 * math.cos(math.radians(-ang)), sy + 95 * math.sin(math.radians(-ang)), 0.8, ang)
    d = ImageDraw.Draw(im)
    for i, (key, name, col) in enumerate(ITEMS):
        k = back((t - 0.4 - i * 0.3) / 0.35)
        if k <= 0: continue
        bob = 6 * math.sin(t * 4 + i)
        put(im, key, ITEM_X[i], 560 + bob, 0.72 * k); d = ImageDraw.Draw(im)
        d.ellipse((ITEM_X[i] + 70, 470, ITEM_X[i] + 130, 530), fill=col, outline=INK, width=5)
        txt(d, ITEM_X[i] + 100, 502, str(i + 1), 44, WHT, stroke=3)
    if t > 3.2:
        b = 16 * abs(math.sin((t - 3.2) * 6))
        txt(d, 790, 150 - b, "?", 150, (255, 95, 110), stroke=9)
    a = ease((t - 0.2) / 0.4)
    label(d, 1230 + (1 - a) * 60, "첫 번째 갈림길", 104)
    if a > 0: pill(d, W / 2, 1370, "돌잡이로 미래가 정해진다", 52)
    return im

def s5(t, dur):
    im = base("bg_vote"); d = ImageDraw.Draw(im)
    put(im, baby_key(t, "o", 1.4), 540, 360, 0.82 * breathe(t))
    d = ImageDraw.Draw(im)
    label(d, 700, "댓글로 골라주세요!", 100)
    for i, (key, name, col) in enumerate(ITEMS):
        x = ITEM_X[i]; k = back((t - 0.2 - i * 0.18) / 0.4)
        if k <= 0: continue
        pul = 1 + 0.04 * math.sin(t * 5 + i * 1.4); w2, h2 = 145 * k * pul, 175 * k * pul; cy = 1240
        d.rounded_rectangle((x - w2 + 6, cy - h2 + 10, x + w2 + 6, cy + h2 + 10), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy + h2), radius=34, fill=WHT, outline=INK, width=6)
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy - h2 + 70 * k), radius=34, fill=col, outline=INK, width=6)
        if k > 0.9:
            txt(d, x, cy - h2 + 38, f"{i + 1}번", 48, WHT, stroke=4)
            put(im, key, x, cy + 10, 0.55); d = ImageDraw.Draw(im)
            txt(d, x, cy + 125, name, 58, INK)
    return im

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5)
if __name__ == "__main__":
    V1.main()
