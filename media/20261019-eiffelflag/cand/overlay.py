"""릴스 제목 오버레이. 사용법: overlay2.py out.png "줄1" "줄2" "줄3"
'작은따옴표' 안은 노란 강조. 따옴표가 하나도 없으면 마지막 줄 전체를 노랑으로."""
import sys
from PIL import Image, ImageDraw, ImageFont

F = "/home/claude/cardnews/assets/fonts/"
out, lines = sys.argv[1], sys.argv[2:]
UP = 140 * max(0, len(lines) - 3)  # 4줄 이상이면 전체를 위로
W, H = 1080, 1920
YEL, WHITE, SH = (255, 216, 77, 255), (255, 255, 255, 255), (60, 60, 60, 255)

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
grad = Image.new("L", (1, H))
for y in range(H):
    grad.putpixel((0, y), 0 if y < 950 - UP else min(215, int(215 * (y - 950 + UP) / 430)))
img.putalpha(grad.resize((W, H)))
img = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), grad.resize((W, H)))

d = ImageDraw.Draw(img)
small = ImageFont.truetype(F + "Pretendard-ExtraBold.otf", 38)
big = ImageFont.truetype(F + "Pretendard-Black.otf", 118)
d.ellipse((70, 1160 - UP, 88, 1178 - UP), fill=YEL)
d.text((102, 1150 - UP), "TODAY.WORTHY", font=small, fill=WHITE)

any_quote = any("'" in ln for ln in lines)
y = 1235 - UP
for i, ln in enumerate(lines):
    if any_quote:
        segs = [(p, YEL if k % 2 else WHITE) for k, p in enumerate(ln.split("'")) if p]
    else:
        segs = [(ln, YEL if i == len(lines) - 1 else WHITE)]
    x = 70
    for txt, col in segs:
        d.text((x + 6, y + 6), txt, font=big, fill=SH)
        d.text((x, y), txt, font=big, fill=col)
        x += d.textlength(txt, font=big)
    assert x < W - 40, f"line too wide: {ln} ({x:.0f}px)"
    y += 140
img.save(out)
print("ok", out)
