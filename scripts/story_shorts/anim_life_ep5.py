# 인생 댓글로 정함 5화 '삼천 원 거래' (2026.10.27) — 세 살이 아빠 게임기를 삼천 원에 팖
# 콜드 오픈(게임기 내밀고 동전 받음, '3천 원' 도장) → 설정 + 1등 댓글 "2 돈 어케벌지" → 중고거래 5분 만에 거래 완료(정가 50만)
# → 통장 14만→14만 3천, 아빠 베란다 → 갈림길(아빠 차도 판다 / 번 돈으로 주식 / 놀이터 통행료), 안 정하면 엄마 가방 올림
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep5.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d6.py(kidug_* console) + life_3d5.py(kidu_happy/blink/o, kidut_proud/blink) + life_3d3.py(dad_cry) + life_3d2.py(money)
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter
SPR = sys.argv.pop(2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import anim_life_ep1_v2 as V2
from anim_life_ep1 import W, H, YEL, WHT, ease, back, blink

S = V2.S
put, txt, label, pill, breathe = V2.put, V2.txt, V2.label, V2.pill, V2.breathe
INK = V2.INK
RED = (235, 70, 80); GREEN = (60, 175, 95); NAVY = (52, 64, 120); SKIN = (255, 214, 190)
EP = "5화"

def with_shadow(im, k=0.1):
    pad = int(im.height * k); out = Image.new("RGBA", (im.width + 40, im.height + pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    cx, cy = out.width / 2, im.height + pad * 0.25
    d.ellipse((cx - im.width * 0.38, cy - pad * 0.28, cx + im.width * 0.38, cy + pad * 0.28), fill=(60, 40, 30, 85))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(pad * 0.25)))
    out.alpha_composite(im, (20, 0)); return out

def load(key, file, width, shadow=True):
    im = Image.open(os.path.join(SPR, file)).convert("RGBA"); im = im.crop(im.getbbox())
    im = im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)
    S[key] = with_shadow(im) if shadow else im

# 원복 김댓글: 같은 캔버스 → 합친 상자로 함께 잘라 위치 맞춤
KIDS = ["kidu_happy", "kidu_blink", "kidu_o", "kidut_proud", "kidut_blink", "kidug_proud", "kidug_blink", "kidug_o"]
raw = {k: Image.open(os.path.join(SPR, f"{k}.png")).convert("RGBA") for k in KIDS}
bx = [raw[k].getbbox() for k in KIDS]
box = (min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx))
w_body = raw["kidu_happy"].getbbox(); kscale = 360 / (w_body[2] - w_body[0])
for k in KIDS:
    im = raw[k].crop(box); S[k] = with_shadow(im.resize((int(im.width * kscale), int(im.height * kscale)), Image.LANCZOS))
load("dad_cry", "dad_cry.png", 380)
load("money", "money.png", 230, False); load("console", "console.png", 300, False)

# ---------- 배경 ----------
def bg_park():  # 아파트 단지 놀이터
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((150, 205, 255), (215, 238, 255))))
    for i, (x, h) in enumerate(((-40, 820), (300, 700), (640, 860), (900, 760))):  # 아파트 동
        d.rectangle((x, 1130 - h, x + 300, 1130), fill=(236, 230, 222), outline=(170, 160, 150), width=5)
        for yy in range(1130 - h + 40, 1100, 70):
            for xx in range(x + 30, x + 280, 62): d.rectangle((xx, yy, xx + 36, yy + 40), fill=(180, 210, 235))
        d.text((x + 150, 1130 - h + 20), f"{101 + i}동", font=V1.F(34), fill=(140, 130, 120), anchor="mm")
    d.rectangle((0, 1130, W, H), fill=(235, 205, 150)); d.rectangle((0, 1130, W, 1146), fill=(205, 170, 120))
    for i in range(30):  # 모래알
        x = (i * 137) % W; y = 1170 + (i * 71) % 300; d.ellipse((x, y, x + 8, y + 8), fill=(215, 182, 128))
    return im

