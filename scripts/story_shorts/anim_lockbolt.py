#!/usr/bin/env python3
"""흔들어도 안 풀리는 볼트(록볼트·허크볼트) — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.03 오늘의쓸모.
  python3 scripts/story_shorts/anim_lockbolt.py <출력폴더>
  → loosen.mp4 (옆에서 본 볼트·너트: 철판이 옆으로 흔들릴 때마다 너트가 조금씩 돌아 내려가며 조임 힘 게이지가 줄어듦)
    swage.mp4  (단면: 홈 파인 핀 + 매끈한 고리 → 공구가 핀을 당기며 고리를 홈에 '꾹' 눌러 박음 → 꼬리 '툭')
    where.mp4  (화물열차·트럭 실루엣에 볼트 점이 하나씩 박힘 — '해군·화물열차용으로 개발')
근거: Junker test(1969, 가로 진동에서 볼트 체결이 조임 힘을 잃는 시험),
      Fastfix Technology 'Lockbolt benefits'(홈 파인 핀 + 매끈한 고리를 홈에 압착, 진동에 안 풀려 다시 조일 필요 없음,
      미 해군·화물열차 시장용으로 개발), Ovesco 'How strong are HUCK bolts'(1950년대 Louis C. Huck 개발, 너트 대신 압착 고리).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (24, 30, 40); STEEL = (150, 160, 172); STEEL_D = (96, 104, 116); STEEL_L = (205, 212, 222)
PLATE = (70, 110, 150); PLATE_D = (48, 80, 112); WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (232, 60, 52)
GREEN = (80, 200, 120); TOOL = (40, 42, 46)
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


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    d.polygon([(x1, y1), (x1 - head * math.cos(a - 0.45), y1 - head * math.sin(a - 0.45)),
               (x1 - head * math.cos(a + 0.45), y1 - head * math.sin(a + 0.45))], fill=col)


# ── 1. 너트가 풀리는 장면 ───────────────────────────────────────────
def loosen(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 26, "보통 볼트 + 너트", 54, YEL)
    sh = math.sin(t * 2 * math.pi * 3.2) * 26 * clamp(t / 0.3)      # 옆으로 흔들림
    turn = clamp((t - 0.3) / 2.5)                                     # 0→1 풀림 정도
    cx, top = 430, 150
    # 철판 두 장(위 판은 흔들림)
    d.rectangle((cx - 300 + sh, 330, cx + 300 + sh, 390), fill=PLATE, outline=PLATE_D, width=4)
    d.rectangle((cx - 300, 392, cx + 300, 452), fill=PLATE, outline=PLATE_D, width=4)
    for k in (-1, 1):
        arrow(d, cx + k * 330 + sh, 360, cx + k * 400 + sh, 360, WHITE, 8, 20)
    bx = cx + sh * 0.5
    # 볼트 머리·몸통(나사산)
    d.rectangle((bx - 70, top + 120, bx + 70, 330), fill=STEEL, outline=STEEL_D, width=4)
    d.rectangle((bx - 30, 452, bx + 30, 690), fill=STEEL_L)
    for yy in range(462, 690, 16):
        d.line((bx - 30, yy, bx + 30, yy + 8), fill=STEEL_D, width=4)
    # 너트: 돌면서 아래로 내려감
    ny = 452 + 120 * ease(turn)
    d.rectangle((bx - 75, ny, bx + 75, ny + 70), fill=STEEL, outline=STEEL_D, width=4)
    ang = turn * 2.6 * math.pi
    for k in range(3):                                                 # 도는 모서리 무늬
        x = bx + 60 * math.sin(ang + k * 2 * math.pi / 3)
        if math.cos(ang + k * 2 * math.pi / 3) > 0:
            d.line((x, ny + 4, x, ny + 66), fill=STEEL_D, width=5)
    if turn > 0.05:
        gap = ny - 452
        if gap > 8:
            d.rectangle((bx - 90, 452, bx + 90, ny), outline=RED, width=4)
            ctext(d, bx + 210, ny - 10, "틈!", 52, RED)
        ctext(d, bx - 230, 560, "빙글…", 50, YEL)
    # 조임 힘 게이지
    gx, gy = 820, 170
    ctext(d, gx + 60, gy - 10, "조임 힘", 40)
    d.rectangle((gx + 20, gy + 50, gx + 100, gy + 470), outline=WHITE, width=4)
    lvl = 1 - 0.92 * ease(turn)
    col = GREEN if lvl > 0.6 else YEL if lvl > 0.3 else RED
    d.rectangle((gx + 26, gy + 464 - 408 * lvl, gx + 94, gy + 464), fill=col)
    ctext(d, gx + 60, gy + 480, f"{int(lvl * 100)}%", 52, col)


# ── 2. 록볼트를 박는 단면 ───────────────────────────────────────────
GROOVES = [(x, x + 22) for x in range(560, 760, 40)]                  # 핀 홈(가로 위치)


def swage(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 22, "록볼트 (단면)", 54, YEL)
    pull = ease(clamp((t - 0.5) / 0.9))            # 공구가 당김
    sq = ease(clamp((t - 0.9) / 0.8))              # 고리가 눌림
    snap = clamp((t - 1.9) / 0.6)                  # 꼬리 끊김
    cy = 400
    # 철판 두 장(세로)
    d.rectangle((300, 180, 400, 620), fill=PLATE, outline=PLATE_D, width=4)
    d.rectangle((402, 180, 502, 620), fill=PLATE, outline=PLATE_D, width=4)
    ctext(d, 400, 640, "철판 2장", 38)
    off = -40 * pull                                # 핀이 오른쪽 공구 쪽으로 당겨짐(머리는 판에 밀착)
    # 핀 머리
    d.rounded_rectangle((220, cy - 90, 300, cy + 90), 18, fill=STEEL, outline=STEEL_D, width=4)
    # 핀 몸통(홈 포함) 300→780
    d.rectangle((300, cy - 40, 780, cy + 40), fill=STEEL_L, outline=STEEL_D, width=3)
    for a, b in GROOVES:
        d.rectangle((a, cy - 40, b, cy - 28), fill=STEEL_D)
        d.rectangle((a, cy + 28, b, cy + 40), fill=STEEL_D)
    # 꼬리(핀테일) 780→990 : 끊기면 날아감
    tx = 0 if snap <= 0 else 260 * snap
    ty = 0 if snap <= 0 else -180 * snap + 260 * snap * snap
    tail_box = (790 + tx, cy - 32 + ty, 990 + tx, cy + 32 + ty)
    d.rectangle(tail_box, fill=STEEL_L, outline=STEEL_D, width=3)
    if snap > 0 and snap < 0.6:
        ctext(d, 820, 220, "툭!", 76, YEL, 6)
    # 고리(칼라): 바깥 두께가 줄어들며 안쪽이 홈으로 파고듦
    cx0, cx1 = 510, 770
    th = 70 - 26 * sq
    for s in (-1, 1):
        y_out = cy + s * (40 + th)
        pts = [(cx0, cy + s * 40), (cx0, y_out), (cx1, y_out), (cx1, cy + s * 40)]
        d.polygon(pts, fill=(196, 150, 70), outline=(120, 86, 30))
        if sq > 0.05:                                # 눌린 고리 금속이 홈 안으로 흘러 들어감
            for a, b in GROOVES:
                if a >= cx0 and b <= cx1:
                    depth = 12 * sq
                    if s < 0:
                        d.rectangle((a, cy - 40, b, cy - 40 + depth), fill=(196, 150, 70))
                    else:
                        d.rectangle((a, cy + 40 - depth, b, cy + 40), fill=(196, 150, 70))
    # 공구 코(오른쪽에서 고리를 감쌈)
    nose_x = 800 - 40 * pull
    if snap < 0.3:
        for s in (-1, 1):
            d.rectangle((nose_x - 40, cy + s * 170 - 60, 1080, cy + s * 170 + 60), fill=TOOL)
            d.polygon([(nose_x - 40, cy + s * 110), (nose_x - 40, cy + s * (40 + th + 6)),
                       (nose_x + 20, cy + s * (40 + th + 6)), (nose_x + 20, cy + s * 110)], fill=TOOL)
        ctext(d, (nose_x + 1080) / 2, cy + 170 - 30, "공구", 40, STEEL_L, 4)
    # 라벨
    if t < 0.9:
        ctext(d, 680, 150, "홈 파인 핀 + 매끈한 고리", 44)
    elif t < 2.0:
        arrow(d, 960, 700, 1060, 700, YEL, 12, 30)
        ctext(d, 880, 680, "당김", 44, YEL)
        arrow(d, 640, cy - 200, 640, cy - 120 - 10 * sq, YEL, 12, 30)
        arrow(d, 640, cy + 200, 640, cy + 120 + 10 * sq, YEL, 12, 30)
        ctext(d, 640, 120, "고리를 '꾹'", 54, YEL)
    else:
        ctext(d, 520, 690, "고리가 홈에 박혀 → 돌 수가 없다", 46, GREEN)


# ── 3. 쓰이는 곳 ───────────────────────────────────────────────────
def where(img, t):
    d = ImageDraw.Draw(img)
    # 화물열차(위)
    a = ease(clamp(t / 0.5))
    x0 = -600 + 660 * a
    d.rectangle((x0, 120, x0 + 520, 300), fill=(120, 60, 50), outline=(70, 30, 25), width=5)
    for k in range(5):
        d.line((x0 + 20 + k * 120, 125, x0 + 20 + k * 120, 295), fill=(90, 44, 36), width=6)
    d.rectangle((x0 - 10, 300, x0 + 530, 325), fill=(60, 60, 64))
    for wx in (60, 140, 380, 460):
        d.ellipse((x0 + wx - 34, 310, x0 + wx + 34, 378), fill=(40, 40, 44), outline=STEEL, width=5)
    ctext(d, x0 + 260, 385, "화물열차", 46)
    # 트럭(아래)
    b = ease(clamp((t - 0.4) / 0.5))
    x1 = 1100 - 640 * b
    d.rectangle((x1, 470, x1 + 380, 610), fill=(200, 205, 215), outline=STEEL_D, width=4)
    d.polygon([(x1 + 390, 500), (x1 + 500, 500), (x1 + 540, 560), (x1 + 540, 610), (x1 + 390, 610)], fill=(70, 130, 200))
    d.rectangle((x1 - 10, 610, x1 + 550, 630), fill=(60, 60, 64))           # 뼈대(프레임)
    for wx in (60, 140, 460):
        d.ellipse((x1 + wx - 36, 612, x1 + wx + 36, 684), fill=(40, 40, 44), outline=STEEL, width=5)
    ctext(d, x1 + 270, 690, "트럭", 46)
    # 볼트 점이 하나씩 '팍'
    dots = [(x0 + 20 + k * 120, 312) for k in range(5)] + [(x1 + 20 + k * 105, 620) for k in range(6)]
    for i, (x, y) in enumerate(dots):
        p = clamp((t - 1.0 - i * 0.09) / 0.15)
        if p > 0:
            r = 15 + 12 * (1 - p)
            d.ellipse((x - r, y - r, x + r, y + r), fill=YEL, outline=(0, 0, 0), width=2)
    if t > 1.0:
        ctext(d, 820, 40, "처음엔 해군·화물열차용", 42, YEL)


run("loosen", 3.0, loosen)
run("swage", 3.2, swage)
run("where", 3.0, where)
print("ok")
