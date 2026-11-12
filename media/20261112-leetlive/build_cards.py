"""20261112-leetlive: 참고 게시물(@flu.vo DfosVSxH_u0) 흐름 그대로 — 표지 → 미미미누 유튜브 고정 댓글 → 시대인재N 갤 본인 글+신분증 → 서울대 학사정보+댓글.
캡처는 워터마크 없는 원본(유튜브·디시)을 직접 받아 씀. cap3/cap4 합성은 채팅에서 PIL로 만듦(주민번호·학번 흐림)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFilter

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"

c = Image.open(O / "press04.jpg").convert("RGB")
c = c.resize((1080, round(c.height * 1080 / c.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
c.crop((0, 0, 1080, min(c.height, 1350))).save(O / "cover_bg.jpg", quality=95)

spec = [
    {"out": str(O / "c02.jpg"), "sub": "미미미누 유튜브 채널 · 고정 댓글 (11월 12일 15:18)",
     "title": "\"2027 수능 국어\n'실시간 Live'로 풀이합니다\"", "cap": str(O / "src_yt.png"), "cap_crop": [0, 0, 1142, 630],
     "cap_max_h": 640, "caption": "유튜브 미미미누 채널 댓글 캡처 (@이진우-brainaccel)",
     "lines": ["19일 수능 날 문제지가 올라오는 10시 56분에 인쇄해", "11시부터 80분간, 편집 없이 원테이크로 생중계합니다."]},
    {"out": str(O / "c03.jpg"), "sub": "같은 날 디시 시대인재N 갤러리 · 15:26",
     "title": "\"안녕하세요 이진.우입니다\"\n'주민등록증'까지 올렸다", "cap": str(O / "cap3.png"),
     "cap_max_h": 700, "caption": "디시 시대인재N 갤러리 본인 글 캡처 (생년월일·번호 흐림)",
     "lines": ["감독·장소·중계 채널은 16일까지 정하겠다고 했습니다."]},
    {"out": str(O / "c04.jpg"), "sub": "서울대 학사정보 인증 + 댓글",
     "title": "\"시간으로 보여주겠지\"\n본인 답 \"'오래안걸릴거에요'\"", "cap": str(O / "cap4.png"),
     "cap_max_h": 640, "caption": "디시 시대인재N 갤러리 본인 글·댓글 캡처 (학번 흐림)",
     "lines": ["\"ㅈ간지\" \"정면돌파만 한 게 없죠\"", "응원 댓글이 줄줄이 달렸습니다."]},
]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
