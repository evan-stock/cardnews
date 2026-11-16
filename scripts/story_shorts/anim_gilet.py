"""노란 조끼 편 정답 그래픽(2026.10.27): 자동차 → 문 주머니에서 형광 조끼가 나옴 → '2008년부터 의무' → 벌금 135유로.
letterbox 영상 영역 1080x780, 30fps, 9초. 사용: python scripts/story_shorts/anim_gilet.py <작업폴더> <출력.mp4>"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, T = 1080, 780, 30, 9.0
FB = "assets/fonts/Pretendard-Black.otf"
FS = "assets/fonts/Pretendard-SemiBold.otf"
BG = (20, 24, 33); YEL = (255, 212, 59); NEON = (214, 255, 40); RED = (235, 60, 60); WHITE = (255, 255, 255)
CAR = (70, 110, 170); GLASS = (150, 195, 230); DARK = (30, 32, 40); SILVER = (215, 220, 228)


def F(s, p=FB):
    return ImageFont.truetype(p, s)


def ease(t):
    return 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3


def text(d, xy, s, size, fill=WHITE, a=255, path=FB, stroke=5, anchor="mm"):
    d.text(xy, s, font=F(size, path), fill=fill + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, a))


def vest(size):
    """형광 조끼(반사띠 2줄) RGBA 이미지."""
    w, h = size, int(size * 1.15)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = w / 300
    body = [(60, 0), (110, 0), (150, 70), (190, 0), (240, 0), (300, 60), (270, 120), (260, 345), (40, 345), (30, 120), (0, 60)]
    d.polygon([(x * k, y * k) for x, y in body], fill=NEON)
    for y in (200, 260):
        d.rectangle((35 * k, y * k, 265 * k, (y + 26) * k), fill=SILVER)
    d.line([(150 * k, 70 * k), (150 * k, 345 * k)], fill=(170, 200, 30), width=max(2, int(5 * k)))
    return im


def frame(t):
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 640, W, H), fill=(32, 37, 48))
    # 차(옆모습): 0~0.8초 왼쪽에서 들어옴
    cx = int(-500 + 900 * ease(t / 0.8))
    y0 = 600
    d.rounded_rectangle((cx - 330, y0 - 170, cx + 330, y0 - 30), 50, fill=CAR)
    d.polygon([(cx - 200, y0 - 170), (cx - 120, y0 - 300), (cx + 140, y0 - 300), (cx + 230, y0 - 170)], fill=CAR)
    d.polygon([(cx - 175, y0 - 175), (cx - 110, y0 - 280), (cx + 5, y0 - 280), (cx + 5, y0 - 175)], fill=GLASS)
    d.polygon([(cx + 20, y0 - 175), (cx + 20, y0 - 280), (cx + 130, y0 - 280), (cx + 205, y0 - 175)], fill=GLASS)
    for wx in (cx - 200, cx + 200):
        d.ellipse((wx - 70, y0 - 100, wx + 70, y0 + 40), fill=DARK)
        d.ellipse((wx - 32, y0 - 62, wx + 32, y0 + 2), fill=(120, 125, 135))
    # 운전석 문 테두리 + 문 주머니 강조
    door = (cx - 170, y0 - 170, cx + 10, y0 - 40)
    d.rectangle(door, outline=(40, 70, 120), width=6)
    g = ease((t - 1.0) / 0.5)
    if g > 0:
        r = 26 + int(10 * math.sin(t * 6))
        d.rounded_rectangle((cx - 150, y0 - 95, cx - 10, y0 - 50), 12, outline=YEL + (int(255 * g),), width=r // 4)
    # 조끼가 문 주머니에서 솟아오름
    v = ease((t - 1.6) / 0.9)
    if v > 0:
        sz = int(120 + 160 * v)
        vi = vest(sz)
        vx = int((cx - 80) + (300 - (cx - 80)) * v) - vi.width // 2
        vy = int((y0 - 80) + (260 - (y0 - 80)) * v) - vi.height // 2
        im.alpha_composite(vi, (vx, max(0, vy)))
        d = ImageDraw.Draw(im, "RGBA")
        if v > 0.9:
            for k in range(6):  # 반짝
                a = (t * 3 + k / 6) % 1
                ang = k * math.pi / 3
                rr = 170 + 40 * a
                x, y = 300 + rr * math.cos(ang), 260 + rr * math.sin(ang)
                d.line((x, y, x + 18 * math.cos(ang), y + 18 * math.sin(ang)), fill=YEL + (int(255 * (1 - a)),), width=6)
    # 오른쪽 글자
    a1 = ease((t - 2.6) / 0.4)
    if a1 > 0:
        text(d, (790, 150), "2008년부터", 64, WHITE, a=int(255 * a1))
        text(d, (790, 235), "차 안에 의무", 64, YEL, a=int(255 * a1))
        text(d, (790, 300), "손 닿는 곳에 1벌", 34, (200, 205, 215), a=int(255 * a1), path=FS, stroke=0)
    s = t - 4.2
    if s > 0:  # 벌금 도장
        k = 1.8 - 0.8 * ease(s / 0.35)
        a = int(255 * min(1, s / 0.2))
        box = Image.new("RGBA", (470, 150), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle((4, 4, 466, 146), 18, outline=RED + (a,), width=10)
        bd.text((235, 75), "없으면 벌금 135유로", font=F(48), fill=RED + (a,), anchor="mm")
        box = box.resize((int(470 * k), int(150 * k))).rotate(-8, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(box, (790 - box.width // 2, 430 - box.height // 2))
    ImageDraw.Draw(im).text((22, 18), "재현 그래픽", font=F(26, FS), fill=(190, 190, 195))
    return im


if __name__ == "__main__":
    work, out = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    for i in range(int(T * FPS)):
        frame(i / FPS).convert("RGB").save(f"{work}/f{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{work}/f%04d.png",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)
