# 인생 댓글로 정함 2화 — 돌잡이 연필 → 벽 낙서 → 벽지값 → 세 살 → 어린이집 갈림길 (2026.10.24)
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep2.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d2.py(tod_* dad* mom* pencil) + life_3d3.py(kid_* dad_cry mom_wow cap bag bowl)
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
SPR3 = sys.argv.pop(2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import anim_life_ep1_v2 as V2
from anim_life_ep1 import W, H, YEL, WHT, ease, back, blink

S = V2.S
put, txt, label, pill, bubble, breathe = V2.put, V2.txt, V2.label, V2.pill, V2.bubble, V2.breathe
INK = V2.INK
RED = (235, 70, 80); BLUE = (90, 160, 235)
PEN = ImageFont.truetype(os.path.join(V1.ROOT, "assets/fonts/NanumPenScript-Regular.ttf"), 120)

def with_shadow(im, k=0.1):
    pad = int(im.height * k); out = Image.new("RGBA", (im.width + 40, im.height + pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    cx, cy = out.width / 2, im.height + pad * 0.25
    d.ellipse((cx - im.width * 0.38, cy - pad * 0.28, cx + im.width * 0.38, cy + pad * 0.28), fill=(110, 60, 30, 85))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(pad * 0.25)))
    out.alpha_composite(im, (20, 0)); return out

def load(key, file, width, shadow=True):
    im = Image.open(os.path.join(SPR3, file)).convert("RGBA")
    im = im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)
    S[key] = with_shadow(im) if shadow else im

for k in ("tod_o", "tod_blink", "tod_proud"): load(k, f"{k}.png", 400)
for k in ("dad_cry", "mom_wow", "mom_blink"): load(k, f"{k}.png", 380)
for k in ("kid_happy", "kid_blink", "kid_proud", "kid_o"): load(k, f"{k}.png", 360)
load("pencil", "pencil.png", 220, False)
load("cap", "cap.png", 200, False); load("bag", "bag.png", 170, False); load("bowl", "bowl.png", 200, False)
for k in ("bg_living", "bg_dol", "bg_vote"):
    S[k] = S[k].filter(ImageFilter.GaussianBlur(3))

def kid_key(t, expr="happy", seed=0): return "kid_blink" if blink(t, seed) < 1 else f"kid_{expr}"

def heart(d, cx, cy, r, fill=RED):
    d.ellipse((cx - r, cy - r * 0.7, cx, cy + r * 0.3), fill=fill); d.ellipse((cx, cy - r * 0.7, cx + r, cy + r * 0.3), fill=fill)
    d.polygon([(cx - r * 0.97, cy - 0.05 * r), (cx + r * 0.97, cy - 0.05 * r), (cx, cy + r * 1.05)], fill=fill)

def tod_pencil(im, t, cx, cy, sc=1.0, wave=True):
    """돌복 아이 + 오른손에 연필(번쩍 흔들기)"""
    put(im, "tod_proud" if blink(t, 0.3) >= 1 else "tod_blink", cx, cy, sc * breathe(t))
    a = 25 * math.sin(t * 7) if wave else 0
    put(im, "pencil", cx + 120 * sc, cy + 95 * sc, sc * 0.9, 50 + a)

# ---------- 대본(장면 길이 계산용, 실제 목소리는 drafts/life.json) ----------
V1.SCENES = [
    dict(id="s1", say="어제 댓글 일등, 좋아요 두 개. 연필 잡았습니다. 두 개면 일등 돼요. 이 채널 그래요.",
         sub="어제 댓글 1등, ♥2개. 연필 잡았습니다. 2개면 1등 돼요. 이 채널 그래요.", sfx=[("pop", 0.4)]),
    dict(id="s2", say="아빠는 울었고요. 엄마는 의대 얘기를 꺼냈습니다. 돌잔치에서요.", sfx=[("ding", 2.0)]),
    dict(id="s3", say="근데 연필, 공부엔 안 썼습니다. 벽에 썼어요. 전셋집 벽에.", sfx=[("shock", 2.2)]),
    dict(id="s4", say="벽지값 삼십만 원. 통장 팔십칠만 원이 오십칠만 원 됐습니다. 그러고 세 살 됐어요.",
         sub="벽지값 30만 원. 통장 87만 원이 57만 원 됐습니다. 그러고 3살 됐어요.", sfx=[("thud", 2.6)]),
    dict(id="s5", say="두 번째 갈림길, 어디 보낼래요? 영어유치원, 동네 어린이집, 엄마 분식집.", sfx=[("question", 1.6)]),
    dict(id="s6", say="참고로 영어유치원은 한 달 백오십만 원이에요. 통장엔 오십칠만 원. 댓글 일등대로 갑니다. 안 정하면 아무 데나 갑니다.",
         sub="참고로 영어유치원은 한 달 150만 원이에요. 통장엔 57만 원. 댓글 1등대로 갑니다. 안 정하면 아무 데나 갑니다.", sfx=[("tada", 4.6)]),
]
V1.HOOK = ["인생 댓글로 정함 2화", "연필 잡더니 '벽'에 씀"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}  # 말하는 길이(여유 제외)

