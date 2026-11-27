"""20261127-booktalk 표지 배경: 인물 사진(밝은 배경 지우고 어두운 바탕) + 오른쪽 '브레인 악셀' 책 카드(JTBC 화면)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
D = Path(__file__).parent
p = Image.open(D / "cand/lee_photo.jpg").convert("RGB"); a = np.asarray(p).astype(float)
bgc = np.median(np.concatenate([a[:40, :].reshape(-1, 3), a[:, :30].reshape(-1, 3), a[:, -30:].reshape(-1, 3)]), 0)
m = (np.sqrt(((a - bgc) ** 2).sum(2)) > 38).astype(np.uint8) * 255
mi = Image.fromarray(m).filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
W, H = 1080, 1350; k = 1.45; pw, ph = int(p.width * k), int(p.height * k)
ps = p.resize((pw, ph), Image.LANCZOS); ms = mi.resize((pw, ph), Image.LANCZOS)
cv = Image.new("RGB", (W, H), (14, 14, 16))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((-200, -150, 900, 800), fill=90); glow = glow.filter(ImageFilter.GaussianBlur(160))
cv = Image.composite(Image.new("RGB", (W, H), (58, 60, 66)), cv, glow)
cv.paste(ps, (-260, -40), ms)
g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
for y in range(780, 1050): d.line((0, y, W, y), fill=int(255 * (y - 780) / 270))
for y in range(1050, H): d.line((0, y, W, y), fill=255)
cv = Image.composite(Image.new("RGB", (W, H), (12, 12, 14)), cv, g).convert("RGBA")
fr = Image.open(D / "cand/fr/raw132.jpg").convert("RGB")
bk = fr.crop((40, 50, 520, 300)); cw = 430
bk = ImageEnhance.Sharpness(bk.resize((cw, round(bk.height * cw / bk.width)), Image.LANCZOS)).enhance(1.4)
pad = 8; card = Image.new("RGBA", (cw + 2 * pad, bk.height + 2 * pad), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 22, fill=(255, 216, 77, 255))
mk = Image.new("L", bk.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, bk.width - 1, bk.height - 1), 16, fill=255)
card.paste(bk, (pad, pad), mk); card = card.rotate(4, expand=True, resample=Image.BICUBIC)
x, y = W - card.width - 30, 520
sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0)); sh.paste((0, 0, 0, 170), (40, 52), card.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(18))
cv.alpha_composite(sh, (x - 40, y - 40)); cv.alpha_composite(card, (x, y))
cv.convert("RGB").save(D / "cand/cover_bg.jpg", quality=94)
print("ok")
