"""오늘의쓸모 릴스: 각국 '3일치 비축' 권고 지도 모션그래픽 (1080x1920, 30fps)."""
import math, os, sys, warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = "/home/claude/cardnews"
sys.path.insert(0, os.path.join(REPO, "scripts"))
os.chdir(REPO)
from reel_overlay import overlay  # 원래 릴스 양식(로고+제목, 마지막 줄 y=1675)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FB = "assets/fonts/Pretendard-Black.otf"
FX = "assets/fonts/Pretendard-ExtraBold.otf"
FM = "assets/fonts/Pretendard-Medium.otf"
f = lambda p, s: ImageFont.truetype(p, s)
RED, YEL, WHITE = (238, 48, 48), (255, 216, 77), (255, 255, 255)

TITLE = ["영국·일본은", "국민에 '3일치'", "한국 정부는?"]
OV = overlay(TITLE)

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
world = world[world.name != "Antarctica"]
polys = {}
for name, geom in zip(world.name, world.geometry):
    gs = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    polys[name] = [list(g.exterior.coords) for g in gs]

# (영문명, 표시명, 기간, 부가, 시작초)
EU_SEQ = [
    ("United Kingdom", "영국", "3일", "10.22 발표", 0),
    ("France", "프랑스", "72시간", "", 0),
    ("Belgium", "벨기에", "72시간", "", 0),
    ("Netherlands", "네덜란드", "72시간", "", 0),
    ("Ireland", "아일랜드", "72시간", "", 0),
    ("Germany", "독일", "3~10일", "", 0),
    ("Poland", "폴란드", "3일", "", 0),
    ("Denmark", "덴마크", "3일", "", 0),
    ("Norway", "노르웨이", "1주", "", 0),
    ("Sweden", "스웨덴", "1주", "", 0),
    ("Finland", "핀란드", "72시간", "", 0),
    ("Estonia", "에스토니아", "1주", "", 0),
    ("Latvia", "라트비아", "72시간", "", 0),
    ("Lithuania", "리투아니아", "72시간", "", 0),
    ("Switzerland", "스위스", "1주", "", 0),
]
ASIA_SEQ = [
    ("Japan", "일본", "3일~1주", "11.2 대국민 요청", 0),
    ("Taiwan", "대만", "1주", "전 가구 핸드북", 0),
]
T_HOOK = 0.8
STEP = 0.52
t = T_HOOK
for i, c in enumerate(EU_SEQ):
    EU_SEQ[i] = c[:4] + (t,); t += STEP
T_EU = t; t += 1.1           # EU 박스
T_PAN0 = t; t += 1.0          # 아시아로 이동
T_PAN1 = t
for i, c in enumerate(ASIA_SEQ):
    ASIA_SEQ[i] = c[:4] + (t,); t += 1.15
T_KR = t; t += 2.8            # 한국 '?'
T_SHEL = t; t += 4.2          # 대피소 카드
T_END = t; t += 3.6           # 마무리 입장
TOTAL = t
SEQ = EU_SEQ + ASIA_SEQ
NAMES_LIT = [c[0] for c in SEQ]

CAM_EU = (8.5, 54.5, 30.0)   # 중심 경도, 위도, 세로 범위(도)
CAM_AS = (128.5, 31.0, 30.0)
MAP_TOP, MAP_BOT = 250, 960


def ease(x):
    x = max(0, min(1, x)); return x * x * (3 - 2 * x)


def cam_at(tt):
    if tt < T_PAN0: return CAM_EU
    if tt >= T_PAN1: return CAM_AS
    e = ease((tt - T_PAN0) / (T_PAN1 - T_PAN0))
    return tuple(a + (b - a) * e for a, b in zip(CAM_EU, CAM_AS))


def proj(cam):
    lon0, lat0, span = cam
    k = (MAP_BOT - MAP_TOP) / span
    cy = (MAP_TOP + MAP_BOT) / 2
    cl = math.cos(math.radians(lat0))
    return lambda lon, lat: (W / 2 + (lon - lon0) * cl * k, cy - (lat - lat0) * k)


def centroid(name):
    g = world[world.name == name].geometry.iloc[0]
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda p: p.area)
    c = g.representative_point(); return c.x, c.y


CENT = {n: centroid(n) for n in NAMES_LIT + ["South Korea"]}
CENT["Norway"] = (9.5, 61.0)
CENT["France"] = (2.5, 46.8)


