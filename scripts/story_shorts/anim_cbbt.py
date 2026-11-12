#!/usr/bin/env python3
"""체서피크 베이 브리지-터널 모션그래픽(실사 먼저 → 그래픽 설명 구성용, 카드 영상 칸 1080x780) — 2026.11.12 오늘의쓸모.
  python3 scripts/story_shorts/anim_cbbt.py <출력폴더>
  → navy.mp4    (위에서 본 지도: 노퍽 해군기지 ↔ 대서양 바닷길을 다리가 가로지름 → 다리가 무너지면 군함이 갇힘)
    section.mp4 (옆에서 본 단면: 다리 → 인공섬 → 항로 밑 터널 → 인공섬 → 다리, 위로 배가 지나감 → 전체 배치: 섬 4개·터널 2개·28km)
근거: Wikipedia 'Chesapeake Bay Bridge–Tunnel' — "The United States Navy objected to bridging the Thimble Shoals Channel because a
      bridge collapse (possibly by sabotage) ... could cut Naval Station Norfolk off from the Atlantic Ocean", 17.6 mi(28.3 km),
      two one-mile (1.6 km) tunnels beneath the Thimble Shoals and Chesapeake channels, four artificial islands, opened April 1964.
      PBS Building Big 'Chesapeake Bay Bridge-Tunnel' — "due to the importance of shipping in the bay ... two mile-long tunnels".
"""
import subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 205, 40); RED = (225, 35, 45); DARK = (30, 34, 44)
SEA = (28, 78, 120); SEA2 = (36, 96, 146); LAND = (196, 182, 140); ROADC = (232, 232, 236)
NAVY = (120, 130, 145); GREEN = (110, 225, 140)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, base, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = base.copy()
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def ship(d, x, y, s=1.0, col=NAVY):
    """위에서 본 군함(오른쪽을 향함)"""
    L, Wd = 150 * s, 34 * s
    d.polygon([(x - L / 2, y - Wd / 2), (x + L / 2 - 30 * s, y - Wd / 2), (x + L / 2, y),
               (x + L / 2 - 30 * s, y + Wd / 2), (x - L / 2, y + Wd / 2)], fill=col, outline=(40, 44, 52))
    d.rectangle((x - 30 * s, y - 10 * s, x + 20 * s, y + 10 * s), fill=(90, 98, 112))


# ---------- ① 위에서 본 지도 ----------
BX = 640                      # 다리(남북) x
CH_Y = 470                    # 군함 항로 y
def navy_base():
    img = Image.new("RGB", (W, H), SEA); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 120), fill=LAND)                          # 북쪽 땅(이스턴쇼어)
    d.polygon([(0, 640), (0, H), (W, H), (W, 700), (700, 690), (400, 650)], fill=LAND)   # 남쪽 땅
    d.polygon([(0, 520), (150, 560), (220, 640), (0, 660)], fill=LAND)                    # 노퍽 쪽
    # 항로(진한 띠)
    d.rectangle((0, CH_Y - 38, W, CH_Y + 38), fill=SEA2)
    for x in range(0, W, 60):
        d.line((x, CH_Y - 38, x + 30, CH_Y - 38), fill=(150, 200, 235), width=2)
        d.line((x, CH_Y + 38, x + 30, CH_Y + 38), fill=(150, 200, 235), width=2)
    return img


def navy(img, t):
    d = ImageDraw.Draw(img)
    # 라벨
    ctext(d, 120, 575, "노퍽", 40, fill=YEL); ctext(d, 120, 618, "해군기지", 32, fill=YEL)
    ctext(d, 970, 420, "대서양", 44, fill=WHITE)
    # 다리(위에서 아래로 그려짐)
    k = ease(t / 0.9)
    y_end = 120 + (690 - 120) * k
    broken = t > 2.6
    for y in range(120, int(y_end), 8):
        if broken and CH_Y - 60 < y < CH_Y + 60:
            continue
        d.rectangle((BX - 9, y, BX + 9, y + 6), fill=ROADC)
    # 무너짐: 잔해가 항로에 흩어짐
    if broken:
        a = ease((t - 2.6) / 0.5)
        for j, (dx, dy) in enumerate([(-30, -20), (25, 10), (-10, 30), (35, -30), (-40, 15), (5, -5)]):
            cx, cy = BX + dx * a, CH_Y + dy * a
            d.polygon([(cx - 14, cy - 6), (cx + 12, cy - 9), (cx + 15, cy + 7), (cx - 10, cy + 9)], fill=(150, 150, 150), outline=(60, 60, 60))
        if int(t * 6) % 2 == 0 or t > 3.4:
            d.line((BX - 70, CH_Y - 70, BX + 70, CH_Y + 70), fill=RED, width=14)
            d.line((BX - 70, CH_Y + 70, BX + 70, CH_Y - 70), fill=RED, width=14)
    # 군함: 0.6초부터 오른쪽으로, 무너지면 다리 앞에서 멈춤
    if broken:
        sx = 300 + 200 * ease((t - 2.6) / 0.8)
    else:
        sx = -60 + 360 * clamp((t - 0.4) / 2.2)
    ship(d, sx, CH_Y, 1.4)
    ctext(d, 540, 22, "만약 바닷길 위가 전부 다리라면", 46, fill=WHITE)
    if broken and t > 3.3:
        a = ease((t - 3.3) / 0.4)
        y0 = 150 + (1 - a) * 40
        d.rounded_rectangle((170, y0, 910, y0 + 90), 18, fill=(250, 245, 230))
        ctext(d, 540, y0 + 14, "무너지면 군함이 항구에 갇힌다", 44, fill=RED, stroke=0)


