"""20261123-alicechip 캡처 카드(규칙: post_cap_card.py, PC 기사 캡처, 제목·문단만, 흰 여백)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]


def clip(src, boxes, out, w=None):
    ims = [Image.open(O / src).convert("RGB").crop(b) for b in boxes]
    W_ = max(i.width for i in ims); gap = 30
    H_ = sum(i.height for i in ims) + gap * (len(ims) - 1)
    c = Image.new("RGB", (W_ + 80, H_ + 60), (255, 255, 255)); y = 30
    for i in ims: c.paste(i, (40, y)); y += i.height + gap
    c.save(O / out)


clip("ed.jpg", [(0, 500, 1520, 730), (0, 760, 960, 990), (250, 1050, 1520, 1300)], "k02.png")
clip("ed.jpg", [(250, 2480, 1520, 3150)], "k03.png")
clip("ed.jpg", [(250, 4520, 1520, 4790)], "k04.png")
clip("ed.jpg", [(260, 5960, 1500, 6330)], "k05.png")
clip("ed.jpg", [(260, 6790, 1500, 7330)], "k06.png")
clip("ed.jpg", [(260, 7380, 1500, 7920)], "k07.png")
clip("hk.jpg", [(440, 3820, 1760, 4250)], "k08.png")

E = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "이데일리 · 11월 22일", "title": "\"한국인 감금\" 조직과도\n칩 밀수 '연결고리'", "cap": str(O / "k02.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "파이낸셜타임스 11월 21일(현지) 보도", "lines": ["소식통 '10여 명'·기업 공시 수백 건 분석"]},
 {"out": str(O / "c03.jpg"), "sub": "이데일리 · 11월 22일", "title": "프린스그룹 2인자가\n칩 운반 '일부' 맡았다", "cap": str(O / "k03.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "후샤오웨이, 올여름 일본에서 체포", "lines": ["게임 거물·페이퍼컴퍼니 '수백 개'가 맞물려"]},
 {"out": str(O / "c04.jpg"), "sub": "이데일리 · 11월 22일", "title": "그가 돈 번 곳은\n한국 게임 '미르의 전설'", "cap": str(O / "k04.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "위메이드 게임 '사설 서버'로 큰돈", "lines": ["앨리스 황 남편이 투자한 게임사가 '연결고리'"]},
 {"out": str(O / "c05.jpg"), "sub": "이데일리 · 11월 22일", "title": "칩 빼돌린 '세 축'\n끝은 중국 암시장", "cap": str(O / "k05.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "칩 받을 업체 · '깨끗한' 고객 · 지하 조직", "lines": ["\"칩 밀수는 '마약·무기'와 다르지 않다\""]},
 {"out": str(O / "c06.jpg"), "sub": "이데일리 · 11월 22일", "title": "중국 업계에선\n'젠슨의 개인비서'", "cap": str(O / "k06.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "메가스피드의 '믿을 만한' 대외 임원", "lines": ["엔비디아 심사 통과, 동남아 '최대' 고객사로"]},
 {"out": str(O / "c07.jpg"), "sub": "이데일리 · 11월 22일", "title": "1년 신고액 '6조 원'\n급습하니 '빈 서버랙'", "cap": str(O / "k07.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "이데일리 기사 캡처", "label": "칩은 동남아 거쳐 중국 암시장으로", "lines": ["엔비디아 \"작년 메가스피드 '판매 차단'\""]},
 {"out": str(O / "c08.jpg"), "sub": "한국경제 · 11월 22일", "title": "다른 말도 있다\n\"실제 운영자는 '따로'\"", "cap": str(O / "k08.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "한국경제 기사 캡처", "label": "WSJ \"앨리스 황은 대외 '얼굴' 역할\"", "lines": ["프린스그룹도 \"후샤오웨이 일한 적 '없다'\""]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
