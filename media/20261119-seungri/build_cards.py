"""20261119-seungri: 승리, 만삭 20대 아내와 18일 밤 인천공항 입국(스타뉴스 등). 혼인신고 마침·내년 1월 아들 출산(노컷뉴스),
혼전임신설엔 "법적으로 부부, 임신해서 결혼한 것 아니다"(10.28 일간스포츠), 8월 강남 식당 특수폭행 고소는 부인. 아내 얼굴 노출 사진은 안 씀."""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import P, BOX, LN, MU, F, rich, base, logo, head

ImageOps.fit(Image.open(O / "press03.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.62, .5)).save(O / "cover_bg.jpg", quality=94)

def table(d, y, rows, rh=84, lw=170):
    d.rounded_rectangle((P, y, W - P, y + rh * len(rows)), 22, fill=BOX, outline=LN, width=2)
    for k, (lab, txt) in enumerate(rows):
        cy = y + rh * k + rh // 2
        if k: d.line((P + 28, y + rh * k, W - P - 28, y + rh * k), fill=LN, width=2)
        d.text((P + 32, cy), lab, font=F("SemiBold", 26), fill=MU, anchor="lm")
        rich(d, P + lw, cy - 20, txt, F("ExtraBold", 31))
    return y + rh * len(rows)

def photo(im, d, y, src, h, cap, centering=(.5, .5)):
    ph = ImageOps.fit(Image.open(O / src).convert("RGB"), (W - 2 * P, h), Image.LANCZOS, centering=centering)
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), 20, fill=255); im.paste(ph, (P, y), m)
    d.text((W - P, y + h + 16), cap, font=F("Medium", 22), fill=MU, anchor="ra")
    return y + h + 60

# 2장: 공항
im = base(); d = ImageDraw.Draw(im); y = head(d, "18일 밤 인천공항", "만삭 아내와 함께\n'홍콩발' 입국", y=90)
y = photo(im, d, y, "press04.jpg", 500, "사진: 스타뉴스", (.5, .35))
table(d, y, [("언제", "18일 밤 '9시 40분'쯤 입국장"), ("누구와", "20대 비연예인 '만삭' 아내"), ("한 말", "취재진에 \"'여기까지' 찍으시죠\"")])
d.text((W - P, H - 150), "스타뉴스·매일신문 보도", font=F("Medium", 22), fill=MU, anchor="ra")
logo(im); im.save(O / "c02.jpg", quality=93)

# 3장: 결혼 정보
im = base(); d = ImageDraw.Draw(im); y = head(d, "지금까지 알려진 것", "혼인신고 마쳤고\n'내년 1월' 아들 출산", y=90)
y = photo(im, d, y, "press03.jpg", 430, "사진: 스타뉴스", (.5, .3))
table(d, y, [("아내", "20대 '비연예인'"), ("혼인신고", "이미 '마친' 상태"), ("신혼집", "서울 '강남구'"), ("출산", "내년 '1월', 아들"), ("결혼식", "'아직' 계획 없음")], rh=78)
d.text((W - P, H - 150), "노컷뉴스·일간스포츠 보도", font=F("Medium", 22), fill=MU, anchor="ra")
logo(im); im.save(O / "c03.jpg", quality=93)

# 4장: 해명과 논란
im = base(); d = ImageDraw.Draw(im); y = head(d, "본인 해명과 남은 논란", "'혼전임신' 아니다,\n폭행 고소는 '부인'", y=110)
y += 20
blocks = [("혼전임신설 (10월 28일)", ["\"아내와 당연히 '법적으로 부부'\"", "\"임신해서 결혼한 건 '사실 아냐'\""]),
          ("식당 폭행 고소 (8월)", ["강남 식당서 '특수폭행' 혐의로 피소", "\"술병 들었지만 '위협' 안 했다\""]),
          ("버닝썬", ["2023년 2월 '만기 출소'", "징역 1년 6개월 복역"])]
for t, ls in blocks:
    hh = 70 + 56 * len(ls)
    d.rounded_rectangle((P, y, W - P, y + hh), 22, fill=BOX, outline=LN, width=2)
    d.text((P + 32, y + 22), t, font=F("SemiBold", 26), fill=MU)
    for i, l in enumerate(ls): rich(d, P + 32, y + 64 + 56 * i, l, F("ExtraBold", 33))
    y += hh + 22
d.text((W - P, y + 4), "일간스포츠·TV리포트 보도", font=F("Medium", 22), fill=MU, anchor="ra")
logo(im); im.save(O / "c04.jpg", quality=93)
