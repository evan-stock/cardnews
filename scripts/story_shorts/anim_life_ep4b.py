# 인생 댓글로 정함 4화(대안 '가짜 김댓글', 2026.10.26) — 영재 방송 나온 김댓글, 알고 보니 옆집 애
# 콜드 오픈(TV 속 가짜 김댓글 vs 소파의 감기 김댓글) → 설정 + 1등 댓글 탓 → 영유 75만 원·촬영 당일 콧물 감기 → 옆집 애가 이름표 바꿔 달고 대타
#   → 옆집 애 영재로 뜸, 출연료도 옆집, 우리는 감기약 2만 원 → 갈림길: 방송국에 따진다 / 옆집 애로 산다 / 쌍둥이라고 우긴다
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep4b.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d5.py(kidu_* kidut_* kidup_* pd_* nb_* sick_*) + life_3d3.py(cap bag)
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
KIDS = ["kidu_happy", "kidu_blink", "kidu_proud", "kidu_o", "kidu_frown", "kidut_proud", "kidut_blink", "kidup_happy", "kidup_blink", "nb_happy", "nb_blink", "nb_proud", "sick_frown", "sick_blink"]
raw = {k: Image.open(os.path.join(SPR, f"{k}.png")).convert("RGBA") for k in KIDS}
bx = [raw[k].getbbox() for k in KIDS]
box = (min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx))
w_body = raw["kidu_happy"].getbbox(); kscale = 360 / (w_body[2] - w_body[0])
for k in KIDS:
    im = raw[k].crop(box); S[k] = with_shadow(im.resize((int(im.width * kscale), int(im.height * kscale)), Image.LANCZOS))
for k in ("pd_o", "pd_happy", "pd_blink"): load(k, f"{k}.png", 380)
load("cap", "cap.png", 200, False); load("bag", "bag.png", 190, False)

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
S["bg_living_b"] = S["bg_living"].filter(ImageFilter.GaussianBlur(3))

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

# ---------- 4화 대안 추가 소품 ----------
def nb_key(t, expr="happy", seed=0.9): return "nb_blink" if blink(t, seed) < 1 else f"nb_{expr}"
def sick_key(t, seed=0.2): return "sick_blink" if blink(t * 0.6, seed) < 1 else "sick_frown"

def tv_frame(im, x0, y0, x1, y1, inner):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0 - 24 + 8, y0 - 24 + 12, x1 + 24 + 8, y1 + 24 + 12), radius=30, fill=(90, 60, 45))
    d.rounded_rectangle((x0 - 24, y0 - 24, x1 + 24, y1 + 24), radius=30, fill=(40, 40, 48), outline=INK, width=6)
    inner = inner.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    im.alpha_composite(inner, (x0, y0)); d = ImageDraw.Draw(im)
    d.line([((x0 + x1) / 2 - 60, y1 + 24), ((x0 + x1) / 2 - 100, y1 + 80)], fill=INK, width=10)
    d.line([((x0 + x1) / 2 + 60, y1 + 24), ((x0 + x1) / 2 + 100, y1 + 80)], fill=INK, width=10)
    return d

def piano(d, x, y, w=420):
    d.rounded_rectangle((x - w / 2, y - 40, x + w / 2, y + 110), radius=16, fill=(40, 34, 40), outline=INK, width=5)
    n = 10; kw = (w - 30) / n
    for i in range(n): d.rectangle((x - w / 2 + 15 + i * kw, y, x - w / 2 + 15 + (i + 1) * kw - 3, y + 95), fill=WHT)
    for i in (1, 2, 4, 5, 6, 8, 9): d.rectangle((x - w / 2 + 15 + i * kw - 12, y, x - w / 2 + 15 + i * kw + 12, y + 55), fill=INK)

def studio_tv(t):
    """TV 속 방송 화면(1080x1490 그려서 축소): 가짜 김댓글 피아노 + 방송 자막"""
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im)
    put(im, nb_key(t, "proud"), 540, 640, 1.25 * breathe(t)); d = ImageDraw.Draw(im)
    piano(d, 540, 1020, 760)
    for i in range(3):  # 음표
        ph = (t * 0.9 + i / 3) % 1; x = 250 + i * 290 + 30 * math.sin(t * 3 + i); y = 900 - ph * 500
        d.ellipse((x - 34, y + 30, x + 14, y + 66), fill=YEL, outline=INK, width=5); d.line([(x + 10, y + 46), (x + 10, y - 50)], fill=INK, width=9); d.line([(x + 10, y - 50), (x + 50, y - 20)], fill=INK, width=9)
    d.rectangle((0, 1200, W, 1420), fill=(20, 20, 30))
    d.rectangle((0, 1200, 300, 1420), fill=RED); txt(d, 150, 1310, "영재", 96, WHT)
    txt(d, 340, 1310, "김댓글(3세)", 110, WHT, anchor="lm")
    return im