def bg_room():  # 거실 + 베란다 창
    im = Image.new("RGBA", (W, H), (255, 244, 228)); d = ImageDraw.Draw(im)
    for x in range(0, W, 70): d.line([(x, 0), (x, 1130)], fill=(250, 236, 216), width=3)
    d.rectangle((560, 380, 1040, 1130), fill=(200, 230, 250), outline=(150, 120, 95), width=14)  # 베란다 문
    d.line([(800, 380), (800, 1130)], fill=(150, 120, 95), width=10)
    d.rectangle((0, 1130, W, H), fill=(205, 160, 115)); d.rectangle((0, 1130, W, 1146), fill=(175, 130, 90))
    for x in range(0, W, 110): d.line([(x, 1146), (x, H)], fill=(190, 145, 102), width=3)
    return im

S["bg_park"] = bg_park().filter(ImageFilter.GaussianBlur(2))
S["bg_room"] = bg_room().filter(ImageFilter.GaussianBlur(2))
S["bg_vote"] = S["bg_vote"].filter(ImageFilter.GaussianBlur(3))

# ---------- 코드로 그린 소품 ----------
def coin(d, x, y, r=46):
    d.ellipse((x - r, y - r + 8, x + r, y + r + 8), fill=(170, 150, 120))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(225, 225, 230), outline=INK, width=5)
    d.ellipse((x - r * 0.72, y - r * 0.72, x + r * 0.72, y + r * 0.72), outline=(170, 170, 180), width=4)
    txt(d, x, y + 2, "500", int(r * 0.62), (120, 120, 130))

def hand(im, x, y, k):  # 오른쪽에서 들어오는 어른 손(동전 올려 내밈)
    d = ImageDraw.Draw(im); xx = x + (1 - k) * 600
    d.rounded_rectangle((xx + 120, y - 60, xx + 700, y + 70), radius=60, fill=(90, 110, 160), outline=INK, width=6)  # 소매
    d.ellipse((xx - 40, y - 80, xx + 180, y + 80), fill=SKIN, outline=INK, width=6)
    d.ellipse((xx - 70, y - 40, xx + 10, y + 10), fill=SKIN, outline=INK, width=5)  # 엄지
    for i in range(3): coin(d, xx + 30 + i * 46, y - 70 - i * 14, 40)
    return d

def icon_car():
    im = Image.new("RGBA", (260, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 60, 250, 130), radius=26, fill=(80, 140, 230), outline=INK, width=6)
    d.polygon([(60, 64), (95, 15), (175, 15), (210, 64)], fill=(80, 140, 230), outline=INK)
    d.polygon([(82, 60), (104, 28), (130, 28), (130, 60)], fill=(200, 235, 255)); d.polygon([(140, 60), (140, 28), (166, 28), (190, 60)], fill=(200, 235, 255))
    for x in (65, 195): d.ellipse((x - 30, 104, x + 30, 164), fill=(50, 50, 58), outline=INK, width=5); d.ellipse((x - 11, 123, x + 11, 145), fill=(200, 200, 205))
    d.ellipse((226, 76, 246, 94), fill=(255, 230, 120)); return im

def icon_chart():
    im = Image.new("RGBA", (240, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 234, 184), radius=20, fill=(30, 34, 48), outline=INK, width=6)
    for i, (h, up) in enumerate(((60, 1), (90, 0), (50, 1), (110, 0), (40, 0))):
        x = 40 + i * 40; col = (240, 80, 90) if up else (80, 140, 240)
        d.line([(x, 150 - h - 18), (x, 150 + 8)], fill=col, width=4); d.rectangle((x - 12, 150 - h, x + 12, 150), fill=col)
    d.line([(30, 50), (110, 110), (210, 160)], fill=(80, 140, 240), width=9)
    d.polygon([(210, 175), (222, 140), (190, 152)], fill=(80, 140, 240)); return im

def icon_slide():
    im = Image.new("RGBA", (250, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(40, 190), (40, 40)], fill=(240, 90, 90), width=14); d.line([(90, 190), (90, 40)], fill=(240, 90, 90), width=14)
    for y in (80, 120, 160): d.line([(40, y), (90, y)], fill=(240, 90, 90), width=8)
    d.polygon([(90, 40), (110, 40), (235, 175), (205, 190)], fill=(255, 200, 60), outline=INK)
    d.rounded_rectangle((130, 10, 240, 70), radius=12, fill=WHT, outline=INK, width=5)
    d.text((185, 40), "500원", font=V1.F(32), fill=RED, anchor="mm"); return im

