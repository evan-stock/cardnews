"""20261113-jensenout: 엔비디아 공식 발표(뉴스룸) 캡처 카드."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
spec = [{"out": str(O / "c02.jpg"), "sub": "엔비디아 공식 발표 · 현지 11월 12일",
  "title": "사장·CEO·이사직에서\n'즉시' 물러났다", "cap": str(O / "src_nvpr.png"), "cap_bg": "light",
  "caption": "엔비디아 뉴스룸 보도자료 캡처",
  "lines": ["임시 CEO는 2013년부터 CFO를 맡아온 콜레트 크레스.", "이사회는 사임 이유를 밝히지 않았습니다."]}]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
