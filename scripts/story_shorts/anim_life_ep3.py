# 인생 댓글로 정함 3화 — 세 살이 엄마 떡볶이에 '솔루션' 들어감 (2026.10.25)
# 콜드 오픈(정색) → 설정 한 줄 + 1등 댓글 탓 → 냉장고 점검(분유만) → 메뉴 다 지우고 '안 매운 떡볶이' → 줄·통장 → 세 번째 갈림길
# 사용: LIFE_HOLD=3 python3 scripts/story_shorts/anim_life_ep3.py <출력폴더> <3D스프라이트폴더>
#   3D 스프라이트: life_3d4.py(kida_* kidc_* mom_sad) + life_3d3.py(mom_wow cap bowl) + life_3d2.py(mom_blink)
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
SPR3 = sys.argv.pop(2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import anim_life_ep1_v2 as V2
import life_sprites as L
from anim_life_ep1 import W, H, YEL, WHT, ease, back, blink

S = V2.S
put, txt, label, pill, breathe = V2.put, V2.txt, V2.label, V2.pill, V2.breathe
INK = V2.INK
RED = (235, 70, 80); GREEN = (60, 175, 95); CRAY = (225, 55, 65)
PEN = lambda s: ImageFont.truetype(os.path.join(V1.ROOT, "assets/fonts/NanumPenScript-Regular.ttf"), s)
EP = "3화"

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

for k in ("kida_happy", "kida_blink", "kida_proud", "kida_o", "kida_frown"): load(k, f"{k}.png", 360)
_kw = Image.open(os.path.join(SPR3, "kida_proud.png")).width
for k in ("kidc_proud", "kidc_blink"):  # 같은 몸 크기(오른쪽으로 늘어난 크레용만큼 넓음)
    load(k, f"{k}.png", 360 * Image.open(os.path.join(SPR3, f"{k}.png")).width / _kw)
CRAY_DX = (S["kidc_proud"].width - S["kida_proud"].width) / 2
for k in ("mom_wow", "mom_blink", "mom_sad"): load(k, f"{k}.png", 380)
load("cap", "cap.png", 200, False); load("bowl", "bowl.png", 230, False)

# ---------- 분식집 배경(SVG) ----------
def bg_bunsik():
    b = f'<defs>{L._wall("#fff1dc", "#ffe1c2")}</defs><rect width="1080" height="1490" fill="url(#wall)"/>'
    for i, x in enumerate(range(0, 1080, 90)):  # 빨강·흰 줄무늬 차양
        b += f'<rect x="{x}" y="0" width="90" height="120" fill="{"#f0525c" if i % 2 == 0 else "#ffffff"}"/>'
    b += '<path d="M0 120 ' + "".join(f"q45 50 90 0 " for _ in range(12)) + 'v-6 H0Z" fill="#f0525c"/>'
    for y in range(700, 1130, 72):  # 흰 타일
        for x in range(0 + (y // 72 % 2) * 36, 1080, 72):
            b += f'<rect x="{x+2}" y="{y+2}" width="68" height="68" rx="6" fill="#ffffff" stroke="#eadfd2" stroke-width="3"/>'
    for x in (200, 880):  # 전등
        b += f'<path d="M{x} 120 v90" stroke="#5b3a29" stroke-width="5"/><path d="M{x-70} 260 Q{x} 160 {x+70} 260Z" fill="#ffd166" stroke="#5b3a29" stroke-width="5"/><ellipse cx="{x}" cy="268" rx="40" ry="12" fill="#fff6c8"/>'
    b += '<rect y="1130" width="1080" height="360" fill="#d9a678"/><rect y="1130" width="1080" height="14" fill="#c48e5e"/>'
    return L.svg(1080, 1490, b)

def svg_png(key, s):
    os.makedirs(os.path.join(V1.OUT, "_sprites"), exist_ok=True)
    p = os.path.join(V1.OUT, "_sprites", key + ".svg"); open(p, "w", encoding="utf-8").write(s)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-width", "1080", "-height", "1490", "-i", p, "-frames:v", "1", p[:-4] + ".png"], check=True)
    S[key] = Image.open(p[:-4] + ".png").convert("RGBA")
svg_png("bg_bunsik", bg_bunsik())
S["bg_bunsik_b"] = S["bg_bunsik"].filter(ImageFilter.GaussianBlur(3))
S["bg_vote"] = S["bg_vote"].filter(ImageFilter.GaussianBlur(3))

# ---------- 코드로 그린 소품 ----------
def icon_cam():
    im = Image.new("RGBA", (230, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 30, 160, 150), radius=26, fill=(70, 75, 90), outline=INK, width=6)
    d.polygon([(160, 70), (220, 40), (220, 140), (160, 110)], fill=(95, 100, 118), outline=INK, width=6)
    d.ellipse((45, 50, 125, 130), fill=(40, 44, 55), outline=INK, width=5); d.ellipse((65, 70, 90, 95), fill=(150, 200, 255))
    d.ellipse((128, 40, 150, 62), fill=(240, 60, 70)); return im

def icon_ladle():
    im = Image.new("RGBA", (220, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(195, 15), (95, 150)], fill=(150, 95, 55), width=22); d.line([(195, 15), (95, 150)], fill=(190, 130, 80), width=12)
    d.ellipse((20, 120, 150, 215), fill=(205, 210, 220), outline=INK, width=6); d.ellipse((38, 130, 132, 170), fill=(235, 90, 70))
    return im

def candy(r=34):
    im = Image.new("RGBA", (r * 5, r * 2 + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx, cy = r * 2.5, r + 5
    for s in (-1, 1):
        d.polygon([(cx + s * r * 0.8, cy), (cx + s * r * 2.3, cy - r * 0.8), (cx + s * r * 2.3, cy + r * 0.8)], fill=(255, 150, 190), outline=INK)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 110, 160), outline=INK, width=4)
    d.arc((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), 0, 270, fill=WHT, width=6); return im
S["cam"] = icon_cam(); S["ladle"] = icon_ladle(); S["candy"] = candy()

# ---------- 공통 ----------
def chrome(im):
    """상시 칩(댓글 1등대로 사는 아기) + 구석의 작은 화수"""
    d = ImageDraw.Draw(im)
    s = "댓글 1등대로 사는 아기"; w = d.textlength(s, font=V1.F(36))
    d.rounded_rectangle((24, 22, 24 + w + 44, 84), radius=31, fill=(40, 32, 30, 255))
    txt(d, 24 + 22 + w / 2, 54, s, 36, YEL)
    w2 = d.textlength(EP, font=V1.F(34))
    d.rounded_rectangle((W - 24 - w2 - 36, 24, W - 24, 82), radius=29, fill=WHT, outline=INK, width=4)
    txt(d, W - 24 - 18 - w2 / 2, 54, EP, 34, INK)
    return im

def kid_key(t, expr="happy", seed=0): return "kida_blink" if blink(t, seed) < 1 else f"kida_{expr}"

def kid_crayon(im, t, cx, cy, sc=1.0, wave=True):
    key = "kidc_proud" if blink(t, 0.3) >= 1 else "kidc_blink"
    put(im, key, cx + CRAY_DX * sc, cy, sc * breathe(t), 7 * math.sin(t * 6) if wave else 0)

def bubble_r(d, x, y, s, size, tip):
    w = d.textlength(s, font=V1.F(size)); pad = size * 0.5
    box = (x - w / 2 - pad, y - size * 0.8, x + w / 2 + pad, y + size * 0.8)
    bx = min(max(tip[0], box[0] + 60), box[2] - 60)
    d.polygon([(bx - 28, box[3] - 6), (bx + 28, box[3] - 6), tip], fill=WHT, outline=INK, width=5)
    d.rounded_rectangle(box, radius=int(size * 0.7), fill=WHT, outline=INK, width=6)
    d.line([(bx - 24, box[3] - 3), (bx + 24, box[3] - 3)], fill=WHT, width=9)
    txt(d, x, y + 3, s, size, (230, 70, 80))

def sweat(d, x, y, t, k=0):
    ph = (t * 1.6 + k) % 1; yy = y + ph * 60
    d.polygon([(x, yy - 22), (x - 13, yy + 4), (x + 13, yy + 4)], fill=(140, 200, 255)); d.ellipse((x - 13, yy - 8, x + 13, yy + 16), fill=(140, 200, 255))

# ---------- 대본(장면 길이 계산용, 실제 목소리는 drafts/life.json) ----------
V1.SCENES = [
    dict(id="s1", say="세 살이 엄마 떡볶이를 혼내고 있습니다.", sfx=[("thud", 1.0)]),
    dict(id="s2", say="얘는 댓글 일등대로 사는 아기, 김댓글. 댓글 일등이 제이의 백종원 되래서, 됐습니다. 누군지는 모릅니다.",
         sub="댓글 1등대로 사는 아기, 김댓글. 댓글 1등이 '제2의 백종원' 되래서, 됐습니다. 누군지는 모릅니다.", sfx=[("ding", 0.5)]),
    dict(id="s3", say="냉장고 점검 들어갑니다. 분유밖에 없습니다. 본인 거예요.", sfx=[("shock", 1.6)]),
    dict(id="s4", say="솔루션은 하나. 메뉴 다 지우고, 안 매운 떡볶이. 세 살 입맛이에요.", sfx=[("boing", 2.3)]),
    dict(id="s5", say="동네 애들이 줄 섰습니다. 통장 오십칠만 원이 팔십구만 원. 솔루션 비용은 사탕 한 개.",
         sub="동네 애들이 줄 섰습니다. 통장 57만 원이 89만 원. 솔루션 비용은 사탕 1개.", sfx=[("ding", 3.0)]),
    dict(id="s6", say="세 살 사장님, 다음은요? 키즈 유튜버, 분식집 후계자, 아니면 번 돈으로 영어유치원 반 달. 댓글 일등대로 갑니다. 안 정하면 아무거나 돼요. 엄마는 아직 혼나는 중.",
         sub="세 살 사장님, 다음은요? 키즈 유튜버, 분식집 후계자, 아니면 번 돈으로 영어유치원 반 달. 댓글 1등대로 갑니다. 안 정하면 아무거나 돼요. 엄마는 아직 혼나는 중.", sfx=[("question", 0.6)]),
]
V1.HOOK = ["세 살이 엄마 떡볶이에", "'솔루션' 들어감"]
for sc in V1.SCENES:
    sc["dur"] = round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
SPEAK = {sc["id"]: round(V1.syl(sc["say"]) / 6.3 + 0.6, 2) for sc in V1.SCENES}

# ---------- 장면 ----------
def s1(t, dur):  # 콜드 오픈: 한 입 먹고 정색, 그릇 밀어냄
    im = S["bg_bunsik_b"].copy(); d = ImageDraw.Draw(im)
    taste = 0.7
    # 엄마가 옆에서 들어옴(놀람)
    km = ease((t - 0.9) / 0.35)
    if km > 0:
        key = "mom_blink" if blink(t, 1.3) < 1 else "mom_wow"
        put(im, key, 880 + (1 - km) * 330, 690, 0.78 * (1 + 0.015 * math.sin(t * 16)))
        d = ImageDraw.Draw(im); sweat(d, 760, 470, t); sweat(d, 1000, 500, t, 0.5)
    expr = "happy" if t < taste else "frown"
    key = "kida_frown" if expr == "frown" else kid_key(t, "happy")
    put(im, key, 400, 760, 1.05 * breathe(t))
    im.alpha_composite(S["table"], (20, 930)); d = ImageDraw.Draw(im)
    push = ease((t - taste - 0.15) / 0.3)
    bx = 450 + 330 * push
    put(im, "bowl", bx, 930, 1.0); d = ImageDraw.Draw(im)
    if t < taste:
        a = ease(t / 0.3); txt(d, 600, 560, "냠", int(80 * a) or 1, WHT, stroke=7)
    if t > taste + 0.15:
        jx = 6 * math.sin(t * 45) if t < taste + 0.6 else 0
        bubble_r(d, 400 + jx, 380, "이게 뭐예요?", 74, (400, 540))
        if push > 0.9:
            for i in range(3):  # 밀어낸 자국
                d.line([(bx - 170 - i * 30, 905 + i * 18), (bx - 125 - i * 30, 905 + i * 18)], fill=INK, width=6)
    return chrome(im)

def s2(t, dur):  # 설정 한 줄 + 1등 댓글 탓
    im = S["bg_bunsik_b"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s2"]
    who = sp * 0.78
    key = ("kida_o" if blink(t, 2) >= 1 else "kida_blink") if t > who else ("kida_frown" if blink(t, 0.4) >= 1 else "kida_blink")
    put(im, key, 540, 450, 1.25 * breathe(t)); d = ImageDraw.Draw(im)
    if t > who:
        b = 16 * abs(math.sin((t - who) * 6)); txt(d, 820, 220 - b, "?", 160, (255, 95, 110), stroke=9, sfill=WHT)
    k = back((t - 0.15) / 0.4)
    if k > 0:
        s = "댓글 1등대로 사는 아기"; size = int(70 * min(k, 1.1))
        w = d.textlength(s, font=V1.F(size))
        d.rounded_rectangle((540 - w / 2 - 36, 1110 - size * 0.8, 540 + w / 2 + 36, 1110 + size * 0.8), radius=50, fill=YEL, outline=INK, width=6)
        txt(d, 540, 1112, s, size, INK)
    kc = ease((t - sp * 0.4) / 0.4)
    if kc > 0:  # 1등 댓글(다시 그린 모양, 좋아요 숫자 없음)
        x0 = 100 + (1 - kc) * 900
        d.rounded_rectangle((x0 + 8, 1208, x0 + 888, 1408), radius=34, fill=(200, 150, 110))
        d.rounded_rectangle((x0, 1198, x0 + 880, 1398), radius=34, fill=WHT, outline=INK, width=6)
        txt(d, x0 + 40, 1248, "@singhaarva", 40, (140, 130, 125), anchor="lm")
        txt(d, x0 + 40, 1330, "3 엄분식에서 제2의 백종원 ㄱㄱ", 54, INK, anchor="lm")
        d.rounded_rectangle((x0 + 700, 1176, x0 + 870, 1232), radius=26, fill=YEL, outline=INK, width=5)
        txt(d, x0 + 785, 1205, "1등 댓글", 34, INK)
    if t > sp * 0.62:  # 됐습니다 → 위생모 대신 '솔루션' 완장
        a = back((t - sp * 0.62) / 0.35)
        if a > 0: pill(d, 860, 600, "솔루션 담당", int(46 * min(a, 1.1)) or 1, (255, 225, 120))
    return chrome(im)

def fridge(im, t, opn):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = 110, 300, 630, 1120
    d.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=30, fill=(170, 130, 100))
    d.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=(214, 222, 230), outline=INK, width=7)
    ix0, iy0, ix1, iy1 = x0 + 26, y0 + 26, x1 - 26, y1 - 26
    if opn > 0:
        d.rectangle((ix0, iy0, ix1, iy1), fill=(236, 248, 255))
        for i in range(1, 4):  # 선반
            y = iy0 + i * (iy1 - iy0) / 4; d.line([(ix0, y), (ix1, y)], fill=(170, 195, 215), width=8)
        for r in range(4):
            for c in range(4):
                cx = ix0 + 62 + c * 112; by = iy0 + (r + 1) * (iy1 - iy0) / 4 - 6
                pop = back((t - 0.9 - (r * 4 + c) * 0.035) / 0.3)
                if pop <= 0: continue
                h = 120 * min(pop, 1.1); w = 44
                d.rectangle((cx - w, by - h, cx + w, by), fill=WHT, outline=INK, width=4)
                d.rectangle((cx - w, by - h, cx + w, by - h + 26), fill=(120, 175, 240), outline=INK, width=4)
                if pop > 0.9: txt(d, cx, by - 46, "분유", 30, (90, 140, 210))
        # 문(열리며 얇아짐)
        dw = (ix1 - ix0) / 2 * (1 - opn)
        for s, xe in ((1, x0), (-1, x1)):
            xa, xb = (xe, xe + s * (dw + 26)) if s == 1 else (xe - (dw + 26), xe)
            d.rectangle((min(xa, xb), y0, max(xa, xb), y1), fill=(200, 208, 218), outline=INK, width=6)
        # 냉기
        for i in range(5):
            ph = (t * 0.8 + i * 0.2) % 1; xx = ix0 + 40 + i * 95; yy = iy1 - ph * 200
            d.ellipse((xx - 30, yy - 12, xx + 30, yy + 12), outline=(200, 230, 255), width=4)
    else:
        d.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], fill=INK, width=6)
        for s in (-1, 1):
            hx = (x0 + x1) / 2 + s * 30; d.rounded_rectangle((hx - 9, 600, hx + 9, 760), radius=8, fill=(150, 158, 170), outline=INK, width=3)
    return ImageDraw.Draw(im)

