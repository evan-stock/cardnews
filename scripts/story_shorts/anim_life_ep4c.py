# 인생 댓글로 정함 4화(최종 '생방송 폭로', 2026.10.26) — 세 살이 생방송에서 집안 폭로함
# 콜드 오픈(마이크 잡고 "Mommy, no money!") → 설정 + 1등 댓글 탓 → 통장 14만 원 전국 생중계, 엄마 얼음 → 갈림길(엄마한테 사과 / 돈 벌러 간다 / 한 번 더 폭로)
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep4c.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d5.py(kidu_* kidut_* kidup_* kidum_* pd_*) + life_3d3.py(mom_wow) + life_3d2.py(mom_blink money mic)
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
SPR = sys.argv.pop(2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import anim_life_ep1_v2 as V2
import life_sprites as L
from anim_life_ep1 import W, H, YEL, WHT, ease, back, blink

S = V2.S
put, txt, label, pill, breathe = V2.put, V2.txt, V2.label, V2.pill, V2.breathe
INK = V2.INK
RED = (235, 70, 80); GREEN = (60, 175, 95); NAVY = (52, 64, 120); GRAY = (150, 150, 158)
EP = "4화"

def with_shadow(im, k=0.1):
    pad = int(im.height * k); out = Image.new("RGBA", (im.width + 40, im.height + pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    cx, cy = out.width / 2, im.height + pad * 0.25
    d.ellipse((cx - im.width * 0.38, cy - pad * 0.28, cx + im.width * 0.38, cy + pad * 0.28), fill=(60, 40, 30, 85))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(pad * 0.25)))
    out.alpha_composite(im, (20, 0)); return out

def load(key, file, width, shadow=True):
    im = Image.open(os.path.join(SPR, file)).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)
    S[key] = with_shadow(im) if shadow else im

# 원복 김댓글: 잘라내지 않은 같은 캔버스 → 모든 포즈를 합친 상자로 함께 잘라 위치를 맞춘다
KIDS = ["kidu_happy", "kidu_blink", "kidu_proud", "kidu_o", "kidu_frown", "kidut_proud", "kidut_blink", "kidup_happy", "kidup_blink", "kidum_proud", "kidum_blink", "kidum_o"]
raw = {k: Image.open(os.path.join(SPR, f"{k}.png")).convert("RGBA") for k in KIDS}
bx = [raw[k].getbbox() for k in KIDS]
box = (min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx))
w_body = raw["kidu_happy"].getbbox(); kscale = 360 / (w_body[2] - w_body[0])
for k in KIDS:
    im = raw[k].crop(box); S[k] = with_shadow(im.resize((int(im.width * kscale), int(im.height * kscale)), Image.LANCZOS))
for k in ("pd_o", "pd_happy", "pd_blink"): load(k, f"{k}.png", 380)
for k in ("mom_wow", "mom_blink"): load(k, f"{k}.png", 380)
load("money", "money.png", 230, False); load("mic", "mic.png", 130, False)

# ---------- 배경 ----------
def bg_studio():
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; c = tuple(int(a * (1 - t) + b * t) for a, b in zip((52, 46, 88), (96, 70, 130))); d.line([(0, y), (W, y)], fill=c)
    for i in range(7):  # 조명 빛줄기
        x = 80 + i * 155; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.polygon([(x - 20, 0), (x + 20, 0), (x + 170, 1130), (x - 170, 1130)], fill=(255, 240, 200, 26)); im.alpha_composite(lay); d = ImageDraw.Draw(im)
    for i in range(9):  # 위 조명 기구
        x = 60 + i * 120; d.rounded_rectangle((x - 34, 0, x + 34, 46), radius=10, fill=(40, 40, 48)); d.ellipse((x - 24, 26, x + 24, 60), fill=(255, 236, 170))
    d.rounded_rectangle((260, 160, 820, 300), radius=30, fill=(255, 212, 59), outline=INK, width=7)  # 간판
    d.text((540, 232), "영재 발견 쇼", font=V1.F(84), fill=INK, anchor="mm")
    for i in range(14):  # 반짝 점
        x = 260 + i * 40; d.ellipse((x - 6, 148, x + 6, 160), fill=(255, 255, 255) if i % 2 else (255, 120, 140))
    d.rectangle((0, 1130, W, H), fill=(70, 56, 98)); d.rectangle((0, 1130, W, 1146), fill=(120, 100, 160))
    for x in range(0, W, 120): d.line([(x, 1146), (x - 160, H)], fill=(84, 68, 116), width=4)
    return im

