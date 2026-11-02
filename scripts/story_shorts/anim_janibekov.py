#!/usr/bin/env python3
"""자니베코프 효과(중간축 정리) 모션그래픽 — 카드 영상 칸 1080x780 — 2026.11.02 오늘의쓸모.
  python3 scripts/story_shorts/anim_janibekov.py <출력폴더>
  → nut.mp4   (1985 살류트 7호: 자니베코프가 풀어 놓은 나비너트가 혼자 돌다 반 바퀴씩 '휙' 뒤집힘 — 실제 강체 운동 방정식으로 계산)
    axes.mp4  (폰 모양 상자를 세 축으로 돌림: 긴 축 ✓, 납작한 축 ✓, 가운데 축만 뒤집힘 ✗)
    earth.mp4 ('지구도 뒤집힌다?' 소문 → 지구는 가장 안정한 축(관성 모멘트 최대)으로 돌아서 안 뒤집힘)
근거: thatsmaths 'The Intermediate Axis Theorem'(2019, 1985 살류트-7 나비너트·지구는 최대 관성축 회전·휴대폰 예),
      COMSOL 블로그 'Why Do Tennis Rackets Tumble?', Wolfram 블로그(2020) 무중력 시뮬레이션.
움직임은 오일러 강체 방정식(I1 w1' = (I2-I3) w2 w3 …)을 RK4 로 적분해 그린 것(연출 아님).
"""
import math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (14, 18, 34); WHITE = (250, 250, 252); RED = (238, 56, 50); YEL = (255, 210, 60); GRN = (70, 210, 120)
GREY = (150, 160, 180); STEEL = (190, 196, 206); BLUE = (70, 140, 230)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS, i)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def stars(d, seed=3):
    rng = np.random.default_rng(seed)
    for x, y, r in zip(rng.uniform(0, W, 90), rng.uniform(0, H, 90), rng.uniform(1, 2.6, 90)):
        d.ellipse((x - r, y - r, x + r, y + r), fill=(90, 100, 130))


# ---------- 강체 시뮬레이션 ----------
def inertia(boxes):
    """boxes: [(center(3), half(3))] 같은 밀도 상자들의 관성 모멘트(대각)."""
    I = np.zeros(3)
    for c, h in boxes:
        c = np.array(c, float); h = np.array(h, float)
        m = 8 * h[0] * h[1] * h[2]
        a2 = (2 * h) ** 2
        Ic = m / 12 * np.array([a2[1] + a2[2], a2[0] + a2[2], a2[0] + a2[1]])
        I += Ic + m * np.array([c[1] ** 2 + c[2] ** 2, c[0] ** 2 + c[2] ** 2, c[0] ** 2 + c[1] ** 2])
    return I


def simulate(I, w0, dur, sub=40):
    """프레임마다 회전 행렬(몸체→공간) 목록."""
    I = np.array(I, float); w = np.array(w0, float); R = np.eye(3)
    dt = 1.0 / FPS / sub
    f = lambda w: np.array([(I[1] - I[2]) * w[1] * w[2] / I[0], (I[2] - I[0]) * w[2] * w[0] / I[1], (I[0] - I[1]) * w[0] * w[1] / I[2]])
    out = []
    for _ in range(int(dur * FPS) + 1):
        out.append(R.copy())
        for _ in range(sub):
            k1 = f(w); k2 = f(w + dt / 2 * k1); k3 = f(w + dt / 2 * k2); k4 = f(w + dt * k3)
            wm = w + dt / 2 * k1
            w = w + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            th = np.linalg.norm(wm) * dt
            if th > 0:
                k = wm / np.linalg.norm(wm)
                K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
                R = R @ (np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K)
    return out


VIEW = None


def view(tilt=-0.42, yaw=0.5):
    cy, sy, ct, st = math.cos(yaw), math.sin(yaw), math.cos(tilt), math.sin(tilt)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])
    return Rx @ Ry


