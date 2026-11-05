#!/usr/bin/env python3
"""아프리카가 갈라진다? — 동아프리카 열곡 모션그래픽(카드 영상 칸 1080x780) — 2026.11.05 오늘의쓸모.
  python3 scripts/story_shorts/anim_rift.py <출력폴더>
  → buzz.mp4   (아프리카 지도에 열곡 선이 북→남으로 그어지고, 케냐 2018 틈 위치가 깜빡 — '대륙이 갈라진다' 소동)
    ash.mp4    (땅 단면: 옛 단층 틈을 메운 화산재 → 폭우 물이 스며 쓸어 내림 → 위 도로가 '쩍' 꺼짐)
    plates.mp4 (누비아판 ←  → 소말리판, '1년에 몇 mm' → 바닷물이 열곡으로 들어와 새 바다)
    afar.mp4   (2005.9.14~10.4 에티오피아 아파르: 길이 약 60km 틈이 날짜 카운터 1→21일과 함께 열림)
지도: Natural Earth 1:50m 육지·호수(퍼블릭 도메인) — scripts/story_shorts/data/africa_rift.json
근거: National Geographic 2018.4(케냐 틈 = 폭우가 옛 단층의 화산재를 씻어 냄, 열곡은 실제로 벌어지는 중),
      Wright et al. 2006 Nature(2005.9.14~10.4 다바후 — 약 60km 길이 암맥, 최대 약 8m 벌어짐), COMET(NERC),
      Yale e360 2009(아파르 틈 = 바다가 생기는 증거), PBS NewsHour 2018.
"""
import math, subprocess, sys, os, json, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 60, 45); SEA = (22, 52, 92); LAND = (176, 150, 104)
LAND2 = (150, 126, 86); LAKE = (60, 110, 170); NEWSEA = (40, 120, 200)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
DATA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "africa_rift.json")))

# 동아프리카 열곡(대략): 아파르 → 에티오피아 열곡 → 케냐 → 탄자니아 (동쪽 가지), 서쪽 가지는 호수 줄
RIFT_E = [(43.0, 12.6), (41.5, 11.5), (40.0, 9.5), (38.6, 7.6), (37.5, 6.0), (36.3, 4.0), (36.1, 2.0), (36.2, 0.0),
          (36.4, -1.2), (36.0, -3.0), (35.6, -5.0)]
RIFT_W = [(31.0, 2.5), (30.0, 0.5), (29.3, -1.5), (29.4, -4.0), (30.2, -6.5), (31.2, -8.6), (33.8, -9.8),
          (34.6, -12.0), (35.2, -14.5), (35.0, -17.5)]
KENYA = (36.45, -1.15)   # 마이마히우–나록 도로 부근(2018.3 틈)
DABBAHU = (40.5, 12.6)   # 2005 다바후 틈


class Proj:
    def __init__(s, lon0, lon1, lat0, lat1):
        s.lon0, s.lat1 = lon0, lat1
        s.k = min(W / (lon1 - lon0), H / (lat1 - lat0))
        s.ox = (W - (lon1 - lon0) * s.k) / 2
        s.oy = (H - (lat1 - lat0) * s.k) / 2

    def __call__(s, lon, lat):
        return (s.ox + (lon - s.lon0) * s.k, s.oy + (s.lat1 - lat) * s.k)


def base_map(P, lakes=True, land=LAND):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    for ring in DATA["land"]:
        pts = [P(x, y) for x, y in ring]
        if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50:
            continue
        d.polygon(pts, fill=land, outline=LAND2)
    if lakes:
        for ring in DATA["lakes"]:
            d.polygon([P(x, y) for x, y in ring], fill=LAKE)
    return img


def run(name, dur, draw, bg=None):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = draw(i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=6):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def ltext(d, x, y, s, size, fill=WHITE, stroke=5):
    d.text((x, y), s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def polyline_part(pts, k):
    """선의 앞쪽 k(0~1)만큼 돌려줌"""
    if k <= 0:
        return pts[:1]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seg) * k; out = [pts[0]]
    for i, L in enumerate(seg):
        if tot >= L:
            out.append(pts[i + 1]); tot -= L
        else:
            a = tot / L
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a))
            break
    return out


def glow_line(img, pts, width, color=RED):
    if len(pts) < 2:
        return img
    lay = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(lay).line(pts, fill=color, width=width * 3, joint="curve")
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(img, Image.composite(lay, img, lay.convert("L").point(lambda v: min(255, v * 2))), 0.7)
    ImageDraw.Draw(img).line(pts, fill=color, width=width, joint="curve")
    return img


