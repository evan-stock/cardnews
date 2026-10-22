#!/usr/bin/env python3
"""2006 영국 액체폭탄 모의 설명 모션그래픽(카드 영상 칸 1080x780) — 2026.10.23 오늘의쓸모 '기내 액체 금지를 만든 사건'.
  python3 scripts/story_shorts/anim_liquidplot.py <출력폴더>
  → map.mp4(히드로 → 북미 7편) fly.mp4(몇 시간 간격으로 떠 비행 중 노림) bottle.mp4(새 음료수처럼 보이는 병)
    scan.mp4(검색대에서 음료수로 통과될 뻔) rule.mp4(100ml·1L 지퍼백 규칙)
※ 폭발물 성분·제조·위장 방법은 그리지 않는다(사건 개요 수준만).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SEA = (16, 28, 48); LAND = (44, 60, 86); EDGE = (70, 92, 126); INK = (240, 244, 250); GRAY = (150, 162, 182)
YEL = (255, 216, 77); RED = (240, 66, 56); GRN = (46, 196, 100); BLU = (80, 150, 255); CYAN = (90, 220, 240)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGBA", (W, H), SEA + (255,))
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=INK, stroke=0, sfill=(0, 0, 0)):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=sfill)


# ── 지도 ──────────────────────────────────────────────
NA = [(-20, 120), (120, 90), (260, 110), (360, 150), (420, 210), (430, 260), (400, 300), (440, 330), (420, 380),
      (380, 430), (340, 470), (300, 520), (250, 560), (180, 600), (100, 640), (20, 660), (-20, 660)]
UK = [(860, 210), (900, 190), (930, 230), (925, 290), (950, 330), (930, 360), (880, 365), (870, 330), (885, 300),
      (860, 270)]
IE = [(800, 260), (835, 250), (845, 300), (815, 320), (795, 295)]
EU = [(990, 230), (1100, 200), (1100, 600), (1000, 560), (980, 470), (1010, 420), (985, 360), (1000, 300)]
LHR = (905, 335)
CITIES = [("샌프란시스코", (40, 470)), ("시카고", (215, 360)), ("토론토", (300, 315)), ("몬트리올", (370, 270)),
          ("뉴욕", (365, 390)), ("워싱턴", (325, 440))]
# 7편: 시카고는 2편(유나이티드·아메리칸)
ROUTES = [CITIES[0][1], CITIES[1][1], CITIES[1][1], CITIES[2][1], CITIES[3][1], CITIES[4][1], CITIES[5][1]]


def base_map(img, labels=True):
    d = ImageDraw.Draw(img)
    for poly in (NA, UK, IE, EU):
        d.polygon(poly, fill=LAND, outline=EDGE)
    d.ellipse((LHR[0] - 9, LHR[1] - 9, LHR[0] + 9, LHR[1] + 9), fill=YEL)
    d.text((LHR[0] - 70, LHR[1] + 16), "런던 히드로", font=F(30), fill=YEL)
    if labels:
        for name, (x, y) in CITIES:
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=INK)
            d.text((x - 10, y - 44), name, font=F(24), fill=GRAY)
    return d


def arc_pt(dst, k, i):
    lift = 150 + 28 * i
    cx, cy = (LHR[0] + dst[0]) / 2, min(LHR[1], dst[1]) - lift
    x = (1 - k) ** 2 * LHR[0] + 2 * (1 - k) * k * cx + k * k * dst[0]
    y = (1 - k) ** 2 * LHR[1] + 2 * (1 - k) * k * cy + k * k * dst[1]
    return x, y


def plane(d, x, y, ang, s=1.0, col=INK):
    pts = [(26, 0), (6, -4), (-6, -22), (-12, -22), (-4, -4), (-18, -4), (-24, -12), (-28, -12), (-24, 0),
           (-28, 12), (-24, 12), (-18, 4), (-4, 4), (-12, 22), (-6, 22), (6, 4)]
    c, sn = math.cos(ang), math.sin(ang)
    d.polygon([(x + s * (px * c - py * sn), y + s * (px * sn + py * c)) for px, py in pts], fill=col)


def s_map(img, t):
    d = base_map(img)
    n = 0
    for i, dst in enumerate(ROUTES):
        k = ease(clamp((t - 0.2 - i * 0.28) / 0.9))
        if k <= 0:
            continue
        n += 1
        pts = [arc_pt(dst, j / 40 * k, i) for j in range(41)]
        d.line(pts, fill=RED, width=5)
        x, y = pts[-1]; x0, y0 = pts[-2]
        plane(d, x, y, math.atan2(y - y0, x - x0), 0.9)
    # 7편 배지
    a = ease(clamp((t - 2.3) / 0.4))
    if a > 0:
        r = 70 * (0.7 + 0.3 * a)
        d.ellipse((540 - r, 640 - r, 540 + r, 640 + r), fill=RED)
        ctext(d, 540, 640 - r * 0.62, "7편", int(56 * (0.7 + 0.3 * a)))


def s_fly(img, t):
    d = base_map(img, labels=False)
    for i, dst in enumerate(ROUTES):
        pts = [arc_pt(dst, j / 40, i) for j in range(41)]
        d.line(pts, fill=(90, 60, 70), width=3)
    # 시계: 몇 시간 간격 출발
    for i, dst in enumerate(ROUTES):
        k = clamp((t - i * 0.18) / 2.4) * 0.55
        if k <= 0:
            continue
        x, y = arc_pt(dst, k, i); x0, y0 = arc_pt(dst, max(0, k - 0.01), i)
        plane(d, x, y, math.atan2(y - y0, x - x0), 1.1)
        if t > 2.2:  # 경고 표시(폭발 묘사 대신)
            ph = (t - 2.2) * 2.5 + i * 0.3
            rr = 26 + 22 * (ph % 1)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=RED + (int(255 * (1 - ph % 1)),), width=5)
    d.rounded_rectangle((60, 610, 560, 700), 20, fill=(0, 0, 0))
    d.text((90, 624), "몇 시간 간격 출발", font=F(46), fill=YEL)
    if t > 2.2:
        ctext(d, 800, 620, "비행 중 노림", 56, fill=RED)


def bottle(d, cx, by, s=1.0, fill_col=(230, 120, 40), seal=True, wob=0.0):
    w, h = 150 * s, 360 * s
    x0, x1 = cx - w / 2, cx + w / 2
    top = by - h
    # 몸통
    d.rounded_rectangle((x0, top + 90 * s, x1, by), int(40 * s), fill=(210, 230, 245), outline=(255, 255, 255), width=4)
    # 음료
    lv = top + 140 * s
    d.polygon([(x0 + 6, lv + 10 * math.sin(wob)), (x1 - 6, lv - 10 * math.sin(wob)), (x1 - 6, by - 10),
               (x0 + 6, by - 10)], fill=fill_col)
    d.rounded_rectangle((x0 + 6, by - 40 * s, x1 - 6, by - 6), int(30 * s), fill=fill_col)
    # 목·뚜껑
    d.polygon([(x0 + 20 * s, top + 92 * s), (cx - 26 * s, top + 30 * s), (cx + 26 * s, top + 30 * s),
               (x1 - 20 * s, top + 92 * s)], fill=(210, 230, 245))
    d.rectangle((cx - 30 * s, top, cx + 30 * s, top + 34 * s), fill=RED)
    if seal:
        d.rectangle((cx - 32 * s, top + 34 * s, cx + 32 * s, top + 44 * s), fill=(255, 255, 255))
    # 라벨
    d.rectangle((x0, top + 170 * s, x1, top + 250 * s), fill=YEL)
    ft = F(int(40 * s)); tw = d.textlength("SODA", font=ft)
    d.text((cx - tw / 2, top + 182 * s), "SODA", font=ft, fill=(30, 34, 44))


def s_bottle(img, t):
    d = ImageDraw.Draw(img)
    for i in range(14):  # 은은한 배경 줄
        d.line((0, i * 60, W, i * 60), fill=(22, 36, 60), width=2)
    a = ease(clamp(t / 0.5))
    bottle(d, 540, 700 + (1 - a) * 300, 1.4, wob=t * 5)
    if t > 1.0:
        b = ease(clamp((t - 1.0) / 0.4))
        d.rounded_rectangle((640, 120, 1010, 230), 24, fill=(255, 255, 255))
        d.polygon([(660, 220), (620, 270), (700, 225)], fill=(255, 255, 255))
        d.text((675, 140), "뚜껑 봉인 그대로", font=F(40), fill=(30, 34, 44))
    if t > 1.8:
        d.rounded_rectangle((70, 140, 430, 250), 24, fill=GRN)
        d.text((100, 162), "겉보기엔 새 음료", font=F(42), fill=(255, 255, 255))


def s_scan(img, t):
    d = ImageDraw.Draw(img)
    # 컨베이어
    d.rectangle((0, 560, W, 600), fill=(60, 70, 90))
    for i in range(20):
        x = (i * 70 - t * 140) % (W + 70) - 35
        d.line((x, 560, x + 20, 600), fill=(90, 100, 120), width=4)
    # 엑스레이 문
    d.rectangle((420, 230, 660, 560), fill=(30, 46, 72), outline=CYAN, width=6)
    d.rectangle((430, 240, 650, 300), fill=(10, 18, 30))
    d.text((452, 248), "X-RAY", font=F(40), fill=CYAN)
    # 가방 + 병
    bx = -220 + t * 330
    d.rounded_rectangle((bx, 420, bx + 220, 560), 18, fill=(120, 80, 50))
    d.rectangle((bx + 70, 395, bx + 150, 425), outline=(120, 80, 50), width=10)
    if 420 < bx + 110 < 660:  # 문 안: 투시
        bottle(d, bx + 110, 552, 0.36, fill_col=(150, 200, 255))
    # 모니터
    d.rounded_rectangle((760, 120, 1040, 330), 18, fill=(10, 18, 30), outline=GRAY, width=4)
    if t > 1.4:
        d.text((800, 160), "음료수", font=F(50), fill=INK)
        d.text((800, 235), "✓ 통과", font=F(50), fill=GRN)
    if t > 2.3:
        ph = (t * 4) % 1
        d.rounded_rectangle((60, 90, 380, 200), 24, fill=RED if ph < 0.6 else (150, 40, 34))
        d.text((90, 112), "속일 계획", font=F(52), fill=(255, 255, 255))


def zipbag(d, x0, y0, x1, y1):
    d.rounded_rectangle((x0, y0, x1, y1), 20, fill=(200, 225, 245, 90), outline=(255, 255, 255), width=5)
    d.rectangle((x0 + 4, y0 + 14, x1 - 4, y0 + 30), fill=BLU)


def s_rule(img, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # 큰 병 → X
    bottle(d, 230, 640, 1.15)
    if t > 0.5:
        k = ease(clamp((t - 0.5) / 0.35))
        d.line((90, 230, 90 + 280 * k, 230 + 420 * k), fill=RED, width=22)
        d.line((370, 230, 370 - 280 * k, 230 + 420 * k), fill=RED, width=22)
    # 지퍼백 + 작은 병
    zipbag(d, 540, 250, 1000, 680)
    d.text((590, 180), "1L 지퍼백", font=F(48), fill=INK)
    for i in range(3):
        k = ease(clamp((t - 1.0 - i * 0.3) / 0.45))
        if k <= 0:
            continue
        x = 630 + i * 140; y = 640 - (1 - k) * 420
        bottle(d, x, y, 0.55, fill_col=[(230, 120, 40), (150, 200, 255), (240, 170, 200)][i], seal=False)
    if t > 2.0:
        ctext(d, 770, 300, "100ml 씩", 60, fill=YEL, stroke=4)
    img.alpha_composite(lay)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    run("map", 3.4, s_map)
    run("fly", 3.2, s_fly)
    run("bottle", 3.0, s_bottle)
    run("scan", 3.2, s_scan)
    run("rule", 3.2, s_rule)
    print("ok")
