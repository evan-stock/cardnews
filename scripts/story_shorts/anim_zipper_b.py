#!/usr/bin/env python3
"""금문교 이동식 중앙분리대(로드 지퍼) 모션그래픽 B판(실사 먼저 → 그래픽 설명 구성용, 카드 영상 칸 1080x780) — 2026.11.10 오늘의쓸모.
  python3 scripts/story_shorts/anim_zipper_b.py <출력폴더>
  → before.mp4 (2015년 전: 6차로 가운데 노란 플라스틱 막대뿐 → 차가 넘어와 정면충돌 경고, 1970~2015 정면충돌 100여 건·사망 사고 16건)
    shift.mp4  (콘크리트 블록 벽 → 출근길 한 칸(약 3m) 밀어 남쪽 4차로 : 북쪽 2차로, 퇴근길엔 반대)
근거: goldengate.org 'Moveable Median Barrier'(2015.1.10 설치, 이전엔 25피트마다 높이 19인치 노란 플라스틱 튜브,
      약 10피트 이동, 약 30분, 평일 아침 남쪽 4차로·저녁 북쪽 4차로, 3,000만 달러),
      CNBC 2018.02.08(1970년부터 설치 전까지 정면충돌 100건 넘게·그중 16건 사망, 설치 뒤 정면충돌 0건, 블록 1,500파운드),
      MTC 2016.10.25(블록 3,200개·각 1,500파운드, 하루 두 번 배치 변경).
"""
import subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 205, 40); RED = (220, 30, 40); DARK = (30, 34, 44); GREY = (150, 160, 178)
ROAD = (62, 66, 74); BRIDGE = (192, 54, 44); CONC = (205, 205, 200)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))

# 위에서 본 다리: 차로 6개가 가로로 놓임(왼→오 진행: 위 3차로 북쪽행 ←, 아래 3차로 남쪽행 →)
RX0, RX1 = 0, W
RY0, LANE = 170, 82          # 도로 위 끝, 차로 폭
RY1 = RY0 + LANE * 6


def bg():
    img = Image.new("RGB", (W, H), (22, 28, 40)); d = ImageDraw.Draw(img)
    d.rectangle((RX0, RY0 - 26, RX1, RY0), fill=BRIDGE)
    d.rectangle((RX0, RY1, RX1, RY1 + 26), fill=BRIDGE)
    d.rectangle((RX0, RY0, RX1, RY1), fill=ROAD)
    for k in range(1, 6):
        y = RY0 + LANE * k
        for x in range(0, W, 70):
            d.line((x, y, x + 36, y), fill=(220, 220, 220), width=3)
    return img


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


def car(d, x, y, col, rot=0.0, dirn=1):
    """위에서 본 차: (x,y)=중심, rot=기울기(라디안)"""
    L, Wd = 92, 44
    pts = [(-L / 2, -Wd / 2), (L / 2, -Wd / 2), (L / 2, Wd / 2), (-L / 2, Wd / 2)]
    c, s = math.cos(rot), math.sin(rot)
    P = [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]
    d.polygon(P, fill=col, outline=(20, 20, 20))
    # 앞유리
    fx = L / 2 - 26 if dirn > 0 else -L / 2 + 10
    q = [(fx, -Wd / 2 + 6), (fx + 16, -Wd / 2 + 6), (fx + 16, Wd / 2 - 6), (fx, Wd / 2 - 6)]
    d.polygon([(x + px * c - py * s, y + px * s + py * c) for px, py in q], fill=(140, 190, 230))


def lane_y(k):  # k=0..5 위에서부터
    return RY0 + LANE * k + LANE / 2