def bg_kinder():  # 영어유치원 교실
    im = Image.new("RGBA", (W, H), (226, 240, 255)); d = ImageDraw.Draw(im)
    for y in range(0, 1130, 60): d.line([(0, y), (W, y)], fill=(214, 232, 252), width=3)
    d.rounded_rectangle((120, 120, 960, 560), radius=26, fill=(52, 92, 78), outline=(150, 105, 70), width=22)  # 칠판
    for i, ch in enumerate("ABCDEFG"):  # 알파벳 띠
        x = 150 + i * 120; col = [(255, 120, 130), (255, 200, 80), (110, 200, 140), (110, 170, 240)][i % 4]
        d.rounded_rectangle((x - 46, 34, x + 46, 104), radius=14, fill=col, outline=INK, width=4); d.text((x, 70), ch, font=V1.F(56), fill=WHT, anchor="mm")
    d.rectangle((0, 1130, W, H), fill=(240, 200, 150)); d.rectangle((0, 1130, W, 1146), fill=(210, 170, 120))
    for x in range(0, W, 90): d.line([(x, 1146), (x, H)], fill=(228, 186, 136), width=3)
    return im

def bg_gate():  # 영어유치원 정문
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip((170, 220, 255), (225, 245, 255))))
    d.rectangle((90, 260, 990, 1130), fill=(255, 250, 240), outline=INK, width=7)
    d.polygon([(60, 270), (540, 90), (1020, 270)], fill=(120, 140, 230), outline=INK)
    d.rounded_rectangle((200, 300, 880, 430), radius=24, fill=NAVY, outline=INK, width=6)
    d.text((540, 366), "ENGLISH KINDER", font=V1.F(76), fill=YEL, anchor="mm")
    for x in (190, 790):
        d.rounded_rectangle((x, 480, x + 100, 600), radius=12, fill=(190, 225, 255), outline=INK, width=5)
    d.rectangle((0, 1130, W, H), fill=(170, 210, 140)); d.rectangle((0, 1130, W, 1146), fill=(140, 185, 110))
    return im

S["bg_studio"] = bg_studio().filter(ImageFilter.GaussianBlur(2))
S["bg_kinder"] = bg_kinder().filter(ImageFilter.GaussianBlur(2))
S["bg_gate"] = bg_gate().filter(ImageFilter.GaussianBlur(2))
S["bg_vote"] = S["bg_vote"].filter(ImageFilter.GaussianBlur(3))

# ---------- 코드로 그린 소품 ----------
def icon_play(w=200):
    h = int(w * 0.7); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w + 6, h + 6), radius=int(h * 0.3), fill=(235, 50, 55), outline=INK, width=6)
    cx, cy = w / 2 + 6, h / 2 + 6; s = h * 0.24
    d.polygon([(cx - s * 0.8, cy - s), (cx - s * 0.8, cy + s), (cx + s * 1.1, cy)], fill=WHT); return im

def icon_cam():
    im = Image.new("RGBA", (300, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 40, 210, 200), radius=30, fill=(60, 64, 78), outline=INK, width=7)
    d.polygon([(210, 90), (290, 50), (290, 190), (210, 150)], fill=(85, 90, 108), outline=INK, width=7)
    d.ellipse((55, 65, 165, 175), fill=(30, 34, 44), outline=INK, width=6); d.ellipse((80, 90, 112, 122), fill=(150, 200, 255))
    d.ellipse((170, 50, 196, 76), fill=(240, 60, 70)); return im

