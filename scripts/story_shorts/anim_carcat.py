#!/usr/bin/env python3
"""겨울 엔진룸 속 길고양이 — '모닝노크' 모션그래픽(카드 영상 칸 1080x780) — 2026.11.04 오늘의쓸모.
  python3 scripts/story_shorts/anim_carcat.py <출력폴더>
  → heat.mp4  (차 옆모습: 시동 끈 엔진룸이 열화상처럼 한참 붉게 남고 바깥은 영하 → 고양이가 바퀴 안쪽으로 들어가 엔진 위에 웅크림)
    belt.mp4  (엔진 앞 벨트·풀리 확대: 시동 '딸깍' → 벨트가 빠르게 돎, 경고 표시 + 일본 JAF 한 달 24건)
    knock.mp4 (손이 보닛을 '똑똑' → 고양이가 뛰쳐나감 → 문 '쾅'·경적 '빵' 아이콘 → 그다음 시동)
근거: 데일리벳 2015.11.24(고보협·네슬레퓨리나 모닝노크 — 잔열이 남은 엔진룸에 길고양이가 숨음, 보닛 노크·문 세게 닫기·경적),
      데일리벳 2017.12.12(카라·대학 동아리 모닝노크), 쿠루마뉴스 2024.2.21(JAF: 2023.12 한 달 엔진룸 고양이 구조 요청 24건,
      고속으로 도는 엔진 벨트에 휘말림, 두드린 뒤 기척이 있으면 보닛 열어 확인).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (18, 26, 40); WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (235, 64, 52); BLUE = (120, 190, 255)
CAR = (205, 210, 220); DARK = (40, 44, 52); CAT = (120, 124, 134)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def text(d, x, y, s, size, fill=WHITE, anchor="la", stroke=5):
    d.text((x, y), s, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def cat(d, x, y, s=1.0, tail=0.0):
    """웅크린 고양이(옆모습) — 몸통·머리·귀·꼬리."""
    d.ellipse((x - 60 * s, y - 34 * s, x + 50 * s, y + 30 * s), fill=CAT, outline=(0, 0, 0), width=3)
    hx, hy = x + 55 * s, y - 28 * s
    d.ellipse((hx - 32 * s, hy - 28 * s, hx + 32 * s, hy + 28 * s), fill=CAT, outline=(0, 0, 0), width=3)
    for ex in (-18, 12):
        d.polygon([(hx + (ex - 10) * s, hy - 18 * s), (hx + (ex + 10) * s, hy - 18 * s), (hx + ex * s, hy - 46 * s)],
                  fill=CAT, outline=(0, 0, 0))
    d.ellipse((hx + 8 * s, hy - 6 * s, hx + 18 * s, hy + 4 * s), fill=YEL)
    tx = x - 60 * s
    d.line((tx, y, tx - 40 * s, y - 30 * s - 20 * s * math.sin(tail)), fill=CAT, width=int(14 * s))


def car(d, x0, y0, hood_open=0.0, heat=None):
    """차 옆모습(왼쪽이 앞). heat: 엔진룸 색."""
    d.rounded_rectangle((x0, y0 + 120, x0 + 760, y0 + 260), 30, fill=CAR, outline=(0, 0, 0), width=4)
    d.polygon([(x0 + 240, y0 + 120), (x0 + 330, y0 + 30), (x0 + 600, y0 + 30), (x0 + 700, y0 + 120)], fill=CAR, outline=(0, 0, 0))
    d.polygon([(x0 + 350, y0 + 50), (x0 + 450, y0 + 50), (x0 + 450, y0 + 115), (x0 + 290, y0 + 115)], fill=(150, 190, 230))
    d.polygon([(x0 + 470, y0 + 50), (x0 + 590, y0 + 50), (x0 + 670, y0 + 115), (x0 + 470, y0 + 115)], fill=(150, 190, 230))
    if heat:
        d.rounded_rectangle((x0 + 20, y0 + 135, x0 + 230, y0 + 245), 20, fill=heat)
    for wx in (x0 + 140, x0 + 610):
        d.ellipse((wx - 62, y0 + 200, wx + 62, y0 + 324), fill=DARK, outline=(0, 0, 0), width=4)
        d.ellipse((wx - 26, y0 + 236, wx + 26, y0 + 288), fill=(150, 150, 160))


# ── 1) 따뜻한 엔진룸 → 고양이 ───────────────────────────────────
def draw_heat(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 560, W, H), fill=(230, 236, 245))           # 눈 쌓인 바닥
    for k in range(40):                                          # 눈송이
        x = (k * 137 + 40) % W; y = (k * 89 + t * 120) % 560
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(235, 240, 250))
    a = 0.6 + 0.4 * math.sin(t * 4)
    heat = (int(200 + 55 * a), int(70 + 40 * a), 40)
    car(d, 160, 250, heat=heat)
    text(d, 285, 590, "↑ 엔진룸", 44, (200, 80, 40), "ma", 0)
    text(d, 60, 40, "바깥  영하", 50, BLUE)
    text(d, 700, 40, "엔진룸  따뜻", 50, (255, 140, 80))
    # 고양이가 오른쪽에서 걸어와 바퀴 안쪽 → 엔진 위로
    p = ease(clamp((t - 0.6) / 1.6))
    cx = 1000 - (1000 - 280) * p
    cy = 600 - 180 * ease(clamp((t - 1.7) / 0.6))
    s = 0.9 - 0.25 * ease(clamp((t - 1.7) / 0.6))
    cat(d, cx, cy, s, t * 6)


# ── 2) 엔진 벨트 ────────────────────────────────────────────────
def pulley(d, cx, cy, r, ang):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(90, 96, 108), outline=(0, 0, 0), width=4)
    for k in range(4):
        a = ang + k * math.pi / 2
        d.line((cx, cy, cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a)), fill=(200, 205, 215), width=8)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(200, 205, 215))


def draw_belt(img, t):
    d = ImageDraw.Draw(img)
    P = [(330, 230, 110), (700, 200, 80), (560, 520, 130)]
    on = t > 0.8
    sp = 0 if not on else (t - 0.8) * 30
    # 벨트(풀리 바깥을 잇는 굵은 선)
    pts = [(220, 230), (330, 120), (700, 120), (780, 200), (690, 520), (560, 650), (430, 520), (220, 230)]
    d.line(pts, fill=(170, 172, 182), width=26, joint="curve")
    if on:
        for k in range(14):  # 벨트 위 움직이는 표시
            f = ((k / 14) + sp * 0.03) % 1
            n = len(pts) - 1; seg = f * n; i = int(seg); r = seg - i
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=YEL)
    for cx, cy, r in P:
        pulley(d, cx, cy, r, sp * (130 / r) * 0.1)
    if not on:
        text(d, 860, 300, "딸깍", 70, WHITE, "ma")
    else:
        bl = (int(t * 4) % 2) == 0
        d.polygon([(900, 230), (1000, 400), (800, 400)], fill=RED if bl else (150, 40, 30), outline=(0, 0, 0))
        text(d, 900, 300, "!", 90, WHITE, "ma", 0)
        text(d, 900, 430, "고속 회전", 44, YEL, "ma")
    text(d, 40, 690, "일본 JAF: 엔진룸 고양이 구조 요청 한 달 24건 (2023.12)", 34, WHITE)


# ── 3) 노크 → 고양이 도망 → 문 쾅·경적 ───────────────────────────
def draw_knock(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 560, W, H), fill=(230, 236, 245))
    car(d, 160, 250, heat=(120, 70, 50))
    k1 = 0.2 <= t < 1.2
    hx, hy = 300, (370 - 40 * abs(math.sin(t * 12))) if k1 else 300
    d.rounded_rectangle((hx - 40, hy - 90, hx + 40, hy), 20, fill=(240, 200, 170), outline=(0, 0, 0), width=4)
    if k1:
        text(d, 300, 120, "똑똑", 90, YEL, "ma")
    # 고양이 도망
    if t >= 1.0:
        p = ease(clamp((t - 1.0) / 1.0))
        cat(d, 280 + 800 * p, 420 + 170 * p, 0.7, t * 10)
    elif t < 1.0:
        cat(d, 280, 420, 0.65, 0)
    if t > 1.8:
        a = ease(clamp((t - 1.8) / 0.4))
        text(d, 560, 60, "문 '쾅'", int(60 * a) + 1, WHITE, "ma")
    if t > 2.3:
        a = ease(clamp((t - 2.3) / 0.4))
        text(d, 860, 60, "경적 '빵'", int(60 * a) + 1, WHITE, "ma")


run("heat", 3.2, draw_heat)
run("belt", 3.2, draw_belt)
run("knock", 3.2, draw_knock)
print("ok", OUT)
