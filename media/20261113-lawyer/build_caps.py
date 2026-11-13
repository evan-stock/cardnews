"""20261113-lawyer: 세무사 수석 법률대리인 선임. 캡처는 사용자가 보낸 스레드 화면(cand/src_threads.png)에서 잘라냄."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
spec = [
 {"out": str(O / "k02.jpg"), "sub": "법무법인 노바 스레드 · 11월 13일", "title": "\"사실관계 확인 절차에\n'성실히' 임할 것\"",
  "cap": str(O / "cap_post.png"), "caption": "이돈호 변호사 스레드 캡처",
  "label": "대리인은 팔로워 35만 '법률 유튜버'", "lines": ["어제 언론엔 \"지금은 대화가 어렵다\"던 수석.", "하루 만에 변호사를 통해 입장을 냈습니다."]},
 {"out": str(O / "k03.jpg"), "sub": "댓글 반응", "title": "\"실력 입증이라면\n변호사까지 갈 문제인가\"",
  "cap": str(O / "cap_cmt.png"), "caption": "스레드 댓글 캡처",
  "label": "\"당당한 수석이 닉네임이라니\"", "lines": ["자신을 세무사라고 밝힌 댓글이 좋아요 251개로 1위.", "\"이돈호가 맡을 정도면 부정행위 아니란 것\" 반응도."]},
]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
