"""20261126-musk 표지: manual 렌더(01.jpg) 위에 실제 트윗 캡처 카드를 얹는다. manual 다시 돌리면 이것도 다시 실행."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFilter
D = Path(__file__).parent
im = Image.open(D / "01.jpg").convert("RGBA")
cap = Image.open(D / "cand/musk_cap_real.png").convert("RGB")
w = 720; cap = cap.resize((w, round(cap.height * w / cap.width)), Image.LANCZOS); h = cap.height
pad = 16; card = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
d.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 26, fill=(0, 0, 0, 255), outline=(80, 80, 88, 255), width=3)
m = Image.new("L", cap.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=255)
card.paste(cap, (pad, pad), m)
sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((40, 50, card.width + 40, card.height + 50), 26, fill=(0, 0, 0, 170)); sh = sh.filter(ImageFilter.GaussianBlur(18))
x = (im.width - card.width) // 2; y = 712
im.alpha_composite(sh, (x - 40, y - 40)); im.alpha_composite(card, (x, y))
im.convert("RGB").save(D / "01.jpg", quality=93)
print("ok", y + card.height)
