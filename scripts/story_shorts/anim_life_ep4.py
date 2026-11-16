# 인생 댓글로 정함 4화 — 영어유치원 보냈더니 세 살이 '구독' 구걸함 (2026.10.26)
# 콜드 오픈(영재 방송에서 구독 구걸) → 설정 한 줄 + 1등 댓글 탓 → 영유 반 달 75만 원·영어 이름 코멘트 → 배운 영어 'Like, Subscribe'
#   → PD가 구독, 판정 '댓글 유도 영재', 출연료 10만 원 손해 → 섭외 갈림길: 분유 광고 / 대치동 영재학원 / 놀이터 사장(댓글 안 달면 또 손짓)
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep4.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d5.py(kidu_* kidut_* kidup_* pd_*) + life_3d3.py(cap bag)
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
KIDS = ["kidu_happy", "kidu_blink", "kidu_proud", "kidu_o", "kidu_frown", "kidut_proud", "kidut_blink", "kidup_happy", "kidup_blink"]
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

# ---------- 대본(장면 길이 계산용, 실제 목소리는 drafts/life.json) ----------
V1.SCENES = [
    dict(id="s1", say="세 살이 영재 방송에서 구독을 구걸하고 있습니다.", sfx=[("thud", 0.9)]),
    dict(id="s2", say="얘는 댓글 일등대로 사는 아기, 김댓글. 이번엔 댓글 일등이 영유 가서 영재 방송 나가래서, 나갔습니다.",
         sub="댓글 1등대로 사는 아기, 김댓글. 이번엔 댓글 1등이 '영유 가서 영재 방송' 나가래서, 나갔습니다.", sfx=[("ding", 0.5)]),
    dict(id="s3", say="반 달에 칠십오만 원. 통장 팔십구만 원이 십사만 원. 영어 이름은 코멘트. 본인이 골랐습니다.",
         sub="반 달에 75만 원. 통장 89만 원이 14만 원. 영어 이름은 코멘트(COMMENT). 본인이 골랐습니다.", sfx=[("shock", 1.2)]),
    dict(id="s4", say="보름 동안 배운 영어. 라이크, 섭스크라이브. 그게 다입니다. 댓글로 살다 보니 버릇이 들었어요.",
         sub="보름 동안 배운 영어. 'Like, Subscribe.' 그게 다입니다. 댓글로 살다 보니 버릇이 들었어요.", sfx=[("boing", 1.6)]),
    dict(id="s5", say="문제는 하나도 안 풀었습니다. 근데 피디가 구독 눌렀습니다. 판정, 댓글 유도 영재. 출연료 십만 원. 네, 손해입니다.",
         sub="문제는 하나도 안 풀었습니다. 근데 PD가 구독 눌렀습니다. 판정: 댓글 유도 영재. 출연료 10만 원. 네, 손해입니다.", sfx=[("tada", 2.6)]),
    dict(id="s6", say="영재님, 섭외 들어왔습니다. 분유 광고 모델, 대치동 영재학원, 아니면 다 거절하고 놀이터 사장. 댓글 일등대로 갑니다. 댓글 안 달면, 얘가 또 손짓합니다.",
         sub="영재님, 섭외 들어왔습니다. 분유 광고 모델, 대치동 영재학원, 아니면 다 거절하고 놀이터 사장. 댓글 1등대로 갑니다. 댓글 안 달면, 얘가 또 손짓합니다.", sfx=[("question", 0.6)]),
]
V1.HOOK = ["영어유치원 보냈더니", "세 살이 '구독' 구걸함"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

# ---------- 장면 ----------
def s1(t, dur):  # 콜드 오픈: 카메라에 바짝 붙어 구독 구걸, 뒤에서 PD 당황
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im)
    k = ease((t - 0.6) / 0.5)
    put(im, pd_key(t), 880 + (1 - k) * 300, 640, 0.62); d = ImageDraw.Draw(im)
    if k > 0.9: sweat(d, 770, 420, t); sweat(d, 990, 450, t, 0.5)
    zoom = 1.5 + 0.12 * ease(t / 0.8)
    jx = 10 * math.sin(t * 22)
    put(im, kid_fist(t), 420 + jx, 760, zoom * breathe(t)); d = ImageDraw.Draw(im)
    # 주먹 앞 큰 구독 버튼(눌릴 때마다 꾹)
    press = abs(math.sin(t * 7)); bw = 300 - 30 * press
    d.rounded_rectangle((760 - bw / 2 + 8, 1010 - 60 + 10, 760 + bw / 2 + 8, 1010 + 60 + 10), radius=60, fill=(120, 30, 40))
    d.rounded_rectangle((760 - bw / 2, 1010 - 60 + 6 * press, 760 + bw / 2, 1010 + 60), radius=60, fill=(235, 50, 55), outline=INK, width=7)
    txt(d, 760, 1012 + 3 * press, "구독", 72, WHT)
    if t > 0.3:
        b = back((t - 0.3) / 0.35); bubble_r(d, 760, 400, "Subscribe!", int(84 * min(b, 1.1)) or 1, (560, 520))
    im.alpha_composite(S["cam"].rotate(-8, expand=True), (-40, 1150))
    d = ImageDraw.Draw(im); d.ellipse((900, 110, 936, 146), fill=(240, 50, 60) if int(t * 2) % 2 == 0 else (120, 40, 50))
    txt(d, 990, 128, "REC", 40, WHT, stroke=4)
    return chrome(im)

