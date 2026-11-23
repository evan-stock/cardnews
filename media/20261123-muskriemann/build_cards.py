"""20261123-muskriemann: 리만 가설 Lean 인증(11.21) → 머스크 "특이점에 오신 걸 환영"(11.22) → 르쿤 반박(11.23).
표지 = 사용자 제공 이미지(AI 생성 추정), 본문 = 실제 게시물 캡처 카드(post_cap_card)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
src = Image.open(O / "cover_src.jpg").convert("RGB")
s = 1350 / src.height; big = src.resize((round(src.width * s), 1350), Image.LANCZOS)
big.crop((150, 0, 1230, 1350)).save(O / "cover_bg.jpg", quality=94)
spec = [
 {"out": str(O / "c02.jpg"), "sub": "Lean·Mathlib 공동 성명 · 11월 21일(현지)",
  "title": "1,700만 줄 AI 증명\n하루 만에 '맞다' 도장", "cap": str(O / "lean_cap.png"),
  "caption": "Lean 공식 계정 게시물 캡처", "label": "수학 증명을 컴퓨터로 한 줄씩 검사하는 곳",
  "lines": ["앤트로픽 수학자 알푀게가 '클로드'와 만든 증명", "\"증명이 올바르다고 인증한다\""], "cap_max_h": 520},
 {"out": str(O / "c03.jpg"), "sub": "일론 머스크 · 11월 22일",
  "title": "\"명백한 초지능이\n'도착했다'\"", "cap": str(O / "musk_cap.png"),
  "caption": "일론 머스크 게시물 캡처",
  "label": "Unequivocal super intelligence has arrived.",
  "lines": ["리만 가설 얘기에 단 답글 한 줄", "\"'특이점'에 오신 것을 환영합니다\""], "cap_max_h": 420},
 {"out": str(O / "c04.jpg"), "sub": "얀 르쿤(튜링상 수상자) · 11월 23일",
  "title": "9시간 뒤 날아온 답글\n\"꽤 '이상한' 초지능이네요\"", "cap": str(O / "lecun_cap.png"),
  "caption": "얀 르쿤 게시물 캡처", "label": "\"(당신은) 수십억 시간의 데이터가 있는데\"",
  "lines": ["17살도 20시간이면 배우는 운전을", "AI는 아직 '완전 자율주행'으로 못 한다는 것"], "cap_max_h": 500},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