def s3(t, dur):  # 냉장고 점검 → 분유만
    im = S["bg_bunsik_b"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s3"]
    opn = ease((t - 0.55) / 0.35)
    d = fridge(im, t, opn)
    a = ease((t - 0.05) / 0.35); label(d, 205 + (1 - a) * 40, "냉장고 점검", 100)
    mine = sp * 0.68
    key = (kid_key(t, "proud", 0.6) if t > mine else ("kida_o" if blink(t, 0.9) >= 1 else "kida_blink"))
    put(im, key, 850, 900, 0.82 * breathe(t)); d = ImageDraw.Draw(im)
    if t > mine:
        b = back((t - mine) / 0.35); pill(d, 850, 560, "본인 거예요", int(54 * min(b, 1.1)) or 1, YEL)
    return chrome(im)

MENU = [("떡볶이", "4,000"), ("순대", "4,000"), ("튀김", "3,000"), ("김밥", "3,000"), ("라면", "4,500"), ("어묵", "2,000")]
def s4(t, dur):  # 솔루션: 메뉴 다 지우고 '안 매운 떡볶이'
    im = S["bg_bunsik_b"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s4"]
    bx0, by0, bx1, by1 = 70, 150, 1010, 760
    d.rounded_rectangle((bx0 + 10, by0 + 14, bx1 + 10, by1 + 14), radius=30, fill=(170, 130, 100))
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=30, fill=(255, 252, 244), outline=INK, width=7)
    d.rounded_rectangle((bx0, by0, bx1, by0 + 110), radius=30, fill=(240, 82, 92), outline=INK, width=7)
    d.rectangle((bx0 + 4, by0 + 80, bx1 - 4, by0 + 106), fill=(240, 82, 92))
    txt(d, 540, by0 + 58, "메뉴", 66, WHT, stroke=5)
    e0, e1 = sp * 0.15, sp * 0.5  # 지우는 구간
    for i, (nm, pr) in enumerate(MENU):
        cx = 300 if i % 2 == 0 else 780; cy = by0 + 190 + (i // 2) * 160
        txt(d, cx - 170, cy, nm, 62, INK, anchor="lm"); txt(d, cx + 170, cy, pr, 50, (150, 120, 100), anchor="rm")
        p = (t - e0 - i * (e1 - e0) / 6) / ((e1 - e0) / 6)
        if p > 0:
            pts = []
            for j in range(13):
                pts.append((cx - 190 + j * 32, cy + (34 if j % 2 else -34)))
            m = max(2, int(len(pts) * min(p, 1))); d.line(pts[:m], fill=CRAY, width=14, joint="curve")
    w0 = sp * 0.52
    if t > w0:  # 크레용 글씨(지운 메뉴는 흐려짐)
        p = ease((t - w0) / 0.6)
        cov = Image.new("RGBA", (bx1 - bx0 - 20, by1 - by0 - 125), (255, 252, 244, int(225 * min(1, (t - w0) / 0.3))))
        im.alpha_composite(cov, (bx0 + 10, by0 + 115)); d = ImageDraw.Draw(im)
        lay = Image.new("RGBA", (860, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((430, 110), "안 매운 떡볶이", font=PEN(170), fill=CRAY, anchor="mm", stroke_width=8, stroke_fill=WHT)
        lay = lay.crop((0, 0, max(1, int(860 * p)), 220)).rotate(-3, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(lay, (110, 340)); d = ImageDraw.Draw(im)
        if p >= 1:
            s = back((t - w0 - 0.6) / 0.35)
            if s > 0:
                st = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
                sd.ellipse((20, 20, 280, 280), outline=RED, width=14); sd.text((150, 150), "솔루션", font=V1.F(70), fill=RED, anchor="mm")
                st = st.rotate(14, resample=Image.BICUBIC).resize((max(1, int(240 * min(s, 1.2))),) * 2)
                im.alpha_composite(st, (int(880 - st.width / 2), int(650 - st.height / 2))); d = ImageDraw.Draw(im)
    x = 440 + 160 * math.sin(t * 1.6)
    kid_crayon(im, t * 1.4, x, 1120, 0.85)
    km = back((t - sp * 0.72) / 0.35)
    if km > 0:
        put(im, "mom_sad", 905, 1180, 0.55 * km * (1 + 0.02 * math.sin(t * 9))); d = ImageDraw.Draw(im)
        if km > 0.9: pill(d, 905, 960, "메모 중", 40)
    return chrome(im)

def queue(im, t, n=6, dim=False):
    d = ImageDraw.Draw(im)
    for i in range(n):
        tx = 160 + i * 165; k = ease((t - i * 0.12) / 0.7); x = tx + (1 - k) * 1100
        bob = 6 * abs(math.sin(t * 7 + i)); col = (150, 125, 160) if i % 2 else (125, 140, 170)
        y = 1150 - bob
        d.rounded_rectangle((x - 50, y - 160, x + 50, y + 120), radius=45, fill=col)
        d.ellipse((x - 42, y - 255, x + 42, y - 171), fill=col)
        kx = x + 62; ky = y + 40  # 손잡은 아이
        d.rounded_rectangle((kx - 30, ky - 50, kx + 30, ky + 80), radius=28, fill=(255, 170, 120))
        d.ellipse((kx - 30, ky - 110, kx + 30, ky - 52), fill=(255, 170, 120))
        d.line([(x + 40, y - 40), (kx - 20, ky - 20)], fill=col, width=14)
    return d

def s5(t, dur):  # 줄 + 통장 + 사탕
    im = S["bg_bunsik_b"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s5"]
    d = queue(im, t)
    half = sp * 0.33
    if t < half + 0.2:
        a = ease((t - 0.1) / 0.35); label(d, 330 + (1 - a) * 40, "동네 애들 줄 섬", 104)
        put(im, kid_key(t, "proud", 0.2), 540, 640, 0.75 * breathe(t)); d = ImageDraw.Draw(im)
    if t > half:
        a = back((t - half) / 0.4)
        bank = S["card_bank"] if a >= 0.999 else S["card_bank"].resize((max(1, int(760 * a)), max(1, int(330 * a))))
        im.alpha_composite(bank, (int(540 - bank.width / 2), int(430 - bank.height / 2))); d = ImageDraw.Draw(im)
        if a > 0.9:
            up = half + 0.4; p = ease((t - up) / 0.6); won = 570000 + int(320000 * p / 1000) * 1000
            txt(d, 540, 335, "통장 잔고", 54, WHT, stroke=5)
            txt(d, 540, 470, f"{won:,}원", 118, YEL if p < 1 else (140, 240, 150), stroke=8)
            if t > up:
                b = back((t - up) / 0.3); txt(d, 880, 250, "+32만", int(80 * min(b, 1.15)), GREEN, stroke=7, sfill=WHT)
            if p >= 1:
                s = back((t - up - 0.6) / 0.3)
                if s > 0:
                    st = Image.new("RGBA", (320, 320), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
                    sd.ellipse((20, 20, 300, 300), outline=RED, width=14)
                    sd.text((160, 125), "처음으로", font=V1.F(50), fill=RED, anchor="mm"); sd.text((160, 205), "+", font=V1.F(110), fill=RED, anchor="mm")
                    st = st.rotate(-12, resample=Image.BICUBIC).resize((max(1, int(230 * min(s, 1.2))),) * 2)
                    im.alpha_composite(st, (int(870 - st.width / 2), int(700 - st.height / 2))); d = ImageDraw.Draw(im)
    c0 = sp * 0.72
    if t > c0:
        k = back((t - c0) / 0.35)
        if k > 0:
            pill(d, 390, 720, "솔루션 비용: 사탕 1개", int(52 * min(k, 1.1)) or 1, YEL)
            put(im, "candy", 390, 640 - 8 * abs(math.sin(t * 6)), 1.0 * min(k, 1)); d = ImageDraw.Draw(im)
    return chrome(im)

OPTS = (("cam", "키즈 유튜버", (235, 80, 90)), ("ladle", "분식집 후계자", (240, 150, 60)), ("cap", "영어유치원", (90, 150, 235)))
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
            put(im, key, x, cy + 5, 0.8); d = ImageDraw.Draw(im)
            txt(d, x, cy + h2 - 50, name, 44, INK)
            if key == "cap": txt(d, x, cy + h2 - 100, "반 달", 34, (90, 150, 235))
    return d

def s6(t, dur):  # 세 번째 갈림길 → 엄마는 아직 혼나는 중
    im = S["bg_vote"].copy(); d = ImageDraw.Draw(im); sp = SPEAK["s6"]
    sw = sp * 0.6; last = sp * 0.82
    if t < sw:
        put(im, kid_key(t, "proud", 0.2), 540, 510, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        a = ease((t - 0.1) / 0.4); label(d, 185 + (1 - a) * 40, "세 번째 갈림길", 104)
        if t > 0.9:
            b = 16 * abs(math.sin((t - 0.9) * 6)); txt(d, 800, 380 - b, "?", 150, (255, 95, 110), stroke=9, sfill=WHT)
    else:
        a = back((t - sw) / 0.4)
        if a > 0: label(d, 185, "댓글 1등대로 갑니다", int(92 * min(a, 1.1)) or 1)
        if t < last:
            put(im, kid_key(t, "proud", 0.7), 540, 520, 0.95 * breathe(t)); d = ImageDraw.Draw(im)
        else:  # 첫 장면과 이어지게: 정색한 김댓글 + 시무룩한 엄마
            put(im, "kida_frown", 380, 520, 0.95 * breathe(t))
            k = back((t - last) / 0.35)
            put(im, "mom_sad", 790, 520, 0.72 * k * (1 + 0.02 * math.sin(t * 9))); d = ImageDraw.Draw(im)
            if k > 0.9:
                pill(d, 790, 330, "아직 혼나는 중", 46, WHT); sweat(d, 900, 370, t)
    vote_cards(im, t)
    return chrome(im)

V1.FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6)
if __name__ == "__main__":
    V1.main()
