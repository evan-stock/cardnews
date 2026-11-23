"""20261123-gamkang: 감평냥이 '1타 강사 증언'(에펨코리아 11.23, 본인 주장) vs 감평냥이 2차 해명 — 양쪽 다. 에펨·개드립 자동접속 차단으로 원글 화면은 게시글 캡처 이미지(작성자·조회수 포함)에서 잘라 씀."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]


def clip(src, boxes, out, blur=()):
    im0 = Image.open(O / src).convert("RGB")
    for b in blur: im0.paste(im0.crop(b).filter(ImageFilter.GaussianBlur(14)), b[:2])
    ims = [im0.crop(b) for b in boxes]
    W_ = max(i.width for i in ims); gap = 30
    c = Image.new("RGB", (W_ + 80, sum(i.height for i in ims) + gap * (len(ims) - 1) + 60), (255, 255, 255)); y = 30
    for i in ims: c.paste(i, (40, y)); y += i.height + gap
    c.save(O / out)


clip("ig.png", [(40, 680, 1760, 1180), (100, 1280, 1700, 1800)], "k02.png")
clip("g5.jpg", [(40, 1030, 920, 1440)], "k03.png")
clip("g6.jpg", [(40, 1670, 920, 1850)], "k03b.png")
clip("g2.jpg", [(60, 1250, 880, 1392)], "k04a.png", blur=[(240, 1590, 360, 1660)])
E = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "에펨코리아 · 11월 23일", "title": "\"그분 시험지,\n별표 위치가 '이상하다'\"", "cap": str(O / "k02.png"), "box_bg": E, "cap_max_h": 680,
  "caption": "에펨코리아 게시글 캡처(조회 11만)", "label": "\"1타 강사의 증언\"이라며 올라온 글", "lines": ["\"내 기본강의 풀이 방식이 '하나도' 안 보인다\""]},
 {"out": str(O / "c03.jpg"), "sub": "감평냥이 2차 해명문 · 11월 19일", "title": "감평냥이 쪽은\n\"배경지식이 '이미' 있었다\"", "cap": str(O / "k03.png"), "box_bg": E, "cap_max_h": 680,
  "caption": "본인 2차 해명문 캡처", "label": "서울대 학사·도시계획학 석사", "lines": ["\"6개월로 설명한 건 '부적절'했다\" 사과"]},
 {"out": str(O / "c04.jpg"), "sub": "감평냥이 2차 해명문 · 11월 19일", "title": "증거로 내놓은 건\n수강 확인서·'연습 답안'", "cap": str(O / "g4.jpg"), "box_bg": E, "cap_max_h": 680, "cap_crop": [90, 250, 840, 1000],
  "caption": "본인이 공개한 연습 답안", "label": "부정행위는 \"없었다\" 부인", "lines": ["성적은 189명 중 '150등'(한국경제)"]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
c = Image.open(O / "g4.jpg").convert("RGB").crop((90, 250, 840, 1000))
ImageOps.fit(c, (1080, 1350), Image.LANCZOS).save(O / "cover_bg.jpg", quality=95)
print("ok")
