#!/usr/bin/env python3
"""월드컵 트로피 이야기 모션그래픽(카드 영상 칸 1080x780) — 2026.10.24 오늘의쓸모 '월드컵 트로피의 진짜 정체'.
  python3 scripts/story_shorts/anim_wctrophy.py <출력폴더>
  → swap.mp4(진품은 FIFA 금고로, 우승팀은 금도금 복제품) steal.mp4(1966 런던 전시회에서 사라진 트로피)
    dog.mp4(산책하던 개가 울타리 밑 신문지 꾸러미를 찾음) gone.mp4(1983 브라질에서 또 도난, 끝내 못 찾음)
※ 트로피는 실제 디자인을 베끼지 않은 단순한 모양으로 그린다.
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (16, 28, 48); PANEL = (36, 52, 80); EDGE = (70, 92, 126); INK = (240, 244, 250); GRAY = (150, 162, 182)
GOLD = (255, 200, 60); GOLD2 = (200, 140, 30); BRONZE = (170, 110, 60); RED = (240, 66, 56); GRN = (46, 196, 100)
YEL = (255, 216, 77); HEDGE = (40, 120, 60); HEDGE2 = (30, 90, 45)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, ImageDraw.Draw(img), i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=INK, stroke=0, sfill=(0, 0, 0)):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def trophy(d, cx, by, s=1.0, col=GOLD, dark=GOLD2, band=(30, 140, 80)):
    """단순한 우승 트로피(받침 + 몸통 + 공). by=받침 바닥 y"""
    # 받침
    d.rectangle((cx - 60 * s, by - 40 * s, cx + 60 * s, by), fill=dark)
    d.rectangle((cx - 60 * s, by - 30 * s, cx + 60 * s, by - 18 * s), fill=band)
    # 몸통(위로 갈수록 넓어지는 기둥)
    body = [(cx - 40 * s, by - 40 * s), (cx + 40 * s, by - 40 * s), (cx + 22 * s, by - 120 * s),
            (cx + 55 * s, by - 190 * s), (cx - 55 * s, by - 190 * s), (cx - 22 * s, by - 120 * s)]
    d.polygon(body, fill=col)
    d.line([(cx - 10 * s, by - 45 * s), (cx - 30 * s, by - 180 * s)], fill=dark, width=max(2, int(6 * s)))
    d.line([(cx + 10 * s, by - 45 * s), (cx + 30 * s, by - 180 * s)], fill=dark, width=max(2, int(6 * s)))
    # 공
    r = 52 * s
    d.ellipse((cx - r, by - 190 * s - 2 * r + 12 * s, cx + r, by - 190 * s + 12 * s), fill=col, outline=dark,
              width=max(2, int(5 * s)))
    oy = by - 190 * s - r + 12 * s
    d.arc((cx - r * 0.5, oy - r, cx + r * 0.5, oy + r), 0, 360, fill=dark, width=max(2, int(4 * s)))
    d.line([(cx - r, oy), (cx + r, oy)], fill=dark, width=max(2, int(4 * s)))


def cup(d, cx, by, s=1.0, col=GOLD, dark=GOLD2):
    """옛 트로피(날개 달린 받침 위 컵) — 단순화"""
    d.rectangle((cx - 45 * s, by - 50 * s, cx + 45 * s, by), fill=dark)
    d.polygon([(cx - 18 * s, by - 50 * s), (cx + 18 * s, by - 50 * s), (cx + 10 * s, by - 130 * s),
               (cx - 10 * s, by - 130 * s)], fill=col)
    # 날개
    d.polygon([(cx - 10 * s, by - 120 * s), (cx - 70 * s, by - 170 * s), (cx - 20 * s, by - 150 * s)], fill=col)
    d.polygon([(cx + 10 * s, by - 120 * s), (cx + 70 * s, by - 170 * s), (cx + 20 * s, by - 150 * s)], fill=col)
    # 컵
    d.pieslice((cx - 60 * s, by - 230 * s, cx + 60 * s, by - 110 * s), 0, 180, fill=col)
    d.rectangle((cx - 60 * s, by - 176 * s, cx + 60 * s, by - 170 * s), fill=dark)


# ── 1. 진품 ↔ 복제품 ────────────────────────────────
def s_swap(img, d, t):
    # 왼쪽 금고, 오른쪽 선수들
    vx, vy = 250, 160
    d.rounded_rectangle((vx - 170, vy, vx + 170, vy + 420), 24, fill=PANEL, outline=EDGE, width=6)
    door = ease(clamp((t - 1.6) / 0.8))  # 문 닫힘
    ctext(d, vx, vy + 440, "FIFA 금고", 44, GRAY)
    ctext(d, 790, vy + 440, "우승팀", 44, GRAY)
    # 진품 트로피: 가운데서 금고로 이동
    k = ease(clamp(t / 1.4))
    x = 540 + (vx - 540) * k
    trophy(d, x, vy + 380, 1.0)
    ctext(d, x, vy - 70, "진품", 54, YEL, 4)
    if door > 0:
        dw = 340 * door
        d.rounded_rectangle((vx - 170, vy, vx - 170 + dw, vy + 420), 24, fill=(60, 78, 108), outline=EDGE, width=6)
        if door > 0.95:
            d.ellipse((vx - 30, vy + 180, vx + 30, vy + 240), outline=GRAY, width=8)
            d.line([(vx, vy + 210), (vx + 22, vy + 192)], fill=GRAY, width=8)
    # 복제품 등장
    k2 = ease(clamp((t - 2.0) / 0.8))
    if k2 > 0:
        trophy(d, 790, vy + 380 + (1 - k2) * 60, 0.95, col=(235, 185, 70), dark=BRONZE)
        ctext(d, 790, vy - 70, "금도금 '복제품'", 50, INK, 4)
        if t > 2.8:
            ctext(d, 790, vy - 2, "속은 청동", 38, (230, 160, 110), 3)


# ── 2. 1966 도난 ────────────────────────────────────
def s_steal(img, d, t):
    ctext(d, 540, 40, "1966년 3월 · 런던 우표 전시회", 46, GRAY)
    # 유리 진열장
    cx, by = 540, 610
    d.rectangle((cx - 170, by, cx + 170, by + 60), fill=PANEL)
    gone = t > 1.4
    if not gone:
        cup(d, cx, by - 10, 1.4)
    else:
        a = clamp((t - 1.4) / 0.3)
        # 빈 자리 점선
        for i in range(0, 360, 20):
            ang = math.radians(i)
            px, py = cx + 80 * math.cos(ang), by - 110 + 90 * math.sin(ang)
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=GRAY)
        ctext(d, cx, by - 190, "?", 100, GRAY)
    d.rectangle((cx - 190, 150, cx + 190, by), outline=(150, 200, 230), width=5)
    if 1.2 < t < 1.5:
        d.rectangle((0, 0, W, H), fill=(255, 255, 255))
    if gone:
        s = 1 + 0.15 * math.sin(min(1, (t - 1.5) / 0.3) * math.pi)
        sz = int(110 * s)
        ctext(d, cx, 250 - sz / 2, "도난!", sz, RED, 8, (40, 0, 0))
    if t > 2.4:
        d.rounded_rectangle((640, 520, 1050, 690), 16, fill=(245, 240, 225))
        d.text((665, 535), "협박 편지", font=F(34), fill=(120, 40, 30))
        d.text((665, 585), "몸값 1만5천 파운드", font=F(40), fill=(30, 30, 30))
        d.text((665, 635), "안 주면 녹여 버린다", font=F(30), fill=(90, 90, 90))


# ── 3. 산책하던 개 ──────────────────────────────────
def dog(d, x, y, t, sniff):
    bob = 4 * math.sin(t * 12)
    c = (235, 235, 235); k = (30, 30, 30)
    d.ellipse((x - 90, y - 60 + bob, x + 70, y + 20 + bob), fill=c)  # 몸
    for lx in (-70, -40, 30, 55):
        ph = math.sin(t * 12 + lx) * 10 * (0 if sniff else 1)
        d.line([(x + lx, y + 5 + bob), (x + lx + ph, y + 75)], fill=c, width=16)
    hy = y - 70 + bob + (40 if sniff else 0)
    d.ellipse((x + 50, hy - 40, x + 130, hy + 30), fill=c)  # 머리
    d.ellipse((x + 110, hy - 2, x + 150, hy + 26), fill=c)  # 주둥이
    d.ellipse((x + 140, hy + 2, x + 156, hy + 16), fill=k)  # 코
    d.ellipse((x + 88, hy - 18, x + 100, hy - 6), fill=k)  # 눈
    d.polygon([(x + 60, hy - 30), (x + 78, hy - 70), (x + 92, hy - 34)], fill=k)  # 귀
    d.ellipse((x - 70, y - 50 + bob, x - 10, y - 10 + bob), fill=k)  # 얼룩
    wag = math.sin(t * 20) * 25
    d.line([(x - 88, y - 40 + bob), (x - 130, y - 85 + wag)], fill=c, width=12)


def s_dog(img, d, t):
    ctext(d, 540, 40, "일주일 뒤 · 런던 남부 주택가", 46, GRAY)
    d.rectangle((0, 640, W, H), fill=(60, 66, 74))
    # 울타리
    for i in range(0, W + 80, 70):
        d.ellipse((i - 70, 360, i + 60, 520), fill=HEDGE2)
    d.rectangle((0, 450, W, 650), fill=HEDGE)
    for i in range(0, W + 80, 90):
        d.ellipse((i - 50, 420, i + 60, 500), fill=HEDGE)
    # 신문지 꾸러미
    px, py = 720, 600
    found = t > 2.0
    lift = ease(clamp((t - 2.2) / 0.5))
    d.polygon([(px - 70, py + 40), (px + 70, py + 40), (px + 55, py - 30 - 20 * lift), (px - 55, py - 30 - 20 * lift)],
              fill=(215, 210, 195))
    for j in range(4):
        d.line([(px - 45, py - 10 + j * 12), (px + 45, py - 10 + j * 12)], fill=(150, 150, 150), width=3)
    if lift > 0:
        # 꾸러미 사이로 금빛
        d.ellipse((px - 28, py - 60 - 30 * lift, px + 28, py - 20 - 30 * lift), fill=GOLD)
        r = 40 + 30 * lift
        for a in range(0, 360, 45):
            ang = math.radians(a + t * 60)
            d.line([(px + r * math.cos(ang), py - 40 - 30 * lift + r * math.sin(ang)),
                    (px + (r + 26) * math.cos(ang), py - 40 - 30 * lift + (r + 26) * math.sin(ang))],
                   fill=YEL, width=6)
    # 개 이동
    k = ease(clamp(t / 1.8))
    x = -150 + (px - 270 + 150) * k
    dog(d, x, 640 - 80, t, sniff=t > 1.8)
    if found:
        ctext(d, 540, 130, "찾았다!", 110, YEL, 8, (60, 40, 0))
    if t > 2.8:
        ctext(d, 540, 270, "개 이름은 '피클스'", 52, INK, 5)


# ── 4. 1983 또 도난 ─────────────────────────────────
def s_gone(img, d, t):
    cx, by = 540, 600
    a = 1 - ease(clamp((t - 1.0) / 1.2))
    if a > 0:
        tmp = Image.new("RGB", (W, H), BG)
        cup(ImageDraw.Draw(tmp), cx, by, 1.5)
        img.paste(Image.blend(img, tmp, a))
        d = ImageDraw.Draw(img)
    ctext(d, 540, 40, "1983년 · 브라질", 50, GRAY)
    if t < 1.0:
        ctext(d, cx, 120, "또 도난", 90, RED, 7, (40, 0, 0))
    else:
        ctext(d, cx, 120, "끝내 못 찾음", 90, RED, 7, (40, 0, 0))
    if t > 2.2:
        ctext(d, cx, 330, "녹여 버렸다고", 60, INK, 5)
        ctext(d, cx, 410, "알려졌다", 60, INK, 5)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    run("swap", 4.0, s_swap)
    run("steal", 4.0, s_steal)
    run("dog", 4.0, s_dog)
    run("gone", 3.6, s_gone)
