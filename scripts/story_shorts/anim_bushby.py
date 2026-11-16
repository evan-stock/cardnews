#!/usr/bin/env python3
"""'칠레에서 영국 집까지 걸어서 — 칼 부시비 28년' 모션그래픽(영상 칸 1080x780) — 2026.11.08 오늘의쓸모.
  python3 scripts/story_shorts/anim_bushby.py <출력폴더>
  → rule.mp4  (규칙 하나: 집에 닿을 때까지 비행기·자동차·배 금지 → 오직 두 발)
    route.mp4 (도는 지구 위에 경로가 그려짐: 칠레 남쪽 끝 1998 → 얼어붙은 베링 해협 2006 → 카스피해 헤엄 2024 → 영국 헐 2026)
    count.mp4 (걸은 거리 0 → 5만 km, 1998 → 2026 = 28년)
지도: Natural Earth 50m 육지(world-atlas 2.0.2 TopoJSON, 퍼블릭 도메인) — assets/geo/land-50m.json.
근거: NBC News 2026.11.03 'British adventurer Karl Bushby completes 28-year walk around the world'(31,000마일, 1998 출발),
      Al Jazeera·ITV 2026.11.02(헐 도착), Fox News(영국 해협 수영), 위키백과 'Karl Bushby'(1998.11 푼타아레나스 출발,
      2006.3 얼어붙은 베링 해협 횡단, 2024 카스피해 수영). 경로 선은 대략(주요 지점만 정확).
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); GREY = (150, 156, 170)
BG1 = (22, 30, 52); BG2 = (8, 12, 24)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
ease2 = lambda t: 0 if t <= 0 else 1 if t >= 1 else (3 * t * t - 2 * t * t * t)
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


def grad(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - a) + np.array(bot)[None, None, :] * a
    return Image.fromarray(np.repeat(arr, W, axis=1).astype(np.uint8))


BG = grad(BG1, BG2)


def foot(d, x, y, s, ang, col):
    """발자국 하나(타원 발바닥 + 발가락 점)."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(px, py):
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    pts = [P(14 * s * math.cos(k / 20 * 2 * math.pi), 24 * s * math.sin(k / 20 * 2 * math.pi)) for k in range(20)]
    d.polygon(pts, fill=col)
    for k, dx in enumerate((-9, -3, 3, 9)):
        cx, cy = P(dx * s, -34 * s + abs(dx) * 0.6 * s)
        r = (5 - abs(dx) * 0.15) * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


# ---------- 1. rule: 비행기·자동차·배 금지 → 두 발로만 ----------
def icon_plane(d, cx, cy, s, col):
    d.rounded_rectangle([cx - 70 * s, cy - 10 * s, cx + 70 * s, cy + 10 * s], 10 * s, fill=col)
    d.polygon([(cx - 10 * s, cy - 8 * s), (cx + 15 * s, cy - 8 * s), (cx - 20 * s, cy - 60 * s), (cx - 38 * s, cy - 60 * s)], fill=col)
    d.polygon([(cx - 10 * s, cy + 8 * s), (cx + 15 * s, cy + 8 * s), (cx - 20 * s, cy + 60 * s), (cx - 38 * s, cy + 60 * s)], fill=col)
    d.polygon([(cx - 62 * s, cy - 6 * s), (cx - 48 * s, cy - 6 * s), (cx - 66 * s, cy - 30 * s), (cx - 74 * s, cy - 30 * s)], fill=col)


def icon_car(d, cx, cy, s, col):
    d.rounded_rectangle([cx - 70 * s, cy - 10 * s, cx + 70 * s, cy + 22 * s], 12 * s, fill=col)
    d.polygon([(cx - 40 * s, cy - 8 * s), (cx - 24 * s, cy - 40 * s), (cx + 26 * s, cy - 40 * s), (cx + 44 * s, cy - 8 * s)], fill=col)
    for dx in (-40, 40):
        d.ellipse([cx + dx * s - 17 * s, cy + 8 * s, cx + dx * s + 17 * s, cy + 42 * s], fill=(30, 30, 36), outline=col, width=int(5 * s))


def icon_ship(d, cx, cy, s, col):
    d.polygon([(cx - 78 * s, cy), (cx + 78 * s, cy), (cx + 54 * s, cy + 34 * s), (cx - 54 * s, cy + 34 * s)], fill=col)
    d.rectangle([cx - 36 * s, cy - 28 * s, cx + 30 * s, cy], fill=col)
    d.rectangle([cx - 12 * s, cy - 56 * s, cx + 8 * s, cy - 28 * s], fill=col)


