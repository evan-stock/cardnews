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

im = base(); d = ImageDraw.Draw(im); y = head(d, "오늘 확인된 것", "메모는 있었지만\n'부정행위' 언급은 없었다", y=110)
y = blocks(d, y + 20, [("메모", ["현장에서 짧은 메모 발견", "의혹을 '인정·해명'하는 내용은 없어"]),
                        ("출연했던 유튜브", ["미미미누 채널, 출연 영상 '비공개' 전환"]),
                        ("수사", ["피의자 사망 → '공소권 없음' 종결 전망", "경찰 \"지금은 '판단 어렵다'\""])])
d.text((W - P, y + 4), "서울경제·국민일보·톱스타뉴스 보도", font=F("Medium", 22), fill=MU, anchor="ra")
help_line(d); logo(im); im.save(O / "c02.jpg", quality=93)

im = base(); d = ImageDraw.Draw(im); y = head(d, "남은 질문", "의혹은 이대로\n'묻히게' 될까", y=110)
y = blocks(d, y + 20, [("고발인 측", ["\"휴대전화·노트북 등 '유품' 조사해야\"", "추가 수사 계속 요구"]),
                        ("정부", ["리트에 '수능' 의혹까지 제기", "교육부 등 '진상조사' 가능성 거론"]),
                        ("생각해 볼 것", ["의혹 '검증'과 '여론 재판'의 경계는", "어디까지였을까"])])
d.text((W - P, y + 4), "국민일보·시사저널 보도", font=F("Medium", 22), fill=MU, anchor="ra")
help_line(d); logo(im); im.save(O / "c03.jpg", quality=93)
