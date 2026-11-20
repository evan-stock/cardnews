"""20261120-leetsheet: MBC 단독 '리트 만점자 수능시험지 비정상적 풀이 정황'(11.20) + 리트 밀린 답 의혹 + 책 구매자 문서제출명령.
캡처는 앱 안 브라우저 모바일 화면(560폭) 스크린샷. 사망 관련 묘사 없음, 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
def stack(src, boxes, out, gap=14):
    a = Image.open(O / src).convert("RGB"); parts = [a.crop(b) for b in boxes]
    h = Image.new("RGB", (800, sum(p.height for p in parts) + gap * (len(parts) - 1)), a.getpixel((5, boxes[0][1] + 5)))
    y = 0
    for p in parts: h.paste(p, (0, y)); y += p.height + gap
    h.save(O / out, quality=95)
stack("mbc_raw.jpg", [(0, 140, 800, 280), (0, 1075, 800, 1170)], "mbc1.jpg")
stack("mbc_raw.jpg", [(0, 140, 800, 280), (0, 1195, 800, 1380)], "mbc2.jpg")
stack("news1_raw.jpg", [(0, 220, 800, 390), (0, 640, 800, 735)], "news1.jpg")
stack("sbs_raw.jpg", [(0, 60, 800, 215), (0, 805, 800, 985)], "sbs.jpg")
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "top": 340, "sub": "MBC 단독 (11월 20일)", "title": "정답 번호를 '한쪽에 몰아' 적었다",
  "cap": str(O / "mbc1.jpg"), "cap_max_h": 640, **W_, "caption": "MBC 기사 화면",
  "label": "풀이에 있어야 할 수식도 없었다", "lines": ["교육부 등 관계기관이 '정밀 검토' 중"]},
 {"out": str(O / "c03.jpg"), "top": 304, "sub": "같은 기사", "title": "\"부정행위 없어도 '나올 수 있다'\"",
  "cap": str(O / "mbc2.jpg"), "cap_max_h": 640, **W_, "caption": "MBC 기사 화면",
  "label": "그래서 정부는 신중하게 보는 중", "lines": ["경찰은 사망 뒤에도 '수사 계속'"]},
 {"out": str(O / "c04.jpg"), "top": 337, "sub": "뉴스1 (11월 16일)", "title": "리트 시험지엔 '밀린 답' 의혹",
  "cap": str(O / "news1.jpg"), "cap_max_h": 520, **W_, "caption": "뉴스1 기사 화면",
  "label": "지운 답 3개가 앞 문항 정답과 일치", "lines": ["본인은 \"집중력이 떨어져 '잔실수'\" 해명"]},
 {"out": str(O / "c05.jpg"), "top": 276, "sub": "SBS (11월 19일)", "title": "책 구매자들 \"수능 시험지 '보자'\"",
  "cap": str(O / "sbs.jpg"), "cap_max_h": 600, **W_, "caption": "SBS 기사 화면",
  "label": "손해배상 소송 중 법원에 제출명령 신청", "lines": ["풀이 없이 '정답만' 표시됐는지 확인하려는 것"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
print("ok")
# 렌더 후 01.jpg 는 사용자 화질개선 표지(cand/cover_hq_user.png)로 덮어쓴다. CTA 배경은 cover_user_bg.jpg
