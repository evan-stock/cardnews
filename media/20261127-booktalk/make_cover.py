"""20261127-booktalk 표지 배경: 실제 사진(중앙일보 11.17 자택 앞) + JTBC 보도 화면 카드(앵커 '책 내려고 만점자 없는 리트 봤다')."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFilter
D = Path(__file__).parent
W, H = 1080, 1350
bg = ImageOps.fit(Image.open(D / "video/img1.jpg").convert("RGB").crop((420, 0, 1100, 720)), (W, H), Image.LANCZOS, centering=(.62, .5)).convert("RGBA")
fr = Image.open(D / "cand/fr/raw141.jpg").convert("RGB")  # JTBC 앵커 화면(자막 포함)
cw = 560; cap = fr.resize((cw, round(fr.height * cw / fr.width)), Image.LANCZOS)
pad = 6; card = Image.new("RGBA", (cw + 2 * pad, cap.height + 2 * pad), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 18, fill=(255, 255, 255, 255))
m = Image.new("L", cap.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cap.width - 1, cap.height - 1), 13, fill=255)
card.paste(cap, (pad, pad), m)
x, y = 40, 520
sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((40, 52, card.width + 40, card.height + 52), 18, fill=(0, 0, 0, 180)); sh = sh.filter(ImageFilter.GaussianBlur(18))
bg.alpha_composite(sh, (x - 40, y - 40)); bg.alpha_composite(card, (x, y))
bg.convert("RGB").save(D / "cand/cover_bg.jpg", quality=94)
print("ok")
