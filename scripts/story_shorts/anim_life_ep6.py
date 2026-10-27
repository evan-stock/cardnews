# 인생 댓글로 정함 6화 '놀이터 통행료' (2026.10.28) — 세 살인데 놀이터에서 통행료 받음
# 콜드 오픈(매표소 + 1회 500원, '통행료 징수 중' 도장) → 설정 + 1등 댓글 "놀이터 통행료"(@대충드가자) → 3만 벌고 관리사무소 벌금 5만(통장 14만3천→12만3천)
# → 선택지에 없던 4번 댓글대로 집 4천 원에 올림, '전셋집' 도장, 집주인도 봄 → 갈림길(반장 선거 / 집주인 찾아간다 / 짐 싸서 가출)
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep6.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d5.py(kidu_happy/blink/o, kidut_proud/blink, kidup_happy/blink) + life_3d4.py(mom_sad)
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
RED = (235, 70, 80); GREEN = (60, 175, 95); SKIN = (255, 214, 190); GRAY = (150, 140, 135)
EP = "6화"

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
KIDS = ["kidu_happy", "kidu_blink", "kidu_o", "kidut_proud", "kidut_blink", "kidup_happy", "kidup_blink"]
raw = {k: Image.open(os.path.join(SPR, f"{k}.png")).convert("RGBA") for k in KIDS}
bx = [raw[k].getbbox() for k in KIDS]
box = (min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx))
w_body = raw["kidu_happy"].getbbox(); kscale = 360 / (w_body[2] - w_body[0])
for k in KIDS:
    im = raw[k].crop(box); S[k] = with_shadow(im.resize((int(im.width * kscale), int(im.height * kscale)), Image.LANCZOS))
load("mom_sad", "mom_sad.png", 360)

# ---------- 배경 ----------
def bg_park():  # 아파트 단지 놀이터(5화와 같은 동네) + 미끄럼틀
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((150, 205, 255), (215, 238, 255))))
    for i, (x, h) in enumerate(((-40, 820), (300, 700), (640, 860), (900, 760))):
        d.rectangle((x, 1130 - h, x + 300, 1130), fill=(236, 230, 222), outline=(170, 160, 150), width=5)
        for yy in range(1130 - h + 40, 1100, 70):
            for xx in range(x + 30, x + 280, 62): d.rectangle((xx, yy, xx + 36, yy + 40), fill=(180, 210, 235))
        d.text((x + 150, 1130 - h + 20), f"{101 + i}동", font=V1.F(34), fill=(140, 130, 120), anchor="mm")
    d.rectangle((0, 1130, W, H), fill=(235, 205, 150)); d.rectangle((0, 1130, W, 1146), fill=(205, 170, 120))
    for i in range(30):
        x = (i * 137) % W; y = 1170 + (i * 71) % 300; d.ellipse((x, y, x + 8, y + 8), fill=(215, 182, 128))
    # 미끄럼틀(오른쪽)
    d.line([(880, 1150), (880, 600)], fill=(240, 90, 90), width=22); d.line([(990, 1150), (990, 600)], fill=(240, 90, 90), width=22)
    for y in range(680, 1150, 90): d.line([(880, y), (990, y)], fill=(240, 90, 90), width=12)
    d.rectangle((860, 580, 1010, 620), fill=(240, 90, 90), outline=INK, width=5)
    d.polygon([(860, 600), (900, 600), (700, 1150), (640, 1150)], fill=(255, 200, 60), outline=INK)
    return im

def bg_elev():  # 엘리베이터 안
    im = Image.new("RGBA", (W, H), (196, 200, 206)); d = ImageDraw.Draw(im)
    for x in range(0, W, 120): d.line([(x, 0), (x, 1150)], fill=(182, 186, 193), width=4)
    d.rectangle((0, 0, W, 40), fill=(150, 154, 160))
    d.rectangle((1000, 360, 1080, 760), fill=(170, 174, 180), outline=(120, 124, 130), width=5)  # 버튼 패널
    for i in range(6): d.ellipse((1022, 390 + i * 60, 1058, 426 + i * 60), fill=(235, 235, 238), outline=(110, 110, 118), width=3)
    d.rectangle((0, 1150, W, H), fill=(120, 116, 112)); d.rectangle((0, 1150, W, 1166), fill=(95, 92, 88))
    for x in range(0, W, 90): d.line([(x, 1166), (x, H)], fill=(110, 106, 102), width=3)
    return im