def draw_map(tt, lit, korea_mode):
    P = proj(cam_at(tt))
    base = Image.new("RGB", (W, H), (8, 9, 14))
    d = ImageDraw.Draw(base)
    for gx in range(-180, 181, 10):
        pts = [P(gx, la) for la in range(-60, 85, 5)]
        d.line(pts, fill=(18, 20, 30), width=1)
    for gy in range(-60, 85, 10):
        pts = [P(lo, gy) for lo in range(-180, 181, 5)]
        d.line(pts, fill=(18, 20, 30), width=1)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for name, rings in polys.items():
        a = lit.get(name, 0)
        for r in rings:
            pts = [P(x, y) for x, y in r]
            if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50:
                continue
            if a > 0:
                col = tuple(int(c0 + (c1 - c0) * a) for c0, c1 in zip((34, 36, 46), (200, 34, 34)))
                d.polygon(pts, fill=col, outline=(255, 120, 110))
                gd.polygon(pts, fill=tuple(int(c * a) for c in (255, 40, 30)))
            elif name == "South Korea" and korea_mode:
                blink = 0.5 + 0.5 * math.sin(tt * 7)
                col = tuple(int(60 + 120 * blink) for _ in range(3))
                d.polygon(pts, fill=col, outline=(230, 230, 230))
            else:
                d.polygon(pts, fill=(30, 32, 42), outline=(62, 66, 84))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    base = Image.blend(base, Image.eval(base, lambda v: v), 1)
    from PIL import ImageChops
    base = ImageChops.add(base, glow)
    return base, P


def callout(d, P, name, label, dur, sub, age):
    cx, cy = P(*CENT[name])
    s = ease(age / 0.18)
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=WHITE)
    fn, fd, fs = f(FB, 46), f(FB, 40), f(FM, 28)
    tw = max(d.textlength(label, font=fn) + 26 + d.textlength(dur, font=fd), d.textlength(sub, font=fs)) + 44
    bh = 84 + (40 if sub else 0)
    bx = min(max(cx + 40, 30), W - tw - 30)
    by = min(max(cy - bh - 30, MAP_TOP - 30), MAP_BOT - bh)
    if s < 1:
        bx += (1 - s) * 30
    d.line([(cx, cy), (bx, by + bh / 2)], fill=WHITE, width=3)
    d.rounded_rectangle((bx, by, bx + tw, by + bh), 12, fill=(16, 16, 20), outline=RED, width=4)
    d.text((bx + 22, by + 42), label, font=fn, fill=WHITE, anchor="lm")
    lw = d.textlength(label, font=fn)
    d.rounded_rectangle((bx + 22 + lw + 14, by + 18, bx + 22 + lw + 26 + d.textlength(dur, font=fd), by + 66), 8, fill=RED)
    d.text((bx + 22 + lw + 20, by + 42), dur, font=fd, fill=WHITE, anchor="lm")
    if sub:
        d.text((bx + 22, by + 100), sub, font=fs, fill=YEL, anchor="lm")


def banner(d, text, tt):
    y0, y1 = 120, 210
    stripe = 34
    off = int(tt * 60) % (stripe * 2)
    for x in range(-stripe * 2, W + stripe * 2, stripe * 2):
        d.polygon([(x + off, y0), (x + off + stripe, y0), (x + off + stripe - 18, y0 + 14), (x + off - 18, y0 + 14)], fill=YEL)
        d.polygon([(x + off, y1 - 14), (x + off + stripe, y1 - 14), (x + off + stripe - 18, y1), (x + off - 18, y1)], fill=YEL)
    d.rectangle((0, y0 + 14, W, y1 - 14), fill=(10, 10, 10))
    d.text((W / 2, (y0 + y1) / 2), text, font=f(FB, 44), fill=WHITE, anchor="mm")


def hud(d, tt, n):
    rem = max(0, 72 * 3600 - int(tt * 997))
    h, m, s = rem // 3600, rem % 3600 // 60, rem % 60
    d.text((70, 1040), f"{h:02d}:{m:02d}:{s:02d}", font=f(FB, 64), fill=WHITE, anchor="ls")
    d.text((70, 1080), "가정마다 버텨야 할 시간", font=f(FM, 28), fill=(170, 170, 180), anchor="ls")
    d.text((W - 70, 1040), f"{n}", font=f(FB, 84), fill=RED, anchor="rs")
    d.text((W - 70, 1080), "개국 + EU" if n >= 15 and tt >= T_EU else "개국", font=f(FX, 30), fill=WHITE, anchor="rs")