# ① '아프리카가 갈라진다' 소동
P1 = Proj(-22, 62, -37, 39)
MAP1 = base_map(P1)


def buzz(t):
    img = MAP1.copy()
    k = ease(t / 1.6)
    img = glow_line(img, polyline_part([P1(*p) for p in RIFT_E], k), 7)
    img = glow_line(img, polyline_part([P1(*p) for p in RIFT_W], clamp((t - 0.4) / 1.4)), 5)
    d = ImageDraw.Draw(img)
    if t > 1.0:  # 케냐 틈 위치 핀 깜빡
        x, y = P1(*KENYA)
        r = 14 + 10 * abs(math.sin(t * 6))
        d.ellipse((x - r, y - r, x + r, y + r), outline=YEL, width=6)
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=YEL)
        ltext(d, x + 34, y - 26, "케냐 · 2018", 44, fill=YEL)
    ctext(d, 540, 28, "'아프리카가 둘로 갈라진다!'", 56, fill=YEL)
    if t > 0.9:
        ctext(d, 540, 102, "전 세계 뉴스가 들썩", 46)
    return img


# ② 단면: 화산재를 쓸어 낸 폭우
RAIN = [(random.Random(i).random() * W, random.Random(i * 3).random()) for i in range(90)]


def ash(t):
    img = Image.new("RGB", (W, H), (120, 150, 185))
    d = ImageDraw.Draw(img)
    top = 300
    # 땅 층
    d.rectangle((0, top, W, H), fill=(118, 84, 56))
    for k, c in enumerate([(132, 96, 64), (104, 74, 50), (90, 64, 44)]):
        d.rectangle((0, top + 80 + k * 130, W, top + 210 + k * 130), fill=c)
    # 옛 단층 틈(V자) — 처음엔 회색 화산재로 꽉
    vx, vw = 540, 120
    v = [(vx - vw, top), (vx + vw, top), (vx + 14, H), (vx - 14, H)]
    wash = ease((t - 1.2) / 1.5)  # 쓸려 나간 정도(위에서부터)
    d.polygon(v, fill=(30, 22, 18))  # 빈 틈(어둠)
    ash_top = top + (H - top) * wash
    if ash_top < H:
        # 남은 화산재(아래쪽)
        a = (ash_top - top) / (H - top)
        lx = vx - vw + (vw - 14) * a; rx = vx + vw - (vw - 14) * a
        d.polygon([(lx, ash_top), (rx, ash_top), (vx + 14, H), (vx - 14, H)], fill=(168, 166, 160))
        for i in range(40):  # 재 알갱이
            rr = random.Random(i)
            yy = ash_top + rr.random() * (H - ash_top)
            aa = (yy - top) / (H - top)
            xx = vx - vw + (vw - 14) * aa + rr.random() * (2 * (vw - (vw - 14) * aa))
            d.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=(140, 138, 132))
    # 도로(위) — 쓸려 나가면 가운데가 꺼짐
    sag = 60 * ease((t - 2.0) / 0.5)
    d.rectangle((0, top - 22, vx - vw, top), fill=(60, 60, 64))
    d.rectangle((vx + vw, top - 22, W, top), fill=(60, 60, 64))
    if sag < 59:
        d.polygon([(vx - vw, top - 22), (vx + vw, top - 22), (vx + vw, top), (vx - vw, top)], fill=(60, 60, 64))
    else:
        d.polygon([(vx - vw, top - 22), (vx - vw + 40, top - 22 + 80), (vx - vw + 40, top + 80), (vx - vw, top)], fill=(60, 60, 64))
        d.polygon([(vx + vw, top - 22), (vx + vw - 40, top - 22 + 80), (vx + vw - 40, top + 80), (vx + vw, top)], fill=(60, 60, 64))
    for x in range(30, W, 120):
        if abs(x + 30 - vx) > vw + 10:
            d.rectangle((x, top - 13, x + 60, top - 9), fill=(240, 220, 120))
    # 비
    if 0.3 < t < 2.4:
        for x0, ph in RAIN:
            y = ((ph + t * 1.6) % 1) * (top - 30)
            d.line((x0, y, x0 - 8, y + 30), fill=(210, 230, 255), width=3)
    # 물이 틈으로 스며드는 화살표
    if 0.8 < t < 2.4:
        kk = (t * 1.4) % 1
        for dx in (-50, 50):
            y = top + 20 + 200 * kk
            d.line((vx + dx * (1 - kk * 0.6), y, vx + dx * (1 - kk * 0.6), y + 60), fill=(90, 170, 255), width=10)
            d.polygon([(vx + dx * (1 - kk * 0.6) - 16, y + 56), (vx + dx * (1 - kk * 0.6) + 16, y + 56),
                       (vx + dx * (1 - kk * 0.6), y + 84)], fill=(90, 170, 255))
    ctext(d, 540, 24, "땅속 옛 틈을 메운 '화산재'", 54, fill=YEL)
    if t > 1.3:
        ctext(d, 540, 98, "폭우가 쓸어 내자 '쩍'", 54)
    if t < 1.3:
        ltext(d, vx + vw + 30, top + 140, "← 화산재(무름)", 40, fill=WHITE)
    return img