def icon_phone(on=False):
    im = Image.new("RGBA", (170, 290), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((5, 5, 165, 285), radius=26, fill=(40, 40, 48), outline=INK, width=5)
    d.rounded_rectangle((18, 30, 152, 260), radius=14, fill=(250, 250, 252))
    d.rounded_rectangle((30, 50, 140, 120), radius=10, fill=(255, 220, 200))
    if on:
        d.rounded_rectangle((28, 180, 142, 230), radius=24, fill=(205, 205, 210)); d.text((85, 205), "구독중", font=V1.F(32), fill=(90, 90, 96), anchor="mm")
    else:
        d.rounded_rectangle((28, 180, 142, 230), radius=24, fill=(235, 50, 55)); d.text((85, 205), "구독", font=V1.F(36), fill=WHT, anchor="mm")
    return im

def envelope():
    im = Image.new("RGBA", (300, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((10, 10, 290, 200), fill=(255, 246, 225), outline=INK, width=6)
    d.line([(10, 10), (150, 110), (290, 10)], fill=INK, width=6)
    d.text((150, 160), "출연료", font=V1.F(44), fill=(200, 80, 60), anchor="mm"); return im


def icon_formula():  # 분유통
    im = Image.new("RGBA", (170, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 40, 155, 195), radius=18, fill=(250, 250, 252), outline=INK, width=6)
    d.rounded_rectangle((8, 10, 162, 52), radius=14, fill=(110, 170, 240), outline=INK, width=6)
    d.ellipse((50, 85, 120, 150), fill=(255, 212, 59), outline=INK, width=4)
    d.text((85, 172), "분유", font=V1.F(30), fill=(90, 140, 210), anchor="mm"); return im

def icon_sand():  # 모래 양동이 + 삽
    im = Image.new("RGBA", (220, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(30, 70), (150, 70), (135, 190), (45, 190)], fill=(240, 80, 90), outline=INK)
    d.ellipse((24, 58, 156, 86), fill=(235, 200, 140), outline=INK, width=5)
    d.arc((40, 10, 140, 110), 200, 340, fill=INK, width=6)
    d.line([(150, 30), (190, 150)], fill=(255, 200, 60), width=14)
    d.polygon([(175, 140), (210, 135), (215, 190), (185, 195)], fill=(255, 200, 60), outline=INK); return im

S["formula"] = icon_formula(); S["sand"] = icon_sand(); S["play"] = icon_play(); S["cam"] = icon_cam(); S["phone"] = icon_phone(); S["phone_on"] = icon_phone(True); S["env"] = envelope()

def stamp(im, x, y, k, lines, rotd=-12, size=230, col=RED):
    if k <= 0: return
    st = Image.new("RGBA", (320, 320), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.ellipse((20, 20, 300, 300), outline=col, width=14)
    if len(lines) == 1: sd.text((160, 160), lines[0], font=V1.F(96 if len(lines[0]) <= 2 else 70), fill=col, anchor="mm")
    else:
        sd.text((160, 120), lines[0], font=V1.F(56), fill=col, anchor="mm"); sd.text((160, 200), lines[1], font=V1.F(56), fill=col, anchor="mm")
    st = st.rotate(rotd, resample=Image.BICUBIC).resize((max(1, int(size * min(k, 1.2))),) * 2)
    im.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))

# ---------- 공통 ----------
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
def pd_key(t, expr="o", seed=1.1): return "pd_blink" if blink(t, seed) < 1 else f"pd_{expr}"

def bubble_r(d, x, y, s, size, tip, col=(230, 70, 80)):
    w = d.textlength(s, font=V1.F(size)); pad = size * 0.5
    box = (x - w / 2 - pad, y - size * 0.8, x + w / 2 + pad, y + size * 0.8)
    bx = min(max(tip[0], box[0] + 60), box[2] - 60)
    up = tip[1] < box[1]
    ey = box[1] + 6 if up else box[3] - 6
    d.polygon([(bx - 28, ey), (bx + 28, ey), tip], fill=WHT, outline=INK, width=5)
    d.rounded_rectangle(box, radius=int(size * 0.7), fill=WHT, outline=INK, width=6)
    d.line([(bx - 24, ey + (3 if up else 3)), (bx + 24, ey + 3)], fill=WHT, width=9)
    txt(d, x, y + 3, s, size, col)

def sweat(d, x, y, t, k=0):
    ph = (t * 1.6 + k) % 1; yy = y + ph * 60
    d.polygon([(x, yy - 22), (x - 13, yy + 4), (x + 13, yy + 4)], fill=(140, 200, 255)); d.ellipse((x - 13, yy - 8, x + 13, yy + 16), fill=(140, 200, 255))

def arrow_down(d, x, y, s=1.0, col=YEL):
    d.rectangle((x - 22 * s, y - 70 * s, x + 22 * s, y), fill=col, outline=INK, width=5)
    d.polygon([(x - 60 * s, y - 4), (x + 60 * s, y - 4), (x, y + 60 * s)], fill=col, outline=INK)

def bank(im, t, t0, frm, to, cx=540, cy=430):
    a = back((t - t0) / 0.4)
    if a <= 0: return ImageDraw.Draw(im)
    b = S["card_bank"] if a >= 0.999 else S["card_bank"].resize((max(1, int(760 * a)), max(1, int(330 * a))))
    im.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2))); d = ImageDraw.Draw(im)
    if a > 0.9:
        p = ease((t - t0 - 0.4) / 0.7); won = frm + int((to - frm) * p / 10000) * 10000
        txt(d, cx, cy - 95, "통장 잔고", 54, WHT, stroke=5)
        txt(d, cx, cy + 40, f"{won:,}원", 118, YEL if p < 1 else ((255, 120, 120) if to < frm else (140, 240, 150)), stroke=8)
        if t > t0 + 0.4:
            k = back((t - t0 - 0.4) / 0.3); dv = (to - frm) // 10000
            txt(d, cx + 340, cy - 180, f"{dv:+d}만", int(80 * min(k, 1.15)) or 1, RED if dv < 0 else GREEN, stroke=7, sfill=WHT)
    return d


