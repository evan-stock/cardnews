#!/usr/bin/env python3
"""하늘에 뜬 검은 고리 — 연기 소용돌이 고리(vortex ring) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.04 오늘의쓸모.
  python3 scripts/story_shorts/anim_skyring.py <출력폴더>
  → puff.mp4    (땅에서 불꽃 연기가 한 번에 '훅' 솟아 → 위로 가며 납작한 고리로 말림)
    donut.mp4   (고리를 반으로 자른 단면: 양쪽 연기 덩어리가 계속 말려 돎 → 흩어지지 않고 둥둥, 담배 연기 고리와 같은 원리)
    sources.mp4 (실제로 밝혀진 출처: 불꽃놀이(미주리 케이프지라도 경찰) · 성 공연 불꽃 효과(영국 워릭성 2014) · 경기장 불꽃 연출(시애틀 2025, 기상청 '행사 연기'))
근거: Southeast Missourian(케이프지라도 경찰 "확실히 불꽃놀이"), Higgypop/Mirror(워릭성 대변인 '공연용 불꽃 효과 시험'),
      KIRO7 2025.3.31(NWS 기상학자 "루멘 필드 행사 때문으로 보임"), FOX 2024.8.21(윌리엄스버그 — 불꽃·산업 공정·폭발 추정), 위키백과 Vortex ring.
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); SMOKE = (28, 26, 30); ORG = (255, 140, 40); RED = (232, 60, 50)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def sky(top=(96, 140, 200), bot=(190, 210, 232)):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    return img


SKY = sky()


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = SKY.copy()
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def ground(d):
    d.rectangle((0, 690, W, H), fill=(58, 92, 60))
    for x in range(0, W, 90):  # 먼 나무 줄
        d.ellipse((x - 10, 650, x + 70, 712), fill=(44, 74, 48))


def ring(img, cx, cy, rx, ry, th, alpha=1.0, blur=2):
    lay = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(lay)
    ld.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=int(235 * alpha), width=max(2, int(th)))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.new("RGB", (W, H), SMOKE), (0, 0), lay)


def blob(img, cx, cy, r, alpha=1.0):
    lay = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(lay)
    for k in range(7):
        a = k * 2 * math.pi / 7
        ld.ellipse((cx + math.cos(a) * r * 0.45 - r * 0.6, cy + math.sin(a) * r * 0.35 - r * 0.55,
                    cx + math.cos(a) * r * 0.45 + r * 0.6, cy + math.sin(a) * r * 0.35 + r * 0.55), fill=int(220 * alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.new("RGB", (W, H), SMOKE), (0, 0), lay)


# ① 훅 → 고리
def puff(img, t):
    d = ImageDraw.Draw(img)
    ground(d)
    cx = 540
    # 발사 통(불꽃놀이 통)
    sh = 4 * math.sin(t * 60) if 0.15 < t < 0.5 else 0
    d.rectangle((cx - 34 + sh, 600, cx + 34 + sh, 700), fill=(150, 40, 40), outline=(60, 10, 10), width=4)
    if 0.2 < t < 0.6:  # 불꽃
        k = (t - 0.2) / 0.4
        d.polygon([(cx - 26, 600), (cx + 26, 600), (cx, 600 - 90 * (1 - k))], fill=ORG)
    if t > 0.3:
        k = ease((t - 0.3) / 0.9)          # 덩어리 솟기
        y = 590 - 250 * k
        m = clamp((t - 0.9) / 1.0)          # 고리로 바뀌기
        if m < 1:
            blob(img, cx, y, 40 + 70 * k, alpha=1 - m)
        if m > 0:
            rise = (t - 0.9) * 22
            ring(img, cx, y - rise, 90 + 120 * m, 26 + 34 * m, 10 + 6 * m, alpha=m)
    if 0.25 < t:
        a = clamp((t - 0.25) / 0.2)
        ctext(d, 540, 40, "불꽃·폭발 연기를 한 번에 '훅'", 58, fill=YEL)
    if t > 1.6:
        ctext(d, 540, 120, "→ 위로 가며 '고리'로 말린다", 50)


# ② 단면: 계속 말려 도는 연기
PTS = [(random.Random(i).random() * 2 * math.pi, 18 + random.Random(i * 7).random() * 62) for i in range(70)]


def donut(img, t):
    d = ImageDraw.Draw(img)
    cy = 430 - t * 25
    cxs = (300, 780)
    # 고리 윤곽(앞에서 본 모습, 흐리게)
    d.ellipse((300 - 10, cy - 70, 780 + 10, cy + 70), outline=(70, 80, 100), width=3)
    for i, cx in enumerate(cxs):
        sgn = 1 if i == 0 else -1  # 왼쪽은 시계, 오른쪽은 반시계 → 안쪽은 위로
        d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(60, 58, 64))
        for a0, r in PTS:
            a = a0 + sgn * t * 4.2
            x = cx + math.cos(a) * r; y = cy + math.sin(a) * r
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(20, 18, 22))
        # 회전 화살표
        a = sgn * t * 4.2
        for k in range(2):
            st = math.degrees(a) + k * 180
            d.arc((cx - 112, cy - 112, cx + 112, cy + 112), st, st + 110, fill=YEL, width=9)
            e = math.radians(st + 110)
            ex, ey = cx + 112 * math.cos(e), cy + 112 * math.sin(e)
            tx, ty = -math.sin(e) * sgn, math.cos(e) * sgn
            d.polygon([(ex + tx * 26, ey + ty * 26), (ex - ty * 14, ey + tx * 14), (ex + ty * 14, ey - tx * 14)], fill=YEL)
    # 가운데 위로 화살표(안쪽 공기는 위로)
    k = (t * 1.5) % 1
    d.line((540, cy + 80 - 120 * k, 540, cy - 20 - 120 * k), fill=WHITE, width=10)
    d.polygon([(540, cy - 50 - 120 * k), (520, cy - 18 - 120 * k), (560, cy - 18 - 120 * k)], fill=WHITE)
    ctext(d, 540, 36, "고리를 반으로 자르면", 52)
    if t > 0.6:
        ctext(d, 540, 110, "연기가 도넛처럼 '말려 돌며' 안 흩어진다", 50, fill=YEL)
    if t > 1.6:
        ctext(d, 540, 668, "담배 연기 고리와 같은 원리", 50)


# ③ 실제로 밝혀진 출처
def icon_fire(d, cx, cy, t):
    for k in range(10):
        a = k * 2 * math.pi / 10
        r = 75 + 10 * math.sin(t * 10 + k)
        d.line((cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=(255, 120 + k * 12, 60), width=9)


def icon_castle(d, cx, cy, t):
    d.rectangle((cx - 60, cy - 10, cx + 60, cy + 60), fill=(120, 110, 100))
    for k in range(4):
        d.rectangle((cx - 60 + k * 34, cy - 30, cx - 40 + k * 34, cy - 10), fill=(120, 110, 100))
    fl = 30 + 10 * math.sin(t * 20)
    d.polygon([(cx - 14, cy - 30), (cx + 14, cy - 30), (cx, cy - 30 - fl)], fill=ORG)


def icon_stadium(d, cx, cy, t):
    d.chord((cx - 80, cy - 20, cx + 80, cy + 90), 180, 360, fill=(80, 90, 110))
    d.rectangle((cx - 80, cy + 34, cx + 80, cy + 60), fill=(80, 90, 110))
    for x in (cx - 50, cx + 50):
        fl = 34 + 12 * math.sin(t * 18 + x)
        d.polygon([(x - 10, cy + 10), (x + 10, cy + 10), (x, cy + 10 - fl)], fill=ORG)


SRC = [(200, icon_fire, "불꽃놀이", "미국 미주리 · 경찰 확인"),
       (540, icon_castle, "성 공연 불꽃 효과", "영국 워릭성 · 2014"),
       (880, icon_stadium, "경기장 불꽃 연출", "미국 시애틀 · 2025")]


def sources(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, 540, 34, "실제로 밝혀진 '범인'", 60, fill=YEL)
    for i, (cx, icon, name, sub) in enumerate(SRC):
        t0 = 0.25 + i * 0.5
        if t < t0:
            continue
        k = ease((t - t0) / 0.4)
        d.rounded_rectangle((cx - 158, 150 + (1 - k) * 60, cx + 158, 700 + (1 - k) * 60), 24, fill=(214, 226, 240))
        oy = (1 - k) * 60
        icon(d, cx, 500 + oy, t)
        # 출처 위로 떠오르는 작은 고리
        rt = clamp((t - t0 - 0.2) / 1.4)
        ring(img, cx, 420 - 170 * ease(rt) + oy, 50 + 60 * rt, 16 + 16 * rt, 10, alpha=clamp(rt * 3), blur=1)
        d = ImageDraw.Draw(img)
        ctext(d, cx, 600 + oy, name, 40)
        ctext(d, cx, 652 + oy, sub, 28, fill=(200, 210, 225), stroke=3)


run("puff", 3.0, puff)
run("donut", 3.0, donut)
run("sources", 2.8, sources)
print("done", OUT)