S["car"] = icon_car(); S["chart"] = icon_chart(); S["slide"] = icon_slide()

def stamp(im, x, y, k, lines, rotd=-12, size=230, col=RED):
    if k <= 0: return
    st = Image.new("RGBA", (320, 320), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.ellipse((20, 20, 300, 300), outline=col, width=14)
    if len(lines) == 1: sd.text((160, 160), lines[0], font=V1.F(96 if len(lines[0]) <= 2 else 70), fill=col, anchor="mm")
    else:
        sd.text((160, 120), lines[0], font=V1.F(56), fill=col, anchor="mm"); sd.text((160, 200), lines[1], font=V1.F(56), fill=col, anchor="mm")
    st = st.rotate(rotd, resample=Image.BICUBIC).resize((max(1, int(size * min(k, 1.2))),) * 2)
    im.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))

def chrome(im):
    d = ImageDraw.Draw(im)
    s = "댓글 1등대로 사는 아기"; w = d.textlength(s, font=V1.F(36))
    d.rounded_rectangle((24, 22, 24 + w + 44, 84), radius=31, fill=(40, 32, 30, 255))
    txt(d, 24 + 22 + w / 2, 54, s, 36, YEL)
    w2 = d.textlength(EP, font=V1.F(34))
    d.rounded_rectangle((W - 24 - w2 - 36, 24, W - 24, 82), radius=29, fill=WHT, outline=INK, width=4)
    txt(d, W - 24 - 18 - w2 / 2, 54, EP, 34, INK)
    return im

def kid_key(t, expr="happy", seed=0): return "kidu_blink" if blink(t, seed) < 1 else f"kidu_{expr}"
def kid_fist(t, seed=0.3): return "kidut_blink" if blink(t, seed) < 1 else "kidut_proud"
def kid_game(t, expr="proud", seed=0.6): return "kidug_blink" if blink(t, seed) < 1 else f"kidug_{expr}"

def bubble_r(d, x, y, s, size, tip, col=(230, 70, 80)):
    w = d.textlength(s, font=V1.F(size)); pad = size * 0.5
    box = (x - w / 2 - pad, y - size * 0.8, x + w / 2 + pad, y + size * 0.8)
    bx = min(max(tip[0], box[0] + 60), box[2] - 60)
    up = tip[1] < box[1]; ey = box[1] + 6 if up else box[3] - 6
    d.polygon([(bx - 28, ey), (bx + 28, ey), tip], fill=WHT, outline=INK, width=5)
    d.rounded_rectangle(box, radius=int(size * 0.7), fill=WHT, outline=INK, width=6)
    d.line([(bx - 24, ey + 3), (bx + 24, ey + 3)], fill=WHT, width=9)
    txt(d, x, y + 3, s, size, col)

