"""20261113-d19 3판: 실제 캡처 장은 캡처 카드 틀(scripts/post_cap_card.py)로. 조세일보는 GitHub에서 원문 화면을 직접 찍은 것(shots/joseilbo_full.png),
블라인드·'쟤인거지' 댓글은 사용자가 보낸 참고 게시물(@happygram.kr) 화면에서 잘라냄."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
spec = [
 {"out": str(O / "k02.jpg"), "sub": "조세일보 · 11월 12일", "title": "세무사 수석 근황\n'연락 두절'",
  "cap": str(O / "cap_joseilbo.png"), "caption": "조세일보 기사 화면 캡처",
  "label": "\"지금은 대화가 어렵다\"", "lines": ["블로그는 댓글 쓰기도 막힌 상태.", "앞서 다른 인터뷰에선 \"소거법으로 풀었다\"며 부인했습니다."]},
 {"out": str(O / "k03.jpg"), "sub": "직장인 커뮤니티 블라인드 댓글", "title": "\"협회가 조사하려고 불렀는데\n'잠수'탐\"",
  "cap": str(O / "cap_blind.png"), "caption": "블라인드 댓글 캡처",
  "label": "\"수습 안 한다고 함\"", "lines": ["세무사는 합격 뒤 수습 교육을 마쳐야", "등록할 수 있습니다."]},
 {"out": str(O / "k04.jpg"), "sub": "댓글 반응", "title": "\"끝까지 수습 안 하면\n그냥 '쟤'인 거지\"",
  "cap": str(O / "cap_jae.png"), "caption": "커뮤니티 반응 캡처",
  "label": "19일 집체교육에 나타날까", "lines": ["커뮤니티에선 수습 집체교육 첫날을 주목.", "공교롭게 같은 날, 리트 만점자는 수능 국어 생중계."]},
]
sj = D / "cap_spec2.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
