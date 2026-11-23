"""20261123-bujin: 이부진 아들 성본 변경(임→이) 캡처 카드. 아들은 일반인 — 얼굴 가림, 아버지 관련은 확인된 사실만."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]


def clip(src, boxes, out):
    ims = [Image.open(O / src).convert("RGB").crop(b) for b in boxes]
    W_ = max(i.width for i in ims); gap = 30
    c = Image.new("RGB", (W_ + 80, sum(i.height for i in ims) + gap * (len(ims) - 1) + 60), (255, 255, 255)); y = 30
    for i in ims: c.paste(i, (40, y)); y += i.height + gap
    c.save(O / out)


clip("fn.jpg", [(180, 262, 1340, 440), (180, 860, 1340, 985)], "k02.png")
clip("fn.jpg", [(180, 1045, 1340, 1215)], "k03.png")
clip("fn.jpg", [(180, 1278, 1340, 1445)], "k04.png")
clip("fn.jpg", [(180, 1510, 1340, 1678)], "k05.png")

E = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "파이낸셜뉴스 · 11월 23일", "title": "성인이 되자\n아버지 성 '임'→'이'", "cap": str(O / "k02.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "파이낸셜뉴스 기사 캡처", "label": "이부진 호텔신라 사장 아들", "lines": ["어머니 성 '경주 이씨'로 바꿨습니다"]},
 {"out": str(O / "c03.jpg"), "sub": "파이낸셜뉴스 · 11월 23일", "title": "8월 성인, 직접 신청\n10월 말 법원 '허가'", "cap": str(O / "k03.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "파이낸셜뉴스 기사 캡처", "label": "서울가정법원이 신청 받아들여", "lines": ["작년 성본 변경 허가율은 '88.9%'"]},
 {"out": str(O / "c04.jpg"), "sub": "파이낸셜뉴스 · 11월 23일", "title": "성은 바뀌어도\n부자 관계는 '그대로'", "cap": str(O / "k04.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "파이낸셜뉴스 기사 캡처", "label": "민법 781조 6항 '자녀의 복리'", "lines": ["법률상 친자관계에는 '변동 없음'"]},
 {"out": str(O / "c05.jpg"), "sub": "파이낸셜뉴스 · 11월 23일", "title": "1999년 결혼\n2020년 '이혼 확정'", "cap": str(O / "k05.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "파이낸셜뉴스 기사 캡처", "label": "친권·양육권은 이 사장에게", "lines": ["올해 2월 서울대 경제학부에 '입학'"]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
c = Image.open(O / "press01.jpg").convert("RGB")
ImageOps.fit(c, (1080, 1350), Image.LANCZOS, centering=(.35, .35)).save(O / "cover_bg.jpg", quality=95)
print("ok", c.size)