V1.SCENES = [
    dict(id="s1", say="세 살이 아빠 게임기를 삼천 원에 팔았습니다.", sub="세 살이 아빠 게임기를 3천 원에 팔았습니다.", sfx=[("shock", 1.2)]),
    dict(id="s2", say="얘는 댓글 일등대로 사는 아기, 김댓글. 일등 댓글이 이랬거든요. 돈 어케 벌지. 그러게요.",
         sub="댓글 1등대로 사는 아기, 김댓글. 1등 댓글이 이랬거든요. \"돈 어케 벌지\" 그러게요.", sfx=[("ding", 0.4)]),
    dict(id="s3", say="동네 중고거래에 올렸고요. 오 분 만에 팔렸습니다. 그 게임기, 오십만 원짜리예요.",
         sub="동네 중고거래에 올렸고요. 5분 만에 팔렸습니다. 그 게임기, 50만 원짜리예요.", sfx=[("tada", 1.6)]),
    dict(id="s4", say="통장은 십사만 삼천 원. 아빠는 지금 베란다에 있습니다.",
         sub="통장은 14만 3천 원. 아빠는 지금 베란다에 있습니다.", sfx=[("thud", 1.6)]),
    dict(id="s5", say="세 살 사업가, 다음은요? 아빠 차도 판다, 번 돈으로 주식, 아니면 놀이터 통행료. 댓글 일등대로 갑니다. 안 정하면, 엄마 가방 올립니다.",
         sub="세 살 사업가, 다음은요? 아빠 차도 판다, 번 돈으로 주식, 아니면 놀이터 통행료. 댓글 1등대로 갑니다. 안 정하면, 엄마 가방 올립니다.", sfx=[("question", 0.6)]),
]
V1.HOOK = ["세 살이 아빠 게임기를", "'삼천 원'에 팖"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

def s1(t, dur):  # 콜드 오픈: 게임기 내밀고 동전 3천 원 → 도장
    im = S["bg_park"].copy()
    put(im, kid_game(t, "proud" if t < 1.2 else "o"), 380, 760, 1.3 * breathe(t))
    k = ease((t - 0.25) / 0.5)
    if k > 0: hand(im, 760, 640, k)
    d = ImageDraw.Draw(im)
    if t > 0.5:
        b = back((t - 0.5) / 0.3)
        if b > 0: bubble_r(d, 760, 300, "3천 원에 사요", int(70 * min(b, 1.1)) or 1, (840, 520), INK)
    stamp(im, 540, 1250, back((t - 1.1) / 0.3), ["3천 원"], size=300)
    return chrome(im)

def s2(t, dur):  # 설정 + 1등 댓글
    im = S["bg_park"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    put(im, kid_key(t, "o" if t > sp * 0.6 else "happy"), 540, 610, 1.1 * breathe(t)); d = ImageDraw.Draw(im)
    k = back((t - 0.15) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1)); w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.4) / 0.4)
    if kc > 0:
        x0 = 70 + (1 - kc) * 900
        d.rounded_rectangle((x0 + 8, 1208, x0 + 948, 1408), radius=34, fill=(40, 30, 60))
        d.rounded_rectangle((x0, 1198, x0 + 940, 1398), radius=34, fill=WHT, outline=INK, width=6)
        txt(d, x0 + 40, 1248, "@은정-e3r8g", 40, (140, 130, 125), anchor="lm")
        txt(d, x0 + 40, 1330, "2 돈 어케벌지", 58, INK, anchor="lm")
        d.rounded_rectangle((x0 + 760, 1176, x0 + 930, 1232), radius=26, fill=YEL, outline=INK, width=5)
        txt(d, x0 + 845, 1205, "1등 댓글", 34, INK)
    if t > sp * 0.62:
        for i, (x, y) in enumerate(((330, 260), (760, 230), (820, 400))):
            b = back((t - sp * 0.62 - i * 0.1) / 0.3)
            if b > 0: txt(d, x, y, "?", int(110 * min(b, 1.1)) or 1, YEL, stroke=8)
    return chrome(im)

def phone_ui(im, t, sp, cx=540, cy=560):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - 300, cy - 470, cx + 300, cy + 470), radius=60, fill=(40, 40, 48), outline=INK, width=8)
    d.rounded_rectangle((cx - 270, cy - 420, cx + 270, cy + 430), radius=30, fill=(252, 250, 246))
    d.rectangle((cx - 270, cy - 420, cx + 270, cy - 330), fill=(255, 140, 60)); txt(d, cx, cy - 375, "동네 중고거래", 46, WHT)
    d.rounded_rectangle((cx - 230, cy - 300, cx + 230, cy - 20), radius=24, fill=(225, 236, 245))
    put(im, "console", cx, cy - 160, 1.1); d = ImageDraw.Draw(im)
    txt(d, cx - 230, cy + 40, "게임기 팝니다", 52, INK, anchor="lm")
    txt(d, cx - 230, cy + 120, "3,000원", 72, (255, 110, 40), anchor="lm")
    txt(d, cx - 230, cy + 190, "놀이터 앞 직거래", 36, (150, 140, 135), anchor="lm")
    t5 = sp * 0.3
    if t > t5:
        k = back((t - t5) / 0.3)
        if k > 0: pill(d, cx, cy + 300, "5분 뒤", int(52 * min(k, 1.1)) or 1, YEL)
    return d

