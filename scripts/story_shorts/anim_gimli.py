#!/usr/bin/env python3
"""김리 글라이더(1983 에어캐나다 143편) 재연 모션그래픽(카드 영상 칸 1080x780) — 2026.10.26 오늘의쓸모.
  python3 scripts/story_shorts/anim_gimli.py <출력폴더>
  → scrape.mp4(앞바퀴 없이 코로 활주로를 긁으며 불꽃 — 옆에서 따라가는 카메라)
    cockpit.mp4(고도 41,000ft, 엔진 1·2 바늘이 차례로 0 → ENG OUT 경고, 계기 화면 꺼짐)
    fuel.mp4(필요 22,300 kg / 넣음 22,300 lb → 연료통이 절반만 참)
    glide.mp4(엔진 꺼진 767이 소리 없이 미끄러져 내려감, 배 밑 비상 풍차(RAT)만 돎, 고도 숫자 줄어듦)
    runway.mp4(위에서 본 활주로 — 경주 차·사람들, 여객기 그림자가 다가오자 사람들이 흩어짐)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (18, 28, 46); PANEL = (44, 58, 84); EDGE = (86, 106, 140); INK = (240, 244, 250); GRAY = (150, 162, 182)
YEL = (255, 216, 77); RED = (236, 50, 46); GRN = (46, 196, 100); ORG = (255, 140, 40)
ACR = (200, 30, 40)  # 에어캐나다 빨강
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGBA", (W, H), BG + (255,))
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=INK, stroke=0):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def plane_layer(s=1.0, gear_nose=True, gear_main=True, rat=None):
    """옆에서 본 767(코가 왼쪽). 원점 기준 1000x360 레이어, 기준선(바퀴 바닥) y=300."""
    L = Image.new("RGBA", (1000, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    body = (248, 248, 250)
    # 꼬리날개
    d.polygon([(800, 130), (880, 10), (950, 10), (930, 140)], fill=ACR)
    d.ellipse((880, 40, 920, 80), fill=body)
    d.ellipse((890, 50, 910, 70), fill=ACR)
    # 동체
    d.rounded_rectangle((60, 110, 960, 220), 55, fill=body)
    d.pieslice((20, 110, 140, 220), 90, 270, fill=body)
    d.rectangle((80, 110, 140, 220), fill=body)
    # 빨간 줄·창문
    d.rectangle((70, 150, 940, 168), fill=ACR)
    for k in range(22):
        x = 180 + k * 33
        d.ellipse((x, 128, x + 14, 142), fill=(70, 90, 120))
    d.polygon([(48, 140), (100, 128), (110, 146), (52, 150)], fill=(40, 60, 90))  # 조종석 창
    # 날개·엔진
    d.polygon([(380, 190), (560, 190), (470, 250), (380, 250)], fill=(205, 210, 218))
    d.rounded_rectangle((360, 225, 500, 275), 22, fill=(190, 196, 206))
    d.ellipse((350, 225, 390, 275), fill=(60, 66, 80))
    if gear_main:
        d.rectangle((520, 220, 532, 280), fill=(90, 96, 110))
        d.ellipse((500, 268, 552, 310), fill=(30, 30, 34))
    if gear_nose:
        d.rectangle((150, 220, 160, 280), fill=(90, 96, 110))
        d.ellipse((135, 272, 175, 306), fill=(30, 30, 34))
    if rat is not None:  # 비상 풍차(RAT)
        cx, cy = 430, 236
        d.line((cx, 215, cx, cy), fill=(120, 126, 140), width=6)
        for k in range(2):
            a = rat + k * math.pi
            d.line((cx - 26 * math.cos(a), cy - 6 * math.sin(a), cx + 26 * math.cos(a), cy + 6 * math.sin(a)),
                   fill=(60, 66, 80), width=7)
    if s != 1.0:
        L = L.resize((int(1000 * s), int(360 * s)), Image.LANCZOS)
    return L


# ── 1. 코로 활주로 긁기 ────────────────────────────────
PL_NOSEDOWN = plane_layer(1.05, gear_nose=False).rotate(-5.5, resample=Image.BICUBIC, expand=True)
rnd_sp = random.Random(5)
SPARKS = [(rnd_sp.uniform(0, 3.2), rnd_sp.uniform(-0.5, 0.9), rnd_sp.uniform(260, 620), rnd_sp.uniform(0.25, 0.7))
          for _ in range(520)]


def s_scrape(img, t):
    d = ImageDraw.Draw(img)
    # 하늘·나무·활주로
    for y in range(0, 520, 4):
        c = int(150 + y * 0.12)
        d.rectangle((0, y, W, y + 4), fill=(110, c, 235))
    d.rectangle((0, 470, W, 530), fill=(70, 120, 70))
    d.rectangle((0, 530, W, H), fill=(92, 94, 100))
    spd = 900 * (1 - 0.55 * clamp(t / 3.0))
    off = (t * spd) % 260
    for k in range(-1, 6):
        x = k * 260 + off - 260
        d.rectangle((x, 640, x + 140, 656), fill=(236, 236, 230))
    sh = 3 * math.sin(t * 60) * (1 - clamp(t / 3.2))
    px, py = 70, 330 + sh
    img.alpha_composite(PL_NOSEDOWN, (int(px), int(py)))
    nose = (px + 40, 600 + sh)
    # 불꽃
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for st, vy, vx, life in SPARKS:
        a = t - st
        if a < 0 or a > life:
            continue
        x = nose[0] + 20 + vx * a
        y = nose[1] - 10 - 260 * vy * a + 600 * a * a
        al = int(255 * (1 - a / life))
        col = YEL if (st * 100) % 3 > 1 else ORG
        ld.line((x, y, x - 34, y + 6), fill=col + (al,), width=7)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    r = 110 + 16 * math.sin(t * 40)
    gd.ellipse((nose[0] - r + 30, nose[1] - r * 0.6, nose[0] + r + 30, nose[1] + r * 0.6), fill=(255, 190, 60, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(lay)
    # 연기
    sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sm)
    for k in range(18):
        a = (t * 1.3 + k * 0.17) % 1.6
        x = nose[0] + 60 + a * 380; y = nose[1] - 20 - a * 90
        rr = 30 + a * 60
        sd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(210, 210, 214, int(130 * (1 - a / 1.6))))
    img.alpha_composite(sm.filter(ImageFilter.GaussianBlur(10)))


# ── 2. 조종석: 엔진 2개 꺼짐 ─────────────────────────────
def gauge(d, cx, cy, R, val, label, warn):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(14, 18, 26), outline=(90, 100, 120), width=6)
    for k in range(11):
        a = math.radians(-220 + k * 26)
        d.line((cx + math.cos(a) * (R - 26), cy + math.sin(a) * (R - 26), cx + math.cos(a) * (R - 8),
                cy + math.sin(a) * (R - 8)), fill=(200, 206, 216), width=5)
    a = math.radians(-220 + 260 * val)
    d.line((cx, cy, cx + math.cos(a) * (R - 30), cy + math.sin(a) * (R - 30)), fill=(255, 255, 255), width=9)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(200, 206, 216))
    ctext(d, cx, cy + 40, f"{int(val * 100):d}%", 44, RED if warn else GRN)
    ctext(d, cx, cy + R + 14, label, 42, INK)


def s_cockpit(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(26, 30, 38))
    d.rounded_rectangle((40, 30, 1040, 130), 18, fill=(10, 12, 18), outline=(70, 80, 100), width=4)
    ctext(d, 540, 38, "고도 41,000 ft (약 12km)", 58, YEL)
    v1 = 0.92 * (1 - ease(clamp((t - 0.3) / 0.9)))
    v2 = 0.92 * (1 - ease(clamp((t - 1.0) / 0.9)))
    gauge(d, 300, 360, 170, v1, "엔진 1", v1 < 0.05)
    gauge(d, 780, 360, 170, v2, "엔진 2", v2 < 0.05)
    blink = int(t * 6) % 2 == 0
    for cx, on in ((300, v1 < 0.05), (780, v2 < 0.05)):
        if on:
            d.rounded_rectangle((cx - 150, 640, cx + 150, 720), 14, fill=RED if blink else (110, 20, 20))
            ctext(d, cx, 646, "ENG OUT", 52, INK)
    if t > 2.3:  # 화면 꺼짐
        a = clamp((t - 2.3) / 0.25)
        dark = Image.new("RGBA", (W, H), (0, 0, 0, int(200 * a)))
        img.alpha_composite(dark)


# ── 3. 연료 단위 착각 ──────────────────────────────────
def s_fuel(img, t):
    d = ImageDraw.Draw(img)
    # 왼쪽: 두 줄 비교
    a1 = ease(clamp(t / 0.35)); a2 = ease(clamp((t - 0.6) / 0.35))
    if a1 > 0:
        d.rounded_rectangle((50, 120, 640, 280), 20, fill=PANEL)
        d.text((80, 140), "필요", font=F(46), fill=GRAY)
        d.text((80, 192), "22,300", font=F(70), fill=INK)
        d.rounded_rectangle((430, 196, 600, 270), 16, fill=GRN)
        ctext(d, 515, 196, "kg", 56, INK)
    if a2 > 0:
        d.rounded_rectangle((50, 330, 640, 490), 20, fill=PANEL)
        d.text((80, 350), "넣은 양", font=F(46), fill=GRAY)
        d.text((80, 402), "22,300", font=F(70), fill=INK)
        d.rounded_rectangle((430, 406, 600, 480), 16, fill=RED)
        ctext(d, 515, 406, "lb", 56, INK)
    if t > 1.2:
        a = ease(clamp((t - 1.2) / 0.3))
        ctext(d, 345, 540, "1 lb = 0.45 kg", int(20 + 40 * a), YEL)
    # 오른쪽: 연료통
    x0, y0, x1, y1 = 760, 110, 1000, 700
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(30, 38, 56), outline=EDGE, width=6)
    lvl = 0.46 * ease(clamp((t - 0.6) / 1.4))
    top = y1 - 6 - (y1 - y0 - 12) * lvl
    if lvl > 0.04:
        d.rounded_rectangle((x0 + 8, top, x1 - 8, y1 - 8), 24, fill=(255, 176, 40))
    yfull = y0 + 10
    for x in range(x0 + 10, x1 - 10, 30):
        d.line((x, yfull, x + 16, yfull), fill=GRN, width=6)
    ctext(d, (x0 + x1) / 2, y0 - 70, "연료통", 46, INK)
    if t > 2.0:
        a = ease(clamp((t - 2.0) / 0.3))
        d.rounded_rectangle((690, 360, 1070, 450), 18, fill=RED)
        ctext(d, 880, 366, "절반뿐!", int(30 + 30 * a), INK)


# ── 4. 엔진 없이 활공 ──────────────────────────────────
def s_glide(img, t):
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        c = int(60 + y * 0.18)
        d.rectangle((0, y, W, y + 4), fill=(40, c, 170 + y // 12))
    d.polygon([(0, 700), (300, 680), (700, 700), (1080, 690), (1080, 780), (0, 780)], fill=(60, 100, 60))
    # 활주로 표시
    d.rectangle((860, 690, 1060, 704), fill=(120, 120, 126))
    ctext(d, 960, 620, "김리", 44, YEL, 3)
    k = clamp(t / 3.2)
    px = -80 + 640 * k; py = 140 + 300 * k
    P = plane_layer(0.55, gear_nose=False, gear_main=False, rat=t * 30).transpose(Image.FLIP_LEFT_RIGHT).rotate(-14, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(P, (int(px), int(py)))
    d = ImageDraw.Draw(img)
    # 지나온 점선
    for j in range(0, int(30 * k)):
        jx = -80 + 640 * j / 30 + 20; jy = 170 + 300 * j / 30
        d.ellipse((jx - 4, jy - 4, jx + 4, jy + 4), fill=(255, 255, 255, 160))
    alt = int(41000 * (1 - 0.85 * k) / 100) * 100
    d.rounded_rectangle((40, 30, 470, 120), 16, fill=(10, 12, 18))
    d.text((64, 36), f"고도 {alt:,} ft", font=F(54), fill=YEL)
    d.rounded_rectangle((640, 30, 1040, 120), 16, fill=(10, 12, 18))
    d.text((664, 36), "엔진 0개", font=F(54), fill=RED)


# ── 5. 위에서 본 활주로 ────────────────────────────────
rr = random.Random(11)
PEOPLE = [(rr.uniform(380, 700), rr.uniform(300, 760), rr.choice([(255, 210, 60), (90, 190, 255), (255, 120, 160), (250, 250, 250)]))
          for _ in range(46)]
CARS = [(rr.uniform(430, 640), rr.uniform(360, 740), rr.choice([(220, 40, 40), (40, 120, 220), (250, 200, 40)]))
        for _ in range(7)]


def topplane(d, cx, cy, s, col):
    pts_body = [(cx - 22 * s, cy - 210 * s), (cx + 22 * s, cy - 210 * s), (cx + 26 * s, cy + 200 * s),
                (cx - 26 * s, cy + 200 * s)]
    d.polygon(pts_body, fill=col)
    d.ellipse((cx - 24 * s, cy + 170 * s, cx + 24 * s, cy + 230 * s), fill=col)
    d.polygon([(cx, cy - 10 * s), (cx + 230 * s, cy - 90 * s), (cx + 230 * s, cy - 60 * s), (cx, cy + 50 * s),
               (cx - 230 * s, cy - 60 * s), (cx - 230 * s, cy - 90 * s)], fill=col)
    d.polygon([(cx, cy - 170 * s), (cx + 90 * s, cy - 210 * s), (cx + 90 * s, cy - 195 * s), (cx, cy - 150 * s),
               (cx - 90 * s, cy - 195 * s), (cx - 90 * s, cy - 210 * s)], fill=col)


def s_runway(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(80, 130, 70))
    d.rectangle((360, 0, 720, H), fill=(110, 112, 118))
    for y in range(-40, H, 110):
        d.rectangle((534, y, 546, y + 60), fill=(236, 236, 230))
    d.rounded_rectangle((770, 40, 1050, 150), 16, fill=(250, 250, 250))
    ctext(d, 910, 50, "자동차 경주", 40, (30, 40, 60))
    ctext(d, 910, 98, "가족의 날", 34, ACR)
    run_t = clamp((t - 1.1) / 1.4)
    for cx0, cy0, col in CARS:
        x = cx0 + (400 if cx0 > 540 else -400) * ease(run_t)
        d.rounded_rectangle((x - 18, cy0 - 30, x + 18, cy0 + 30), 8, fill=col)
    for k, (x0, y0, col) in enumerate(PEOPLE):
        dirx = 1 if x0 > 540 else -1
        x = x0 + dirx * (260 + 60 * (k % 3)) * ease(run_t)
        d.ellipse((x - 11, y0 - 11, x + 11, y0 + 11), fill=col, outline=(30, 30, 30), width=2)
    # 다가오는 여객기(그림자 + 몸체)
    k = ease(clamp(t / 2.4))
    s = 0.55 + 0.75 * k
    cy = -260 + 420 * k
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    topplane(sd, 560, cy + 70, s, (0, 0, 0, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    topplane(d, 540, cy, s, (246, 246, 248))
    d.line((540, cy - 200 * s, 540, cy + 190 * s), fill=ACR, width=max(3, int(8 * s)))
    if t > 1.2 and int(t * 5) % 2 == 0:
        d.rounded_rectangle((760, 640, 1050, 730), 16, fill=RED)
        ctext(d, 905, 646, "도망쳐!", 54, INK)


run("scrape", 3.2, s_scrape)
run("cockpit", 3.0, s_cockpit)
run("fuel", 3.2, s_fuel)
run("glide", 3.2, s_glide)
run("runway", 3.0, s_runway)
print("ok", OUT)
