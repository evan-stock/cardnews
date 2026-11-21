# 코드만으로 찍는 도트 배경: 180x320 캔버스, 팔레트 + 바이어 디더링 + 원근, 4배 확대
import sys, math, random
from PIL import Image
W, H = 180, 320
random.seed(3)
im = Image.new('RGB', (W, H)); P = im.load()
B4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def ramp(*cs): return [hx(c) for c in cs]
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: P[x, y] = c
def dith(x, y, r, t):
    # t 0..1 → 램프의 두 색 사이를 바이어 행렬로 섞음
    t = max(0, min(0.9999, t)) * (len(r) - 1); i = int(t); f = t - i
    return r[i + 1] if f * 16 > B4[y % 4][x % 4] + 0.5 else r[i]
def fill(x0, y0, x1, y1, fn):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)): put(x, y, fn(x, y))
def poly(pts, fn):
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            if (y0 <= y < y1) or (y1 <= y < y0): xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(int(round(a)), int(round(b))): put(x, y, fn(x, y))
def line(x0, y0, x1, y1, c):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1): t = i / n; put(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), c)
def ell(cx, cy, rx, ry, fn):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: put(x, y, fn(x, y))

WALL = ramp('#5a4a3c', '#7d6650', '#a38a6a', '#c9b08a', '#e8d4a8')
CEIL = ramp('#6e6458', '#948a78', '#bab09a', '#ddd4bc')
FLOOR = ramp('#2c2c34', '#44444f', '#5f606c', '#80828e', '#a3a6b0')
SKY = ramp('#ffd9a0', '#ffe9c4', '#cfe6f2', '#9cc8e8')
BOARD = ramp('#0f2a20', '#173a2c', '#22503c', '#2f6a4e')
WOOD = ramp('#4a2c18', '#7a4a26', '#a8693a', '#cf8f52', '#efb878')
METAL = ramp('#1e2026', '#3a3e48', '#5c6270', '#8a92a2')
NAVY = ramp('#121a30', '#1e2c4e', '#2e4372', '#45619a')
HAIR = ramp('#0b0b10', '#1c1c26', '#33333f', '#4e4e60')
SKIN = ramp('#7a4632', '#b87456', '#e0a07c', '#f6c9a2', '#ffe2c4')
PAPER = ramp('#9c9a90', '#c9c6ba', '#e9e6da', '#fffdf4')
TEAL = ramp('#0e3a3c', '#17595a', '#22807c', '#3aa79c')
VX, VY = 92, 150  # 소실점
# 천장·벽·바닥 큰 면 (빛: 왼쪽 창에서)
fill(0, 0, W, 60, lambda x, y: dith(x, y, CEIL, 0.35 + y / 60 * 0.5 - abs(x - VX) / 400))
fill(0, 60, W, 178, lambda x, y: dith(x, y, WALL, 0.75 - (x / W) * 0.45 - (y - 60) / 600))
fill(0, 178, W, H, lambda x, y: dith(x, y, FLOOR, 0.25 + (y - 178) / 260 + (1 - x / W) * 0.25))
line(0, 60, W, 60, CEIL[0]); line(0, 178, W, 178, WALL[0])
for i in range(-9, 11):  # 바닥 타일선(원근)
    x = VX + i * 60; line(VX + i * 6, 178, x, H, FLOOR[1])
for k in range(1, 7):
    y = 178 + int(150 * (1 - 1 / (1 + k * 0.45))) ; line(0, y, W, y, FLOOR[1])