def sofa(d, cx, cy, w=760):
    d.rounded_rectangle((cx - w / 2, cy - 180, cx + w / 2, cy + 40), radius=60, fill=(230, 120, 110), outline=INK, width=6)
    d.rounded_rectangle((cx - w / 2 - 50, cy - 80, cx - w / 2 + 70, cy + 120), radius=50, fill=(215, 105, 95), outline=INK, width=6)
    d.rounded_rectangle((cx + w / 2 - 70, cy - 80, cx + w / 2 + 50, cy + 120), radius=50, fill=(215, 105, 95), outline=INK, width=6)
    d.rounded_rectangle((cx - w / 2 + 40, cy, cx + w / 2 - 40, cy + 130), radius=40, fill=(240, 140, 128), outline=INK, width=6)

def name_tag(d, x, y, s="김댓글", size=50, rot_k=0):
    w = d.textlength(s, font=V1.F(size))
    d.rounded_rectangle((x - w / 2 - 26, y - size * 0.85, x + w / 2 + 26, y + size * 0.85), radius=16, fill=WHT, outline=NAVY, width=7)
    d.rectangle((x - w / 2 - 26, y - size * 0.85, x + w / 2 + 26, y - size * 0.85 + 18), fill=NAVY)
    txt(d, x, y + 6, s, size, NAVY)

def thermo(d, x, y, k=1.0):
    d.rounded_rectangle((x - 26, y - 220, x + 26, y + 40), radius=26, fill=WHT, outline=INK, width=6)
    h = 200 * k; d.rounded_rectangle((x - 12, y + 20 - h, x + 12, y + 30), radius=12, fill=RED)
    d.ellipse((x - 48, y + 10, x + 48, y + 106), fill=RED, outline=INK, width=6)

def trophy(im, x, y, k=1.0):
    t = Image.new("RGBA", (260, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.pieslice((40, -40, 220, 200), 0, 180, fill=(255, 205, 60), outline=INK, width=6)
    d.arc((0, 30, 80, 130), 90, 270, fill=(255, 205, 60), width=16); d.arc((180, 30, 260, 130), 270, 90, fill=(255, 205, 60), width=16)
    d.rectangle((110, 150, 150, 230), fill=(240, 180, 40), outline=INK, width=5)
    d.rounded_rectangle((60, 230, 200, 300), radius=12, fill=(150, 100, 60), outline=INK, width=5)
    d.text((130, 120), "영재", font=V1.F(46), fill=INK, anchor="mm")
    t = t.resize((max(1, int(260 * k)), max(1, int(320 * k))))
    im.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))

def megaphone():
    im = Image.new("RGBA", (220, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(40, 70), (180, 15), (180, 165), (40, 110)], fill=(240, 90, 80), outline=INK)
    d.rounded_rectangle((15, 60, 55, 120), radius=10, fill=(200, 200, 210), outline=INK, width=5)
    d.rounded_rectangle((60, 105, 90, 170), radius=8, fill=(90, 90, 100), outline=INK, width=4)
    for i in range(3): d.arc((175 - 10 + i * 0, 40 - i * 20, 210 + i * 10, 140 + i * 20), -50, 50, fill=INK, width=5)
    return im

def house():
    im = Image.new("RGBA", (220, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(10, 90), (110, 10), (210, 90)], fill=(240, 120, 90), outline=INK)
    d.rectangle((35, 90, 185, 195), fill=(255, 240, 210), outline=INK, width=6)
    d.rectangle((90, 125, 130, 195), fill=(160, 110, 70), outline=INK, width=4)
    d.rounded_rectangle((60, 30, 160, 70), radius=10, fill=WHT, outline=INK, width=3)
    d.text((110, 52), "옆집", font=V1.F(30), fill=INK, anchor="mm"); return im

