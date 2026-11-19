"""20261119-leetlife: 리트 만점자 이진우 타임라인. 자살보도 권고기준 — 장소·방법·메모·성적표 이미지·현장 사진 안 씀, 109 안내.
근거: 우먼센스·법률저널·엑스포츠뉴스 인터뷰(학력), 중앙·한국일보(17일 인터뷰), 경향·헤럴드(18일 고발·계약해지), JTBC·연합(19일), MK스포츠·위키트리(이후)."""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import P, LN, MU, YE, F, rich, base, logo, head
bg = ImageOps.fit(Image.open(O / "p.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.5, .3))
ImageEnhance.Color(bg).enhance(0.0).save(O / "cover_bg.jpg", quality=94)

FD, FL, LH, GAP = 38, 46, 68, 52

def tl_h(items):
    return sum(64 + LH * len(ls) for _, ls in items) + GAP * (len(items) - 1)

def tl(d, y, items):
    x = P + 16
    ys, yy = [], y
    for _, ls in items:
        ys.append(yy); yy += 64 + LH * len(ls) + GAP
    d.line((x, ys[0] + 24, x, ys[-1] + 24), fill=LN, width=5)
    for (date, ls), y0 in zip(items, ys):
        d.ellipse((x - 14, y0 + 10, x + 14, y0 + 38), fill=YE)
        d.text((x + 46, y0), date, font=F("SemiBold", FD), fill=YE)
        for i, l in enumerate(ls):
            rich(d, x + 46, y0 + 64 + LH * i, l, F("ExtraBold", FL))
    return yy - GAP

def card(n, sub, title, items, src, help=False):
    im = base(); d = ImageDraw.Draw(im); y = head(d, sub, title, y=120)
    bottom = H - (190 if help else 140)
    y0 = y + max(40, (bottom - y - tl_h(items) - 60) // 2)
    y2 = tl(d, y0, items)
    d.text((W - P, y2 + 30), src, font=F("Medium", 24), fill=MU, anchor="ra")
    if help: d.text((W // 2, H - 140), "힘들 땐 자살예방 상담전화 109 (24시간)", font=F("SemiBold", 26), fill=MU, anchor="mm")
    logo(im); im.save(O / f"c{n:02d}.jpg", quality=93)

card(2, "① 출발", "고2 자퇴,\n수능 국어 '7등급'", [
    ("고등학교 2학년 2학기", ["학교 공부에 적응 못 해 '자퇴'", "\"중학교 땐 반 10등도 힘들었다\""]),
    ("2018학년도 수능", ["국어 '7등급'", "\"평생 완독한 책은 딱 한 권\""]),
], "본인 인터뷰(우먼센스·엑스포츠뉴스)")
card(3, "② 공식 이력에 없던 과거", "개명 전 이름의\n'판결문'", [
    ("시기 미상 · 개명 전", ["공갈 혐의로 '집행유예'", "두 달 뒤 같은 범죄로 '징역형'"]),
    ("함께 수감됐다는 재소자", ["\"사기로 돈 모아 '학습교재'", "만든다고 했다\""]),
    ("JTBC 확인", ["개명 전 이름·생년월일 '일치'", "본인 측 해명은 나오지 않아"]),
], "JTBC 보도(11.19)")
card(4, "③ 반전", "고려대, 그리고\n'서울대 치대'", [
    ("2024학년도 수능", ["고려대 '정치외교학과' 진학"]),
    ("2025년 11월 10일", ["고려대 커뮤니티 '생2 과외' 구인글", "본인 글로 '지목'(확인 안 됨)"]),
    ("2026학년도 수능", ["'전 과목 1등급', 생2 50점 만점", "정시로 '서울대 치대' 입학"]),
], "법률저널·중앙일보 보도, 고파스 캡처")
card(5, "④ 정점", "19년 만의\n'리트 첫 만점'", [
    ("2026년 7~8월", ["리트 70문항 모두 맞혀 '첫 만점'", "8월 18일 성적 발표"]),
    ("2주 뒤", ["공부법 책 '출간'", "출판사 대표도 '본인'"]),
    ("11월 초", ["입시업체 시대인재 '브레인코치' 계약"]),
], "법률저널·헤럴드경제 보도, 온라인 커뮤니티")
card(6, "⑤ 의혹", "'AI 부정행위'\n의심이 번지다", [
    ("11월 중순", ["세무사 시험 'AI 부정' 사건 뒤", "그의 만점에도 의혹 제기"]),
    ("11월 12일", ["\"수능 국어 '생중계'로 풀겠다\""]),
    ("11월 17일", ["\"차라리 '수사'를 받겠다\"", "시험지 답 고친 흔적엔", "\"확률 '희박'한 건 인정\""]),
], "톱스타뉴스·중앙일보·한국일보 보도")
card(7, "⑥ 마지막 사흘", "고발, 계약 해지,\n그리고 '불참'", [
    ("11월 18일", ["변호사들 경찰에 '고발'", "시대인재 계약 '해지'"]),
    ("11월 19일 오전", ["예고한 '공개 검증'에 나타나지 않아", "신변 우려 신고 접수"]),
    ("11월 19일 오후", ["숨진 채 발견"]),
], "경향신문·연합뉴스 보도", help=True)
card(8, "⑦ 남은 것", "의혹은\n'확인되지 않은' 채", [
    ("그 뒤", ["미미미누·백지연, 인터뷰 영상 비공개", "서울대 입학취소 심의도 멈춰"]),
    ("수사", ["광역수사단, 수능 시험지 '증거보전'", "부정행위 여부는 끝내 밝혀지지 않아"]),
], "MK스포츠·위키트리·연합뉴스 보도", help=True)