LIGHT = np.array([-0.4, -0.7, -0.6]); LIGHT /= np.linalg.norm(LIGHT)
FACES = [((0, 1, 3, 2), (-1, 0, 0)), ((4, 6, 7, 5), (1, 0, 0)), ((0, 4, 5, 1), (0, -1, 0)),
         ((2, 3, 7, 6), (0, 1, 0)), ((0, 2, 6, 4), (0, 0, -1)), ((1, 5, 7, 3), (0, 0, 1))]


def draw_boxes(d, boxes, R, cx, cy, scale, V, face_cols=None):
    """boxes: [(center, half, color)] → 정사영(화면 y 아래, z 는 화면 안쪽 깊이)."""
    polys = []
    M = V @ R
    for bi, (c, h, col) in enumerate(boxes):
        c = np.array(c, float); h = np.array(h, float)
        verts = [c + h * np.array([sx, sy, sz]) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        P = [M @ v for v in verts]
        for fi, (idx, n) in enumerate(FACES):
            nn = M @ np.array(n, float)
            if nn[2] > 0:   # 화면 안쪽을 향한 면은 안 그림(시점은 -z 쪽)
                continue
            depth = sum(P[i][2] for i in idx) / 4
            lam = max(0.0, -float(nn @ LIGHT))
            base = face_cols[bi][fi] if face_cols and face_cols[bi] else col
            sh = tuple(int(min(255, ch * (0.45 + 0.65 * lam))) for ch in base)
            pts = [(cx + P[i][0] * scale, cy + P[i][1] * scale) for i in idx]
            polys.append((depth, pts, sh))
    for depth, pts, sh in sorted(polys, key=lambda q: -q[0]):
        d.polygon(pts, fill=sh, outline=(20, 22, 30))


# ---------- 1. 나비너트(T자 손잡이 모양으로 단순화) ----------
_raw = [((0, 0, 0), (0.70, 0.10, 0.10)),          # 가로 막대(날개)
        ((0, 0.42, 0), (0.10, 0.34, 0.10))]       # 가운데 몸통(볼트 구멍 쪽)
_m = [8 * h[0] * h[1] * h[2] for c, h in _raw]
_com = sum(np.array(c) * m for (c, h), m in zip(_raw, _m)) / sum(_m)
NUTB = [(tuple(np.array(c) - _com), h) for c, h in _raw]
I_NUT = inertia(NUTB)
MID = int(np.argsort(I_NUT)[1])
NUT = [(NUTB[0][0], NUTB[0][1], STEEL), (NUTB[1][0], NUTB[1][1], (255, 160, 50))]
w0 = np.full(3, 0.10); w0[MID] = 2 * math.pi * 1.5
NUT_R = simulate(I_NUT, w0, 3.4)


def nut(img, t, i):
    d = ImageDraw.Draw(img); stars(d)
    V = view(-0.3, 0.25)
    draw_boxes(d, NUT, NUT_R[i], 540, 400, 300, V)
    d.rounded_rectangle((30, 26, 560, 150), 18, fill=(10, 14, 26), outline=(70, 80, 110), width=3)
    ctext(d, 295, 34, "1985 · 소련 우주정거장 살류트 7호", 30, fill=GREY, stroke=0)
    ctext(d, 295, 78, "자니베코프가 푼 '나비너트'", 44, fill=YEL, stroke=0)
    # 주황 몸통이 위/아래 어느 쪽을 향하는지 — 뒤집힐 때마다 바뀜
    v = V @ NUT_R[i] @ np.array([0, 1.0, 0])
    up = v[1] < 0
    d.rounded_rectangle((700, 40, 1050, 130), 18, fill=(10, 14, 26), outline=(255, 160, 50), width=3)
    ctext(d, 875, 52, "주황 쪽: " + ("위" if up else "아래"), 46, fill=(255, 160, 50), stroke=0)


# ---------- 2. 세 축 ----------
PHONE = [((0, 0, 0), (0.62, 0.32, 0.07), (60, 64, 76))]
I_PH = inertia([(c, h) for c, h, _ in PHONE])     # x 가장 작음, y 가운데, z 가장 큼
PH_FACE = [[(60, 64, 76), (60, 64, 76), (60, 64, 76), (60, 64, 76), (40, 120, 220), (60, 64, 76)]]   # 화면(-z)은 파랑


def ph_sim(axis, eps=0.06, dur=3.4, rate=1.25):
    w = np.full(3, eps); w[axis] = 2 * math.pi * rate
    return simulate(I_PH, w, dur)


PH = [ph_sim(0), ph_sim(2), ph_sim(1, eps=0.12)]
AX_COL = [GRN, GRN, RED]
AX_NAME = ["긴 축", "납작한 축", "가운데 축"]
AX_VEC = [np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, 1.0, 0])]


