"""20261113-mock: '이때부터 안경 테스트?' 세무사 수석이 쳤다는 모의고사 — 참고 @healing.cook(DfqUqlLE_Hc) 흐름.
캡처는 참고 게시물(embed를 GitHub에서 찍은 media/ref-DfqUqlLE_Hc) 화면에서 성적표·댓글 부분만 잘라냄. 캡처 카드 틀."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
spec = [
 {"out": str(O / "c02.jpg"), "sub": "2026년 4월 5일 시행 · 학원 세무사 1차 전국 모의고사", "title": "평균 37점 과목에\n최고점 '100점'",
  "cap": str(O / "cap_sheet_top.png"), "cap_max_h": 560, "caption": "커뮤니티에 퍼진 모의고사 성적표 캡처",
  "label": "재정학 100 · 세법 95 · 회계 100 · 선택법 97.5", "lines": ["회계학개론 평균 37.85점, 재정학 평균 47.9점.", "응시자 1,229명."]},
 {"out": str(O / "c03.jpg"), "sub": "커뮤니티에 퍼진 성적표 확대", "title": "\"이 점수 자체가\n'말이 안 된다'\"",
  "cap": str(O / "cap_zoom.png"), "caption": "같은 성적표 확대",
  "label": "\"이때부터 안경 성능 테스트\"라는 말까지", "lines": ["수석이 이 모의고사를 쳤다는 글과 함께 퍼졌습니다.", "표의 최고 총점은 385점."]},
 {"out": str(O / "c04.jpg"), "sub": "댓글 반응", "title": "\"학원 모의고사가\n실제 시험보다 '몇 배' 어려운데\"",
  "cap": str(O / "cap_cmt.png"), "caption": "커뮤니티 반응 캡처",
  "label": "\"재정학 100 진짜…\"", "lines": ["실제 시험에선 재정학 97.5, 나머지 세 과목 100점."]},
]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
