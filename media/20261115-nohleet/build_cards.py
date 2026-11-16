"""20261115-nohleet: 리트 언어이해 강사 노형석(메가로스쿨)이 리트 첫 만점자 이진우 씨 시험지에 의문 제기 + '만나서 풀어보자' 제안.
원본: 스레드 @hyungseoknoh 게시물·답글 직접 캡처(크롬, 다크 모드). wide.magazine 카드는 워터마크가 있어 쓰지 않음.
표지 사진: 노형석 = 메가로스쿨 강사 프로필(img.megals.co.kr/prof/pcnhs_a.png, 누끼), 이진우 = 20261115-nowyeosi 누끼 재사용."""
import json, subprocess, sys
from pathlib import Path

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
TH = (16, 16, 16)  # 스레드 다크 모드 바탕
SUB = "리트 언어이해 강사 노형석 스레드 · 11월 15일"
spec = [
    {"out": str(O / "c02.jpg"), "sub": SUB,
     "title": "\"27번 3번은\n'가장 확실한' 오답\"", "cap": str(O / "cap_b.png"), "cap_max_h": 620, "box_bg": TH,
     "caption": "스레드 @hyungseoknoh 게시물 캡처 (조회 3.2만, 27번 부분)",
     "label": "리트 언어이해 만점 경험 · 본시험 13번 응시",
     "lines": ["만점자 시험지에서 3번을 골랐다 지운 흔적을 짚었습니다."]},
    {"out": str(O / "c03.jpg"), "sub": SUB,
     "title": "\"리트를 다 맞았다는 건\n'설명하지 못하겠다'\"", "cap": str(O / "cap_c.png"), "cap_max_h": 620, "box_bg": TH,
     "caption": "스레드 @hyungseoknoh 게시물 캡처",
     "label": "\"선지 고른 흔적만 보면 생각을 안다\"",
     "lines": ["매년 수험생 시험지를 보며 상담해 왔다고 밝혔습니다."]},
    {"out": str(O / "c04.jpg"), "sub": "같은 글에 직접 단 답글",
     "title": "\"부디 '우연'이길\n간절히 바랍니다\"", "cap": str(O / "cap_wish.png"), "cap_max_h": 620, "box_bg": TH,
     "caption": "스레드 @hyungseoknoh 답글 캡처",
     "label": "부정행위라고 단정하지는 않았습니다",
     "lines": ["자신이 파악 못 한 사고 과정이 있길 바란다고 했습니다."]},
    {"out": str(O / "c05.jpg"), "sub": "1시간 반 뒤 올린 새 글",
     "title": "\"만나서 기출 몇 문제\n'같이 풀어봅시다'\"", "cap": str(O / "cap_offer.png"), "cap_max_h": 620, "box_bg": TH,
     "caption": "스레드 @hyungseoknoh 게시물 캡처",
     "label": "\"이게 왜 답이야?\" 물어보면 된다",
     "lines": ["다른 학원 소속이면 '타사 공간'에서 해도 괜찮다고 했습니다."]},
    {"out": str(O / "c06.jpg"), "sub": "\"만점자가 진짜면 은퇴하라\"는 요구에",
     "title": "\"아이가 '초1'이고\n외벌이 가장입니다\"", "cap": str(O / "cap_retire.png"), "cap_max_h": 620, "box_bg": TH,
     "caption": "스레드 @hyungseoknoh 답글 캡처",
     "label": "\"문제 제기를 막으려는 걸로 보인다\"",
     "lines": ["수능처럼 공정성이 보장되면 검증 수단이 된다고도 했습니다."]},
]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