def s2(t, dur):  # 설정 한 줄 + 1등 댓글 탓
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    put(im, kid_key(t, "proud", 0.2), 540, 640, 1.1 * breathe(t)); d = ImageDraw.Draw(im)
    k = back((t - 0.15) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1))
        w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.42) / 0.4)
    if kc > 0:  # 1등 댓글(다시 그린 모양, 좋아요 숫자 없음)
        x0 = 70 + (1 - kc) * 900
        d.rounded_rectangle((x0 + 8, 1208, x0 + 948, 1408), radius=34, fill=(40, 30, 60))
        d.rounded_rectangle((x0, 1198, x0 + 940, 1398), radius=34, fill=WHT, outline=INK, width=6)
        txt(d, x0 + 40, 1248, "@요아에오", 40, (140, 130, 125), anchor="lm")
        txt(d, x0 + 40, 1330, "영어유치원 가서 영재티비 촬영 캐스팅", 50, INK, anchor="lm")
        d.rounded_rectangle((x0 + 760, 1176, x0 + 930, 1232), radius=26, fill=YEL, outline=INK, width=5)
        txt(d, x0 + 845, 1205, "1등 댓글", 34, INK)
    if t > sp * 0.8:
        a = back((t - sp * 0.8) / 0.35)
        if a > 0: pill(d, 850, 420, "영재 방송 출연", int(50 * min(a, 1.1)) or 1, (255, 225, 120))
    return chrome(im)

