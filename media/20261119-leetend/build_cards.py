"""20261119-leetend: 리트 만점자 사망 후속. 자살보도 권고기준 따름 — 장소·방법·메모 문구·성적표·현장 사진 안 씀, 109 안내.
보도 기준: 메모에 부정행위 인정·해명 없음(서울경제·톱스타뉴스), 미미미누 출연 영상 비공개 전환, 수사 '공소권 없음' 종결 전망·경찰 "판단 어렵다", 고발인 추가 수사 요구(국민일보·시사저널)."""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import P, BOX, LN, MU, F, rich, base, logo, head
bg = ImageOps.fit(Image.open(O / "p.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.5, .3))
ImageEnhance.Color(bg).enhance(0.0).save(O / "cover_bg.jpg", quality=94)

def blocks(d, y, items):
    for t, ls in items:
        hh = 70 + 56 * len(ls)
        d.rounded_rectangle((P, y, W - P, y + hh), 22, fill=BOX, outline=LN, width=2)
        d.text((P + 32, y + 22), t, font=F("SemiBold", 26), fill=MU)
        for i, l in enumerate(ls): rich(d, P + 32, y + 64 + 56 * i, l, F("ExtraBold", 33))
        y += hh + 22
    return y

def help_line(d):
    d.text((W // 2, H - 140), "힘들 땐 자살예방 상담전화 109 (24시간)", font=F("SemiBold", 26), fill=MU, anchor="mm")

# 사용자: '불신사회가 됐다 — 리트냥이 사태가 우리에게 남긴 것' 주제로
im = base(); d = ImageDraw.Draw(im); y = head(d, "무슨 일이 있었나", "'첫 만점'에서\n의혹, 그리고 사망까지", y=110)
y = blocks(d, y + 20, [("7월 리트", ["시험 사상 '첫 만점' 나와"]),
                        ("이후", ["'AI 부정행위' 의혹 제기, 경찰 고발", "본인은 부인하며 '공개 검증' 예고"]),
                        ("19일", ["공개 검증 불참, 숨진 채 발견", "의혹은 '확인되지 않은' 채 남아"])])
d.text((W - P, y + 4), "국민일보·서울경제·연합뉴스 보도", font=F("Medium", 22), fill=MU, anchor="ra")
help_line(d); logo(im); im.save(O / "c02.jpg", quality=93)

im = base(); d = ImageDraw.Draw(im); y = head(d, "이 사태가 남긴 것", "'잘 본 시험'도\n의심받는 사회", y=110)
y = blocks(d, y + 20, [("① 만점 = 의혹", ["실력보다 '부정'을 먼저 떠올리는 시선", "고득점자는 '증명'부터 해야 하나"]),
                        ("② 시험 자체를 못 믿는다", ["세무사 시험 'AI 부정행위' 수사 중", "오늘 수능장서 초소형 '카메라·이어폰'"]),
                        ("③ 검증이 '구경거리'로", ["생중계 검증에 쏠린 관심과 조롱", "사실 확인보다 '여론 재판'이 앞섰다"])])
d.text((W - P, y + 4), "SBS·연합뉴스 보도", font=F("Medium", 22), fill=MU, anchor="ra")
help_line(d); logo(im); im.save(O / "c03.jpg", quality=93)

im = base(); d = ImageDraw.Draw(im); y = head(d, "그래서 필요한 것", "의심 대신\n'믿을 수 있는 제도'", y=110)
y = blocks(d, y + 20, [("시험 관리", ["AI·초소형 기기 시대에 맞는 '감독' 기준"]),
                        ("의혹 검증", ["개인 '생중계'가 아닌 공식 '조사'로"]),
                        ("수사", ["피의자 사망으로 '종결' 전망", "고발인·정부 '진상조사' 요구는 계속"])])
d.text((W - P, y + 4), "국민일보·시사저널 보도", font=F("Medium", 22), fill=MU, anchor="ra")
help_line(d); logo(im); im.save(O / "c04.jpg", quality=93)