def mic_key(t, expr="proud", seed=0.4): return "kidum_blink" if blink(t, seed) < 1 else f"kidum_{expr}"
def mom_key(t): return "mom_blink" if blink(t, 1.3) < 1 else "mom_wow"

def on_air(d, t, x=880, y=130):
    on = int(t * 2.5) % 2 == 0
    d.rounded_rectangle((x - 150, y - 50, x + 150, y + 50), radius=20, fill=(235, 45, 55) if on else (120, 40, 50), outline=INK, width=6)
    txt(d, x, y + 2, "ON AIR", 62, WHT)

def audience(d, t, gasp=False, y0=1280):
    for i in range(9):
        x = 60 + i * 120; b = 8 * abs(math.sin(t * 4 + i)) if gasp else 0
        col = [(70, 60, 100), (90, 75, 120), (60, 55, 90)][i % 3]
        d.ellipse((x - 48, y0 - 70 - b, x + 48, y0 + 26 - b), fill=col); d.rounded_rectangle((x - 62, y0 + 10, x + 62, y0 + 220), radius=40, fill=col)
    if gasp:
        for i, x in enumerate((180, 540, 900)):
            k = back((t - i * 0.12) / 0.3)
            if k > 0: txt(d, x, 1150, "헉", int(76 * min(k, 1.1)) or 1, YEL, stroke=7)

def heart():
    im = Image.new("RGBA", (200, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((10, 10, 110, 110), fill=(240, 80, 110), outline=INK, width=6); d.ellipse((90, 10, 190, 110), fill=(240, 80, 110), outline=INK, width=6)
    d.polygon([(18, 80), (182, 80), (100, 172)], fill=(240, 80, 110), outline=INK)
    d.ellipse((16, 16, 104, 104), fill=(240, 80, 110)); d.ellipse((96, 16, 184, 104), fill=(240, 80, 110))
    d.polygon([(24, 76), (176, 76), (100, 160)], fill=(240, 80, 110))
    d.text((100, 85), "미안", font=V1.F(44), fill=WHT, anchor="mm"); return im
S["heart"] = heart()

V1.SCENES = [
    dict(id="s1", say="세 살이 생방송에서 집안을 폭로했습니다.", sfx=[("shock", 1.1)]),
    dict(id="s2", say="얘는 댓글 일등대로 사는 아기, 김댓글. 댓글 일등대로 영유 보냈더니, 배운 영어가 이거예요.",
         sub="댓글 1등대로 사는 아기, 김댓글. 댓글 1등대로 영유 보냈더니, 배운 영어가 이거예요.", sfx=[("ding", 0.4)]),
    dict(id="s3", say="영유비 칠십오만 원 내고, 남은 통장 십사만 원. 전국에 생중계됐습니다. 엄마는 객석에서 얼었고요.",
         sub="영유비 75만 원 내고, 남은 통장 14만 원. 전국에 생중계됐습니다. 엄마는 객석에서 얼었고요.", sfx=[("thud", 1.0)]),
    dict(id="s4", say="세 살, 다음은요? 엄마한테 사과, 돈 벌러 간다, 아니면 한 번 더 폭로. 댓글 일등대로 갑니다. 안 정하면, 아빠 월급도 공개합니다.",
         sub="세 살, 다음은요? 엄마한테 사과, 돈 벌러 간다, 아니면 한 번 더 폭로. 댓글 1등대로 갑니다. 안 정하면, 아빠 월급도 공개합니다.", sfx=[("question", 0.6)]),
]
V1.HOOK = ["세 살이 생방송에서", "집안 '폭로'함"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

def s1(t, dur):  # 콜드 오픈: 마이크 잡고 "Mommy, no money!"
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im)
    on_air(d, t)
    sh = 12 * math.sin(t * 40) if 0.9 < t < 1.6 else 0
    put(im, mic_key(t, "proud" if t > 0.5 else "o"), 470 + sh, 700, 1.35 * breathe(t)); d = ImageDraw.Draw(im)
    if t > 0.4:
        b = back((t - 0.4) / 0.35); bubble_r(d, 560 + sh, 250, "Mommy, no money!", int(82 * min(b, 1.1)) or 1, (640, 400))
    audience(d, t, gasp=t > 1.0)
    return chrome(im)

def s2(t, dur):  # 설정 + 1등 댓글 탓
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    on_air(d, t)
    put(im, mic_key(t, "proud", 0.7), 540, 600, 1.1 * breathe(t)); d = ImageDraw.Draw(im)
    k = back((t - 0.15) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1)); w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.42) / 0.4)
    if kc > 0:
        x0 = 70 + (1 - kc) * 900
        d.rounded_rectangle((x0 + 8, 1208, x0 + 948, 1408), radius=34, fill=(40, 30, 60))
        d.rounded_rectangle((x0, 1198, x0 + 940, 1398), radius=34, fill=WHT, outline=INK, width=6)
        txt(d, x0 + 40, 1248, "@요아에오", 40, (140, 130, 125), anchor="lm")
        txt(d, x0 + 40, 1330, "영어유치원 가서 영재티비 촬영 캐스팅", 50, INK, anchor="lm")
        d.rounded_rectangle((x0 + 760, 1176, x0 + 930, 1232), radius=26, fill=YEL, outline=INK, width=5)
        txt(d, x0 + 845, 1205, "1등 댓글", 34, INK)
    if t > sp * 0.78:
        b = back((t - sp * 0.78) / 0.3)
        if b > 0: bubble_r(d, 560, 240, "No money!", int(84 * min(b, 1.1)) or 1, (640, 390))
    return chrome(im)