def bg_room():  # 거실 + 베란다 창(5화와 같은 집)
    im = Image.new("RGBA", (W, H), (255, 244, 228)); d = ImageDraw.Draw(im)
    for x in range(0, W, 70): d.line([(x, 0), (x, 1130)], fill=(250, 236, 216), width=3)
    d.rectangle((560, 380, 1040, 1130), fill=(200, 230, 250), outline=(150, 120, 95), width=14)
    d.line([(800, 380), (800, 1130)], fill=(150, 120, 95), width=10)
    d.rectangle((0, 1130, W, H), fill=(205, 160, 115)); d.rectangle((0, 1130, W, 1146), fill=(175, 130, 90))
    for x in range(0, W, 110): d.line([(x, 1146), (x, H)], fill=(190, 145, 102), width=3)
    return im

S["bg_park"] = bg_park().filter(ImageFilter.GaussianBlur(2))
_z = S["bg_park"].crop((40, 60, W - 40, H - 60)).resize((W, H), Image.LANCZOS); S["bg_park_z"] = _z
S["bg_elev"] = bg_elev().filter(ImageFilter.GaussianBlur(1.5))
S["bg_room"] = bg_room().filter(ImageFilter.GaussianBlur(2))
S["bg_vote"] = S["bg_vote"].filter(ImageFilter.GaussianBlur(3))

# ---------- 코드로 그린 소품 ----------
def coin(d, x, y, r=46):
    d.ellipse((x - r, y - r + 8, x + r, y + r + 8), fill=(170, 150, 120))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(225, 225, 230), outline=INK, width=5)
    d.ellipse((x - r * 0.72, y - r * 0.72, x + r * 0.72, y + r * 0.72), outline=(170, 170, 180), width=4)
    txt(d, x, y + 2, "500", int(r * 0.62), (120, 120, 130))

def booth(im):  # 박스 매표소 + 팻말
    d = ImageDraw.Draw(im)
    d.rectangle((300, 860, 780, 1150), fill=(205, 160, 105), outline=INK, width=7)
    d.line([(300, 900), (780, 900)], fill=(170, 125, 80), width=6)
    d.line([(540, 900), (540, 1150)], fill=(185, 140, 92), width=4)
    d.rounded_rectangle((380, 960, 700, 1060), radius=18, fill=(255, 248, 230), outline=INK, width=5)
    txt(d, 540, 1012, "매표소", 64, (120, 70, 40))
    # 팻말(왼쪽)
    d.line([(150, 900), (150, 1180)], fill=(150, 105, 70), width=16)
    d.rounded_rectangle((40, 760, 260, 920), radius=20, fill=WHT, outline=INK, width=6)
    txt(d, 150, 808, "1회", 46, INK); txt(d, 150, 870, "500원", 58, RED)
    return d

def hand_left(im, x, y, k):  # 왼쪽에서 들어오는 동네 애 손(동전 1개)
    d = ImageDraw.Draw(im); xx = x - (1 - k) * 600
    d.rounded_rectangle((xx - 520, y - 46, xx - 40, y + 50), radius=46, fill=(120, 190, 120), outline=INK, width=6)
    d.ellipse((xx - 90, y - 62, xx + 70, y + 62), fill=SKIN, outline=INK, width=6)
    coin(d, xx + 10, y - 66, 40)
    return d

def bubble_r(d, x, y, s, size, tip, col=(230, 70, 80)):
    w = d.textlength(s, font=V1.F(size)); pad = size * 0.5
    box_ = (x - w / 2 - pad, y - size * 0.8, x + w / 2 + pad, y + size * 0.8)
    bx_ = min(max(tip[0], box_[0] + 60), box_[2] - 60)
    up = tip[1] < box_[1]; ey = box_[1] + 6 if up else box_[3] - 6
    d.polygon([(bx_ - 28, ey), (bx_ + 28, ey), tip], fill=WHT, outline=INK, width=5)
    d.rounded_rectangle(box_, radius=int(size * 0.7), fill=WHT, outline=INK, width=6)
    d.line([(bx_ - 24, ey + 3), (bx_ + 24, ey + 3)], fill=WHT, width=9)
    txt(d, x, y + 3, s, size, col)

