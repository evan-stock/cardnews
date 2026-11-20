"""20261120-leetthen: 리트 만점 발표 당시(2026년 7~8월) 디시 반응 모음. '그때 vs 지금'.
캡처는 m.dcinside.com 실제 화면(댓글만 남기고 나머지 숨김) 스크린샷. 사망 관련 묘사 없음, 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
# 표지: 백지연 채널 인터뷰 장면(이전 게시물 표지에 안 쓴 사진). 채널 로고 없는 영역으로 자른 cover_b.jpg 사용
Image.open(O / "cover_b.jpg").convert("RGB").crop((40, 0, 1000, 1200)).resize((1080, 1350), Image.LANCZOS).save(O / "cover_bg.jpg", quality=94)  # 아래 자막 잘라냄
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "디시 싱글벙글 지구촌 갤러리 (7월 22일)", "title": "\"20년 만에 LEET '만점자 탄생'\"",
  "cap": str(O / "sb_post.jpg"), "cap_max_h": 760, **W_, "caption": "조회 1.7만, 댓글 112개가 달린 당시 글",
  "label": "리트 성적 발표 직후", "lines": ["서울대 치대 26학번, '공부법 테스트'로 응시"]},
 {"out": str(O / "c03.jpg"), "sub": "같은 글 댓글 (7월 22일)", "title": "\"신이 '테스트로 만들어봤나봐'\"",
  "cap": str(O / "sb_cmt_wow.jpg"), "cap_max_h": 700, **W_, "caption": "",
  "label": "그때는 감탄이 먼저였다", "lines": ["반년 뒤 '1타 강사' 데뷔를 점친 댓글도"]},
 {"out": str(O / "c04.jpg"), "sub": "디시 오리지널 티켓 갤러리 (8월 31일)", "title": "\"얼굴도 '잘생겼네' 이러면 안되지\"",
  "cap": str(O / "ot_face.jpg"), "cap_max_h": 640, **W_, "caption": "'33살 사상 첫 리트 만점 서울대 치대생 성적 변화' 글 댓글",
  "label": "인터뷰가 나오자", "lines": ["\"저 얼굴에 '공부까지' 잘하네\""]},
 {"out": str(O / "c05.jpg"), "sub": "디시 법학전문대학원 갤러리 (7월 21일)", "title": "\"그래도 '역사와 함께'해서 영광임\"",
  "cap": str(O / "law_honor.jpg"), "cap_max_h": 520, **W_, "caption": "",
  "label": "같은 시험을 본 수험생", "lines": ["19년 만의 첫 만점 회차에 '내가 있었다'"]},
 {"out": str(O / "c06.jpg"), "sub": "디시 회계사 수험 갤러리 (8월 20일)", "title": "\"아무튼 'ㅈㄴ 대단한 사람'인듯\"",
  "cap": str(O / "cpa.jpg"), "cap_max_h": 700, **W_, "caption": "",
  "label": "그의 '폰 끊기' 공부법을", "lines": ["따라 해 본 수험생도 있었다"]},
 {"out": str(O / "c07.jpg"), "sub": "다시 7월 22일, 같은 글 댓글", "title": "그때도 '이런 댓글'은 있었다",
  "cap": str(O / "sb_cmt_ai.jpg"), "cap_max_h": 600, **W_, "caption": "",
  "label": "\"공부법 하나 바꾼다고 만점이 돼?\"", "lines": ["넉 달 뒤, 이 질문이 '모든 것'이 됐다"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
print("ok")
