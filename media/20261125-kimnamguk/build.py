"""김남국 재산 -84.6% 2장. 사용자 제공 재산 조회 화면 + 기사 사실."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]
s = Image.open(O / "src.jpg").convert("RGB")   # 1080x1700
from PIL import ImageFilter
ph = s.crop((404, 40, 678, 436)); ph = ph.resize((ph.width * 1080 // ph.width, ph.height * 1080 // ph.width), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
ImageOps.fit(ph, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.0)).save(O / "cover.jpg", quality=95)
s.crop((48, 480, 1032, 1320)).save(O / "cap_num.png")
spec = [{"out": str(O / "c02.jpg"), "sub": "2024년 22억 8천만 원 → 2026년 3억 5천만 원", "box_bg": [255, 255, 255],
  "title": "코인 판 47억\n다른 코인에 '재투자'", "cap": str(O / "cap_num.png"), "cap_max_h": 560,
  "caption": "국회의원 재산 조회 화면(2026년 신고 기준)", "label": "경찰 \"재산 숨긴 것 아닌 시세 하락\"",
  "lines": ["2022년 코인 47억 원어치 매도 → 다른 코인에 재투자", "이후 값이 떨어져 재산 급감 · 9월 불송치(혐의 없음)"]}]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
cap = """[김남국 의원 재산, 2년 만에 22억 원대에서 3억 원대로]

더불어민주당 김남국 의원(경기 안산갑)의 재산은 2024년 신고 때 약 22억 8천만 원이었지만, 2026년에는 약 3억 5천만 원으로 신고됐습니다. 감소 폭은 약 19억 원, 84%가량입니다.

김 의원은 6·3 보궐선거 때 재산 축소 신고 의혹으로 고발됐습니다. 경찰은 2022년 가상자산 47억 원어치를 판 돈이 다른 가상자산에 재투자됐고, 이후 가격이 떨어지며 전체 재산이 크게 줄어든 것으로 보고 9월 14일 불송치(혐의 없음) 결정을 내렸습니다. 김 의원도 "코인 가격 하락에 따른 자산 가치 감소"라고 설명해 왔습니다.

출처: 연합뉴스·헤럴드경제(9.16), 더팩트(5.21), 참여연대 열려라국회(2024 신고 재산)"""
d = [{"id": "20261125-kimnamguk", "slot": "lunch", "mode": "render", "topic": "김남국 의원 재산 2024 22.8억 → 2026 3.5억(-84.6%), 코인 47억 재투자 후 하락, 9월 불송치",
      "category": "사회", "images": ["cover.jpg", "c02.jpg"],
      "slides": [{"lay": "one", "t": "코인 폭락으로\n재산 '-84%' 된 국회의원"}, {"raw": True}],
      "caption": cap, "hashtags": ["김남국", "코인", "가상자산", "재산공개", "국회의원"],
      "sources": [{"publisher": "연합뉴스·헤럴드경제", "date": "2026.09.16"}, {"publisher": "더팩트", "date": "2026.05.21"}],
      "photo_credits": ["국회의원 재산 조회 화면 캡처"]}]
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1); print("ok")
