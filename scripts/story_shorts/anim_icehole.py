#!/usr/bin/env python3
"""얼음 구멍에 몰리는 물고기 — 겨울 질식(замор) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.02 오늘의쓸모.
  python3 scripts/story_shorts/anim_icehole.py <출력폴더>
  → lid.mp4   (얼음이 '뚜껑'처럼 닫히면 공기 속 산소가 못 들어오고, 물속 산소 게이지가 빨갛게 바닥남)
    rush.mp4  (얼음에 구멍 하나 → 산소가 구멍으로 들어오고, 물고기 떼가 그 아래로 몰려듦)
    reeds.mp4 (구멍 수가 0 → 25,000 개로 늘어남(아스트라한 2014) → 구멍에 꽂은 갈대 다발이 '빨대'처럼 숨길을 열어 둠)
근거: Moscow Times·RIA 2014.2(아스트라한 2만5천 개, 1ha당 10~12개, 갈대를 꽂아 숨 쉬게·안 얼게),
      벨라루스 지방정부 'замор' 안내(얼음이 공기 속 산소를 막음, 산소가 모자라면 구멍으로 먼저 몰려듦).
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SKY = (120, 170, 225); NAVY = (16, 34, 66); WATER = (22, 56, 98); ICE = (226, 240, 250); ICE_E = (150, 190, 220)
WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); O2C = (150, 230, 255); FISH = (170, 180, 150)
REED = (196, 160, 80)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
ICE_Y0, ICE_Y1 = 190, 270          # 얼음 층(위·아래)
random.seed(11)
BUB = [(random.uniform(40, 1040), random.uniform(290, 760), random.uniform(0, 6.28), random.uniform(0.6, 1.0)) for _ in range(46)]
AIR = [(random.uniform(40, 1040), random.uniform(20, 170), random.uniform(0, 6.28)) for _ in range(30)]
FISHES = [(random.uniform(80, 1000), random.uniform(380, 740), random.uniform(0, 6.28), random.choice((-1, 1)), random.uniform(0.8, 1.25)) for _ in range(14)]


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), WATER)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def fish(d, x, y, dirn, sc, col=FISH, gasp=0.0):
    L = 70 * sc; Hh = 26 * sc
    d.ellipse((x - L / 2, y - Hh / 2, x + L / 2, y + Hh / 2), fill=col, outline=(60, 70, 60), width=2)
    tx = x - dirn * L / 2
    d.polygon([(tx, y), (tx - dirn * 26 * sc, y - 18 * sc), (tx - dirn * 26 * sc, y + 18 * sc)], fill=col, outline=(60, 70, 60))
    ex = x + dirn * L * 0.28
    d.ellipse((ex - 5 * sc, y - 7 * sc, ex + 5 * sc, y + 3 * sc), fill=(20, 20, 20))
    if gasp > 0:  # 입 벌림
        mx = x + dirn * L / 2
        r = 5 * sc * gasp
        d.ellipse((mx - r, y - r + 2, mx + r, y + r + 2), fill=(90, 30, 30))


def bubble(d, x, y, r, a=1.0):
    col = tuple(int(c * a + w * (1 - a)) for c, w in zip(O2C, WATER))
    d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=4)
    if r > 15:
        ft = F(int(r * 0.9)); fs = F(int(r * 0.5))
        w = d.textlength("O", font=ft) + d.textlength("2", font=fs)
        d.text((x - w / 2, y - r * 0.62), "O", font=ft, fill=col)
        d.text((x - w / 2 + d.textlength("O", font=ft), y - r * 0.05), "2", font=fs, fill=col)


def sky(d, top_h):
    d.rectangle((0, 0, W, top_h), fill=SKY)


def ice(d, x_holes=(), hole_w=110, reed=None):
    """얼음 층. x_holes 의 x 중심마다 구멍."""
    xs = [0] + [v for h in sorted(x_holes) for v in (h - hole_w / 2, h + hole_w / 2)] + [W]
    for a, b in zip(xs[0::2], xs[1::2]):
        d.rectangle((a, ICE_Y0, b, ICE_Y1), fill=ICE, outline=ICE_E, width=3)
    # 얼음 금 무늬
    for k in range(9):
        x = 60 + k * 120
        if any(abs(x - h) < hole_w for h in x_holes):
            continue
        d.line((x, ICE_Y0 + 14, x + 26, ICE_Y0 + 40, x + 8, ICE_Y1 - 14), fill=ICE_E, width=2)


def gauge(d, level, label="물속 산소"):
    d.rounded_rectangle((760, 300, 1040, 380), 16, fill=(10, 20, 40), outline=(90, 110, 140), width=3)
    ctext(d, 900, 304, label, 26, stroke=0)
    col = (60, 200, 120) if level > 0.55 else YEL if level > 0.3 else RED
    d.rounded_rectangle((780, 344, 780 + int(240 * max(level, 0.02)), 368), 8, fill=col)


def lid(img, t):
    d = ImageDraw.Draw(img)
    sky(d, ICE_Y0)
    close = ease(clamp(t / 0.8))
    # 공기 속 산소 알갱이 — 처음엔 물로 내려가다가 얼음이 닫히면 튕겨 나감
    for k, (x, y, ph) in enumerate(AIR):
        yy = y + 8 * math.sin(t * 3 + ph)
        bubble(d, x, yy, 13)
    # 얼음이 양옆에서 닫힘
    gap = int((1 - close) * 1080)
    xl = (W - gap) / 2; xr = (W + gap) / 2
    d.rectangle((0, ICE_Y0, xl, ICE_Y1), fill=ICE, outline=ICE_E, width=3)
    d.rectangle((xr, ICE_Y0, W, ICE_Y1), fill=ICE, outline=ICE_E, width=3)
    if close > 0.98:
        ctext(d, 540, ICE_Y0 + 10, "얼음 = 뚜껑", 54, fill=(20, 40, 80), stroke=0)
        for k, x in enumerate((160, 420, 680, 940)):  # 막힌 표시
            if t > 1.0 + k * 0.12:
                d.line((x - 22, ICE_Y0 - 70, x + 22, ICE_Y0 - 26), fill=RED, width=9)
                d.line((x + 22, ICE_Y0 - 70, x - 22, ICE_Y0 - 26), fill=RED, width=9)
    # 물속 산소 방울 — 시간이 갈수록 하나씩 사라짐
    level = 1 - ease(clamp((t - 0.9) / 2.0)) * 0.88
    n = int(len(BUB) * level)
    for x, y, ph, a in BUB[:n]:
        bubble(d, x + 6 * math.sin(t * 2 + ph), y + 6 * math.cos(t * 2.4 + ph), 20, a)
    # 물고기: 느려지고 입 뻐끔
    for x, y, ph, dirn, sc in FISHES[:9]:
        sp = 40 * level
        xx = (x + dirn * sp * t) % 1080
        fish(d, xx, y + 6 * math.sin(t * 2 + ph), dirn, sc, gasp=(1 - level) * (0.5 + 0.5 * math.sin(t * 10 + ph)))
    gauge(d, level)


def rush(img, t):
    d = ImageDraw.Draw(img)
    sky(d, ICE_Y0)
    for x, y, ph in AIR:
        bubble(d, x, y + 8 * math.sin(t * 3 + ph), 13)
    hole = 540
    ice(d, x_holes=(hole,), hole_w=150)
    # 구멍으로 산소가 줄줄이 들어옴
    for k in range(10):
        ph = (t * 1.1 + k / 10) % 1.0
        y = 120 + ph * 330
        bubble(d, hole + 18 * math.sin(k * 2.1 + t * 3), y, 18, a=1 - ph * 0.6)
    # 물고기 떼가 구멍 아래로 몰려듦
    k_in = ease(clamp(t / 1.8))
    for i, (x, y, ph, dirn, sc) in enumerate(FISHES):
        tx = hole + (i % 5 - 2) * 46; ty = 300 + (i // 5) * 40
        xx = x + (tx - x) * k_in; yy = y + (ty - y) * k_in
        dd = 1 if tx >= x else -1
        fish(d, xx + 4 * math.sin(t * 9 + ph), yy, dd, sc, gasp=0.6 + 0.4 * math.sin(t * 11 + ph))
    gauge(d, 0.15 + 0.25 * ease(clamp((t - 1.0) / 1.6)), "구멍 아래 산소")
    if t > 1.4:
        ctext(d, 300, 120, "숨구멍", 62, fill=YEL)


def reeds(img, t):
    d = ImageDraw.Draw(img)
    sky(d, ICE_Y0)
    # 구멍 수 카운터 0 → 25,000
    k = ease(clamp(t / 1.5))
    n = int(25000 * k)
    d.rounded_rectangle((40, 30, 560, 160), 18, fill=(20, 28, 44))
    ctext(d, 300, 38, "러시아 아스트라한 2014", 28, fill=(170, 185, 210), stroke=0)
    ctext(d, 300, 76, f"구멍 {n:,}개", 58, fill=YEL, stroke=0)
    holes = [100 + i * 110 for i in range(int(1 + 8 * k))]
    ice(d, x_holes=holes[1:], hole_w=46)
    # 가운데 큰 구멍 + 갈대 다발(빨대)
    hole = 760
    d.rectangle((hole - 70, ICE_Y0, hole + 70, ICE_Y1), fill=WATER)
    drop = ease(clamp((t - 1.2) / 0.6))
    ry = -160 + 260 * drop
    for j in range(7):
        x = hole - 48 + j * 16
        d.rectangle((x, ICE_Y0 + ry - 60, x + 10, ICE_Y1 + ry + 70), fill=REED, outline=(120, 90, 40))
    if drop > 0.95:
        # 빈 줄기 속으로 공기가 오르내림
        for q in range(6):
            ph = (t * 1.4 + q / 6) % 1.0
            y = ICE_Y0 - 40 + ph * 220
            x = hole - 43 + (q % 7) * 16
            d.ellipse((x, y, x + 10, y + 10), fill=O2C)
        # 구멍 둘레 얼음이 다시 얼려다 멈춤
        frz = 0.5 + 0.5 * math.sin(t * 6)
        d.rectangle((hole - 70, ICE_Y0, hole - 56 - 6 * frz, ICE_Y1), fill=ICE)
        d.rectangle((hole + 56 + 6 * frz, ICE_Y0, hole + 70, ICE_Y1), fill=ICE)
        ctext(d, 360, 330, "갈대 = 빨대", 60, fill=YEL)
        ctext(d, 360, 406, "숨길이 다시 안 얼게", 36)
    for x, y, ph, dirn, sc in FISHES[:6]:
        xx = (x + dirn * 30 * t) % 1080
        fish(d, xx, max(y, 470), dirn, sc)


run("lid", 3.2, lid)
run("rush", 3.0, rush)
run("reeds", 3.2, reeds)
print("ok")