# ① 2015년 전: 플라스틱 막대뿐
def before(img, t):
    d = ImageDraw.Draw(img)
    mid = RY0 + LANE * 3
    # 노란 플라스틱 막대(위에서 본 점) — 0.3초부터 하나씩 나타남
    n = int(clamp((t - 0.2) / 0.8) * 28)
    for k in range(n):
        x = 20 + k * 38
        d.ellipse((x - 9, mid - 9, x + 9, mid + 9), fill=YEL, outline=(120, 90, 0), width=2)
    # 흐르는 차들
    for k, (ln, sp, off, col) in enumerate([(0, -260, 200, (90, 140, 220)), (1, -230, 700, (230, 230, 235)),
                                             (2, -250, 950, (60, 60, 64)), (4, 240, 100, (200, 60, 60)),
                                             (5, 260, 600, (240, 240, 240))]):
        x = (off + sp * t) % (W + 200) - 100
        car(d, x, lane_y(ln), col, 0, 1 if sp > 0 else -1)
    # 주인공 차: 남쪽행 3번째 차로(위에서 3)에서 미끄러져 중앙을 넘음
    k = ease((t - 1.6) / 1.4)
    x = 140 + 330 * clamp((t - 0.0) / 3.0)
    y = lane_y(3) - k * LANE * 1.05
    car(d, x, y, (255, 255, 255), -0.35 * k, 1)
    # 마주 오는 차(북쪽행)
    x2 = 1000 - 300 * clamp(t / 3.0)
    car(d, x2, lane_y(2), (60, 120, 210), 0, -1)
    if t > 2.9:
        a = clamp((t - 2.9) / 0.25)
        cx, cy = (x + x2) / 2 + 30, lane_y(2) + 10
        r = 70 + 30 * a
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=10)
        ctext(d, cx, cy - 40, "쾅!", 60, fill=YEL)
    # 위 라벨
    ctext(d, 540, 40, "2015년 전 · 가운데엔 노란 플라스틱 막대뿐", 46, fill=WHITE)
    if t > 3.3:
        a = ease((t - 3.3) / 0.4)
        y0 = 660 + (1 - a) * 80
        d.rounded_rectangle((120, y0, 960, y0 + 96), 18, fill=(250, 245, 230))
        ctext(d, 540, y0 + 16, "1970~2015 정면충돌 100여 건 · 사망 사고 16건", 40, fill=DARK, stroke=0)


# ② 블록 벽을 한 칸 민다
def shift(img, t):
    d = ImageDraw.Draw(img)
    k2 = ease((t - 3.5) / 1.1)                # 3.5~4.6초 퇴근길: 반대쪽으로 두 칸
    tx = -140 + 1460 * clamp((t - 0.5) / 2.6)   # 노란 트럭(벽을 따라 왼→오)
    def bpos(x):  # 트럭이 지나간 곳만 한 칸 위로(트럭 몸통 안에서 S자로 옮겨짐)
        kk = ease(clamp((tx - 60 - x) / 160))
        return 3 - kk + 2 * k2
    for i in range(0, W, 30):
        mb = RY0 + LANE * bpos(i + 15)
        d.rectangle((i + 2, mb - 12, i + 28, mb + 12), fill=CONC, outline=(120, 120, 120))
        d.line((i + 2, mb, i + 28, mb), fill=YEL, width=3)
    b = 3 - (1 if tx > 540 else 0) + 2 * k2
    # 방향 화살표와 차로 수
    n_north = int(round(b))
    mid = RY0 + LANE * (2.5 + 2 * k2)
    n_south = 6 - n_north
    for ln in range(6):
        y = lane_y(ln)
        south = ln >= (6 - n_south)
        x = 540 + (180 if south else -180) * math.sin(t * 2.2 + ln) * 0.15
        if south:
            d.polygon([(x + 40, y), (x - 10, y - 22), (x - 10, y + 22)], fill=(120, 230, 140))
            d.rectangle((x - 60, y - 7, x - 10, y + 7), fill=(120, 230, 140))
        else:
            d.polygon([(x - 40, y), (x + 10, y - 22), (x + 10, y + 22)], fill=(255, 150, 120))
            d.rectangle((x + 10, y - 7, x + 60, y + 7), fill=(255, 150, 120))
    # 노란 트럭(벽을 따라 왼→오)
    if -150 < tx < W + 150:
        d.rounded_rectangle((tx - 80, mid - 34, tx + 80, mid + 34), 10, fill=YEL, outline=(110, 80, 0), width=4)
        d.rectangle((tx + 40, mid - 26, tx + 70, mid + 26), fill=(140, 190, 230))
    ctext(d, 540, 40, "블록 1개 680kg × 3,200여 개", 48, fill=YEL)
    lab = "출근길: 벽을 한 칸(약 3m) 밀어 4 : 2" if t < 3.4 else "퇴근길엔 반대로 2 : 4"
    ctext(d, 540, 676, lab, 46, fill=WHITE)
    ctext(d, 980, RY0 + LANE * 4.2, f"{n_south}", 64, fill=(120, 230, 140))
    ctext(d, 980, RY0 + LANE * 0.7, f"{n_north}", 64, fill=(255, 150, 120))


if __name__ == "__main__":
    B = bg()
    run("before", 5.0, B, before)
    run("shift", 5.0, B, shift)
    print("ok", OUT)