def s3(t, dur):  # 통장 14만 원 전국 생중계 → 엄마 얼음
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s3"]
    on_air(d, t)
    # 큰 전광판
    d.rounded_rectangle((90, 320, 990, 820), radius=30, fill=(30, 30, 40), outline=INK, width=10)
    d = bank(im, t, 0.2, 890000, 140000, cx=540, cy=600)
    if t > sp * 0.38:
        k = back((t - sp * 0.38) / 0.35)
        if k > 0: pill(d, 560, 890, "전국 생중계", int(70 * min(k, 1.1)) or 1, (255, 120, 120))
    put(im, mic_key(t, "proud", 0.2), 230, 1080, 0.75 * breathe(t)); d = ImageDraw.Draw(im)
    mt = sp * 0.62
    if t > mt:
        k = ease((t - mt) / 0.35)
        put(im, "mom_wow", 790, 1060 + (1 - k) * 400, 0.85); d = ImageDraw.Draw(im)
        if k >= 1:  # 얼음
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((590, 830, 990, 1420), radius=40, fill=(170, 220, 255, 110), outline=(120, 190, 240, 255), width=8)
            for i in range(4): ld.line([(620 + i * 90, 860), (680 + i * 90, 940)], fill=(255, 255, 255, 220), width=8)
            im.alpha_composite(lay); d = ImageDraw.Draw(im)
            b = back((t - mt - 0.35) / 0.3)
            if b > 0: label(d, 1360, "엄마 얼음", int(100 * min(b, 1.1)) or 1, (150, 210, 255))
    return chrome(im)

OPTS = (("heart", "엄마한테 사과", (240, 90, 120)), ("money", "돈 벌러 간다", (90, 170, 100)), ("mic", "한 번 더 폭로", (235, 70, 80)))
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
            put(im, key, x, cy + 10, 0.75); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 50, name, 40, INK)
    return d

def s4(t, dur):  # 갈림길 → 안 정하면 아빠 월급도 공개
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    sw = sp * 0.5; last = sp * 0.76
    if t < sw:
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "다음은?", 120)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
    lift = 0 if t < last else 30 * abs(math.sin((t - last) * 6))
    put(im, mic_key(t, "proud", 0.3), 540, 560 - lift, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
    if t > last:
        k = back((t - last) / 0.35)
        if k > 0: pill(d, 540, 330, "아빠 월급도 공개?", int(58 * min(k, 1.1)) or 1, (255, 120, 120))
    vote_cards(im, t)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4)
if __name__ == "__main__":
    V1.main()
