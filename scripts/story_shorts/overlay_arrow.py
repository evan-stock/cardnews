#!/usr/bin/env python3
"""영상 칸(1080x780)용 투명 PNG: 빨간 화살표 + 라벨. — 오늘의쓸모 2026.11.12
  python3 scripts/story_shorts/overlay_arrow.py out.png tipx tipy tailx taily "라벨" labelx labely
"""
import sys, math
from PIL import Image, ImageDraw, ImageFont
out, tx, ty, sx, sy, lab, lx, ly = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6], *map(float, sys.argv[7:9])
im = Image.new("RGBA", (1080, 780), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
RED = (235, 30, 40, 255)
ang = math.atan2(ty - sy, tx - sx); hl = 46
bx, by = tx - hl * math.cos(ang), ty - hl * math.sin(ang)
d.line((sx, sy, bx, by), fill=(255, 255, 255, 255), width=22)
d.line((sx, sy, bx, by), fill=RED, width=14)
p = [(tx, ty), (bx + 30 * math.cos(ang + math.pi / 2), by + 30 * math.sin(ang + math.pi / 2)),
     (bx - 30 * math.cos(ang + math.pi / 2), by - 30 * math.sin(ang + math.pi / 2))]
d.polygon(p, fill=RED, outline=(255, 255, 255, 255))
f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", 52)
w = d.textlength(lab, font=f)
d.rounded_rectangle((lx - 18, ly - 8, lx + w + 18, ly + 72), 14, fill=RED)
d.text((lx, ly), lab, font=f, fill=(255, 255, 255, 255))
im.save(out)