def text_card(img, tt, t0, lines, foot=None):
    """지도 위 어둡게 + 큰 글씨 카드. lines: [(글, 크기, 색)]"""
    a = ease((tt - t0) / 0.35)
    dark = Image.new("RGB", (W, H), (6, 6, 10))
    img = Image.blend(img, dark, 0.86 * a)
    d = ImageDraw.Draw(img)
    total = sum(s * 1.32 for _, s, _ in lines)
    y = (MAP_TOP + 1060) / 2 - total / 2
    for k, (txt, size, col) in enumerate(lines):
        ak = ease((tt - t0 - 0.12 * k) / 0.3)
        if ak <= 0: break
        d.text((70, y + size + (1 - ak) * 26), txt, font=f(FB if size >= 56 else FX, size),
               fill=tuple(int(c * ak + 6 * (1 - ak)) for c in col), anchor="ls")
        y += size * 1.32
    if foot and tt - t0 > 0.6:
        d.text((70, 1060), foot, font=f(FM, 26), fill=(150, 150, 160), anchor="ls")
    return img


def frame(i):
    tt = i / FPS
    lit, n = {}, 0
    for c in SEQ:
        if tt >= c[4]:
            lit[c[0]] = ease((tt - c[4]) / 0.25); n += 1
    img, P = draw_map(tt, lit, tt >= T_KR)
    d = ImageDraw.Draw(img)
    banner(d, "각국 정부가 국민에게 '비축'을 요청", tt)
    if tt < T_SHEL:
        hud(d, tt, n)
        cur = [c for c in SEQ if tt >= c[4]]
        if T_EU <= tt < T_PAN0:
            fe = f(FB, 64)
            bw = d.textlength("EU 전체 · 72시간", font=fe) + 60
            d.rounded_rectangle(((W - bw) / 2, 560, (W + bw) / 2, 680), 16, fill=(16, 16, 20), outline=YEL, width=5)
            d.text((W / 2, 620), "EU 전체 · 72시간", font=fe, fill=YEL, anchor="mm")
        elif tt < T_KR and cur and not (T_PAN0 <= tt < T_PAN1):
            c = cur[-1]
            callout(d, P, c[0], c[1], c[2], c[3], tt - c[4])
        elif tt >= T_KR:
            cx, cy = P(*CENT["South Korea"])
            fn = f(FB, 52)
            label = "한국 정부 권고:"
            bw = d.textlength(label, font=fn) + 50 + 50
            bx, by = cx - bw - 60, cy - 170
            d.line([(cx, cy), (bx + bw, by + 50)], fill=WHITE, width=3)
            d.rounded_rectangle((bx, by, bx + bw, by + 100), 14, fill=(16, 16, 20), outline=WHITE, width=4)
            d.text((bx + 25, by + 50), label, font=fn, fill=WHITE, anchor="lm")
            d.text((bx + bw - 30, by + 50), "?", font=f(FB, 70), fill=YEL, anchor="rm")
    if tt >= T_SHEL:
        if tt < T_END:
            img = text_card(img, tt, T_SHEL, [
                ("우리 동네 대피소", 84, WHITE),
                ("어딘지 아세요?", 110, YEL),
                ("4곳 중 1곳은 자리도 부족", 54, WHITE),
            ], foot="시군구 55곳 민방위 대피시설 수용률 100% 미달 · 행안부 국회 제출 자료(2025년 말)")
        else:
            img = text_card(img, tt, T_END, [
                ("북한과 마주한 나라가", 84, WHITE),
                ("제일 태평하다", 110, YEL),
            ], foot="영국 10.22 권고 · 일본 11.2 대국민 요청 예정 · 대만 전 가구 핸드북 배포")
    img = img.convert("RGBA")
    img.alpha_composite(OV)
    return img.convert("RGB")


if __name__ == "__main__":
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    N = int(TOTAL * FPS)
    print("total", round(TOTAL, 2), "s", N, "frames")
    rng = [int(float(x) * FPS) for x in only] if only else range(N)
    for i in rng:
        frame(i).save(f"{OUT}/f{i:05d}.jpg", quality=90)
