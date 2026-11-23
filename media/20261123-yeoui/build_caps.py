import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]


def clip(src, boxes, out):
    ims = [Image.open(O / src).convert("RGB").crop(b) for b in boxes]
    W_ = max(i.width for i in ims); gap = 30
    c = Image.new("RGB", (W_ + 80, sum(i.height for i in ims) + gap * (len(ims) - 1) + 60), (255, 255, 255)); y = 30
    for i in ims: c.paste(i, (40, y)); y += i.height + gap
    c.save(O / out)


clip("np.jpg", [(180, 640, 1720, 740), (180, 1990, 1720, 2100)], "k03.png")
clip("np.jpg", [(180, 2805, 1720, 3040)], "k04.png")
E = [255, 255, 255]
spec = [
 {"out": str(O / "c03.jpg"), "sub": "뉴스핌 · 11월 23일", "title": "그리고 오늘\n코스피 '매도 사이드카'", "cap": str(O / "k03.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "뉴스핌 기사 캡처", "label": "코스피 장중 5.61% 급락, 4600선 붕괴", "lines": ["미국 반도체주 '폭락' 여파"]},
 {"out": str(O / "c04.jpg"), "sub": "뉴스핌 · 11월 23일", "title": "삼전 17만·닉스 105만\n팻말 '1차' 숫자 깨졌다", "cap": str(O / "k04.png"), "box_bg": E, "cap_max_h": 660,
  "caption": "뉴스핌 기사 캡처(오전 11시 45분 기준)", "label": "삼성전자 -5.90% · SK하이닉스 -5.66%", "lines": ["남은 건 '2차' 삼전 14만·닉스 75만"]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