# ---------- ② 옆에서 본 단면 → 전체 배치 ----------
SURF, BED = 330, 560
def sec_base():
    img = Image.new("RGB", (W, H), (150, 196, 232)); d = ImageDraw.Draw(img)
    d.rectangle((0, SURF, W, BED), fill=SEA)
    d.rectangle((0, BED, W, H), fill=(120, 98, 70))
    return img


def road_y(x):
    """단면 도로 높이: 다리(SURF-90) → 섬(330~430) → 터널(바닥 밑) → 섬(650~750) → 다리"""
    if x < 300: return SURF - 90
    if x < 400: return SURF - 90 + (SURF - 30 - (SURF - 90)) * (x - 300) / 100
    if x < 680:
        top, low = SURF - 30, BED + 45
        if x < 470: return top + (low - top) * (0.5 - 0.5 * math.cos(math.pi * (x - 400) / 70))
        if x < 610: return low
        return low + (top - low) * (0.5 - 0.5 * math.cos(math.pi * (x - 610) / 70))
    if x < 780: return SURF - 30 - 60 * (x - 680) / 100
    return SURF - 90


def section(img, t):
    d = ImageDraw.Draw(img)
    if t < 2.7:
        # 인공섬 2개(돌 더미)
        for cx in (350, 730):
            d.polygon([(cx - 90, BED), (cx - 50, SURF - 30), (cx + 50, SURF - 30), (cx + 90, BED)], fill=(170, 160, 140), outline=(90, 80, 60))
        # 다리 기둥
        for x in list(range(20, 300, 60)) + list(range(800, W, 60)):
            d.rectangle((x, SURF - 90, x + 10, BED), fill=(200, 200, 205))
        # 도로선
        pts = [(x, road_y(x)) for x in range(0, W + 1, 8)]
        d.line(pts, fill=ROADC, width=14)
        # 터널 튜브 윤곽
        d.line([(x, road_y(x) - 20) for x in range(400, 681, 8)], fill=(255, 255, 255), width=4)
        d.line([(x, road_y(x) + 20) for x in range(400, 681, 8)], fill=(255, 255, 255), width=4)
        # 차(점)가 다리 → 터널 → 다리
        cx = (t / 2.6) * (W + 40) - 20
        d.ellipse((cx - 16, road_y(cx) - 16, cx + 16, road_y(cx) + 16), fill=YEL, outline=(0, 0, 0), width=3)
        # 배: 터널 위 수면을 지나감(옆모습)
        sx = 540 + 40 * math.sin(t * 1.5)
        d.polygon([(sx - 130, SURF - 50), (sx + 150, SURF - 50), (sx + 110, SURF + 10), (sx - 110, SURF + 10)], fill=NAVY, outline=(40, 44, 52))
        d.rectangle((sx - 40, SURF - 100, sx + 50, SURF - 50), fill=(100, 108, 122))
        ctext(d, 540, 22, "배가 다니는 곳만 바닷속 터널로", 50, fill=WHITE)
        ctext(d, 540, 640, "터널 길이 약 1.6km", 44, fill=YEL)
        ctext(d, sx, SURF - 160, "큰 배·군함", 36, fill=WHITE)
    else:
        # 전체 배치(위에서 본 선): 다리-섬-터널-섬-다리-섬-터널-섬-다리
        a = ease((t - 2.7) / 0.45)
        d.rectangle((0, 0, W, H), fill=SEA)
        y = 400
        segs = [("b", 60, 260), ("i", 260, 300), ("t", 300, 420), ("i", 420, 460), ("b", 460, 640),
                ("i", 640, 680), ("t", 680, 800), ("i", 800, 840), ("b", 840, 1020)]
        xmax = 60 + 960 * a
        n_is = 0
        for kind, x0, x1 in segs:
            if x0 > xmax: break
            x1c = min(x1, xmax)
            if kind == "b":
                d.line((x0, y, x1c, y), fill=ROADC, width=14)
            elif kind == "t":
                for x in range(int(x0), int(x1c), 22):
                    d.line((x, y, min(x + 12, x1c), y), fill=YEL, width=10)
            else:
                d.ellipse((x0 - 6, y - 30, x1 + 6, y + 30), fill=(196, 182, 140), outline=(90, 80, 60), width=3)
                n_is += 1
        # 배 2척이 터널 위를 지나감
        if t > 3.3:
            for cx in (360, 740):
                sy = 180 + 440 * clamp((t - 3.3) / 1.7)
                d.polygon([(cx - 16, sy - 60), (cx + 16, sy - 60), (cx + 16, sy + 40), (cx, sy + 60), (cx - 16, sy + 40)], fill=NAVY, outline=(40, 44, 52))
        ctext(d, 540, 22, "바다 위 28km · 1964년 개통", 50, fill=WHITE)
        if t > 3.0:
            ctext(d, 540, 520, f"인공섬 {min(n_is, 4)}개 · 바닷속 터널 2개", 50, fill=YEL)
        if a > 0.95:
            ctext(d, 160, 330, "다리", 36); ctext(d, 360, 452, "터널", 36, fill=YEL); ctext(d, 740, 452, "터널", 36, fill=YEL)


if __name__ == "__main__":
    run("navy", 5.0, navy_base(), navy)
    run("section", 5.2, sec_base(), section)
    print("ok", OUT)
