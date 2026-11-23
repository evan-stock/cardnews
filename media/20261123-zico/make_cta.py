"""20261123-zico 마지막 장: 누리꾼 반응 댓글 + 팔로우(우리 CTA 양식: 표지 흐림 배경·로고·외곽선 버튼)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
COMMENTS = ["출근하는 사람 비웃더니 ㅋㅋ", "이것도 방송용 아님?", "결국 별풍선 달라는 거잖아", "세금은 꼭 다 내고 울어라"]

bg = ImageOps.fit(Image.open(O / "cover_bg.jpg").convert("RGB"), (W, H), Image.LANCZOS)
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(26))).enhance(.35).convert("RGBA")
d = ImageDraw.Draw(bg)
d.text((W / 2, 200), "누리꾼 반응", font=F("SemiBold", 40), fill=YE, anchor="ms")
y = 270; bh = 108; gap = 34
for c in COMMENTS:
    box = Image.new("RGBA", (W - 160, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((0, 0, box.width - 1, bh - 1), 22, fill=(255, 255, 255, 245))
    bd.text((44, bh / 2), c, font=F("Black", 46), fill=(18, 18, 22), anchor="lm")
    bg.alpha_composite(box, (80, y)); y += bh + gap
d = ImageDraw.Draw(bg)
y += 40
d.text((W / 2, y + 40), "여러분 생각은?", font=F("Black", 60), fill=(255, 255, 255), anchor="ms")
d.text((W / 2, y + 100), "팔로우하면 매일 화제 소식 먼저", font=F("Medium", 34), fill=(220, 220, 226), anchor="ms")
bt = "＋ 팔로우  @today.worthy"; f = F("SemiBold", 32); tw = d.textlength(bt, font=f)
by = y + 150; d.rounded_rectangle(((W - tw) / 2 - 36, by, (W + tw) / 2 + 36, by + 66), 33, outline=(255, 255, 255), width=3)
d.text((W / 2, by + 33), bt, font=f, fill=(255, 255, 255), anchor="mm")
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 54; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); bg.alpha_composite(lg, ((W - lw) // 2, H - 70 - lh))
bg.convert("RGB").save(O / "cta.jpg", quality=93)
print("ok")
