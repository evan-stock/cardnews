"""X(트위터) 게시물을 X 다크 모드 화면처럼 그린다(글 원문은 X 공식 데이터 그대로). 2026.11.22
사용: python3 scripts/x_dark_card.py out.jpg avatar.jpg 이름 핸들 시각 본문파일"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R = Path(__file__).resolve().parent.parent
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
out, av, name, handle, when, txtf = sys.argv[1:7]
text = open(txtf).read().rstrip("\n")
W, P = 1400, 56
BG, BD, FG, MU, BL = (0, 0, 0), (47, 51, 54), (231, 233, 234), (113, 118, 123), (29, 155, 240)
fb = F("Medium", 44); lh = 66
fh = ImageFont.truetype(str(R / "assets/fonts/noto/NotoSansCJK-Bold.ttc"), 44, index=1)  # 한자는 Pretendard에 없어 Noto로
han = lambda c: 0x3400 <= ord(c) <= 0x9FFF or 0xF900 <= ord(c) <= 0xFAFF
tl = lambda t: sum(d0.textlength(c, font=fh if han(c) else fb) for c in t)
d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def wrap(t):
    out = []
    for para in t.split("\n"):
        if not para: out.append(""); continue
        line = ""
        for ch in para:
            if tl(line + ch) > W - 2 * P: out.append(line); line = ch
            else: line += ch
        out.append(line)
    return out
lines = wrap(text)
H = 60 + 120 + 30 + lh * len(lines) + 40 + 50 + 50
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
d.rounded_rectangle((2, 2, W - 3, H - 3), 36, outline=BD, width=3)
a = Image.open(av).convert("RGB").resize((112, 112), Image.LANCZOS)
m = Image.new("L", (112, 112), 0); ImageDraw.Draw(m).ellipse((0, 0, 111, 111), fill=255)
im.paste(a, (P, 60), m)
x = P + 112 + 26
d.text((x, 70), name, font=F("ExtraBold", 42), fill=FG)
bx = x + d.textlength(name, font=F("ExtraBold", 42)) + 12
d.ellipse((bx, 76, bx + 38, 114), fill=BL)
d.line([(bx + 10, 96), (bx + 17, 103), (bx + 29, 88)], fill=(255, 255, 255), width=5, joint="curve")
d.text((x, 124), handle, font=F("Medium", 36), fill=MU)
for i in range(3): d.ellipse((W - P - 50 + i * 18, 92, W - P - 40 + i * 18, 102), fill=MU)
y = 60 + 120 + 30
for l in lines:
    xx = P
    for c in l:
        f = fh if han(c) else fb
        d.text((xx, y), c, font=f, fill=FG); xx += d.textlength(c, font=f)
    y += lh
y += 30; d.text((P, y), when, font=F("Medium", 34), fill=MU)
im.save(out, quality=95); print(out, im.size)
