#!/usr/bin/env python3
"""망가진 나사 구멍을 녹인 주석으로 되살리는 원리 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.16 오늘의쓸모.
  python3 scripts/story_shorts/anim_scrw.py <출력폴더>
  → fill.mp4 (단면: 나사산이 뭉개진 구멍 → 볼트가 헛돎 → 녹인 주석을 부어 구멍을 메움 → 망치로 눌러 빈틈까지 꽉)
    tap.mp4  (단면: 주석 가운데를 드릴로 뚫음 → 탭이 무른 주석에 새 나사산을 깎음 → 볼트가 다시 물림 → 주석은 물러 가벼운 볼트용)
근거: 원촬영자 영상 제목 'Thread restored with melted tin!'(YouTube Vinicinn_torneiro, 2026.09.10),
      주석 녹는점 231.9℃·무른 금속(위키백과 'Tin', 영국왕립화학회 원소표),
      나사산 수리의 정석은 헬리코일·인서트(Jalopnik 2020 'Definitive best method of fixing a stripped thread', Hagerty UK).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (28, 34, 44); IRON = (120, 104, 84); IRON_D = (84, 72, 58); IRON_L = (150, 132, 108)
TIN = (205, 210, 218); TIN_D = (160, 166, 176); TIN_L = (240, 244, 250)
STEEL = (90, 96, 104); STEEL_L = (140, 146, 156)
WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); GREEN = (70, 200, 110)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
TOP, BOT = 330, 720           # 부품 윗면·아랫면
HX, HW = 540, 80              # 구멍 중심, 폭/2(뭉개진 구멍)
HB = 650                      # 구멍 바닥


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


def arrow(d, x0, y0, x1, y1, col, w=7, head=20):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    d.polygon([(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
               (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))], fill=col)


def part(d):
    """주철 부품 단면(구멍 자리는 비워 둠)."""
    d.rectangle((60, TOP, W - 60, BOT), fill=IRON)
    for k in range(0, W, 46):  # 단면 빗금
        d.line((k, BOT, k + 120, TOP), fill=IRON_D, width=3)
    d.rectangle((0, 0, W, TOP), fill=BG)
    d.rectangle((0, BOT, W, H), fill=BG)
    d.rectangle((0, TOP, 60, BOT), fill=BG); d.rectangle((W - 60, TOP, W, BOT), fill=BG)
    d.line((60, TOP, W - 60, TOP), fill=IRON_L, width=5)


def crushed_hole(d, col=BG, marks=True):
    """나사산이 뭉개진 구멍: 벽이 울퉁불퉁하고 넓어짐."""
    left, right = [], []
    for k, y in enumerate(range(TOP, HB + 1, 16)):
        j = [6, -4, 10, 2, -6, 8, 0, 12, -2, 7, 3, -5, 9, 1, 5, -3, 8, 2, 6, 0, 4, -2, 7][k % 23]
        left.append((HX - HW - j, y)); right.append((HX + HW + j, y))
    d.polygon(left + [(HX - HW, HB), (HX + HW, HB)] + right[::-1], fill=col)
    if not marks:
        return
    for (x, y) in left[1:-1:2]:
        d.line((x, y, x + 16, y + 6), fill=IRON_D, width=4)
    for (x, y) in right[1:-1:2]:
        d.line((x, y, x - 16, y + 6), fill=IRON_D, width=4)


def bolt(d, x, ytip, half=58, phase=0.0, head=True, length=330):
    """옆에서 본 볼트. phase 로 나사선이 흘러 '도는' 느낌."""
    y0 = ytip - length
    d.rectangle((x - half, y0, x + half, ytip), fill=STEEL)
    pitch = 26
    off = (phase * pitch) % pitch
    y = y0 + off
    while y < ytip - 6:
        d.line((x - half, y, x + half, y + 12), fill=STEEL_L, width=6)
        y += pitch
    # 톱니 가장자리
    for yy in range(int(y0), int(ytip), pitch):
        yy2 = yy + (off % pitch)
        if yy2 < ytip - 8:
            d.polygon([(x - half, yy2), (x - half - 12, yy2 + 8), (x - half, yy2 + 16)], fill=STEEL)
            d.polygon([(x + half, yy2 + 6), (x + half + 12, yy2 + 14), (x + half, yy2 + 22)], fill=STEEL)
    if head:
        d.rectangle((x - 100, y0 - 70, x + 100, y0), fill=STEEL, outline=STEEL_L, width=4)


def spin_mark(d, x, y, t, col):
    a0 = (t * 400) % 360
    d.arc((x - 150, y - 34, x + 150, y + 34), a0, a0 + 250, fill=col, width=8)
    a = math.radians(a0 + 250)
    px, py = x + 150 * math.cos(a), y + 34 * math.sin(a)
    d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=col)


def fill(img, t):
    d = ImageDraw.Draw(img)
    part(d)
    crushed_hole(d)
    # ① 0~2.3초: 볼트가 헛돎
    if t < 2.4:
        k = ease(clamp(t / 0.6))
        ytip = 160 + (HB - 20 - 160) * k
        bolt(d, HX, ytip, phase=t * 6 if t > 0.6 else 0)
        if t > 0.7:
            spin_mark(d, HX, TOP - 60, t, RED)
            ctext(d, HX, 30, "나사산이 뭉개져 볼트가 '헛돎'", 54, fill=RED)
            arrow(d, 860, 520, HX + HW + 22, 520, YEL, w=7)
            ctext(d, 930, 470, "뭉개진", 40, fill=YEL)
            ctext(d, 930, 520, "나사산", 40, fill=YEL)
        return
    # ② 2.4~3.9초: 녹인 주석을 부음
    k = ease(clamp((t - 2.4) / 1.2))
    level = HB - (HB - TOP + 40) * k          # 차오르는 높이(넘쳐 볼록)
    tin = Image.new("RGB", (W, H), BG); crushed_hole(ImageDraw.Draw(tin), TIN)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle((0, max(level, TOP), W, HB + 2), fill=255)
    hm = Image.new("L", (W, H), 0); crushed_hole(ImageDraw.Draw(hm), 255, marks=False)
    from PIL import ImageChops
    img.paste(tin, (0, 0), ImageChops.multiply(m, hm)); d = ImageDraw.Draw(img)
    if level <= TOP:
        dome = (TOP - level)
        flat = ease(clamp((t - 4.1) / 0.4))
        dome *= (1 - flat * 0.85)
        d.chord((HX - HW - 30, TOP - dome * 2, HX + HW + 30, TOP + dome * 0.2), 180, 360, fill=TIN, outline=TIN_D)
    if t < 3.7:
        sx = HX
        d.polygon([(sx - 160, 40), (sx + 60, 40), (sx + 20, 120), (sx - 120, 120)], fill=(70, 70, 76))
        d.line((sx, 120, sx, max(level, TOP - 40)), fill=TIN_L, width=22)
    ctext(d, HX, 150 if t < 3.7 else 16, "녹는점 232℃ '주석'을 부으면", 50, fill=WHITE)
    arrow(d, 860, 560, HX + HW + 20, 560, YEL, w=7)
    ctext(d, 930, 500, "구멍 꽉", 40, fill=YEL)
    # ③ 3.9초~: 망치로 눌러 빈틈까지
    if t > 3.8:
        hk = clamp((t - 3.8) / 0.5)
        hy = TOP - 8 - 110 * abs(math.cos(hk * math.pi * 2)) if hk < 1 else TOP - 8
        d.rounded_rectangle((HX - 150, hy - 100, HX + 150, hy), 14, fill=(110, 80, 50), outline=(70, 50, 30), width=5)
        d.rectangle((HX - 18, max(90, hy - 230), HX + 18, hy - 100), fill=(150, 110, 70))
        if hk > 0.4:
            ctext(d, 880, 160, "망치로 꾹꾹", 50, fill=YEL)
            for s in (-1, 1):
                arrow(d, HX + s * 40, 470, HX + s * (HW + 6), 470, YEL, w=6, head=16)


def part_top_mask(d, level):
    """주석이 덜 찼을 때 구멍 위쪽 벽을 다시 그림(뭉개진 결 유지)."""
    for y in range(TOP, int(level), 16):
        d.line((HX - HW - 8, y, HX - HW + 8, y + 6), fill=IRON_D, width=4)
        d.line((HX + HW + 8, y, HX + HW - 8, y + 6), fill=IRON_D, width=4)


def threaded_hole(d, depth_y, cut=1.0):
    """주석 속에 새로 깎인 나사 구멍(톱니 벽). cut=0이면 매끈한 드릴 구멍."""
    r0, r1 = 46, 46 + 14 * cut
    d.rectangle((HX - r0, TOP, HX + r0, depth_y), fill=BG)
    pitch = 26
    for y in range(TOP, int(depth_y) - 10, pitch):
        d.polygon([(HX - r0, y), (HX - r1, y + 10), (HX - r0, y + 20)], fill=BG)
        d.polygon([(HX + r0, y + 6), (HX + r1, y + 16), (HX + r0, y + 26)], fill=BG)


def tap(img, t):
    d = ImageDraw.Draw(img)
    part(d)
    crushed_hole(d, TIN)
    d.line((HX - HW - 20, TOP, HX + HW + 20, TOP), fill=TIN_L, width=5)
    ctext(d, 900, 640, "주석", 40, fill=TIN_L)
    # ① 0~1.3초: 드릴로 가운데를 뚫음
    if t < 1.4:
        k = ease(clamp(t / 1.2))
        dep = TOP + (HB - 10 - TOP) * k
        d.rectangle((HX - 46, TOP, HX + 46, dep), fill=BG)
        x = HX
        d.rectangle((x - 44, dep - 420, x + 44, dep), fill=STEEL_L)
        for yy in range(int(dep - 420), int(dep), 40):
            o = (t * 160) % 40
            d.line((x - 44, yy + o, x + 44, yy + o + 26), fill=STEEL, width=8)
        ctext(d, HX, 30, "가운데를 드릴로 뚫고", 54)
        return
    # ② 1.4~3.0초: 탭이 새 나사산을 깎음
    if t < 3.0:
        k = ease(clamp((t - 1.4) / 1.4))
        dep = TOP + (HB - 10 - TOP) * k
        threaded_hole(d, HB - 10, cut=0)
        threaded_hole(d, dep, cut=1)
        bolt(d, HX, dep, half=46, phase=t * 8, head=False, length=440)
        spin_mark(d, HX, TOP - 150, t, YEL)
        ctext(d, HX, 30, "'탭'으로 나사산을 새로 깎는다", 54, fill=YEL)
        if t > 2.0:
            arrow(d, 860, 520, HX + 70, 520, YEL, w=7)
            ctext(d, 930, 470, "새 나사산", 40, fill=YEL)
        return
    # ③ 3.0~5초: 볼트가 다시 물림
    threaded_hole(d, HB - 10, cut=1)
    k = ease(clamp((t - 3.0) / 1.0))
    ytip = 200 + (HB - 20 - 200) * k
    bolt(d, HX, ytip, half=58, phase=t * 6 if k < 1 else 0)
    if k >= 1:
        ctext(d, HX, 30, "볼트가 다시 '꽉'", 60, fill=GREEN)
        d.line((850, 210, 890, 250), fill=GREEN, width=14); d.line((890, 250, 970, 150), fill=GREEN, width=14)
    if t > 4.1:
        d.rounded_rectangle((40, 100, 470, 230), 18, fill=(18, 26, 36), outline=YEL, width=4)
        ctext(d, 255, 112, "단, 주석은 무른 금속", 36, fill=YEL, stroke=0)
        ctext(d, 255, 166, "→ 힘 적게 받는 곳만", 36, fill=WHITE, stroke=0)


run("fill", 5.0, fill)
run("tap", 5.2, tap)
print("ok")
