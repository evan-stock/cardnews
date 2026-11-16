#!/usr/bin/env python3
"""비행 중 비행기 벽이 통째로 뜯겨 나갔다 — 알래스카항공 1282편 도어 플러그 모션그래픽(영상 칸 1080x780) — 2026.11.06 오늘의쓸모.
  python3 scripts/story_shorts/anim_doorplug.py <출력폴더>
  → plug.mp4  (옆에서 본 동체: 창문 줄 사이 '막아 둔 비상문(도어 플러그)' → 고정 볼트 4개가 없음 → 판이 통째로 떨어져 나감)
    suck.mp4  (동체 단면: 기내 공기(점)가 구멍 밖으로 한꺼번에 빠져나가고 물건이 딸려 나감, 고도 약 4,900m)
    seats.mp4 (좌석 배치도 25~27열: 구멍 바로 옆 26A·26B 는 빈자리, 나머지는 벨트를 맨 채 앉아 있음 → 177명 생존)
근거: NTSB 최종보고서(2025.6) — 도어 플러그 고정 볼트 4개가 보잉 공장 수리 뒤 다시 끼워지지 않음, 고도 약 16,000ft(약 4,900m),
      승객 171명·승무원 6명, 26A·26B 빈자리, 좌석벨트 표시등 켜짐. CBS News 2024.1(10대 승객 셔츠가 뜯겨 나감).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BG = (22, 28, 40)
SKY = (30, 44, 70); BODY = (226, 230, 236); BODY_D = (170, 176, 186); WIN = (40, 56, 80); GREEN = (80, 220, 130); BLUE = (110, 180, 255)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(draw(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=6):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x0, y0, x1, y1, col, w=12):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    p1 = (x1 + L * math.cos(a + 2.6), y1 + L * math.sin(a + 2.6))
    p2 = (x1 + L * math.cos(a - 2.6), y1 + L * math.sin(a - 2.6))
    d.polygon([(x1 + w * 0.6 * math.cos(a), y1 + w * 0.6 * math.sin(a)), p1, p2], fill=col)


def check(d, x, y, s, col):
    d.line([(x, y), (x + s * 0.35, y + s * 0.4), (x + s, y - s * 0.45)], fill=col, width=max(4, int(s / 6)), joint="curve")


# ---------- 1. plug: 옆에서 본 동체 ----------
FY0, FY1 = 250, 560
PX0, PX1, PY0, PY1 = 560, 680, 300, 500   # 도어 플러그 판


def plug(t):
    im = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(im)
    # 천천히 확대(카메라 줌)
    z = 1 + 0.12 * ease(t / 3.0)
    d.rounded_rectangle([-200, FY0, W + 200, FY1], radius=150, fill=BODY)
    d.rectangle([-200, FY1 - 60, W + 200, FY1 - 40], fill=BODY_D)
    for x in range(40, W, 110):
        if PX0 - 60 < x < PX1 + 20:
            continue
        d.rounded_rectangle([x, 360, x + 52, 430], radius=22, fill=WIN)
    fly = ease((t - 1.5) / 1.0)
    if fly <= 0:
        # 판 + 판 속 창문 하나(겉보기엔 평범한 창문)
        d.rectangle([PX0, PY0, PX1, PY1], fill=BODY, outline=YEL if t > 0.3 else BODY_D, width=8 if t > 0.3 else 3)
        d.rounded_rectangle([PX0 + 34, 360, PX0 + 86, 430], radius=22, fill=WIN)
        # 볼트 4개 자리 — 깜빡이는 빨간 X
        if t > 0.8:
            on = int(t * 6) % 2 == 0
            for bx, by in [(PX0 + 14, PY0 + 14), (PX1 - 14, PY0 + 14), (PX0 + 14, PY1 - 14), (PX1 - 14, PY1 - 14)]:
                c = RED if on else (120, 30, 20)
                d.line([(bx - 10, by - 10), (bx + 10, by + 10)], fill=c, width=6)
                d.line([(bx - 10, by + 10), (bx + 10, by - 10)], fill=c, width=6)
    else:
        # 구멍 + 날아가는 판
        d.rectangle([PX0, PY0, PX1, PY1], fill=(8, 10, 16))
        for k in range(6):
            yy = PY0 + 20 + k * 30
            d.line([(PX0 + 6, yy), (PX0 + 6 + 30 * math.sin(t * 20 + k), yy + 10)], fill=(200, 190, 150), width=5)
        ox, oy, rot = 260 * fly, 320 * fly, 70 * fly
        panel = Image.new("RGBA", (PX1 - PX0 + 20, PY1 - PY0 + 20), (0, 0, 0, 0))
        pd = ImageDraw.Draw(panel)
        pd.rectangle([10, 10, PX1 - PX0 + 10, PY1 - PY0 + 10], fill=BODY, outline=YEL, width=8)
        pd.rounded_rectangle([44, 70, 96, 140], radius=22, fill=WIN)
        panel = panel.rotate(-rot, expand=True)
        im.paste(panel, (int(PX0 + ox - 20), int(PY0 + oy - 20)), panel)
    if z != 1:
        cw, ch = W / z, H / z
        cx, cy = (PX0 + PX1) / 2, (FY0 + FY1) / 2
        x0 = max(0, min(W - cw, cx - cw / 2)); y0 = max(0, min(H - ch, cy - ch / 2))
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H))
    d = ImageDraw.Draw(im)
    ctext(d, W / 2, 40, "막아 둔 비상문 = '도어 플러그'", 62, YEL)
    if 0.8 < t < 1.6:
        ctext(d, W / 2, 640, "고정 볼트 4개가 빠진 채", 56, WHITE)
    if t >= 1.6:
        ctext(d, W / 2, 640, "통째로 '뻥'", 64, RED)
    return im


# ---------- 2. suck: 동체 단면 ----------
CX, CY, R = 540, 430, 270
random.seed(3)
DOTS = [(random.uniform(-0.85, 0.85), random.uniform(-0.8, 0.8)) for _ in range(140)]
DOTS = [(x, y) for x, y in DOTS if x * x + y * y < 0.72]
HOLE = (CX + R, CY - 20)


def suck(t):
    im = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(im)
    d.ellipse([CX - R - 18, CY - R - 18, CX + R + 18, CY + R + 18], fill=BODY_D)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=(52, 60, 78))
    d.rectangle([CX - R + 40, CY + 120, CX + R - 40, CY + 140], fill=(90, 96, 110))   # 바닥
    # 구멍(오른쪽 벽)
    open_ = ease(t / 0.4)
    hh = int(70 * open_)
    d.rectangle([CX + R - 10, HOLE[1] - hh, CX + R + 30, HOLE[1] + hh], fill=SKY)
    # 공기 점들이 구멍 쪽으로 빨려 나감
    for i, (x, y) in enumerate(DOTS):
        sx, sy = CX + x * R, CY + y * R
        k = clamp((t - 0.3 - (1 - (x + 1) / 2) * 0.9) / 1.2)
        k = ease(k)
        px = sx + (HOLE[0] + 160 + (i % 7) * 25 - sx) * k
        py = sy + (HOLE[1] + ((i % 5) - 2) * 30 - sy) * k
        if k > 0.88:
            continue
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=BLUE)
    # 화살표
    if t > 0.4:
        for dy in (-60, 0, 60):
            a = ease((t - 0.4) / 0.5)
            arrow(d, CX + 40, CY - 20 + dy, CX + 40 + int(300 * a), HOLE[1] + dy // 3, YEL, 12)
    ctext(d, W / 2, 30, "기압이 높은 안 → 낮은 밖", 58, WHITE)
    ctext(d, 250, 640, "고도 약 4,900m", 50, YEL)
    if t > 1.6:
        ctext(d, 820, 640, "휴대폰·옷까지 밖으로", 46, RED)
        # 날아가는 휴대폰 두 개
        for j in range(2):
            k = ease((t - 1.6 - j * 0.2) / 1.0)
            x = HOLE[0] + 30 + 220 * k; y = HOLE[1] - 40 + j * 70 + 120 * k
            ph = Image.new("RGBA", (40, 70), (0, 0, 0, 0)); pdd = ImageDraw.Draw(ph)
            pdd.rounded_rectangle([0, 0, 39, 69], radius=8, fill=(20, 20, 24), outline=WHITE, width=3)
            ph = ph.rotate(200 * k + j * 40, expand=True)
            im.paste(ph, (int(x), int(y)), ph)
    return im


# ---------- 3. seats: 좌석 배치도 ----------
def seat(d, x, y, col, person, belt):
    d.rounded_rectangle([x, y, x + 92, y + 92], radius=16, fill=col)
    if person:
        d.ellipse([x + 30, y + 10, x + 62, y + 42], fill=(240, 205, 170))
        d.rounded_rectangle([x + 20, y + 40, x + 72, y + 86], radius=12, fill=(70, 110, 170))
        if belt:
            d.line([(x + 14, y + 66), (x + 78, y + 66)], fill=YEL, width=8)


def seats(t):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    rows = [25, 26, 27]
    x0, y0, gap = 240, 170, 108
    cols = ["A", "B", "C", "D", "E", "F"]
    for ri, r in enumerate(rows):
        y = y0 + ri * 150
        ft = F(40); d.text((24, y + 20), str(r), font=ft, fill=WHITE)
        for ci, c in enumerate(cols):
            x = x0 + ci * gap + (70 if ci >= 3 else 0)
            empty = (r == 26 and c in "AB")
            belt = t > 1.6
            if empty:
                hl = ease((t - 0.6) / 0.5)
                col = tuple(int(70 + (v - 70) * hl) for v in GREEN)
                seat(d, x, y, col, False, False)
                if hl > 0.5:
                    d.text((x + 12, y + 22), "빈자리", font=F(28), fill=(10, 30, 15))
            else:
                seat(d, x, y, (90, 98, 116), True, belt)
    # 왼쪽 벽 구멍(26열 창 쪽)
    hy = y0 + 150
    d.rectangle([188, hy - 10, 220, hy + 102], fill=(8, 10, 16))
    for k in range(5):
        arrow(d, 182, hy + 10 + k * 22, 182 - int(60 * ease(t / 0.6)), hy + 10 + k * 22, BLUE, 6)
    ctext(d, W / 2, 40, "구멍 바로 옆 26A·26B", 60, GREEN)
    if t > 1.6:
        ctext(d, W / 2, 660, "나머지는 모두 벨트를 맨 채", 56, YEL)
        check(d, 905, 680, 50, YEL)
    return im


run("plug", 3.0, plug)
run("suck", 3.0, suck)
run("seats", 3.3, seats)
print("ok")