def rule(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 40, "규칙은 딱 하나", 64, fill=YEL)
    icons = [(icon_plane, "비행기"), (icon_car, "자동차"), (icon_ship, "배")]
    for k, (fn, name) in enumerate(icons):
        cx = 200 + k * 340; cy = 280
        a = ease((t - 0.1 - k * 0.15) / 0.3)
        if a <= 0:
            continue
        s = 1.25 * (0.6 + 0.4 * a)
        fn(d, cx, cy, s, (205, 210, 222))
        ctext(d, cx, 370, name, 46)
        x = ease((t - 0.75 - k * 0.22) / 0.18)      # 빨간 X 도장
        if x > 0:
            L = 95 * (1.4 - 0.4 * x)
            w = int(18 * x) + 4
            d.line([(cx - L, cy - L), (cx + L, cy + L)], fill=RED, width=w)
            d.line([(cx - L, cy + L), (cx + L, cy - L)], fill=RED, width=w)
    # 아래: 오직 두 발 — 발자국이 왼쪽에서 오른쪽으로 찍힘
    b = clamp((t - 1.55) / 1.1)
    if b > 0:
        n = 9
        for i in range(n):
            if i / n > b:
                break
            x = 120 + i * 105; y = 640 + (-30 if i % 2 else 30)
            foot(d, x, y, 1.7, math.pi / 2, YEL)
        ctext(d, W / 2, 480, "집에 닿을 때까지 '두 발'로만", 58, fill=WHITE)
    return im


# ---------- 2. route: 도는 지구 위 경로 ----------
def load_land():
    tj = json.load(open(os.path.join(ROOT, "assets/geo/land-50m.json")))
    sc, tr = tj["transform"]["scale"], tj["transform"]["translate"]
    arcs = []
    for arc in tj["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(ids):
        out = []
        for i in ids:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out
    polys = []
    for g in tj["objects"]["land"]["geometries"]:
        if g["type"] == "Polygon":
            polys.append([ring(r) for r in g["arcs"]])
        elif g["type"] == "MultiPolygon":
            for p in g["arcs"]:
                polys.append([ring(r) for r in p])
    MW, MH = 2880, 1440
    m = Image.new("L", (MW, MH), 0); md = ImageDraw.Draw(m)
    for p in polys:
        for k, r in enumerate(p):
            if len(r) < 3:
                continue
            # 날짜변경선을 넘는 고리(러시아 동쪽 끝 등)는 경도를 이어 붙여 세 번(-360/0/+360) 그린다 — 띠 모양 오류 방지
            jump = any(abs(r[i + 1][0] - r[i][0]) > 180 for i in range(len(r) - 1))
            if jump and min(la for _, la in r) > -60:
                u = [r[0][0]]
                for i in range(1, len(r)):
                    dl = r[i][0] - r[i - 1][0]
                    dl -= 360 * round(dl / 360)
                    u.append(u[-1] + dl)
                ring_ = list(zip(u, [la for _, la in r]))
                offs = (-360, 0, 360)
            else:
                ring_ = r; offs = (0,)
            for o in offs:
                pts = [((lon + o + 180) / 360 * MW, (90 - lat) / 180 * MH) for lon, lat in ring_]
                md.polygon(pts, fill=255 if k == 0 else 0)
    return np.array(m) > 127, MW, MH


LAND, MW, MH = None, 0, 0
CX, CY, R = W / 2, 400, 345
yy, xx = np.mgrid[0:H, 0:W]
NX = (xx - CX) / R; NY = -(yy - CY) / R
RR = NX ** 2 + NY ** 2
INSIDE = RR <= 1.0
NZ = np.sqrt(np.clip(1 - RR, 0, 1))

# (경도, 위도) — 경도는 이어지게 펼침(베링 해협 넘어 -180 아래로)
WP = [(-70.9, -53.2), (-70.6, -33.4), (-77.0, -12.0), (-78.5, -0.2), (-77.7, 8.0), (-84.0, 10.0), (-99.1, 19.4),
      (-118.2, 34.0), (-122.3, 47.6), (-135.0, 60.7), (-147.7, 64.8), (-165.4, 64.5), (-168.5, 65.7), (-169.8, 66.2),
      (-182.5, 64.7), (-230.3, 62.0), (-280.0, 52.0), (-308.8, 43.6), (-310.1, 40.4), (-315.2, 41.7), (-331.0, 41.0),
      (-343.6, 48.2), (-358.15, 50.95), (-358.7, 51.1), (-360.33, 53.74)]
LABELS = [(0, "칠레 남쪽 끝", "1998"), (13, "얼어붙은 베링 해협", "2006"), (18, "카스피해는 헤엄", "2024"), (24, "영국 헐(집)", "2026")]


def densify(wp, step=0.8):
    pts, idx = [], []
    for k in range(len(wp) - 1):
        (a, b), (c, e) = wp[k], wp[k + 1]
        n = max(2, int(math.hypot(c - a, e - b) / step))
        idx.append(len(pts))
        for i in range(n):
            u = i / n
            pts.append((a + (c - a) * u, b + (e - b) * u))
    idx.append(len(pts)); pts.append(wp[-1])
    return pts, idx


RP, RIDX = densify(WP)


def proj(lon, lat, lon0, lat0):
    lo, la, lo0, la0 = map(math.radians, (lon, lat, lon0, lat0))
    cosc = math.sin(la0) * math.sin(la) + math.cos(la0) * math.cos(la) * math.cos(lo - lo0)
    x = math.cos(la) * math.sin(lo - lo0)
    y = math.cos(la0) * math.sin(la) - math.sin(la0) * math.cos(la) * math.cos(lo - lo0)
    return CX + x * R, CY - y * R, cosc > 0.02


def globe(lon0, lat0):
    la0 = math.radians(lat0)
    lat = np.arcsin(np.clip(NZ * math.sin(la0) + NY * math.cos(la0), -1, 1))
    lon = math.radians(lon0) + np.arctan2(NX, NZ * math.cos(la0) - NY * math.sin(la0))
    mx = (((np.degrees(lon) + 180) % 360) / 360 * MW).astype(int) % MW
    my = np.clip(((90 - np.degrees(lat)) / 180 * MH).astype(int), 0, MH - 1)
    land = LAND[my, mx]
    shade = (0.55 + 0.45 * NZ)[..., None]
    ocean = np.array([30, 74, 130]); ground = np.array([96, 150, 92])
    col = np.where(land[..., None], ground, ocean) * shade
    base = np.array(BG).astype(float)
    out = np.where(INSIDE[..., None], col, base)
    # 테두리 빛
    rim = (RR > 0.97) & (RR <= 1.0)
    out[rim] = out[rim] * 0.5 + np.array([120, 180, 255]) * 0.5
    return Image.fromarray(out.astype(np.uint8))


def route(t):
    prog = ease2(clamp((t - 0.15) / 3.0))
    n = int(prog * (len(RP) - 1))
    # 지구 중심 = 경로 머리를 조금 늦게 따라감
    m = max(0, n - 25)
    lon0, lat0 = RP[m][0], RP[m][1] * 0.75 + 20 * 0.25
    im = globe(lon0, lat0); d = ImageDraw.Draw(im)
    seg = []
    for i in range(n + 1):
        x, y, vis = proj(RP[i][0], RP[i][1], lon0, lat0)
        if vis:
            seg.append((x, y))
        else:
            if len(seg) > 1:
                d.line(seg, fill=RED, width=9, joint="curve")
            seg = []
    if len(seg) > 1:
        d.line(seg, fill=RED, width=9, joint="curve")
    hx, hy, hv = proj(RP[n][0], RP[n][1], lon0, lat0)
    if hv:
        r = 14 + 3 * math.sin(t * 12)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=YEL, outline=(0, 0, 0), width=3)
    # 라벨: 지나간 지점 중 가장 최근 것만 크게
    shown = [L for L in LABELS if RIDX[L[0]] <= n]
    for L in shown:
        x, y, v = proj(WP[L[0]][0], WP[L[0]][1], lon0, lat0)
        if v:
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=WHITE, outline=(0, 0, 0), width=3)
    if shown:
        L = shown[-1]
        ctext(d, W / 2, 26, L[2] + "  " + L[1], 60, fill=YEL)
    ctext(d, W - 130, 740, "경로는 대략", 26, fill=GREY, stroke=3)
    return im