# ---------- 장면 ----------
def s1(t, dur):  # 어제 댓글 1등 카드
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im)
    a = ease(t / 0.35); label(d, 110 - (1 - a) * 50, "어제 댓글 1등", 108)
    k = back((t - 0.25) / 0.45)
    if k > 0:
        card = Image.new("RGBA", (920, 400), (0, 0, 0, 0)); c = ImageDraw.Draw(card)
        c.rounded_rectangle((10, 18, 910, 392), radius=40, fill=(200, 150, 110))
        c.rounded_rectangle((0, 0, 900, 374), radius=40, fill=WHT, outline=INK, width=6)
        txt(c, 50, 70, "@DOL_haru", 50, (140, 130, 125), anchor="lm")
        txt(c, 50, 180, "1번잡고 공부잘해.", 84, INK, anchor="lm")
        heart(c, 80, 290, 30); txt(c, 130, 292, "2", 64, RED, anchor="lm")
        txt(c, 860, 292, "답글", 44, (160, 150, 145), anchor="rm")
        c.rounded_rectangle((700, -2, 900, 70), radius=30, fill=YEL, outline=INK, width=5)
        txt(c, 800, 35, "1등", 50, INK)
        card = card.resize((max(1, int(920 * k)), max(1, int(400 * k))), Image.LANCZOS)
        im.alpha_composite(card, (int(540 - card.width / 2), int(420 - card.height / 2))); d = ImageDraw.Draw(im)
    if t > 1.2:  # 좋아요 2개 강조(작게 콕콕)
        p = 1 + 0.15 * abs(math.sin((t - 1.2) * 5))
        heart(d, 160, 510, 30 * p)
    k2 = back((t - 1.6) / 0.45)
    if k2 > 0:
        tod_pencil(im, t, 540, 1260, 0.62 * k2); d = ImageDraw.Draw(im)
        if t > 2.2: pill(d, 830, 1150, "연필 당첨", 46, YEL)
    return im

def s2(t, dur):  # 아빠 울고 엄마 의대
    im = S["bg_dol"].copy(); d = ImageDraw.Draw(im)
    put(im, "dad_cry", 230, 420, 0.8 * (1 + 0.02 * math.sin(t * 14)))
    d = ImageDraw.Draw(im)
    for i in range(6):  # 눈물 방울
        ph = (t * 1.3 + i / 6) % 1; x = 230 + (-70 if i % 2 else 70) + (i - 3) * 4; y = 330 + ph * 260
        d.ellipse((x - 9, y - 13, x + 9, y + 13), fill=(140, 200, 255))
    at = SPEAK["s2"] * 0.32
    k = back((t - at) / 0.4)
    if k > 0:
        key = "mom_blink" if blink(t, 1.7) < 1 else "mom_wow"
        put(im, key, 850, 420, 0.8 * k * breathe(t)); d = ImageDraw.Draw(im)
        for i in range(4):  # 반짝
            a = (t * 1.6 + i * 0.25) % 1; x = 850 + 190 * math.cos(i * 1.6 + 0.3); y = 330 + 170 * math.sin(i * 1.6 + 0.3)
            r = 14 * math.sin(a * math.pi); d.polygon([(x, y - r * 2), (x + r, y), (x, y + r * 2), (x - r, y)], fill=(255, 205, 80))
        if t > at + 0.4: bubble(d, 760, 120, "의대 가자", 64)
    tod_pencil(im, t, 540, 560, 0.55, wave=True); d = ImageDraw.Draw(im)
    a = ease((t - 0.3) / 0.4)
    if a > 0:
        label(d, 1230 + (1 - a) * 60, "기대치: 폭등", 110)
        pill(d, W / 2, 1375, "돌잔치에서 생긴 일", 50)
    return im