def axes(img, t, i):
    d = ImageDraw.Draw(img); stars(d, 5)
    V = view(-0.5, 0.6)
    for k in range(3):
        cx = 190 + k * 350; cy = 380
        show = t > k * 0.35
        d.rounded_rectangle((cx - 165, 120, cx + 165, 700), 22, outline=AX_COL[k] if show else (50, 56, 70), width=4)
        if not show:
            continue
        j = i - int(k * 0.35 * FPS)
        R = PH[k][max(0, j)]
        # 회전축(공간에 고정된 처음 축 방향)
        a = V @ AX_VEC[k]
        d.line((cx - a[0] * 170, cy - a[1] * 170, cx + a[0] * 170, cy + a[1] * 170), fill=(*AX_COL[k],), width=5)
        draw_boxes(d, PHONE, R, cx, cy, 200, V, PH_FACE)
        ctext(d, cx, 140, AX_NAME[k], 40, fill=AX_COL[k], stroke=4)
        if t > 1.6 + k * 0.2:
            ctext(d, cx, 600, "안정" if k < 2 else "뒤집힘!", 46, fill=AX_COL[k], stroke=4)
    if t > 2.2:
        ctext(d, 540, 30, "가운데 축으로 돌면 '반드시' 뒤집힌다", 46, fill=YEL)


# ---------- 3. 지구 ----------
def earth(img, t, i):
    d = ImageDraw.Draw(img); stars(d, 9)
    cx, cy, rx, ry = 540, 430, 230, 218        # 살짝 납작한 지구
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(30, 90, 170))
    # 대륙 무늬 대신 회전하는 경선
    for k in range(10):
        lon = (k / 10) * 2 * math.pi + t * 1.6
        c = math.cos(lon)
        if math.sin(lon) < 0:
            continue
        w = abs(c) * rx
        d.ellipse((cx - w, cy - ry, cx + w, cy + ry), outline=(70, 160, 110), width=3)
    for lat in (-0.5, 0, 0.5):
        y = cy + lat * ry * 1.6
        hw = rx * math.sqrt(max(0, 1 - (lat * 1.6) ** 2))
        d.line((cx - hw, y, cx + hw, y), fill=(70, 160, 110), width=2)
    d.line((cx, cy - ry - 90, cx, cy + ry + 60), fill=GRN, width=7)
    d.polygon([(cx, cy - ry - 120), (cx - 20, cy - ry - 84), (cx + 20, cy - ry - 84)], fill=GRN)
    # 소문 → X
    k = ease(clamp(t / 0.5))
    ctext(d, 540, 24, "\"지구도 언젠가 뒤집힌다?\"", 56, fill=WHITE)
    if t > 0.9:
        x0, x1 = 170, 910
        p = ease(clamp((t - 0.9) / 0.35))
        d.line((x0, 58, x0 + (x1 - x0) * p, 58), fill=RED, width=10)
    if t > 1.4:
        d.rounded_rectangle((640, 560, 1060, 740), 18, fill=(10, 14, 26), outline=GRN, width=4)
        ctext(d, 850, 574, "지구가 도는 축", 40, fill=GREY, stroke=0)
        ctext(d, 850, 640, "= 가장 안정한 축", 52, fill=GRN, stroke=0)


run("nut", 3.2, nut)
run("axes", 3.2, axes)
run("earth", 3.0, earth)
print("ok", I_NUT, I_PH)
