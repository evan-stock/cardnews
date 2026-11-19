"""20261119-leetticket: 리트 만점자 18수능 수험표를 두고 대학가 에타 반응(수원대 글, 연세대 글+댓글, 고려대·성균관대·서강대·건국대 댓글).
자살보도 권고기준: 캡처 속 장소('모텔방')·'자살'·죽음 단어 흐림, 죽음을 미화하는 본문 줄 흐림. 수리남 장면·얼굴 합성 밈·송강 드립·유서 언급 글은 뺌. 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "수원대 에브리타임 익명 글 (11/19 14:38)", "title": "\"동정표 그딴 거 '아니고'\"",
  "cap": str(O / "suwon.jpg"), "cap_max_h": 760, **W_, "caption": "수원대 에브리타임 익명 게시글 캡처",
  "label": "왜 하필 18수능 수험표였을까", "lines": ["\"유일하게 '진실'이었던 것이라 그런 거냐\""]},
 {"out": str(O / "c03.jpg"), "sub": "연세대 에브리타임 익명 글과 댓글 (11/19 14:23)", "title": "\"모든 게 가짜였던 자의 '유일한 진짜'\"",
  "cap": str(O / "yonsei.jpg"), "cap_max_h": 760, **W_, "caption": "연세대 에브리타임 익명 게시글 캡처 (전남대·연세대·서울대 댓글)",
  "label": "학생들이 본 그 수험표", "lines": ["\"자기 인생에 '유일한 진실'이었음\""]},
 {"out": str(O / "c04.jpg"), "sub": "같은 글 댓글 (고려대·성균관대·서강대·건국대)", "title": "\"딱 '한 장밖에' 없는 수험표\"",
  "cap": str(O / "cmts.jpg"), "cap_max_h": 780, **W_, "caption": "연세대 에브리타임 게시글 댓글 캡처",
  "label": "수학 나형, 유일하게 받은 1등급", "lines": ["\"스스로 노력해서 얻은 '유일한 자부심'\""]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
