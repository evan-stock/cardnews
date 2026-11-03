#!/usr/bin/env python3
"""그물 속 물고기를 빨아 먹는 고래상어 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.03 오늘의쓸모.
  python3 scripts/story_shorts/anim_whaleshark.py <출력폴더>
  → size.mp4  (사람 1.7m · 버스 12m · 고래상어 최대 약 18m 크기 비교, 자 눈금이 0→18m)
    bagan.mp4 (밤바다 어부 뗏목 '바간': 불빛에 작은 물고기가 모이고, 그물을 올릴 때 그물코로 새는 물고기를 아래 고래상어가 빨아들임)
    luck.mp4  (어부가 양동이로 작은 물고기를 던지면 고래상어들이 올라옴 — '고래상어 = 행운', 매일 아침 먹이)
근거: Australian Geographic 2013.11(Conservation International 촬영, 첸드라와시 만, 바간 불빛·그물, 어부들은 행운으로 여김),
      Rappler(크와티소레 바간, 매일 아침 ikan puri 를 던져 줌·이름을 붙임, 최대 18m),
      Conservation International 블로그(바간 어부들은 고래상어를 '행운의 신호'로 봄, 관광이 주민 소득),
      My Modern Met(그물을 올릴 때 그물코로 새는 작은 물고기를 먹음, 어부들이 수십 년간 먹이를 줌).
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SEA = (18, 70, 120); DEEP = (10, 30, 62); NIGHT = (8, 14, 34); SKY = (130, 185, 235)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (232, 48, 44); SHARK = (78, 98, 122); BELLY = (196, 206, 214)
WOOD = (150, 105, 60); NET = (40, 40, 40); SILVER = (220, 232, 240); BUS = (240, 180, 40)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(7)
SPOTS = [(random.uniform(0.05, 0.85), random.uniform(-0.8, 0.2)) for _ in range(70)]


def run(name, dur, draw, bg):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), bg)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def shark(d, x, y, L, t, mouth=0.0, dirn=-1):
    """옆에서 본 고래상어. x,y = 머리 끝(입) 위치, L = 몸길이(px), dirn=-1 이면 왼쪽을 봄."""
    h = L * 0.17
    sw = math.sin(t * 5) * h * 0.25          # 꼬리 흔들림
    pts = []
    for k in range(41):                         # 위쪽 윤곽
        u = k / 40
        thick = h * (0.55 * math.sin(math.pi * min(1, u * 1.15)) ** 0.7 + 0.05)
        pts.append((x - dirn * u * L, y - thick + sw * u ** 3))
    low = []
    for k in range(40, -1, -1):                 # 아래쪽 윤곽
        u = k / 40
        thick = h * (0.42 * math.sin(math.pi * min(1, u * 1.15)) ** 0.7 + 0.05)
        low.append((x - dirn * u * L, y + thick + sw * u ** 3))
    d.polygon(pts + low, fill=SHARK)
    d.polygon([(x - dirn * L * 0.05, y + h * 0.1)] + low[-12:], fill=BELLY)
    # 등지느러미·꼬리
    bx = x - dirn * L * 0.55
    d.polygon([(bx, y - h * 0.45), (bx - dirn * L * 0.09, y - h * 1.05), (bx - dirn * L * 0.14, y - h * 0.4)], fill=SHARK)
    tx, ty = x - dirn * L, y + sw
    d.polygon([(tx + dirn * L * 0.03, ty), (tx - dirn * L * 0.12, ty - h * 1.2), (tx - dirn * L * 0.06, ty), (tx - dirn * L * 0.1, ty + h * 0.7)], fill=SHARK)
    # 가슴지느러미
    px = x - dirn * L * 0.3
    d.polygon([(px, y + h * 0.3), (px - dirn * L * 0.12, y + h * 0.95), (px - dirn * L * 0.13, y + h * 0.35)], fill=(64, 82, 104))
    # 흰 점 무늬
    for u, v in SPOTS:
        sx = x - dirn * u * L; sy = y + v * h * 0.6 + sw * u ** 3
        r = max(2, L * 0.006)
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(225, 232, 238))
    # 눈·입
    ex = x - dirn * L * 0.06
    d.ellipse((ex - 4, y - h * 0.18 - 4, ex + 4, y - h * 0.18 + 4), fill=(15, 15, 20))
    mh = h * (0.08 + 0.32 * mouth)
    d.ellipse((x - 6 - abs(dirn) * mh * 0.4, y - mh / 2, x + 6, y + mh / 2), fill=(30, 20, 26))


def person(d, x, ground, hpx, col=WHITE):
    head = hpx * 0.13
    d.ellipse((x - head / 2, ground - hpx, x + head / 2, ground - hpx + head), fill=col)
    d.line((x, ground - hpx + head, x, ground - hpx * 0.45), fill=col, width=max(3, int(hpx * 0.06)))
    d.line((x, ground - hpx * 0.45, x - hpx * 0.12, ground), fill=col, width=max(3, int(hpx * 0.06)))
    d.line((x, ground - hpx * 0.45, x + hpx * 0.12, ground), fill=col, width=max(3, int(hpx * 0.06)))
    d.line((x - hpx * 0.18, ground - hpx * 0.7, x + hpx * 0.18, ground - hpx * 0.7), fill=col, width=max(3, int(hpx * 0.05)))


# ── 1. 크기 비교 ─────────────────────────────────────────
def size(img, t):
    d = ImageDraw.Draw(img)
    for yy in range(H):  # 위는 밝고 아래는 깊은 바다
        c = tuple(int(a + (b - a) * yy / H) for a, b in zip((40, 120, 180), DEEP))
        d.line((0, yy, W, yy), fill=c)
    M = 52  # 1m = 52px → 18m = 936px
    X0, GY = 72, 640
    # 자
    k = ease(clamp(t / 1.6))
    m = 18 * k
    d.line((X0, GY + 40, X0 + m * M, GY + 40), fill=YEL, width=6)
    for i in range(int(m) + 1):
        tick = 22 if i % 5 == 0 else 12
        d.line((X0 + i * M, GY + 40 - tick, X0 + i * M, GY + 40), fill=YEL, width=4)
    ctext(d, min(X0 + m * M, 960), GY + 52, f"{m:.0f}m", 44, fill=YEL)
    # 버스 12m
    if t > 0.5:
        a = ease(clamp((t - 0.5) / 0.5))
        bx = X0 + 120
        bw = 12 * M
        top = GY + 30 - 3.2 * M * 0.9
        d.rounded_rectangle((X0, top, X0 + bw * a, GY + 30), 14, fill=BUS)
        if a > 0.9:
            for wx in range(int(X0 + 30), int(X0 + bw - 60), 70):
                d.rectangle((wx, top + 18, wx + 50, top + 60), fill=(60, 90, 120))
            ctext(d, X0 + bw / 2, top + 72, "버스 12m", 40, fill=(40, 30, 0), stroke=0)
    # 사람 1.7m — 버스 끝 옆에 섬
    PX = X0 + 12 * M + 60
    person(d, PX, GY + 30, 1.7 * M)
    ctext(d, PX, GY - 1.7 * M - 30, "사람 1.7m", 30)
    # 고래상어 최대 약 18m — 오른쪽에서 헤엄쳐 들어옴
    if t > 1.0:
        s = ease(clamp((t - 1.0) / 1.2))
        L = 18 * M
        hx = X0 + (1 - s) * 900          # 머리 위치(왼쪽 끝)
        shark(d, hx, 250, L, t, mouth=0.3 + 0.3 * math.sin(t * 4), dirn=-1)
    if t > 2.2:
        ctext(d, 540, 40, "고래상어 최대 약 18m", 58, fill=YEL)
        ctext(d, 540, 112, "세상에서 가장 큰 물고기", 36)


# ── 2. 바간(어부 뗏목)과 새는 물고기 ──────────────────────
FISHB = [(random.uniform(330, 750), random.uniform(330, 520), random.uniform(0, 6.28)) for _ in range(90)]
LEAK = [(random.uniform(380, 700), random.uniform(0, 1), random.uniform(0, 6.28)) for _ in range(30)]


def bagan(img, t):
    d = ImageDraw.Draw(img)
    SURF = 260
    d.rectangle((0, 0, W, SURF), fill=NIGHT)
    for yy in range(SURF, H):
        c = tuple(int(a + (b - a) * (yy - SURF) / (H - SURF)) for a, b in zip((14, 52, 92), (4, 14, 30)))
        d.line((0, yy, W, yy), fill=c)
    # 뗏목(대나무 틀) + 등불
    d.rectangle((250, SURF - 26, 830, SURF - 6), fill=WOOD)
    for x in (270, 540, 810):
        d.rectangle((x - 8, SURF - 150, x + 8, SURF - 6), fill=WOOD)
    d.rectangle((262, SURF - 156, 818, SURF - 140), fill=WOOD)
    glow = 0.8 + 0.2 * math.sin(t * 9)
    for x in (360, 540, 720):
        r = 70 * glow
        for k in range(5, 0, -1):
            rr = r * k / 5
            c = (int(80 + 35 * k), int(70 + 30 * k), int(20 + 6 * k))
            d.ellipse((x - rr, SURF - 120 - rr, x + rr, SURF - 120 + rr), outline=c, width=3)
        d.ellipse((x - 16, SURF - 136, x + 16, SURF - 104), fill=(255, 240, 160))
    # 불빛이 물속으로 퍼짐
    d.polygon([(330, SURF), (750, SURF), (860, 620), (220, 620)], fill=(30, 72, 108))
    # 그물: t 1.0 이후 위로 올라감
    lift = ease(clamp((t - 0.9) / 1.4))
    ny = 560 - 230 * lift
    d.line((300, SURF, 300, ny), fill=NET, width=4); d.line((780, SURF, 780, ny), fill=NET, width=4)
    d.line((300, ny, 780, ny), fill=NET, width=6)
    for x in range(300, 781, 24):
        d.line((x, ny - 40, x, ny), fill=(60, 60, 60), width=2)
    for y in range(int(ny) - 40, int(ny) + 1, 14):
        d.line((300, y, 780, y), fill=(60, 60, 60), width=2)
    # 작은 물고기 떼(불빛에 모임) — 그물과 함께 올라감
    for x, y, ph in FISHB:
        yy = max(SURF + 14, min(y - 230 * lift, ny - 46)) + 5 * math.sin(t * 6 + ph)
        xx = x + 8 * math.sin(t * 4 + ph)
        d.ellipse((xx - 7, yy - 2, xx + 7, yy + 2), fill=SILVER)
    # 고래상어: 그물 아래에서 입을 위로
    sx = 540 + 30 * math.sin(t * 1.2)
    shark(d, sx + 70, 690, 760, t, mouth=0.4 + 0.6 * ease(clamp((t - 1.4) / 0.6)), dirn=-1)
    mouth = (sx + 70, 690)
    # 그물코로 새는 물고기 → 입으로 빨려 들어감
    if t > 1.3:
        for x, ph0, ph in LEAK:
            q = ((t - 1.3) * 0.9 + ph0) % 1.0
            sx0, sy0 = x, ny + 4
            fx = sx0 + (mouth[0] - sx0) * q ** 1.6
            fy = sy0 + (mouth[1] - sy0) * q
            d.ellipse((fx - 7, fy - 2, fx + 7, fy + 2), fill=SILVER)
    if t < 1.5:
        ctext(d, 540, 24, "바간 = 불빛으로 물고기 모으는 뗏목", 44, fill=YEL)
    else:
        ctext(d, 540, 24, "그물코로 '새는' 물고기를 쪽쪽", 50, fill=YEL)


# ── 3. 행운 — 매일 아침 먹이 ─────────────────────────────
def luck(img, t):
    d = ImageDraw.Draw(img)
    SURF = 300
    d.rectangle((0, 0, W, SURF), fill=SKY)
    d.ellipse((860, 40, 960, 140), fill=(255, 225, 120))  # 아침 해
    for yy in range(SURF, H):
        c = tuple(int(a + (b - a) * (yy - SURF) / (H - SURF)) for a, b in zip((40, 130, 185), (12, 50, 96)))
        d.line((0, yy, W, yy), fill=c)
    # 뗏목 끝과 어부
    d.rectangle((0, SURF - 30, 330, SURF - 8), fill=WOOD)
    for x in (40, 180, 310):
        d.rectangle((x - 7, SURF - 40, x + 7, SURF + 40), fill=WOOD)
    person(d, 250, SURF - 30, 150, col=(30, 30, 40))
    # 양동이 던지기(0.3~1.1초 반복 두 번)
    for rep in (0.2, 1.6):
        q = (t - rep) / 1.2
        if 0 <= q <= 1:
            for k in range(40):
                vx = 220 + (k * 37) % 330; vy = -260 + (k * 53) % 120
                fx = 300 + vx * q; fy = SURF - 140 + vy * q + 420 * q * q
                if fy > SURF + 4:
                    fy = SURF + 4 + (fy - SURF) * 0.15
                d.ellipse((fx - 10, fy - 4, fx + 10, fy + 4), fill=SILVER, outline=(120, 140, 160))
    d.rectangle((280, SURF - 150, 320, SURF - 112), fill=(90, 120, 150))  # 양동이
    # 고래상어 세 마리가 아래에서 올라옴
    for i, (x0, d0) in enumerate(((620, 0.3), (840, 0.7), (460, 1.1))):
        up = ease(clamp((t - d0) / 1.2))
        y = 760 - 330 * up + 6 * math.sin(t * 3 + i)
        shark(d, x0 - 30, y, 420, t + i, mouth=0.5 + 0.5 * math.sin(t * 5 + i), dirn=-1)
    if t > 0.6:
        ctext(d, 680, 170, "고래상어 = '행운'", 64, fill=YEL)
    if t > 1.6:
        ctext(d, 680, 250, "매일 아침 먹이 주기", 40)


run("size", 3.2, size, DEEP)
run("bagan", 3.2, bagan, NIGHT)
run("luck", 3.0, luck, SKY)
print("ok")