# 낙서 벽: 선이 하나씩 그려진다
R = random.Random(7)
def _scribbles():
    out = []
    for i in range(14):
        cx, cy = R.randrange(80, 1000), R.randrange(60, 700)
        kind = i % 4; pts = []
        if kind == 0:  # 동글동글 나선
            for j in range(60):
                a = j * 0.35; r = 10 + j * 1.6; pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.8))
        elif kind == 1:  # 지그재그
            for j in range(14): pts.append((cx - 130 + j * 20, cy + (40 if j % 2 else -40)))
        elif kind == 2:  # 해
            pts = [(cx + 55 * math.cos(j / 30 * 2 * math.pi), cy + 55 * math.sin(j / 30 * 2 * math.pi)) for j in range(31)]
        else:  # 졸라맨 비슷한 낙서
            pts = [(cx, cy - 60), (cx, cy + 40), (cx - 40, cy + 100), (cx, cy + 40), (cx + 40, cy + 100), (cx, cy + 40), (cx, cy), (cx - 50, cy - 10), (cx + 50, cy - 10)]
        out.append(pts)
    return out
SCRIB = _scribbles()
WORDS = [("엄마", 170, 560, -8), ("아빠", 900, 470, 6), ("댓글", 560, 330, -4)]

def wall_doodle(t, prog):
    im = S["bg_living"].copy(); d = ImageDraw.Draw(im)
    n = len(SCRIB)
    for i, pts in enumerate(SCRIB):
        p = (prog * (n + 2) - i)
        if p <= 0: continue
        m = max(2, int(len(pts) * min(p, 1)))
        d.line(pts[:m], fill=(70, 70, 80), width=7, joint="curve")
    for i, (w, x, y, r) in enumerate(WORDS):  # 글씨는 흰 테두리로 읽히게
        if prog * (n + 2) > 4 + i * 4:
            lay = Image.new("RGBA", (420, 220), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((210, 110), w, font=PEN, fill=(60, 60, 75), anchor="mm", stroke_width=6, stroke_fill=(240, 250, 244))
            lay = lay.rotate(r, resample=Image.BICUBIC); im.alpha_composite(lay, (x - 210, y - 110)); d = ImageDraw.Draw(im)
    return im

def s3(t, dur):
    sp = SPEAK["s3"]; prog = ease(t / (sp * 0.85))
    im = wall_doodle(t, prog); d = ImageDraw.Draw(im)
    x = 540 + 260 * math.sin(t * 1.4)
    put(im, "tod_proud" if blink(t) >= 1 else "tod_blink", x, 1250, 0.68 * breathe(t))
    put(im, "pencil", x + 150, 1150 + 25 * math.sin(t * 9), 0.8, 40 + 30 * math.sin(t * 9)); d = ImageDraw.Draw(im)
    hit = sp * 0.45
    if t > hit:
        a = back((t - hit) / 0.35)
        if a > 0:
            j = 6 * math.sin(t * 40) if t < hit + 0.6 else 0
            label(d, 680 + j, "여기 전셋집이에요", int(96 * min(a, 1.1)), (255, 110, 110))
    return im

def receipt(t):
    w, h = 520, 300
    r = Image.new("RGBA", (w + 20, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    pts = [(10, 10), (w + 10, 10), (w + 10, h)]
    for i in range(14):
        x = w + 10 - (i + 0.5) * w / 14; pts.append((x, h + (18 if i % 2 == 0 else 0)))
    pts += [(10, h)]
    d.polygon(pts, fill=WHT, outline=INK)
    txt(d, w / 2 + 10, 65, "영수증", 56, INK)
    d.line([(40, 110), (w - 20, 110)], fill=(200, 190, 180), width=4)
    txt(d, 40, 170, "벽지 다시 바름", 46, INK, anchor="lm")
    txt(d, w - 20, 245, "300,000원", 64, RED, anchor="rm")
    return r.rotate(-5, resample=Image.BICUBIC, expand=True)

def s4(t, dur):
    im = S["bg_living"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    k = back(t / 0.4)
    if k > 0:
        rc = receipt(t); rc = rc.resize((max(1, int(rc.width * k)), max(1, int(rc.height * k))))
        im.alpha_composite(rc, (int(300 - rc.width / 2), int(170 - rc.height / 2)))
    # 통장 카드
    a = back((t - 0.5) / 0.4)
    if a > 0:
        bank = S["card_bank"] if a >= 0.999 else S["card_bank"].resize((max(1, int(760 * a)), max(1, int(330 * a))))
        im.alpha_composite(bank, (int(560 - bank.width / 2), int(520 - bank.height / 2))); d = ImageDraw.Draw(im)
        if a > 0.9:
            drop = sp * 0.3; p = ease((t - drop) / 0.5); won = 870000 - int(300000 * p / 1000) * 1000
            shake = 8 * math.sin(t * 50) if drop < t < drop + 0.5 else 0
            txt(d, 560, 425, "통장 잔고", 54, WHT, stroke=5)
            txt(d, 560 + shake, 560, f"{won:,}원", 118, YEL if p < 1 else (255, 140, 140), stroke=8)
            if t > drop:
                b = back((t - drop) / 0.3); txt(d, 900, 360, "-30만", int(80 * min(b, 1.15)), RED, stroke=7, sfill=WHT)
    # 세 살: 펑 하고 바뀜
    grow = sp * 0.72
    if t < grow:
        put(im, "tod_o" if blink(t) >= 1 else "tod_blink", 540, 1270, 0.62 * breathe(t))
    else:
        g = back((t - grow) / 0.4)
        if t < grow + 0.35:
            d = ImageDraw.Draw(im)
            for i in range(10):
                a2 = i / 10 * 2 * math.pi; rr = 60 + 260 * (t - grow); x, y = 540 + rr * math.cos(a2), 1270 + rr * math.sin(a2)
                d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(255, 255, 255))
        put(im, kid_key(t, "happy"), 540, 1260, 0.78 * g * breathe(t)); d = ImageDraw.Draw(im)
        if g > 0.8:
            pill(d, 810, 1130, "3살", 70, YEL)
    return im

OPTS = (("cap", "영어유치원", (90, 150, 235)), ("bag", "동네 어린이집", (80, 180, 110)), ("bowl", "엄마 분식집", (235, 100, 120)))
OX = (190, 540, 890)

def vote_cards(im, t, cy=1250, scale=1.0, hot=-1):
    d = ImageDraw.Draw(im)
    for i, (key, name, col) in enumerate(OPTS):
        x = OX[i]; k = back((t - 0.2 - i * 0.18) / 0.4) * scale
        if k <= 0: continue
        pul = 1 + 0.035 * math.sin(t * 5 + i * 1.4); w2, h2 = 165 * k * pul, 180 * k * pul
        d.rounded_rectangle((x - w2 + 6, cy - h2 + 10, x + w2 + 6, cy + h2 + 10), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy + h2), radius=34, fill=WHT, outline=INK, width=6)
        d.rounded_rectangle((x - w2, cy - h2, x + w2, cy - h2 + 70 * k), radius=34, fill=col, outline=INK, width=6)
        if k > 0.9 * scale:
            txt(d, x, cy - h2 + 38, f"{i + 1}번", 48, WHT, stroke=4)
            put(im, key, x, cy + 15, 0.85 * scale); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 45, name, int(46 * scale), INK)
    return d

def s5(t, dur):
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im)
    put(im, kid_key(t, "o", 1.1), 540, 330, 0.9 * breathe(t)); d = ImageDraw.Draw(im)
    a = ease((t - 0.1) / 0.4)
    label(d, 655 + (1 - a) * 40, "두 번째 갈림길", 104)
    if t > 1.4:
        b = 16 * abs(math.sin((t - 1.4) * 6)); txt(d, 800, 140 - b, "?", 150, (255, 95, 110), stroke=9)
    vote_cards(im, t)
    return im

