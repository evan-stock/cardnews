"""20261117-ljm: 이재명 대통령 X 게시물(11.17 긴급대책 영상회의) 표지(lay one)+정리 카드 2장 캐러셀(1장 게시 불가) — 부정행위 신고 포상금 '1억 이상'.
게시물 원문에서 발췌(뜻 바꾸지 않음). 포상금은 '최대'가 아니라 '건당 1억원 이상, 인원수만큼 가산', 검토·도입 지시 단계."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(R / "scripts"))
from xpost_cards import W, H, P, FG, MU, YE, LN, BOX, F, wrap, rich, base, logo, head, avatar

im = base(); d = ImageDraw.Draw(im)
y = head(d, "11월 17일 · 이재명 대통령 X 게시물", "긴급대책 회의 뒤\n추가로 지시한 '3가지'", y=100)
x0, x1 = P, W - P; cx = x0 + 36; inner = x1 - x0 - 72
items = [
    ("① 신고 포상", "부정 '한 건당 1억원 이상'", "입시부정 인원수만큼 가산, 공동 부정 신고자는 처벌 감면"),
    ("② 재난문자", "최고등급 재난문자 '시험 중에도 수시로'", "소리를 줄이거나 차단해도 울린다"),
    ("③ AI 회사 기록", "시험 중 문제지 찍어 질문한 '모든 사례' 제공", "앞으로는 정부 요청 시 의무 제출 법률 추진"),
]
fh, fb, fs = F("SemiBold", 28), F("Black", 38), F("Medium", 28)
h = 36 + 68 + 26 + len(items) * 150 + 10
d.rounded_rectangle((x0, y, x1, y + h), 28, fill=BOX, outline=LN, width=3)
avatar(im, d, cx, y + 36, "이", (40, 90, 170))
d.text((cx + 88, y + 40), "이재명", font=F("Black", 30), fill=FG)
d.text((cx + 88, y + 78), "@Jaemyung_Lee · 첨단기술활용 입시부정 긴급대책 영상회의", font=F("Medium", 24), fill=MU)
ty = y + 36 + 68 + 30
for k, (lab, main, sub) in enumerate(items):
    if k: d.line((cx, ty - 22, x1 - 36, ty - 22), fill=LN, width=2)
    d.text((cx, ty), lab, font=fh, fill=MU); rich(d, cx, ty + 38, main, fb); d.text((cx, ty + 90), sub, font=fs, fill=(205, 205, 212))
    ty += 150
y += h + 40
for ln in ['"공연히 요행을 노리다가 \'인생 망치지 마시고\',', '본인이나 모두를 위해 포기하시기 바랍니다."']:
    rich(d, P, y, ln, F("Bold" if False else "SemiBold", 34)); y += 50
d.text((P, y + 14), "X 게시물 내용을 옮겨 구성 · 포상금은 '도입 검토 지시' 단계", font=F("Medium", 24), fill=MU)
logo(im); im.save(Path(__file__).parent / "cand" / "c02_rebuilt_unused.jpg", quality=93)  # 2장은 사용자 제공 트윗 캡처(cand/spec.json → scripts/post_cap_card.py); print("ok", y)
# 표지 배경(사용자 지정): 왼쪽 대통령 사진, 오른쪽 수능 D-7 학원 사진(뉴스1) 나란히, 경계 페이드. 아래는 글자 자리로 어둡게.
# D-7 사진 위쪽 '11월 12일(목)' 글씨는 이번 수능 날짜(19일)와 달라 잘라냄.
from PIL import ImageFilter, ImageOps
A = Image.open(Path(__file__).parent / "cand" / "user_photo3.jpg").convert("RGB")  # 2026-11-17 사용자 교체 사진(고화질)
B = Image.open(Path(__file__).parent / "cand" / "user_d7.jpg").convert("RGB").crop((0, 88, 300, 369))
TH = 950
A = ImageOps.fit(A, (620, TH), Image.LANCZOS, centering=(.5, 0)).filter(ImageFilter.UnsharpMask(2, 60, 2))
B = ImageOps.fit(B, (620, TH), Image.LANCZOS, centering=(.55, .5)).filter(ImageFilter.UnsharpMask(2, 60, 2))
L = Image.new("RGB", (W, TH)); L.paste(A, (0, 0)); Rr = Image.new("RGB", (W, TH)); Rr.paste(B, (W - 620, 0))
row = Image.new("L", (W, 1)); row.putdata([0 if x < 470 else 255 if x > 610 else int(255 * (x - 470) / 140) for x in range(W)])
top = Image.composite(Rr, L, row.resize((W, TH)))
OY = 0; bg = Image.new("RGB", (W, H), (14, 14, 16)); bg.paste(top, (0, OY))
g = Image.new("L", (W, 260)); g.putdata([int(255 * y / 259) for y in range(260) for _ in range(W)])
bg.paste(Image.new("RGB", (W, 260), (14, 14, 16)), (0, OY + TH - 260), g)
bg.save(Path(__file__).parent / "cand" / "cover_bg.jpg", quality=95)