# ---------- 3. count: 0 → 5만 km, 1998 → 2026 ----------
def count(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = ease2(clamp((t - 0.1) / 2.0))
    km = int(round(50000 * a, -2))
    year = 1998 + int(28 * a)
    ctext(d, W / 2, 70, "걸은 거리", 52, fill=GREY)
    ctext(d, W / 2, 130, f"{km:,} km", 150, fill=WHITE, stroke=8)
    # 진행 막대 + 발자국
    bx0, bx1, by = 120, 960, 420
    d.rounded_rectangle([bx0, by, bx1, by + 26], 13, fill=(50, 58, 80))
    d.rounded_rectangle([bx0, by, bx0 + (bx1 - bx0) * a, by + 26], 13, fill=YEL)
    for i in range(int(a * 8) + 1):
        foot(d, bx0 + 30 + i * 108, by - 56 + (12 if i % 2 else -12), 1.2, math.pi / 2, (200, 205, 215))
    ctext(d, W / 2, 500, f"{1998} → {year}", 82, fill=WHITE)
    b = ease((t - 2.15) / 0.35)
    if b > 0:
        s = int(120 * (1.5 - 0.5 * b))
        ctext(d, W / 2, 600 - (s - 120) / 2, "= 28년", s, fill=YEL, stroke=8)
    return im


if __name__ == "__main__":
    LAND, MW, MH = load_land()
    run("rule", 3.0, rule)
    run("route", 3.6, route)
    run("count", 3.1, count)