def s6(t, dur):
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s6"]
    sw = sp * 0.5  # 앞 절반: 원비 vs 통장 / 뒤 절반: 댓글 1등대로
    if t < sw:
        k = back(t / 0.4)
        put(im, "cap", 270, 260, 1.2 * k); d = ImageDraw.Draw(im)
        if k > 0.9:
            pill(d, 270, 470, "영어유치원 한 달", 44)
            txt(d, 270, 600, "150만", 120, RED, stroke=8, sfill=WHT)
        k2 = back((t - sp * 0.28) / 0.4)
        if k2 > 0:
            bank = S["card_bank"].resize((max(1, int(420 * k2)), max(1, int(182 * k2))))
            im.alpha_composite(bank, (int(810 - bank.width / 2), int(300 - bank.height / 2))); d = ImageDraw.Draw(im)
            if k2 > 0.9:
                txt(d, 810, 248, "통장", 40, WHT, stroke=4)
                txt(d, 810, 330, "57만", 80, YEL, stroke=6)
                put(im, kid_key(t, "o", 0.5), 810, 560, 0.5 * breathe(t)); d = ImageDraw.Draw(im)
                txt(d, 540, 330, "vs", 80, INK, stroke=6, sfill=WHT)
    else:
        put(im, kid_key(t, "proud", 0.2), 540, 330, 0.9 * breathe(t)); d = ImageDraw.Draw(im)
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 655, "댓글 1등대로 갑니다", int(96 * min(a, 1.1)))
    vote_cards(im, t)
    return im

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6)
if __name__ == "__main__":
    V1.main()
