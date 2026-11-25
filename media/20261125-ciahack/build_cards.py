"""20261125-ciahack: CIA·ODNI 공개정보 분석망 해킹 + 한 달 새 FAA·NSA·FBI 사고. 기사 PC 캡처 카드."""
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

stitch("ap_cia.jpg", [(60, 510, 1480, 700), (60, 950, 1480, 1335)], "cap_cia.png")
stitch("ap_cia.jpg", [(60, 2745, 1480, 3100)], "cap_clayton.png")
stitch("faa.jpg", [(330, 400, 1780, 490), (520, 815, 1680, 1340)], "cap_faa.png")
stitch("nsa2.jpg", [(20, 110, 1400, 330), (20, 815, 1440, 990), (20, 2060, 1440, 2370)], "cap_nsa.png")
stitch("fbi.jpg", [(290, 455, 1720, 745), (290, 905, 1720, 1000), (290, 1635, 1720, 1885)], "cap_fbi.png")

W = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "AP통신 · 11월 24일(현지)", "box_bg": W,
  "title": "뚫린 곳은 CIA\n'공개정보 분석망'", "cap": str(O / "cap_cia.png"),
  "caption": "AP통신 기사 캡처", "label": "인터넷·위성사진·데이터 업체 자료를 분석하는 시스템",
  "lines": ["\"기밀은 없었고 이미 해결됐다\"(소식통)", "무엇이 새 나갔는지·누구 짓인지는 아직 모른다"], "cap_max_h": 520},
 {"out": str(O / "c03.jpg"), "sub": "시작은 · 11월 13일", "box_bg": W,
  "title": "미국 전역 비행기\n'이륙 중지'", "cap": str(O / "cap_faa.png"),
  "caption": "로이터 기사 캡처(크리스천사이언스모니터 게재)", "label": "관제 통신 장애, 9·11 이후 두 번째",
  "lines": ["7,000편 가까이 지연·취소", "같은 달 마이크로소프트·JP모건·애플 시스템도 멈춤"], "cap_max_h": 520},
 {"out": str(O / "c04.jpg"), "sub": "11월 17일 · 국가안보국", "box_bg": W,
  "title": "NSA 기밀 통신망\n'먹통'", "cap": str(O / "cap_nsa.png"),
  "caption": "알자지라 기사 캡처", "label": "NSA \"정기 점검 중 일시적 저하\"",
  "lines": ["직원들에겐 출근을 늦추라는 안내", "16일부터는 농무부 농가 지급 시스템도 침해(NBC)"], "cap_max_h": 520},
 {"out": str(O / "c05.jpg"), "sub": "11월 20~21일 · FBI", "box_bg": W,
  "title": "FBI 전국 범죄정보 DB\n'해킹' 조사", "cap": str(O / "cap_fbi.png"),
  "caption": "AP통신 기사 캡처(PBS 게재)", "label": "트럼프 \"방금 들었다. 좋지 않다\"",
  "lines": ["수배자·실종자·전과 기록을 경찰끼리 나누는 망", "FBI는 두 달 새 두 번째 해킹 피해"], "cap_max_h": 520},
 {"out": str(O / "c06.jpg"), "sub": "정부 설명", "box_bg": W,
  "title": "정부 해명은\n'AI 해커' 때문", "cap": str(O / "cap_clayton.png"),
  "caption": "AP통신 기사 캡처", "label": "행정부: 조직적 사이버 공격은 아니라는 입장",
  "lines": ["AI로 무장한 해커보다 앞서려고", "서둘러 고치고 업그레이드하다 생긴 장애가 대부분"], "cap_max_h": 420},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