def s3(t, dur):  # 영유 등록: 통장 89만→14만, 영어 이름 COMMENT
    im = S["bg_gate"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s3"]
    put(im, "cap", 540, 230, 0.7 + 0.03 * math.sin(t * 4)); d = ImageDraw.Draw(im)
    if t < sp * 0.55:
        a = ease((t - 0.05) / 0.35); label(d, 560 + (1 - a) * 40, "반 달 75만 원", 104)
        put(im, kid_key(t, "o", 0.4), 540, 900, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        d = bank(im, t, 0.5, 890000, 140000, cy=1260)
    else:
        t2 = t - sp * 0.55
        put(im, kid_key(t, "proud", 0.8), 540, 880, 1.05 * breathe(t)); d = ImageDraw.Draw(im)
        k = back(t2 / 0.4)
        if k > 0:  # 이름표
            sz = int(78 * min(k, 1.1)) or 1; s = "COMMENT"; w = d.textlength(s, font=V1.F(sz))
            d.rounded_rectangle((540 - w / 2 - 40, 540 - sz, 540 + w / 2 + 40, 540 + sz), radius=22, fill=WHT, outline=NAVY, width=9)
            d.rectangle((540 - w / 2 - 40, 540 - sz, 540 + w / 2 + 40, 540 - sz + 26), fill=NAVY)
            txt(d, 540, 548, s, sz, NAVY)
        if t2 > 0.9:
            b = back((t2 - 0.9) / 0.35); pill(d, 540, 1260, "본인이 골랐습니다", int(56 * min(b, 1.1)) or 1, YEL)
    return chrome(im)

def s4(t, dur):  # 수업: What's your name? → Like! Subscribe!
    im = S["bg_kinder"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    txt(d, 540, 340, "What's your name?", 84, WHT)
    for i, x in enumerate((140, 940)):  # 다른 아이들(뒷모습)
        col = (255, 175, 140) if i else (180, 160, 230)
        d.ellipse((x - 70, 900, x + 70, 1040), fill=(255, 220, 200)); d.rounded_rectangle((x - 90, 1020, x + 90, 1200), radius=70, fill=col)
        if t > sp * 0.45:
            b = 10 * abs(math.sin(t * 5 + i)); txt(d, x, 840 - b, "?", 100, (255, 95, 110), stroke=7, sfill=WHT)
    a = ease((t - 0.05) / 0.35); label(d, 640 + (1 - a) * 40, "보름 동안 배운 영어", 92)
    half = sp * 0.42
    if t < half:
        put(im, kid_fist(t), 540, 960, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        if t > 0.5:
            b = back((t - 0.5) / 0.3); bubble_r(d, 540, 760, "Like!", int(90 * min(b, 1.1)) or 1, (560, 820))
    else:
        put(im, kid_point(t), 540, 960, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        b = back((t - half) / 0.3); bubble_r(d, 540, 760, "Subscribe!", int(90 * min(b, 1.1)) or 1, (560, 820))
    if t > sp * 0.7:
        k = back((t - sp * 0.7) / 0.35)
        if k > 0: pill(d, 540, 1300, "그게 다입니다", int(60 * min(k, 1.1)) or 1, WHT)
    return chrome(im)

def s5(t, dur):  # 문제는 방치, PD가 구독 → 판정 → 출연료 손해
    im = S["bg_studio"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s5"]
    # 문제판(뒤에 방치)
    d.rounded_rectangle((70, 380, 430, 700), radius=20, fill=(250, 250, 245), outline=INK, width=6)
    txt(d, 250, 430, "영재 문제 1", 44, NAVY); txt(d, 250, 540, "3 + 4 = ?", 64, INK)
    if t > 0.3:
        k = back((t - 0.3) / 0.3); stamp(im, 330, 640, k, ["0점"], 10, 170); d = ImageDraw.Draw(im)
    put(im, kid_point(t), 340, 920, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
    tp = sp * 0.25
    put(im, pd_key(t, "happy" if t > tp + 0.5 else "o"), 800, 820, 0.7); d = ImageDraw.Draw(im)
    ph = "phone_on" if t > tp + 0.4 else "phone"
    put(im, ph, 640, 960 - 20 * ease((t - tp) / 0.3), 0.8); d = ImageDraw.Draw(im)
    if tp < t < tp + 0.6:
        r = 30 + 90 * ((t - tp) / 0.6); d.ellipse((640 - r, 1010 - r, 640 + r, 1010 + r), outline=YEL, width=8)
    jt = sp * 0.48
    if t > jt:  # 판정 띠
        k = back((t - jt) / 0.35)
        if k > 0:
            sz = int(100 * min(k, 1.1)) or 1; s = "댓글 유도 영재"; w = d.textlength(s, font=V1.F(sz))
            d.rounded_rectangle((540 - w / 2 - 50, 230 - sz * 0.8, 540 + w / 2 + 50, 230 + sz * 0.8), radius=30, fill=RED, outline=INK, width=8)
            txt(d, 540, 234, s, sz, WHT, stroke=6)
            if k > 0.9: txt(d, 540, 110, "판정", 60, YEL, stroke=6)
    et = sp * 0.68
    if t > et:  # 출연료 → 손해
        k = back((t - et) / 0.35)
        put(im, "env", 300, 1270, min(k, 1.1)); d = ImageDraw.Draw(im)
        if k > 0.9: pill(d, 640, 1270, "10만 원", 64, YEL)
        if t > et + 0.7:
            stamp(im, 880, 1250, back((t - et - 0.7) / 0.3), ["손해"], -14, 220)
    return chrome(im)

OPTS = (("formula", "분유 광고", (90, 150, 235), "모델"), ("cap", "영재학원", (150, 100, 220), "대치동"), ("sand", "놀이터 사장", (240, 150, 60), "다 거절"))
OX = (190, 540, 890)
def vote_cards(im, t, cy=1250):
    d = ImageDraw.Draw(im)
    for i, (key, name, col, sub) in enumerate(OPTS):
        x = OX[i]; k = back((t - 0.4 - i * 0.18) / 0.4)
        if k <= 0: continue
        pul = 1 + 0.035 * math.sin(t * 5 + i * 1.4); w2, h2 = 165 * k * pul, 185 * k * pul
        d.rounded_rectangle((x - w2 + 6, cy - h2 + 10, x + w2 + 6, cy + h2 + 10), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy + h2), radius=34, fill=WHT, outline=INK, width=6)
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy - h2 + 70 * k), radius=34, fill=col, outline=INK, width=6)
        if k > 0.9:
            txt(d, x, cy - h2 + 38, f"{i + 1}번", 48, WHT, stroke=4)
            put(im, key, x, cy + 20, 0.66 if key == "cap" else 0.72); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 50, name, 44, INK)
            if sub: txt(d, x, cy - h2 + 102, sub, 36, col)
    return d

def s6(t, dur):  # 네 번째 갈림길 → 댓글 안 달면 또 손짓
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s6"]
    sw = sp * 0.55; last = sp * 0.78
    if t < sw:
        put(im, kid_key(t, "proud", 0.2), 540, 520, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "섭외 들어옴", 110)
        if t > 0.9:
            b = 16 * abs(math.sin((t - 0.9) * 6)); txt(d, 800, 380 - b, "?", 150, (255, 95, 110), stroke=9, sfill=WHT)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
        if t < last:
            put(im, kid_key(t, "happy", 0.7), 540, 520, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        else:  # 첫 장면과 이어지게: 아래(댓글창)를 콕콕
            jab = 14 * abs(math.sin((t - last) * 9))
            put(im, kid_point(t), 540, 520 + jab, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
            k = back((t - last) / 0.35)
            if k > 0.9:
                pill(d, 540, 290, "댓글 달아 주세요", 50, WHT)
                arrow_down(d, 860, 640 + jab * 1.6, 0.9)
    vote_cards(im, t)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6)
if __name__ == "__main__":
    V1.main()
