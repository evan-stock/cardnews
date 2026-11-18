"""20261118-leetlec: 리트 만점자 특강 후기 — '엔트로피' 나오면 '트로피'를 떠올린다, 필기 안 함(고려대 커뮤니티 고파스 익명 후기, X @itwillbe_sage 경유)
+ 리트 국어 강사(노형석)가 설명회에서 '계'를 '강아지'로 연상한다는 설명을 듣고 끝까지 안 듣고 나왔다는 내용(나무위키 인용). 실명 안 씀, 인스타 사진은 안 씀. 표지: 유튜브 DreamSchool 인터뷰 화면."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
specs = [
 {"out": str(O / "c02.jpg"), "sub": "고려대 커뮤니티 '고파스' 특강 후기(익명)", "title": "'엔트로피' 나오면\n'트로피'를 떠올린다?", "cap": str(O / "cap_gopas.png"), "cap_max_h": 640, "box_bg": [255, 255, 255],
  "caption": "고파스 게시물 캡처(X 게시물 경유)", "label": "후기에 적힌 공부법", "lines": ["단어를 '그림'으로 바꿔 떠올리기", "필기는 '전혀' 안 하고 기출만 반복"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import P, BOX, LN, MU, FG, F, rich, base, logo, head, wrap
from PIL import ImageDraw
im = base(); d = ImageDraw.Draw(im); y = head(d, "리트 국어 강사도 직접 들었다", "'계'를 '강아지'로\n연상한다는 설명", y=120)
rows = [("누가", "리트 국어 '노형석' 강사"), ("어디서", "의혹 전 메가로스쿨 설명회에 '호기심에' 참석"), ("들은 것", "텍스트를 '이미지'로 바꿔야 한다며, '계'를 '강아지'로 연상"),
        ("그래서", "평소 문제 푸는 방식과 달라 '끝까지 안 듣고' 나왔다")]
for lab, txt in rows:
    d.rounded_rectangle((P, y, W - P, y + 150), 22, fill=BOX, outline=LN, width=2)
    d.text((P + 30, y + 24), lab, font=F("SemiBold", 28), fill=MU)
    for k, ln in enumerate(wrap(d, txt, F("Black", 36), W - 2 * P - 60)[:2]): rich(d, P + 30, y + 64 + k * 44, ln, F("Black", 36))
    y += 172
d.text((P, y + 20), "나무위키 인용(해당 강사 발언 출처 표기)", font=F("Medium", 26), fill=MU)
logo(im); im.save(O / "c03.jpg", quality=93)
from PIL import ImageFilter
# 표지(사용자: 본인이 나오되 다른 사진): DreamSchool 인터뷰 화면(책장 앞, 10초) — 아래 박힌 자막은 잘라냄
ImageOps.fit(Image.open(O / "ds_10.png").convert("RGB").crop((640, 0, 1260, 625)), (W, H), Image.LANCZOS, centering=(.45, .3)).filter(ImageFilter.UnsharpMask(2, 70, 2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
