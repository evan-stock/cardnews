#!/usr/bin/env python3
"""JAL516 하네다 화재 탈출 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.02 오늘의쓸모.
  python3 scripts/story_shorts/anim_jal516.py <출력폴더>
  → exits.mp4 (위에서 본 A350, 문 8개 중 5개에 X → 앞 2개·뒤 왼쪽 1개만 열려 사람 점이 줄줄이 빠져나감, '3 / 8')
    aisle.mp4 (통로 두 줄 비교: 빈손 줄은 술술, 가방 꺼내는 사람이 선 줄은 뒤가 꽉 막힘)
    busan.mp4 (2025.1.28 김해 에어부산 화재 — 선반에서 가방 꺼내는 사람 때문에 통로가 막힘, 176명은 모두 탈출)
근거: Reuters 'Inside the escape from Flight JL516'(367+12=379명, 8개 문 중 3개만 사용, 기내 방송 고장, 승객들은 짐을 두고 나옴),
      Reuters 2024.1.3(17:47 충돌 → 18:05 전원 탈출), NYT 승객 영상('Leave your bags behind!'),
      뉴시스 2025.1.31·위키트리(에어부산 BX391 176명 탈출, 짐 꺼내던 승객이 통로를 막아 비판).
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (18, 22, 34); TARMAC = (44, 48, 58); BODY = (236, 238, 244); EDGE = (150, 158, 175)
WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); GRN = (60, 210, 110)
FIRE = (255, 120, 30); PERSON = (255, 220, 120); BAG = (90, 140, 230); GREY = (120, 126, 140)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(5)


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def xmark(d, x, y, r, a=1.0):
    r = r * a
    d.line((x - r, y - r, x + r, y + r), fill=RED, width=12)
    d.line((x + r, y - r, x - r, y + r), fill=RED, width=12)


def flames(d, cx, cy, sz, t, n=9):
    for k in range(n):
        ph = t * 7 + k * 1.7
        x = cx + (k - n / 2) * sz * 0.22 + 6 * math.sin(ph)
        h = sz * (0.6 + 0.4 * math.sin(ph * 1.3))
        d.polygon([(x - sz * 0.16, cy), (x + sz * 0.16, cy), (x + 4 * math.sin(ph), cy - h)], fill=FIRE)
        d.polygon([(x - sz * 0.08, cy), (x + sz * 0.08, cy), (x, cy - h * 0.55)], fill=YEL)


# ---------- 1. 문 8개 중 3개 ----------
PX0, PX1, PY = 120, 960, 400      # 동체 앞(왼쪽=기수)~뒤, 중심선
PH = 64                           # 동체 반폭
DOORS = {  # 이름: (x, 위(L)=-1/아래(R)=+1)
    "L1": (190, -1), "R1": (190, 1), "L2": (360, -1), "R2": (360, 1),
    "L3": (640, -1), "R3": (640, 1), "L4": (880, -1), "R4": (880, 1)}
OPEN = ("L1", "R1", "L4")


def plane(d):
    # 날개·꼬리날개
    d.polygon([(470, PY - PH), (600, PY - PH), (700, PY - 330), (640, PY - 330)], fill=BODY, outline=EDGE)
    d.polygon([(470, PY + PH), (600, PY + PH), (700, PY + 330), (640, PY + 330)], fill=BODY, outline=EDGE)
    d.polygon([(900, PY - 20), (960, PY - 20), (1010, PY - 150), (985, PY - 150)], fill=BODY, outline=EDGE)
    d.polygon([(900, PY + 20), (960, PY + 20), (1010, PY + 150), (985, PY + 150)], fill=BODY, outline=EDGE)
    # 동체
    d.rounded_rectangle((PX0, PY - PH, PX1, PY + PH), 60, fill=BODY, outline=EDGE, width=3)
    d.ellipse((PX0 - 40, PY - PH, PX0 + 90, PY + PH), fill=BODY, outline=EDGE, width=3)
    d.rectangle((PX0 + 20, PY - PH + 3, PX0 + 60, PY + PH - 3), fill=BODY)
    # 좌석 줄
    for x in range(250, 900, 26):
        d.line((x, PY - PH + 14, x, PY - 10), fill=(200, 205, 215), width=4)
        d.line((x, PY + 10, x, PY + PH - 14), fill=(200, 205, 215), width=4)


def exits(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=TARMAC)
    plane(d)
    # 뒤쪽·가운데에 불·연기
    flames(d, 560, PY + PH + 60, 70, t)
    flames(d, 760, PY - PH - 30, 55, t + 1)
    for k, name in enumerate(DOORS):
        x, side = DOORS[name]
        y = PY + side * (PH - 4)
        d.rectangle((x - 22, y - 10, x + 22, y + 10), fill=(70, 80, 100))
    # 막힌 문 5개에 X 하나씩
    shut = [n for n in DOORS if n not in OPEN]
    for k, name in enumerate(shut):
        a = ease(clamp((t - 0.3 - k * 0.18) / 0.25))
        if a > 0:
            x, side = DOORS[name]
            xmark(d, x, PY + side * (PH + 34), 26, a)
    # 열린 문 3개: 초록 + 미끄럼틀 + 사람 점
    go = clamp((t - 1.3) / 0.3)
    if go > 0:
        for name in OPEN:
            x, side = DOORS[name]
            y0 = PY + side * PH
            d.polygon([(x - 26, y0), (x + 26, y0), (x + 34, y0 + side * 150), (x - 34, y0 + side * 150)], fill=YEL)
            d.rectangle((x - 22, y0 - side * 4 - 10, x + 22, y0 - side * 4 + 10), fill=GRN)
            for q in range(7):
                ph = (t * 1.6 + q / 7) % 1.0
                yy = y0 + side * (ph * 230 - 40)
                if (t - 1.3) * 1.6 > ph:
                    d.ellipse((x - 9, yy - 9, x + 9, yy + 9), fill=PERSON)
    # 숫자
    d.rounded_rectangle((40, 30, 400, 150), 18, fill=(12, 16, 26))
    n = min(3, int(max(0, t - 1.3) * 6) + (1 if t > 1.3 else 0))
    ctext(d, 220, 30, "쓸 수 있는 문", 30, fill=(180, 190, 210), stroke=0)
    ctext(d, 220, 64, f"{n if t > 1.3 else '?'} / 8", 62, fill=GRN if t > 1.3 else WHITE, stroke=0)
    if t > 1.0:
        ctext(d, 740, 40, "기내 방송도 고장", 40, fill=YEL)


# ---------- 2. 빈손 vs 가방 ----------
def lane(d, y, t, blocked):
    d.rounded_rectangle((60, y - 55, 1020, y + 55), 20, fill=(34, 40, 56), outline=(80, 90, 110), width=3)
    d.rectangle((990, y - 50, 1040, y + 50), fill=GRN)  # 출구
    ctext(d, 1015, y - 22, "문", 30, stroke=0)
    stop_x = 640
    for k in range(10):
        base = 120 + k * 80 - (0 if blocked else 0)
        if not blocked:
            x = base + t * 260
            x = 80 + (x - 80) % 940
        else:
            # 가방 든 사람(맨 앞)은 stop_x 에서 멈춤, 뒤는 줄줄이 밀착
            lead = min(stop_x, 300 + t * 260)
            x = min(base + t * 260, lead - (9 - k) * 0) if k == 9 else min(base + t * 260, lead - (9 - k) * 34)
        col = PERSON
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=col)
        if blocked and k == 9:
            # 가방 끌어내리는 사람 — 가방이 흔들림
            sh = 6 * math.sin(t * 14)
            d.rounded_rectangle((x - 30, y - 50 + sh, x + 10, y - 20 + sh), 6, fill=BAG)
    if blocked and t > 1.2:
        d.rectangle((60, y - 55, 640, y + 55), outline=RED, width=6)


def aisle(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, 300, 70, "빈손", 48, fill=GRN)
    lane(d, 240, t, False)
    ctext(d, 300, 400, "짐 꺼내는 사람 1명", 44, fill=YEL)
    lane(d, 570, t, True)
    if t > 1.4:
        ctext(d, 340, 650, "뒤에 선 사람이 다 멈춘다", 44, fill=RED)


# ---------- 3. 2025 김해 에어부산 ----------
def busan(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 28, 720, 150), 18, fill=(12, 16, 26))
    ctext(d, 380, 36, "2025.1.28 김해공항 에어부산", 38, fill=WHITE, stroke=0)
    ctext(d, 380, 88, "선반 쪽에서 불 → 176명 탈출", 34, fill=(190, 200, 220), stroke=0)
    # 기내 단면(통로 옆에서 본 모습): 선반, 좌석, 통로
    d.rectangle((60, 190, 1020, 230), fill=(70, 78, 96))           # 선반
    for x in range(80, 1000, 120):
        d.rectangle((x, 194, x + 100, 226), outline=(110, 120, 140), width=2)
    flames(d, 930, 196, 60, t)                                       # 뒤쪽 선반 불
    d.rectangle((60, 600, 1020, 640), fill=(60, 64, 80))             # 바닥
    d.rectangle((0, 380, 50, 600), fill=GRN)                          # 출구(왼쪽)
    ctext(d, 25, 460, "문", 28, stroke=0)
    # 사람들: 오른쪽(불)에서 왼쪽(문)으로 — 가운데 사람이 가방을 끌어내리며 멈춤
    bx = 470
    pull = ease(clamp((t - 0.4) / 0.8))
    for k in range(9):
        x0 = 980 - k * 40
        x = max(x0 - t * 240, bx + 60 + (8 - k) * 0) if k < 8 else bx
        if k < 8:
            x = max(x0 - t * 260, bx + 58 + (7 - k) * 46)
        d.ellipse((x - 22, 430, x + 22, 474), fill=PERSON)          # 머리
        d.rounded_rectangle((x - 26, 478, x + 26, 590), 12, fill=(200, 160, 90))
    # 가방 끄는 사람
    d.ellipse((bx - 22, 430, bx + 22, 474), fill=PERSON)
    d.rounded_rectangle((bx - 26, 478, bx + 26, 590), 12, fill=(200, 160, 90))
    by = 196 + pull * 260
    d.rounded_rectangle((bx - 70, by, bx - 10, by + 80), 10, fill=BAG, outline=(40, 70, 140), width=3)
    if t > 1.3:
        d.rectangle((bx - 90, 400, 1000, 600), outline=RED, width=6)
        ctext(d, 700, 300, "통로 '꽉'", 64, fill=RED)
    if t > 2.0:
        ctext(d, 540, 670, "'국민 빌런' 비판", 48, fill=YEL)


run("exits", 3.2, exits)
run("aisle", 3.2, aisle)
run("busan", 3.2, busan)
print("ok")
