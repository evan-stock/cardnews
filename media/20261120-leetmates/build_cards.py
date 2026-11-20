"""20261120-leetmates: 리트 만점자 서울대 치대 동기들이 디시 시대인재 갤러리에 남긴 글 3개 전달(우리 의견 장 없음).
캡처: 디시 모바일 화면 스크린샷(X @jutingstar9999가 모아 올린 이미지). 3번 글의 학원 광고 배너만 잘라냄. 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "디시 시대인재 N 재수종합 갤러리 (11/20 01:42)", "title": "\"옹호와 비난, 꼭 '둘 중 하나'여야 하나\"",
  "cap": str(O / "p1.jpg"), "cap_max_h": 760, **W_, "caption": "'형, 오빠를 보내며(설치 인증)' 글 캡처",
  "label": "좋아했던 만큼 배신감도 컸다", "lines": ["\"고인의 범죄에 '피해받은 이'에게 유감\""]},
 {"out": str(O / "c03.jpg"), "sub": "디시 시대인재 N 재수종합 갤러리 (11/20 04:06)", "title": "\"지난 일주일, '너무 혼란스러운' 나날\"",
  "cap": str(O / "p2a.jpg"), "cap_max_h": 780, **W_, "caption": "'설치26 입니다' 글 캡처 (1/2)",
  "label": "전과가 공개되며 크게 실망했고 분노도 컸다", "lines": ["학기 초 '가까워지려 노력하던' 형"]},
 {"out": str(O / "c05.jpg"), "sub": "같은 글 (이어서)", "title": "\"언론 속 사기꾼과 '내 기억 속 형'\"",
  "cap": str(O / "p2b.jpg"), "cap_max_h": 780, **W_, "caption": "'설치26 입니다' 글 캡처 (2/2)",
  "label": "슬픔, 배신감, 분노, 혼란", "lines": ["그래도 '입체적인 존재'의 다른 면을 봤다"]},
 {"out": str(O / "c04.jpg"), "sub": "디시 시대인재 N 재수종합 갤러리 (11/19 21:45)", "title": "\"치팅이 사실이라면 '죄지은 거 맞죠'\"",
  "cap": str(O / "p3.jpg"), "cap_max_h": 760, **W_, "caption": "'진우형 치대 동기입니다' 글 캡처 · 작성자 신원 미확인",
  "label": "8개월 동안 동기들에게는 좋은 형", "lines": ["\"그냥 '고생했다'고 말해주고 싶어요\""]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
print("ok")

# 표지: 흰 배경 손짓 인터뷰 사진(11/18 특강 게시물 표지에 한 번만 쓴 사진) 흑백. 증명사진은 표지에 8번 써서 바꿈(11/20 사용자 지시)
from PIL import Image, ImageOps
ImageOps.grayscale(Image.open(O / "cover_src.jpg")).convert("RGB").save(O / "cover_bg.jpg", quality=94)