def twins():
    im = Image.new("RGBA", (240, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for cx in (65, 175):
        d.ellipse((cx - 55, 20, cx + 55, 130), fill=(255, 222, 196), outline=INK, width=5)
        for ex in (-20, 20): d.ellipse((cx + ex - 7, 60, cx + ex + 7, 76), fill=INK)
        d.arc((cx - 18, 75, cx + 18, 105), 20, 160, fill=INK, width=4)
    d.text((120, 160), "=", font=V1.F(60), fill=RED, anchor="mm"); return im

S["mega"] = megaphone(); S["house"] = house(); S["twins"] = twins()

# ---------- 대본(장면 길이 계산용, 실제 목소리는 drafts/life.json) ----------
V1.SCENES = [
    dict(id="s1", say="방송에 김댓글이 나왔습니다. 근데 얘, 김댓글 아닙니다.", sfx=[("shock", 2.3)]),
    dict(id="s2", say="얘가 진짜. 댓글 일등대로 사는 아기, 김댓글. 댓글 일등이 영유 가서 영재 방송 나가래서, 섭외까진 됐습니다.",
         sub="얘가 진짜. 댓글 1등대로 사는 아기, 김댓글. 댓글 1등이 '영유 가서 영재 방송' 나가래서, 섭외까진 됐습니다.", sfx=[("ding", 0.4)]),
    dict(id="s3", say="반 달에 칠십오만 원. 통장 십사만 원. 그리고 촬영 당일, 콧물 감기.",
         sub="반 달에 75만 원. 통장 14만 원. 그리고 촬영 당일, 콧물 감기.", sfx=[("thud", 2.6)]),
    dict(id="s4", say="피디는 안 기다립니다. 옆집 애가 대신 나갔어요. 이름표만 바꿔 달고.",
         sub="PD는 안 기다립니다. 옆집 애가 대신 나갔어요. 이름표만 바꿔 달고.", sfx=[("boing", 2.4)]),
    dict(id="s5", say="옆집 애, 영재로 떴습니다. 출연료 십만 원도 옆집이 가져갔고요. 우리는 감기약 값만 이만 원.",
         sub="옆집 애, 영재로 떴습니다. 출연료 10만 원도 옆집이 가져갔고요. 우리는 감기약 값만 2만 원.", sfx=[("tada", 0.4)]),
    dict(id="s6", say="진짜 김댓글은 누굽니까. 방송국에 따진다, 그냥 옆집 애로 산다, 아니면 쌍둥이라고 우긴다. 댓글 일등대로 갑니다. 안 정하면, 오화엔 옆집 애가 나옵니다.",
         sub="진짜 김댓글은 누굽니까? 방송국에 따진다, 그냥 옆집 애로 산다, 아니면 쌍둥이라고 우긴다. 댓글 1등대로 갑니다. 안 정하면, 5화엔 옆집 애가 나옵니다.", sfx=[("question", 0.6)]),
]
V1.HOOK = ["영재 방송 나온 김댓글", "알고 보니 '옆집 애'"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

# ---------- 장면 ----------
def s1(t, dur):  # TV 속 가짜 김댓글 vs 소파의 감기 김댓글
    im = S["bg_living_b"].copy(); sp = SPEAK["s1"]
    tv = studio_tv(t)
    d = tv_frame(im, 150, 140, 930, 690, tv)
    sofa(d, 540, 1180)
    put(im, sick_key(t), 540, 1010, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
    ph = (t * 0.7) % 1  # 콧물 훌쩍
    if ph < 0.15: txt(d, 700, 860, "훌쩍", 56, (120, 170, 230), stroke=5, sfill=WHT)
    no = sp * 0.55
    if t > no:
        k = back((t - no) / 0.3)
        if k > 0:
            sz = int(110 * min(k, 1.1)) or 1; s = "김댓글 아님"; w = d.textlength(s, font=V1.F(sz))
            d.rounded_rectangle((540 - w / 2 - 40, 415 - sz * 0.8, 540 + w / 2 + 40, 415 + sz * 0.8), radius=30, fill=RED, outline=INK, width=8)
            txt(d, 540, 420, s, sz, WHT, stroke=6)
            if k > 0.9: pill(d, 830, 800, "진짜는 여기", 46, YEL)
    return chrome(im)

def s2(t, dur):  # 진짜 김댓글 + 1등 댓글 탓
    im = S["bg_living_b"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    put(im, sick_key(t), 540, 600, 1.15 * breathe(t)); d = ImageDraw.Draw(im)
    a = back((t - 0.1) / 0.35)
    if a > 0: pill(d, 830, 250, "진짜", int(64 * min(a, 1.1)) or 1, YEL)
    k = back((t - 0.5) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1))
        w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.45) / 0.4)
    if kc > 0:
        x0 = 70 + (1 - kc) * 900
        d.rounded_rectangle((x0 + 8, 1208, x0 + 948, 1408), radius=34, fill=(170, 130, 100))
        d.rounded_rectangle((x0, 1198, x0 + 940, 1398), radius=34, fill=WHT, outline=INK, width=6)
        txt(d, x0 + 40, 1248, "@요아에오", 40, (140, 130, 125), anchor="lm")
        txt(d, x0 + 40, 1330, "영어유치원 가서 영재티비 촬영 캐스팅", 50, INK, anchor="lm")
        d.rounded_rectangle((x0 + 760, 1176, x0 + 930, 1232), radius=26, fill=YEL, outline=INK, width=5)
        txt(d, x0 + 845, 1205, "1등 댓글", 34, INK)
    if t > sp * 0.82:
        b = back((t - sp * 0.82) / 0.35)
        if b > 0: pill(d, 250, 420, "섭외 성공", int(54 * min(b, 1.1)) or 1, (255, 225, 120))
    return chrome(im)

def s3(t, dur):  # 영유 75만 원 → 촬영 당일 콧물 감기
    sp = SPEAK["s3"]; cut = sp * 0.48
    if t < cut:
        im = S["bg_gate"].copy(); d = ImageDraw.Draw(im)
        put(im, "cap", 540, 230, 0.7 + 0.03 * math.sin(t * 4)); d = ImageDraw.Draw(im)
        a = ease((t - 0.05) / 0.35); label(d, 560 + (1 - a) * 40, "반 달 75만 원", 104)
        put(im, kid_key(t, "o", 0.4), 540, 900, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        d = bank(im, t, 0.4, 890000, 140000, cy=1260)
        return chrome(im)
    t2 = t - cut
    im = S["bg_living_b"].copy(); d = ImageDraw.Draw(im)
    # 달력
    d.rounded_rectangle((90, 170, 470, 560), radius=20, fill=WHT, outline=INK, width=6)
    d.rounded_rectangle((90, 170, 470, 260), radius=20, fill=RED, outline=INK, width=6)
    txt(d, 280, 216, "촬영 날", 56, WHT, stroke=4); txt(d, 280, 410, "D-DAY", 92, RED)
    k = back(t2 / 0.35)
    if k > 0:
        stamp(im, 380, 500, k, ["X"], 0, 200); d = ImageDraw.Draw(im)
    put(im, sick_key(t), 600, 900, 1.0 * breathe(t)); d = ImageDraw.Draw(im)
    tk = ease((t2 - 0.3) / 0.8)
    thermo(d, 880, 520, 0.3 + 0.7 * tk)
    if tk >= 1: txt(d, 880, 220, "38도", 80, RED, stroke=6, sfill=WHT)
    if t2 > 0.6:
        b = back((t2 - 0.6) / 0.35)
        if b > 0: label(d, 1290, "콧물 감기", int(110 * min(b, 1.1)) or 1)
    return chrome(im)

def s4(t, dur):  # PD는 안 기다림 → 옆집 애가 이름표 받아 닮
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    swap = sp * 0.38
    if t < swap:
        tap = 8 * abs(math.sin(t * 12))
        put(im, pd_key(t, "o"), 540, 700 - tap, 0.95); d = ImageDraw.Draw(im)
        sweat(d, 380, 420, t); sweat(d, 700, 440, t, 0.4)
        # 시계
        d.ellipse((780, 250, 960, 430), fill=WHT, outline=INK, width=8)
        ang = t * 8; d.line([(870, 340), (870 + 60 * math.sin(ang), 340 - 60 * math.cos(ang))], fill=RED, width=8)
        d.line([(870, 340), (870, 290)], fill=INK, width=8)
        a = ease((t - 0.05) / 0.3); label(d, 1250 + (1 - a) * 30, "PD는 안 기다림", 100)
    else:
        t2 = t - swap
        put(im, pd_key(t, "happy"), 860, 700, 0.6); d = ImageDraw.Draw(im)
        k = ease(t2 / 0.4)
        put(im, nb_key(t, "proud"), 1300 - 840 * k, 860, 1.0 * breathe(t)); d = ImageDraw.Draw(im)
        a = ease((t2 - 0.5) / 0.6)  # 이름표 날아와 붙음
        tx, ty = 120 + (460 - 120) * a, 300 + (920 - 300) * a
        if t2 > 0.2: name_tag(d, tx, ty, "김댓글", 50)
        if a >= 1:
            b = back((t2 - 1.1) / 0.35)
            if b > 0: label(d, 1250, "이름표만 바꿔 달고", int(96 * min(b, 1.1)) or 1)
        if t2 > 0.3: label(d, 230, "대타: 옆집 애", 96)
    return chrome(im)

def s5(t, dur):  # 옆집 애 영재로 뜸, 출연료도 옆집 → 우리 통장 14만→12만
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s5"]
    half = sp * 0.55
    r = __import__("random").Random(int(t * 10))
    if t < half:
        for i in range(40):  # 꽃가루
            x = (i * 97 + t * 160 * (1 + i % 3)) % W; y = (i * 53 + t * 380) % 1100
            d.rectangle((x, y, x + 14, y + 22), fill=[(255, 110, 130), YEL, (120, 200, 255), (140, 230, 150)][i % 4])
        put(im, nb_key(t, "proud"), 420, 820, 1.05 * breathe(t)); d = ImageDraw.Draw(im)
        name_tag(d, 420, 960, "김댓글", 40)
        trophy(im, 790, 760, min(back((t - 0.2) / 0.4), 1.1)); d = ImageDraw.Draw(im)
        a = back((t - 0.3) / 0.35)
        if a > 0: label(d, 260, "영재로 뜸", int(120 * min(a, 1.1)) or 1)
        e = ease((t - sp * 0.3) / 0.6)
        if t > sp * 0.3:
            put(im, "env", 790 + 400 * e, 1180, 0.9); d = ImageDraw.Draw(im)
            pill(d, 560, 1180, "출연료 10만 원은 옆집", 48, YEL)
    else:
        im = S["bg_living_b"].copy(); d = ImageDraw.Draw(im)
        put(im, sick_key(t), 540, 980, 0.9 * breathe(t)); d = ImageDraw.Draw(im)
        d = bank(im, t, half, 140000, 120000, cy=440)
        if t > half + 0.9:
            pill(d, 540, 1300, "감기약 2만 원", 60, WHT)
            stamp(im, 880, 1120, back((t - half - 1.2) / 0.3), ["손해"], -14, 230)
    return chrome(im)

OPTS = (("mega", "방송국에 따진다", (235, 80, 90)), ("house", "옆집 애로 산다", (110, 170, 120)), ("twins", "쌍둥이라 우김", (150, 100, 220)))
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
            put(im, key, x, cy + 10, 0.8); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 50, name, 40, INK)
    return d

def s6(t, dur):  # 진짜 vs 가짜 → 갈림길 → 안 정하면 5화엔 옆집 애
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s6"]
    sw = sp * 0.55; last = sp * 0.78
    if t < sw:
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "진짜 김댓글은?", 104)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
    if t < last:
        put(im, sick_key(t), 300, 560, 0.85 * breathe(t)); put(im, nb_key(t, "happy"), 780, 560, 0.85 * breathe(t, 1))
        d = ImageDraw.Draw(im); name_tag(d, 300, 760, "김댓글", 40); name_tag(d, 780, 760, "김댓글", 40)
        b = 16 * abs(math.sin(t * 6)); txt(d, 540, 520 - b, "?", 150, (255, 95, 110), stroke=9, sfill=WHT)
    else:  # 옆집 애가 가운데로 쓱, 진짜는 밀려남
        k = ease((t - last) / 0.5)
        put(im, sick_key(t), 300 - 260 * k, 600, 0.85 * breathe(t)); put(im, nb_key(t, "proud"), 780 - 240 * k, 540, (0.85 + 0.15 * k) * breathe(t, 1))
        d = ImageDraw.Draw(im); name_tag(d, 780 - 240 * k, 760 + 30 * k, "김댓글", 44)
        if k >= 1: pill(d, 540, 340, "5화 주인공?", 56, YEL)
    vote_cards(im, t)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6)
if __name__ == "__main__":
    V1.main()