def s3(t, dur):  # 중고거래 앱 → 5분 만에 거래 완료 → 정가 50만
    im = S["bg_room"].copy(); sp = SPEAK["s3"]
    phone_ui(im, t, sp)
    stamp(im, 700, 520, back((t - sp * 0.4) / 0.3), ["거래", "완료"], rotd=10, size=300)
    put(im, kid_fist(t), 190, 1200, 0.75 * breathe(t)); d = ImageDraw.Draw(im)
    if t > sp * 0.7:
        k = back((t - sp * 0.7) / 0.35)
        if k > 0: pill(d, 640, 1250, "원래 50만 원", int(70 * min(k, 1.1)) or 1, (255, 120, 120))
    return chrome(im)

def s4(t, dur):  # 통장 14만 → 14만 3천, 아빠 베란다
    im = S["bg_room"].copy(); sp = SPEAK["s4"]
    # 아빠: 베란다 문 안쪽에서 쪼그려 울기(작게, 흔들림)
    sh = 6 * math.sin(t * 18)
    put(im, "dad_cry", 820 + sh, 940, 0.82)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle((560, 380, 1040, 1130), fill=(210, 235, 255, 70)); im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    a = back((t - 0.15) / 0.4)
    if a > 0:
        b = S["card_bank"] if a >= 0.999 else S["card_bank"].resize((max(1, int(760 * a)), max(1, int(330 * a))))
        im.alpha_composite(b, (int(540 - b.width / 2), int(300 - b.height / 2))); d = ImageDraw.Draw(im)
        if a > 0.9:
            p = ease((t - 0.6) / 0.5); won = 140000 + int(3000 * p / 1000) * 1000
            txt(d, 540, 205, "통장 잔고", 54, WHT, stroke=5)
            txt(d, 540, 340, f"{won:,}원", 118, YEL if p < 1 else (140, 240, 150), stroke=8)
            if t > 0.9:
                k = back((t - 0.9) / 0.3); txt(d, 880, 130, "+3천", int(80 * min(k, 1.15)) or 1, GREEN, stroke=7, sfill=WHT)
    put(im, kid_key(t, "happy"), 230, 1050, 0.8 * breathe(t)); d = ImageDraw.Draw(im)
    if t > sp * 0.45:
        k = back((t - sp * 0.45) / 0.35)
        if k > 0: label(d, 1360, "아빠 베란다행", int(100 * min(k, 1.1)) or 1, (150, 210, 255))
    return chrome(im)

OPTS = (("car", "아빠 차도 판다", (80, 140, 230)), ("chart", "번 돈으로 주식", (235, 70, 80)), ("slide", "놀이터 통행료", (90, 170, 100)))
OX = (190, 540, 890)
def vote_cards(im, t, cy=1250):
    d = ImageDraw.Draw(im)
    for i, (key, name, col) in enumerate(OPTS):
        x = OX[i]; k = back((t - 0.4 - i * 0.18) / 0.4)
        if k <= 0: continue
        pul = 1 + 0.035 * math.sin(t * 5 + i * 1.4); w2, h2 = 165 * k * pul, 185 * k * pul
        d.rounded_rectangle((x - w2 + 6, cy - h2 + 10, x + w2 + 6, cy + h2 + 10), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy + h2), radius=34, fill=WHT, outline=INK, width=6)
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy - h2 + 70 * k), radius=34, fill=col, outline=INK, width=6)
        if k > 0.9:
            txt(d, x, cy - h2 + 38, f"{i + 1}번", 48, WHT, stroke=4)
            put(im, key, x, cy + 10, 0.95); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 50, name, 40, INK)
    return d

def s5(t, dur):  # 갈림길 → 안 정하면 엄마 가방 올림
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s5"]
    sw = sp * 0.55; last = sp * 0.78
    if t < sw:
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "세 살 사업가, 다음은?", 96)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
    lift = 0 if t < last else 30 * abs(math.sin((t - last) * 6))
    put(im, kid_fist(t, 0.2), 540, 600 - lift, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
    if t > last:
        k = back((t - last) / 0.35)
        if k > 0: pill(d, 540, 340, "엄마 가방 올림?", int(58 * min(k, 1.1)) or 1, (255, 120, 120))
    vote_cards(im, t)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5)
if __name__ == "__main__":
    V1.main()
