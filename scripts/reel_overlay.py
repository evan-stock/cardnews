"""릴스 오버레이(원래 양식 + 새 로고·글꼴).
원래 양식: 영상 9:16 꽉, 왼쪽 정렬, 위에서부터 로고 → (빨간 태그) → 굵은 제목 줄들(마지막 줄 노랑).
바뀐 점: '● TODAY.WORTHY' 글자 대신 today.worthy 로고, 제목은 Pretendard Black.
사용: python scripts/reel_overlay.py out.png "줄1\n줄2\n줄3" [태그] [커버용_배경이미지 out_cover.jpg]
"""
import sys
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
FB = "assets/fonts/Pretendard-Black.otf"
LOGO = "brand/logo_typo_A.png"


def overlay(lines, tag=None):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    g0, g1 = 950, 1380
    for y in range(g0, H):
        t = min(1, (y - g0) / (g1 - g0))
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(215 * t)))
    f = ImageFont.truetype(FB, 118)
    y = 1235
    if tag:
        y += 0
    lg = Image.open(LOGO).convert("RGBA")
    lh = 44
    lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    top = y - 118 - (80 if tag else 0) - 30 - lh
    ov.alpha_composite(lg, (70, top))
    if tag:
        tf = ImageFont.truetype("assets/fonts/Pretendard-ExtraBold.otf", 34)
        tw = d.textlength("● " + tag, font=tf) + 32
        ty = y - 118 - 70
        d.rounded_rectangle((70, ty, 70 + tw, ty + 52), radius=10, fill=(228, 30, 40))
        d.text((70 + 16, ty + 26), "● " + tag, font=tf, fill=(255, 255, 255), anchor="lm")
    for k, l in enumerate(lines):
        d.text((70, y + k * 140), l, font=f, fill=(255, 216, 77) if k == len(lines) - 1 else (255, 255, 255), anchor="ls")
    return ov


if __name__ == "__main__":
    lines = sys.argv[2].replace("\\n", "\n").split("\n")
    tag = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
    ov = overlay(lines, tag)
    ov.save(sys.argv[1])
    if len(sys.argv) > 5:
        bg = Image.open(sys.argv[4]).convert("RGB")
        r = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
        bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).convert("RGBA")
        Image.alpha_composite(bg, ov).convert("RGB").save(sys.argv[5], quality=93)
