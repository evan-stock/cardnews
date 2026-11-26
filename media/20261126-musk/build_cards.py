"""20261126-musk: 머스크 게시물 캡처 카드(헤더는 머스크 계정 캡처, 본문은 실제 게시물 원문) + 사진 정리."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
D = Path(__file__).parent; R = D.parents[1]; C = D / "cand"
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
# 캡처: 머스크 계정 머리줄 + 원문
head = Image.open(C / "musk_head_src.png").convert("RGB").crop((0, 0, 870, 78))
cap = Image.new("RGB", (870, 250), (0, 0, 0)); cap.paste(head, (0, 0)); d = ImageDraw.Draw(cap)
f = F("Medium", 27)
for i, ln in enumerate(["Every child in America will receive two SpaceX shares,", "one from the company and one from me personally"]):
    d.text((18, 104 + i * 40), ln, font=f, fill=(231, 233, 234))
d.text((18, 200), "오후 12:43 · 2026년 11월 26일 · 671만 조회수", font=F("Medium", 22), fill=(113, 118, 123))
cap.save(C / "musk_cap.png")
# 사진
V = D / "video"
ImageOps.fit(Image.open(V / "img1.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .2)).save(C / "cover_bg.jpg", quality=94)
ImageOps.fit(Image.open(V / "img4.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .5)).save(C / "starship.jpg", quality=94)
ImageOps.fit(Image.open(V / "img3.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .3)).save(C / "musk2.jpg", quality=94)
spec = {"out": str(C / "c02.jpg"), "sub": "일론 머스크 · 11월 25일(현지)", "title": "\"1주는 회사가,\n1주는 '내가' 준다\"",
        "cap": str(C / "musk_cap.png"), "caption": "일론 머스크 엑스 게시물 캡처", "label": "\"미국의 모든 아이가 스페이스X 주식 2주를 받는다\"",
        "lines": ["1주는 회사(스페이스X)에서", "1주는 머스크 '개인 주식'에서"], "cap_max_h": 420}
json.dump([spec], open(C / "c02.json", "w"), ensure_ascii=False)
subprocess.run(["python3", str(R / "scripts/post_cap_card.py"), str(C / "c02.json")], check=True)
print("ok")
