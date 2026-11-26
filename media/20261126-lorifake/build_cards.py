"""20261126-lorifake: '로리 황 입장문' 가짜 팩트체크. 퍼진 글 캡처(특정인 이름 줄 가림 + '가짜' 도장) 카드 + 사진 정리."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
D = Path(__file__).parent; R = D.parents[1]; C = D / "cand"; V = D / "video"
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
im = Image.open(C / "fake_statement.jpg").convert("RGB")
box = (180, 306, 690, 358)  # '콜레트 크레스와 관련된 혐의' 부분 흐리게
im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(9)), box[:2])
# 빨간 '가짜' 도장
st = Image.new("RGBA", (420, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
d.rounded_rectangle((4, 4, 415, 145), 18, outline=(226, 40, 40, 255), width=10)
d.text((210, 76), "가짜 입장문", font=F("Black", 74), fill=(226, 40, 40, 255), anchor="mm")
st = st.rotate(12, expand=True, resample=Image.BICUBIC)
im = im.convert("RGBA"); im.alpha_composite(st, (im.width - st.width - 30, 380)); im.convert("RGB").save(C / "fake_cap.png")
ImageOps.fit(Image.open(V / "img1.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .3)).save(C / "cover_bg.jpg", quality=94)
ImageOps.fit(Image.open(V / "img3.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .3)).save(C / "jh2.jpg", quality=94)
ImageOps.fit(Image.open(V / "img2.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .3)).save(C / "jh3.jpg", quality=94)
spec = [{"out": str(C / "c02.jpg"), "sub": "온라인에 퍼진 '로리 황 입장문'", "title": "\"남편을 '용서'합니다\"\n…진짜일까?",
         "cap": str(C / "fake_cap.png"), "caption": "엑스·커뮤니티에 퍼진 글 캡처(특정인 언급 부분 가림)",
         "label": "해외 팩트체크 \"지어낸 글\"", "lines": ["로리 황은 지금까지 공식 입장을 낸 적 없음"], "cap_max_h": 640}]
json.dump(spec, open(C / "c02.json", "w"), ensure_ascii=False)
subprocess.run(["python3", str(R / "scripts/post_cap_card.py"), str(C / "c02.json")], check=True)