def stamp(im, x, y, k, lines, rotd=-12, size=230, col=RED):
    if k <= 0: return
    st = Image.new("RGBA", (320, 320), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.ellipse((20, 20, 300, 300), outline=col, width=14)
    if len(lines) == 1: sd.text((160, 160), lines[0], font=V1.F(96 if len(lines[0]) <= 2 else 74), fill=col, anchor="mm")
    else:
        sd.text((160, 118), lines[0], font=V1.F(60), fill=col, anchor="mm"); sd.text((160, 202), lines[1], font=V1.F(56), fill=col, anchor="mm")
    st = st.rotate(rotd, resample=Image.BICUBIC).resize((max(1, int(size * min(k, 1.2))),) * 2)
    im.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))

def comment_card(d, x0, y0, nick, body, tag=None, tagcol=YEL, wid=940):
    d.rounded_rectangle((x0 + 8, y0 + 10, x0 + wid + 8, y0 + 210), radius=34, fill=(40, 30, 60))
    d.rounded_rectangle((x0, y0, x0 + wid, y0 + 200), radius=34, fill=WHT, outline=INK, width=6)
    if nick: txt(d, x0 + 40, y0 + 50, nick, 40, GRAY, anchor="lm"); tx = x0 + 40
    else:
        d.ellipse((x0 + 30, y0 + 26, x0 + 90, y0 + 86), fill=(200, 196, 192)); tx = x0 + 40
    size = 58 if len(body) <= 10 else 50
    txt(d, tx, y0 + 132, body, size, INK, anchor="lm")
    if tag:
        tw = d.textlength(tag, font=V1.F(34))
        d.rounded_rectangle((x0 + wid - tw - 70, y0 - 22, x0 + wid - 10, y0 + 34), radius=26, fill=tagcol, outline=INK, width=5)
        txt(d, x0 + wid - 40 - tw / 2, y0 + 7, tag, 34, INK)

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
def kid_point(t, seed=0.5): return "kidup_blink" if blink(t, seed) < 1 else "kidup_happy"

