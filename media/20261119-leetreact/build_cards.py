"""20261119-leetreact: 리트 만점자 사망, 그를 만났던 사람들의 반응 모음.
표지: 오늘 공개검증 현장 영상(leetlive-reel)에서 노형석 강사가 우는 장면. 노형석 강사 스레드(사용자 제공 캡처), 미미미누 커뮤니티 공지(X @Argent_wave 경유 캡처).
자살보도 권고기준: 장소·방법·메모 내용 안 씀, 109 안내."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
fr = Image.open(O / "nhs_cry.png").convert("RGB").crop((230, 685, 850, 1375))
ImageOps.fit(fr, (W, H), Image.LANCZOS, centering=(.5, .35)).save(O / "cover_bg.jpg", quality=94)
specs = [
 {"out": str(O / "c02.jpg"), "sub": "노형석 리트 국어 강사 (스레드)", "title": "\"제가 '잘못'했습니다\"", "cap": str(O / "cap_nhs.jpg"), "cap_crop": [0, 0, 1080, 1000], "cap_max_h": 700,
  "caption": "노형석 강사 스레드 캡처", "label": "공개 검증 현장에서 울먹였던 강사", "lines": ["\"평생 무겁게 '미안한 마음' 잊지 않겠습니다\""]},
 {"out": str(O / "c03.jpg"), "sub": "미미미누 (유튜브 커뮤니티 공지)", "title": "\"매우 '마음이 무겁고'\"", "cap": str(O / "cap_mimi.jpg"), "cap_max_h": 640,
  "caption": "미미미누 커뮤니티 공지 캡처", "label": "만점자 인터뷰를 처음 올렸던 유튜버", "lines": ["출연 영상은 '비공개' 처리", "백지연 채널도 인터뷰 영상 비공개"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
