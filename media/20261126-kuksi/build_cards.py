"""20261126-kuksi: 의사·간호사 국시 일부 과목 만점자 급증(이만희 의원·국시원 자료, 11.25~26 보도) 기사 PC 캡처 카드."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"

def stitch(src, boxes, out, pad=(40, 30), gap=24):
    im = Image.open(O / src).convert("RGB")
    parts = [im.crop(b) for b in boxes]
    w = max(p.width for p in parts) + pad[0] * 2
    h = sum(p.height for p in parts) + gap * (len(parts) - 1) + pad[1] * 2
    c = Image.new("RGB", (w, h), "white"); y = pad[1]
    for p in parts:
        c.paste(p, (pad[0], y)); y += p.height + gap
    c.save(O / out)

stitch("fn.jpg", [(160, 260, 1400, 445), (180, 1165, 1345, 1325)], "cap_doc.png")
stitch("wt2.jpg", [(0, 555, 1960, 650), (0, 2050, 1490, 2245), (0, 2318, 1490, 2515)], "cap_nurse.png")
stitch("wt2.jpg", [(0, 2584, 1490, 2853), (0, 3116, 1490, 3385)], "cap_more.png")
stitch("wt2.jpg", [(0, 4335, 1490, 4445), (0, 4510, 1490, 4780)], "cap_twist.png")
stitch("wt2.jpg", [(0, 4868, 1490, 5265)], "cap_mohw.png")

W = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "의사 국가시험 · 국시원 자료", "box_bg": W,
  "title": "법규 과목 만점자\n20명 → '137명'", "cap": str(O / "cap_doc.png"),
  "caption": "파이낸셜뉴스 기사 캡처", "label": "2022년보다 약 7배",
  "lines": ["올해는 의정 갈등 여파로 시험을 두 번 봤다", "응시자는 오히려 2022년보다 적었다"], "cap_max_h": 520},
 {"out": str(O / "c03.jpg"), "sub": "간호사 국가시험 · 정신간호학", "box_bg": W,
  "title": "만점자 47명 →\n'1263명'", "cap": str(O / "cap_nurse.png"),
  "caption": "위키트리 기사 캡처", "label": "1년 만에 약 26.9배",
  "lines": ["응시자는 4% 늘었는데", "만점자 비율 0.19% → 4.82%"], "cap_max_h": 520},
 {"out": str(O / "c04.jpg"), "sub": "다른 과목도", "box_bg": W,
  "title": "모성간호학 '30배'\n치과의사는 8명 중 1명", "cap": str(O / "cap_more.png"),
  "caption": "위키트리 기사 캡처", "label": "모성간호학 6명 → 184명",
  "lines": ["치과의사 법규 과목 6명 → 98명", "만점자 비율 0.79% → 12.39%"], "cap_max_h": 520},
 {"out": str(O / "c05.jpg"), "sub": "그런데", "box_bg": W,
  "title": "3년 전엔 만점자\n'2335명'이었다", "cap": str(O / "cap_twist.png"),
  "caption": "위키트리 기사 캡처", "label": "부정행위 적발은 '0건'",
  "lines": ["2023년 정신간호학 만점자·평균점수가 올해보다 높았다", "AI 부정행위와 관련 있는지는 확인 안 됨"], "cap_max_h": 520},
 {"out": str(O / "c06.jpg"), "sub": "보건복지부 입장", "box_bg": W,
  "title": "복지부 \"만점자 수만 갖고\n이상 있다고 보긴 어렵다\"", "cap": str(O / "cap_mohw.png"),
  "caption": "위키트리 기사 캡처", "label": "기본간호학 만점자는 오히려 절반으로",
  "lines": ["이만희 의원 \"보건의료인 국시도", "부정행위 전수조사 대상에 포함해야\""], "cap_max_h": 520},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
