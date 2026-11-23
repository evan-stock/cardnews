"""20261123-byeonri: 변리사 2차 평균 60점 이상 3명→42명(산인공→이헌승 의원 자료, 11.23). 본문 = 데일리안·위키트리 기사 캡처 카드."""
import json, subprocess, sys, random
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
bg = Image.new("RGB", (1080, 1350), (18, 18, 22)); random.seed(3)
for i, n in enumerate(["cap_main", "cap_years", "cap_mins", "cap_score", "cap_main", "cap_years", "cap_mins"]):
    im = Image.open(O / f"{n}.png").convert("RGBA"); s = 900 / im.width
    im = im.resize((900, int(im.height * s))).rotate(random.uniform(-7, 7), expand=True, fillcolor=(0, 0, 0, 0))
    bg.paste(im, (random.randint(-250, 400), -100 + i * 200), im)
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(2))).enhance(0.5)
bg.save(O / "cover_bg.jpg", quality=94)
W = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "변리사 2차 · 산업인력공단 국회 제출 자료", "box_bg": W,
  "title": "평균 60점 이상\n1년 새 3명 → '42명'", "cap": str(O / "cap_main.png"),
  "caption": "데일리안 기사 캡처", "label": "응시자는 1,130명으로 작년(1,138명)과 비슷",
  "lines": ["최근 5년 최다였던 2024년(16명)의 2.6배", "비율로는 0.3% → 3.7%"], "cap_max_h": 520},
 {"out": str(O / "c03.jpg"), "sub": "변리사 2차 · 최근 7년", "box_bg": W,
  "title": "많아야 16명이던 시험\n올해 '42명'", "cap": str(O / "cap_years.png"),
  "caption": "위키트리 기사 캡처", "label": "연도별 평균 60점 이상 인원",
  "lines": ["2020년  3명", "2021년  11명", "2022년  4명", "2023년  5명", "2024년  16명", "2025년  3명", "2026년  '42명'"], "cap_max_h": 330},
 {"out": str(O / "c04.jpg"), "sub": "합격자 점수도 올랐다", "box_bg": W,
  "title": "합격선 53 → 56.44점\n'생동차' 5명 → 11명", "cap": str(O / "cap_score.png"),
  "caption": "데일리안 기사 캡처", "label": "합격자 평균 55.35 → 58.65점",
  "lines": ["합격선은 최근 7년 중 가장 높았습니다", "1·2차를 한 해에 붙은 합격자, 2년 연속 11명"], "cap_max_h": 380},
 {"out": str(O / "c05.jpg"), "sub": "반론도 있다", "box_bg": W,
  "title": "민사소송법만\n평균 '14.65점' 올랐다", "cap": str(O / "cap_mins.png"),
  "caption": "위키트리 기사 캡처", "label": "쉬운 한 과목이 전체 평균을 끌어올렸다는 분석",
  "lines": ["최고점은 64.44점으로 2024년과 같았습니다", "일부만 튄 게 아니라 분포 전체가 올라간 모양"], "cap_max_h": 520},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
