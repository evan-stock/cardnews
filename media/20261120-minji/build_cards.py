"""20261120-minji: 리트 만점자 사망 뒤 재조명된 '하버드 박사' 김민지 사건(2025.6).
캡처는 앱 안 브라우저 모바일 화면(560폭) 스크린샷. 엑스 이미지(워터마크) 대신 기사 원문 캡처 사용.
자살예방 보도준칙: 방법·장소 묘사 없음(한국일보 본문 인용 중 방법 언급 부분·CCTV 사진 제외), 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
def crop(src, box, out):
    Image.open(O / src).convert("RGB").crop(box).save(O / out, quality=95)
# 표지: 한경 기사 사진(이진우·김민지 나란히)
im = Image.open(O / "hk_raw.jpg").convert("RGB").crop((0, 680, 776, 1212))
im.resize((1080, round(532 * 1080 / 776)), Image.LANCZOS).save(O / "cover_pair.jpg", quality=95)
def stack(src, boxes, out, gap=14):
    a = Image.open(O / src).convert("RGB"); parts = [a.crop(b) for b in boxes]
    h = Image.new("RGB", (800, sum(p.height for p in parts) + gap * (len(parts) - 1)), a.getpixel((5, boxes[0][1] + 5)))
    y = 0
    for p in parts: h.paste(p, (0, y)); y += p.height + gap
    h.save(O / out, quality=95)
stack("hk_raw.jpg", [(0, 20, 800, 220), (0, 505, 800, 650)], "hk_head.jpg")
crop("asiae_book_raw.jpg", (0, 0, 800, 878), "book.jpg")
stack("asiae_top_raw.jpg", [(0, 0, 800, 270), (0, 380, 800, 775)], "asiae_head.jpg")
crop("gilbut_raw.jpg", (16, 165, 784, 590), "gilbut.jpg")
crop("aju_raw.jpg", (0, 30, 800, 875), "aju.jpg")
a = Image.open(O / "hankook_raw.jpg").convert("RGB")
top, bul = a.crop((0, 60, 800, 280)), a.crop((0, 700, 800, 840))
h = Image.new("RGB", (800, top.height + bul.height + 10), a.getpixel((20, 300)))
h.paste(top, (0, 0)); h.paste(bul, (0, top.height + 10)); h.save(O / "hankook.jpg", quality=95)
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "한국경제 (11월 20일)", "title": "리트 만점자와 '평행이론'",
  "cap": str(O / "hk_head.jpg"), "cap_max_h": 720, "caption": "한국경제 기사 화면",
  "label": "이진우 씨가 숨진 다음 날", "lines": ["1년 5개월 전 '하버드 멘토' 사건이 다시 소환됐다"]},
 {"out": str(O / "c03.jpg"), "sub": "2025년 1월 출간 · 길벗", "title": "\"하버드·UCLA '임상심리학 박사'\"",
  "cap": str(O / "book.jpg"), "cap_max_h": 760, **W_, "caption": "책 홍보 이미지 (아시아경제 기사 화면)",
  "label": "띠지엔 '하버드 교수 추천사'까지", "lines": ["심리 분야 판매 1위, 교육청·대검 강연까지 다녔다"]},
 {"out": str(O / "c03b.jpg"), "sub": "아티브뉴스 기사 화면", "title": "사망 후 드러난 '과거 행적'",
  "cap": str(O / "tattoo_clean.jpg"), "cap_max_h": 740, **W_, "caption": "본인 강의 홍보 영상 장면 (아티브뉴스 기사 화면)",
  "label": "본인 강의 홍보 영상 속 양팔 문신", "lines": ["띠지 속 '흰 가운'과는 다른 모습"]},
 {"out": str(O / "c04.jpg"), "sub": "아시아경제 (2025년 6월 10일)", "title": "논문도 학위도 '검색이 안 됐다'",
  "cap": str(O / "asiae_head.jpg"), "cap_max_h": 720, **W_, "caption": "아시아경제 기사 화면",
  "label": "\"뉴욕 면허 있어요?\" 댓글 하나에서 시작", "lines": ["의혹이 퍼지자 저자는 SNS를 모두 닫았다"]},
 {"out": str(O / "c05.jpg"), "sub": "길벗출판사 공식 입장 (2025년 6월 10일)", "title": "\"주요 이력 '상당 부분 허위'\"",
  "cap": str(O / "gilbut.jpg"), "cap_max_h": 600, **W_, "caption": "출판사 입장문 (KNEWSLA 기사 화면)",
  "label": "추천사도 '직접 받은 게 아니었다'", "lines": ["책은 판매 중지·회수, 법적 책임 예고"]},
 {"out": str(O / "c06.jpg"), "sub": "아주경제 (2025년 6월 11일)", "title": "의혹 이틀 만에 '부고'",
  "cap": str(O / "aju.jpg"), "cap_max_h": 720, **W_, "caption": "아주경제 기사 화면 (부고 일부는 기사에서 가림)",
  "label": "향년 43세", "lines": ["남편 SNS에 부고가 올라왔다"]},
 {"out": str(O / "c07.jpg"), "sub": "한국일보 (11월 20일)", "title": "\"열광하다가 '사냥개처럼'\"",
  "cap": str(O / "hankook.jpg"), "cap_max_h": 600, "caption": "한국일보 기사 화면",
  "label": "신재용 서울대 경영대 교수", "lines": ["\"불과 1년여 만에 '비슷한 일'이 또 발생했다\""]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
print("ok")
# 표지 배경: 사용자 화질개선본(cand/cover_hq_user.png)의 박힌 글자 부분을 검게 덮은 cover_user_bg.jpg