# 천장 형광등(원근)
for (x, y, w) in ((92, 18, 46), (92, 40, 30), (92, 52, 20)):
    fill(x - w // 2, y, x + w // 2, y + max(2, w // 12), lambda xx, yy: PAPER[3]); line(x - w // 2, y + max(2, w // 12), x + w // 2, y + max(2, w // 12), CEIL[1])
# 왼쪽 창문 + 햇살
for (x0, x1) in ((2, 22), (26, 46)):
    fill(x0, 70, x1, 150, lambda x, y: dith(x, y, SKY, (y - 70) / 80 * 0.9 + 0.05))
    for y in range(70, 150, 3): pass
    fill(x0, 108, x1, 110, lambda x, y: WALL[1]); line(x0 - 1, 69, x1, 69, WALL[0]); line(x0 - 1, 150, x1, 150, WALL[0]); line(x0 - 1, 69, x0 - 1, 150, WALL[0]); line(x1, 69, x1, 150, WALL[0])
    for i in range(6):  # 건물 실루엣
        bx = x0 + 1 + i * 3 + random.randint(0, 2); bh = random.randint(8, 22); fill(bx, 150 - bh, bx + 3, 150, lambda x, y: (150, 160, 180))
poly([(22, 110), (46, 110), (120, 300), (60, 320)], lambda x, y: dith(x, y, [(0, 0, 0), WALL[4]], 0.0) if False else P[x, y])
for y in range(150, H):  # 햇살 띠: 기존 색을 한 단계 밝게(디더)
    for x in range(W):
        a, b = 10 + (y - 150) * 0.55, 40 + (y - 150) * 0.75
        if a < x < b and B4[y % 4][x % 4] < 6:
            r, g, bb = P[x, y]; P[x, y] = (min(255, r + 28), min(255, g + 24), min(255, bb + 14))
# 칠판 + 분필 글씨 + 받침
fill(56, 84, 132, 128, lambda x, y: dith(x, y, BOARD, 0.75 - (x - 56) / 76 * 0.5 + random.random() * 0.08))
line(55, 83, 132, 83, WOOD[1]); line(55, 128, 132, 128, WOOD[1]); line(55, 83, 55, 128, WOOD[1]); line(132, 83, 132, 128, WOOD[1])
fill(54, 128, 134, 131, lambda x, y: dith(x, y, WOOD, 0.6 - (y - 128) * 0.15))
chalk = (226, 232, 220)
for row, (y, n) in enumerate(((90, 9), (99, 14), (106, 11), (113, 16))):
    x = 61
    for _ in range(n):
        w = random.choice((2, 3, 3, 4))
        for i in range(w): put(x + i, y + random.choice((0, 0, 1)), chalk if random.random() > 0.15 else BOARD[3])
        if random.random() > 0.5: put(x + 1, y - 1, chalk)
        x += w + random.choice((1, 2))
for i in range(6): put(120 + i, 125, chalk)  # 지우개 자국
# 시계, 비상구 표시, 문
ell(150, 74, 7, 7, lambda x, y: PAPER[3] if (x - 150) ** 2 + (y - 74) ** 2 < 30 else METAL[1])
line(150, 74, 150, 69, METAL[0]); line(150, 74, 153, 76, (190, 40, 40))
fill(146, 92, 170, 98, lambda x, y: (40, 150, 70)); fill(148, 94, 152, 96, lambda x, y: (230, 255, 230))
poly([(146, 100), (170, 98), (170, 178), (146, 172)], lambda x, y: dith(x, y, NAVY, 0.55 - (x - 146) / 60))
line(146, 100, 170, 98, NAVY[0]); line(146, 100, 146, 172, NAVY[0]); fill(149, 112, 152, 128, lambda x, y: SKY[2]); fill(165, 136, 168, 138, lambda x, y: METAL[3])
# 책상·의자 줄(원근, 뒤→앞)
def desk(cx, y, s):
    w, d = 26 * s, 7 * s
    top = [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 + 2 * s, y + d), (cx - w / 2 - 2 * s, y + d)]
    poly(top, lambda x, yy: dith(x, yy, WOOD, 0.85 - (yy - y) / max(1, d) * 0.35 - (x - cx) / 300))
    line(top[0][0], y, top[1][0], y, WOOD[4]); fill(int(cx - w / 2 - 2 * s), int(y + d), int(cx + w / 2 + 2 * s), int(y + d + max(1, s)), lambda x, yy: WOOD[1])
    for lx in (cx - w / 2, cx + w / 2 - s): fill(int(lx), int(y + d), int(lx + max(1, s)), int(y + d + 13 * s), lambda x, yy: METAL[1])
def student(cx, y, s, hood):
    ell(cx, y - 5 * s, 9 * s, 7 * s, lambda x, yy: dith(x, yy, hood, 0.7 - (x - cx + 9 * s) / (18 * s) * 0.6))
    fill(int(cx - 9 * s), int(y - 5 * s), int(cx + 9 * s + 1), int(y + 4 * s), lambda x, yy: dith(x, yy, hood, 0.7 - (x - cx + 9 * s) / (18 * s) * 0.6))
    ell(cx, y - 15 * s, 5.5 * s, 6 * s, lambda x, yy: dith(x, yy, HAIR, 0.85 - ((x - cx + 3 * s) ** 2 + (yy - y + 19 * s) ** 2) ** 0.5 / (8 * s)))
for (cx, y, s, hood) in ((70, 160, 0.55, TEAL), (114, 160, 0.55, ramp('#4a1e1e', '#7a2e2e', '#a8443e', '#d0645a')),
                         (44, 182, 0.85, ramp('#3a2a0a', '#6a4e12', '#9c761e', '#cfa232')), (140, 182, 0.85, NAVY)):
    student(cx, y, s, hood); desk(cx, y + 2 * s, s)
student(92, 214, 1.4, ramp('#2a1e3a', '#45305e', '#634688', '#8462b0')); desk(92, 218, 1.4)
# 내 책상(전경) + 시험지 + 손
poly([(-10, 262), (W + 10, 262), (W + 10, H), (-10, H)], lambda x, y: dith(x, y, WOOD, 0.75 - (y - 262) / 120 - x / 900))
line(0, 262, W, 262, WOOD[4])
poly([(52, 268), (122, 266), (130, H), (46, H)], lambda x, y: dith(x, y, PAPER, 0.95 - (y - 266) / 300))
for i in range(5):
    y = 280 + i * 8; put(58, y, (60, 60, 70))
    for j in range(4):
        cx = 70 + j * 12; ell(cx, y, 2.5, 2, lambda x, yy: PAPER[0] if not (i < 3 and j == (i * 3) % 4) else (40, 40, 50))
fill(60, 271, 110, 273, lambda x, y: (70, 70, 80))
for sx, hx0 in ((-1, 34), (1, 146)):
    ell(hx0, 312, 22, 15, lambda x, y: dith(x, y, SKIN, 0.75 - ((x - hx0 + sx * 6) ** 2 + (y - 306) ** 2) ** 0.5 / 40))
    fill(hx0 - 22, 316, hx0 + 22, H, lambda x, y: dith(x, y, TEAL, 0.5 - (y - 316) / 30))
line(120, 300, 150, 284, (240, 190, 40)); line(121, 301, 151, 285, (200, 150, 30)); put(119, 301, (40, 40, 40))
# 외곽 어둡게(비네트, 디더)
for y in range(H):
    for x in range(W):
        d = ((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2
        if d > 0.75 and B4[y % 4][x % 4] < (d - 0.75) * 30:
            r, g, b = P[x, y]; P[x, y] = (int(r * 0.75), int(g * 0.72), int(b * 0.8))
im.resize((W * 4, H * 4), Image.NEAREST).save(sys.argv[1]); print('ok')