# ③ 판이 벌어지고 → 바다
P3 = Proj(8, 62, -22, 22)
MAP3 = base_map(P3)


def arrow(d, x0, y0, x1, y1, col, w=16):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    d.polygon([(x1 + 34 * math.cos(a), y1 + 34 * math.sin(a)),
               (x1 + 24 * math.cos(a + 2.2), y1 + 24 * math.sin(a + 2.2)),
               (x1 + 24 * math.cos(a - 2.2), y1 + 24 * math.sin(a - 2.2))], fill=col)


def plates(t):
    img = MAP3.copy()
    flood = ease((t - 1.6) / 1.3)
    if flood > 0:  # 열곡을 따라 북쪽(아파르)에서부터 바닷물이 차오름
        d0 = ImageDraw.Draw(img)
        part = polyline_part([P3(*p) for p in RIFT_E], flood)
        d0.line(part, fill=NEWSEA, width=int(16 + 34 * flood), joint="curve")
    img = glow_line(img, [P3(*p) for p in RIFT_E], 6)
    d = ImageDraw.Draw(img)
    s = 26 * ease(t / 0.8) + 8 * math.sin(t * 5)
    ax, ay = P3(24, 2); bx, by = P3(46, 2)
    arrow(d, ax, ay, ax - 60 - s, ay, WHITE)
    arrow(d, bx, by, bx + 60 + s, by, WHITE)
    ctext(d, ax - 30, ay + 40, "누비아판", 44)
    ctext(d, bx + 30, by + 40, "소말리판", 44)
    if t < 1.6:
        ctext(d, 540, 28, "진짜로 벌어지는 중", 56, fill=YEL)
        ctext(d, 540, 102, "1년에 '몇 mm'씩", 50)
    else:
        ctext(d, 540, 28, "수백만 년 뒤엔 여기가 '바다'", 56, fill=YEL)
        ctext(d, 540, 102, "바닷물이 열곡으로 들어온다", 46)
    return img


# ④ 2005 아파르: 열흘 만에 약 60km
P4 = Proj(38.6, 42.6, 11.0, 14.2)
MAP4 = base_map(P4, lakes=False)


def afar(t):
    img = MAP4.copy()
    d = ImageDraw.Draw(img)
    # 다바후 틈: 북북서-남남동 방향 약 60km(위도 약 0.55도)
    x0, y0 = P4(DABBAHU[0] - 0.12, DABBAHU[1] + 0.27)
    x1, y1 = P4(DABBAHU[0] + 0.12, DABBAHU[1] - 0.27)
    k = ease((t - 0.4) / 1.8)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ex0, ey0 = cx + (x0 - cx) * k, cy + (y0 - cy) * k
    ex1, ey1 = cx + (x1 - cx) * k, cy + (y1 - cy) * k
    if k > 0:
        img = glow_line(img, [(ex0, ey0), (ex1, ey1)], int(10 + 14 * k))
        d = ImageDraw.Draw(img)
    day = 1 + int(20 * clamp((t - 0.4) / 1.8))
    ltext(d, 60, 560, f"{day}일째", 84, fill=YEL, stroke=7)
    ltext(d, 60, 670, f"길이 약 {int(60 * k)}km", 52, stroke=6)
    # 축척 막대 60km
    sx0, sy = P4(41.5, 11.35); sx1, _ = P4(41.5 + 60 / 109.0, 11.35)
    d.line((sx0, sy, sx1, sy), fill=WHITE, width=8)
    ltext(d, sx0, sy - 56, "60km", 36)
    ax, ay = P4(DABBAHU[0] + 0.35, DABBAHU[1] + 0.05)
    ltext(d, ax, ay, "아파르 사막", 44, fill=WHITE)
    ctext(d, 540, 24, "2005년 에티오피아 사막에서", 52, fill=YEL)
    ctext(d, 540, 96, "땅이 3주 만에 '쭉'", 52)
    return img


run("buzz", 2.8, buzz)
run("ash", 3.0, ash)
run("plates", 3.2, plates)
run("afar", 3.0, afar)
print("done", OUT)