def icon_sash():
    im = Image.new("RGBA", (250, 200), (0, 0, 0, 0))
    band = Image.new("RGBA", (330, 74), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.rounded_rectangle((0, 0, 329, 73), radius=14, fill=(230, 60, 70), outline=INK, width=5)
    bd.text((165, 38), "기호 1번", font=V1.F(42), fill=WHT, anchor="mm")
    band = band.rotate(-32, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(band, ((250 - band.width) // 2, (200 - band.height) // 2)); return im

def icon_door():
    im = Image.new("RGBA", (240, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((40, 6, 170, 196), fill=(150, 100, 65), outline=INK, width=6)
    d.rectangle((62, 30, 148, 100), outline=(120, 78, 50), width=5); d.rectangle((62, 116, 148, 176), outline=(120, 78, 50), width=5)
    d.ellipse((140, 100, 160, 120), fill=(250, 210, 90), outline=INK, width=3)
    d.rounded_rectangle((188, 60, 232, 120), radius=10, fill=(235, 235, 238), outline=INK, width=4)
    d.ellipse((199, 74, 221, 96), fill=(240, 90, 90), outline=INK, width=3)
    return im

def icon_bag():
    im = Image.new("RGBA", (220, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in (70, 150): d.ellipse((x - 26, 0, x + 26, 46), fill=(190, 140, 90), outline=INK, width=4)  # 곰 귀
    d.ellipse((60, 6, 160, 96), fill=(205, 155, 100), outline=INK, width=5)  # 곰 머리
    d.ellipse((90, 40, 100, 52), fill=INK); d.ellipse((120, 40, 130, 52), fill=INK); d.ellipse((102, 56, 118, 68), fill=(90, 60, 40))
    d.arc((40, 40, 180, 140), 200, 340, fill=INK, width=8)
    d.rounded_rectangle((26, 66, 194, 206), radius=36, fill=(255, 200, 60), outline=INK, width=6)
    d.rounded_rectangle((56, 130, 164, 196), radius=18, fill=(250, 170, 40), outline=INK, width=5)
    return im

S["sash"] = icon_sash(); S["door"] = icon_door(); S["bag"] = icon_bag()

V1.SCENES = [
    dict(id="s1", say="세 살인데, 놀이터에서 통행료 받습니다.", sub="세 살인데, 놀이터에서 통행료 받습니다.", sfx=[("shock", 1.8)]),
    dict(id="s2", say="얘는 댓글 일등대로 사는 아기, 김댓글. 일등 댓글이 놀이터 통행료래서, 받았습니다.",
         sub="댓글 1등대로 사는 아기, 김댓글. 1등 댓글이 \"놀이터 통행료\"래서, 받았습니다.", sfx=[("ding", 2.2)]),
    dict(id="s3", say="삼만 원 벌었고요. 관리사무소 벌금 오만 원. 통장 십이만 삼천 원.",
         sub="3만 원 벌었고요. 관리사무소 벌금 5만 원. 통장 12만 3천 원.", sfx=[("thud", 1.6)]),
    dict(id="s4", say="선택지에도 없던 사번 댓글이, 집을 사천 원에 팔래서, 올렸습니다. 근데 그 집, 전셋집이에요. 집주인도 봤고요.",
         sub="선택지에도 없던 4번 댓글이 집을 4천 원에 팔래서, 올렸습니다. 근데 그 집, 전셋집이에요. 집주인도 봤고요.", sfx=[("boing", 4.6)]),
    dict(id="s5", say="다음은요? 반장 선거, 집주인 찾아간다, 아니면 가출. 댓글 일등대로 갑니다. 안 정하면, 사천 원에 진짜 팔립니다.",
         sub="다음은요? 1 아파트 반장 선거 2 집주인 찾아간다 3 짐 싸서 가출. 댓글 1등대로 갑니다. 안 정하면, 4천 원에 진짜 팔립니다.", sfx=[("question", 0.3)]),
]
V1.HOOK = ["세 살이 놀이터에서", "'통행료' 받음"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

def s1(t, dur):  # 콜드 오픈: 매표소에서 500원 받기 → 도장
    im = S["bg_park"].copy()
    lean = 18 * math.sin(math.pi * min(max((t - 1.2) / 0.4, 0), 1))
    pop = back(t / 0.35) if t < 0.35 else 1
    put(im, kid_fist(t), 540, 690 + lean, 1.05 * max(pop, 0.01) * breathe(t))
    booth(im)
    k = ease((t - 0.6) / 0.4)
    if k > 0 and t < 1.5: hand_left(im, 330, 880, k)
    d = ImageDraw.Draw(im)
    if 1.5 <= t < 1.9:  # 동전이 상자 안으로 쏙
        p = ease((t - 1.5) / 0.4); coin(d, 340 + 200 * p, 814 + 80 * p, 40 * (1 - p) + 6)
    if t > 0.3:
        b = back((t - 0.3) / 0.3)
        if b > 0: bubble_r(d, 560, 250, "오백 원.", int(76 * min(b, 1.1)) or 1, (560, 420), INK)
    stamp(im, 540, 1320, back((t - 1.8) / 0.3), ["통행료", "징수 중"], size=300)
    return chrome(im)

def s2(t, dur):  # 설정 + 1등 댓글 + 동전 더미
    im = S["bg_park_z"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    lv = min(3, int(max(0, t - sp * 0.65) / 0.35) + (1 if t > sp * 0.65 else 0))
    for side in (-1, 1):
        for j in range(lv * 3):
            coin(d, 540 + side * (260 + (j % 3) * 30), 900 - j * 34, 44)
    put(im, kid_key(t, "happy"), 540, 610, 1.1 * breathe(t)); d = ImageDraw.Draw(im)
    k = back((t - 0.15) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1)) or 1; w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.42) / 0.4)
    if kc > 0: comment_card(d, 70 + (1 - kc) * 900, 1210, "@대충드가자", "놀이터 통행료", "1등 댓글")
    return chrome(im)

def s3(t, dur):  # 3만 벌고 → 관리사무소 벌금 5만 → 12만 3천
    im = S["bg_elev"].copy(); sp = SPEAK["s3"]
    t_n = 1.4; t_m = 2.3
    shake = 10 * math.sin(t * 60) * max(0, 1 - (t - t_n - 0.25) / 0.3) if t > t_n + 0.25 else 0
    # 공지문: 위에서 떨어져 붙음
    if t > t_n:
        p = min(1, (t - t_n) / 0.25); y = -400 + (620 + 400) * (p * p)
        nt = Image.new("RGBA", (560, 440), (0, 0, 0, 0)); nd = ImageDraw.Draw(nt)
        nd.rectangle((6, 8, 554, 436), fill=(90, 90, 96)); nd.rectangle((0, 0, 548, 428), fill=WHT, outline=INK, width=6)
        nd.rectangle((0, 0, 548, 70), fill=RED, outline=INK, width=6); nd.text((274, 36), "안내", font=V1.F(48), fill=WHT, anchor="mm")
        nd.text((274, 130), "놀이터 무단 영업 금지", font=V1.F(46), fill=INK, anchor="mm")
        nd.text((274, 200), "미끄럼틀 통행료 적발", font=V1.F(40), fill=GRAY, anchor="mm")
        nd.text((274, 290), "벌금 50,000원", font=V1.F(66), fill=RED, anchor="mm")
        nd.text((274, 380), "관리사무소", font=V1.F(40), fill=INK, anchor="mm")
        im.alpha_composite(nt, (int(260 + shake), int(y - 220)))
    sad = min(1, max(0, (t - 3.0) / 0.4))
    put(im, "mom_sad", 830, 1180 + 20 * sad, 0.92)
    put(im, kid_key(t, "o" if t > t_n else "happy"), 230, 1230, 0.8 * breathe(t))
    d = ImageDraw.Draw(im)
    a = back((t - 0.05) / 0.35)
    if a > 0:
        cw, ch = 640, 280
        b = S["card_bank"].resize((max(1, int(cw * min(a, 1))), max(1, int(ch * min(a, 1)))))
        im.alpha_composite(b, (int(540 - b.width / 2 + shake), int(190 - b.height / 2))); d = ImageDraw.Draw(im)
        if a > 0.9:
            p1 = ease((t - 0.4) / 0.5); p2 = ease((t - t_m) / 0.6)
            won = 143000 + int(30 * p1) * 1000 - int(50 * p2) * 1000
            col = YEL if t < 0.4 else ((140, 240, 150) if t < t_m else (255, 130, 130))
            txt(d, 540, 112, "통장 잔고", 46, WHT, stroke=5)
            txt(d, 540, 222, f"{won:,}원", 100, col, stroke=8)
            if 0.4 < t < t_m + 0.4:
                k = back((t - 0.4) / 0.3); txt(d, 960, 330, "+3만", int(76 * min(k, 1.15)) or 1, GREEN, stroke=7, sfill=WHT)
            if t > t_m:
                k = back((t - t_m) / 0.3); txt(d, 960, 330, "-5만", int(80 * min(k, 1.15)) or 1, RED, stroke=7, sfill=WHT)
    return chrome(im)

def apt_pic(d, x0, y0, x1, y1):
    d.rounded_rectangle((x0, y0, x1, y1), radius=22, fill=(205, 228, 245))
    bx0 = x0 + (x1 - x0) * 0.22; bx1 = x1 - (x1 - x0) * 0.22
    d.rectangle((bx0, y0 + 30, bx1, y1 - 10), fill=(240, 234, 226), outline=(150, 140, 130), width=4)
    for yy in range(int(y0) + 50, int(y1) - 30, 44):
        for xx in range(int(bx0) + 18, int(bx1) - 30, 50): d.rectangle((xx, yy, xx + 28, yy + 26), fill=(170, 205, 235))

def s4(t, dur):  # 4번 댓글 → 집 팝니다 4,000원 → 알림 → 전셋집 → 집주인도 봄
    im = S["bg_room"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    t_post = sp * 0.36; t_stamp = sp * 0.62; t_owner = sp * 0.84
    cx, cy = 600, 760
    d.rounded_rectangle((cx - 280, cy - 420, cx + 280, cy + 420), radius=56, fill=(40, 40, 48), outline=INK, width=8)
    d.rounded_rectangle((cx - 252, cy - 375, cx + 252, cy + 385), radius=28, fill=(252, 250, 246))
    d.rectangle((cx - 252, cy - 375, cx + 252, cy - 295), fill=(255, 140, 60)); txt(d, cx, cy - 335, "동네 중고거래", 44, WHT)
    kp = ease((t - t_post) / 0.4)
    if kp > 0:
        off = (1 - kp) * 120
        apt_pic(d, cx - 220, cy - 270 + off, cx + 220, cy - 30 + off)
        txt(d, cx - 220, cy + 30 + off, "집 팝니다", 58, INK, anchor="lm")
        txt(d, cx - 220, cy + 115 + off, "4,000원", 80, (255, 110, 40), anchor="lm")
        txt(d, cx - 220, cy + 190 + off, "거래 장소: 놀이터 매표소", 34, GRAY, anchor="lm")
    else:
        txt(d, cx, cy, "글 쓰는 중...", 46, GRAY)
    # 알림 3개: 휴대폰 아래 줄에 차례로
    for i, s in enumerate(("채팅 37건", "찜 128", "지금 갈게요")):
        tt = t_post + 0.7 + i * 0.3
        if t > tt:
            k = back((t - tt) / 0.3)
            if k > 0: pill(d, (430, 680, 920)[i], 1275, s, int(42 * min(k, 1.1)) or 1, (255, 235, 160))
    stamp(im, cx + 10, cy - 120, back((t - t_stamp) / 0.3), ["전셋집"], rotd=12, size=320)
    put(im, kid_point(t), 170, 1180, 0.72 * breathe(t)); d = ImageDraw.Draw(im)
    # 4번 댓글 카드(닉네임 없음) — 맨 위
    kc = back((t - 0.1) / 0.4)
    if kc > 0:
        cw = int(940 * min(kc, 1))
        comment_card(d, 70, 120, None, "4번 자기 집 4천원에 팔기", "선택지에 없음", (255, 210, 80), wid=max(cw, 300))
    if t > t_owner:
        k = back((t - t_owner) / 0.35)
        if k > 0:
            s = "집주인님이 이 글을 봤습니다"; size = int(56 * min(k, 1.1)) or 1; w = d.textlength(s, font=V1.F(size))
            d.rounded_rectangle((540 - w / 2 - 40, 1400 - size * 0.85, 540 + w / 2 + 40, 1400 + size * 0.85), radius=30, fill=(40, 40, 48), outline=INK, width=5)
            txt(d, 540, 1402, s, size, (255, 150, 150))
    return chrome(im)

OPTS = (("sash", "아파트 반장 선거", (235, 70, 80)), ("door", "집주인 찾아간다", (150, 100, 65)), ("bag", "짐 싸서 가출", (90, 170, 100)))
OX = (190, 540, 890)
def vote_cards(im, t, sp, cy=1250):
    d = ImageDraw.Draw(im)
    for i, (key, name, col) in enumerate(OPTS):
        x = OX[i]; k = back((t - (0.9, 1.7, 2.6)[i]) / 0.4)
        if k <= 0: continue
        pul = 1 + 0.035 * math.sin(t * 5 + i * 1.4); w2, h2 = 165 * k * pul, 185 * k * pul
        d.rounded_rectangle((x - w2 + 6, cy - h2 + 10, x + w2 + 6, cy + h2 + 10), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy + h2), radius=34, fill=WHT, outline=INK, width=6)
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy - h2 + 70 * k), radius=34, fill=col, outline=INK, width=6)
        if k > 0.9:
            txt(d, x, cy - h2 + 38, f"{i + 1}번", 48, WHT, stroke=4)
            put(im, key, x, cy + 6, 0.92); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 48, name, 38 if len(name) <= 7 else 34, INK)
    return d

def s5(t, dur):  # 갈림길 → 안 정하면 4천 원에 진짜 팔림
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s5"]
    sw = sp * 0.55; last = sp * 0.74
    if t < sw:
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "세 살, 다음은?", 100)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
    lift = 0 if t < last else 30 * abs(math.sin((t - last) * 6))
    put(im, kid_key(t, "o", 0.2), 540, 600 - lift, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
    if t > last:
        k = back((t - last) / 0.35)
        if k > 0:
            blinkon = int((t - last) * 4) % 2 == 0 or t > last + 1.0
            if blinkon: pill(d, 540, 340, "안 정하면 4천 원에 진짜 팔림", int(50 * min(k, 1.1)) or 1, (255, 120, 120))
    vote_cards(im, t, sp)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5)
if __name__ == "__main__":
    V1.main()
