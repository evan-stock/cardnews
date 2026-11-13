"""20261113-leetdiet: 다시 재조명되는 리트 만점자 식단 공부법. jensenout과 같은 검은 바탕 frame 틀(kress/build_cards.py 재사용).
사진: 우먼센스(인터뷰), 헤럴드경제(리트 시험장). 6·7장은 스레드·엑스 글을 우리 인용 카드로 다시 그림(캡처 아님)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; O = D / "cand"
src = (D.parent / "20261113-kress/build_cards.py").read_text().split("# 표지 배경")[0]
ns = {"__file__": str((D.parent / "20261113-kress/build_cards.py").resolve())}; exec(src, ns)
frame, F, fit, YE = ns["frame"], ns["F"], ns["fit"], ns["YE"]

def up(p, w, h, c=(.5, .5)):
    return fit(p, w, h, c).filter(ImageFilter.UnsharpMask(2, 50, 2))

def quote(acc, lines, foot, w=940):
    fb, fm, fs = F("SemiBold", 34), F("Medium", 38), F("Medium", 28)
    h = 70 + 60 * len(lines) + 90
    im = Image.new("RGB", (w, h), (247, 247, 249)); d = ImageDraw.Draw(im)
    d.ellipse((40, 30, 84, 74), fill=(200, 200, 208)); d.text((100, 64), acc, font=fb, fill=(20, 20, 24), anchor="ls")
    y = 140
    for ln in lines:
        d.text((40, y), ln, font=fm, fill=(30, 30, 34), anchor="ls"); y += 60
    d.text((40, h - 34), foot, font=fs, fill=(130, 130, 140), anchor="ls")
    return im

# 표지
up(O / "press04.jpg", 1080, 1350, (.5, .3)).save(O / "cover_bg.jpg", quality=95)

frame(("헤럴드경제 인터뷰 · 8월", "가장 먼저 끊은 건 '스크린'과 '정제 탄수화물'"), up(O / "press03.jpg", 940, 640, (.6, .4)),
      "\"덜어내면 2주 안에도 집중력이 달라진다\"", sub="공부법을 더하기 전에 방해 요소부터 줄였다는 설명").save(O / "c02.jpg", quality=95)

# 3장: 20·20·20·40 막대
g = Image.new("RGB", (940, 600), (22, 22, 26)); d = ImageDraw.Draw(g)
items = [("타고난 능력", 20), ("리트 훈련", 20), ("독해·추론 체계", 20), ("수면·식단·운동", 40)]
for i, (lab, v) in enumerate(items):
    y = 70 + i * 130; bw = int(430 * v / 40)
    d.text((40, y + 48), lab, font=F("SemiBold", 36), fill=(230, 230, 236), anchor="ls")
    d.rounded_rectangle((320, y, 320 + bw, y + 64), 14, fill=YE if v == 40 else (90, 90, 100))
    d.text((320 + bw + 20, y + 48), f"{v}%", font=F("Black", 44), fill=YE if v == 40 else (230, 230, 236), anchor="ls")
frame(("본인이 분석한 만점 비결", "타고난 머리는 '20%'뿐"), g,
      "나머지 40%는 '수면·식단·운동'", sub="본인 표현으로 '신체 및 인지 최적화' (헤럴드경제)").save(O / "c03.jpg", quality=95)

frame(("우먼센스 인터뷰 · 10월", "식후엔 '아이스크림', 밥은 '두 공기'"), up(O / "press01.jpg", 940, 640, (.5, .35)),
      "당을 줄이자 컨디션이 일정해졌다", sub="\"단 음식을 먹으면 기운이 올랐다가 금세 처졌다\"").save(O / "c04.jpg", quality=95)

frame(("7월 19일 리트 시험 당일 아침", "빈 고사장 계단을 '오르내렸다'"), up(O / "hall.jpg", 940, 640, (.5, .5)),
      "그리고 전 문항 정답, 19년 만의 첫 만점", sub="평소에도 집중이 떨어지면 숨찰 만큼 계단 (우먼센스)").save(O / "c05.jpg", quality=95)

frame(("공부법 책 「브레인 악셀」 독자 반응", "\"'AI와 대화하며' 정리한 책 같다\""),
      quote("스레드 독자 감상평", ["자신이 고민하고 궁금했던 문제를", "AI와 대화하며 쉽고 간단하게 정리한", "책이라는 인상을 받았다.", "", "뇌과학 설명은 나오지만, 자신의 인지가", "어떻게 바뀌었는지 분석은 전혀 없다."], "스레드 @memetaedu"),
      "1인 출판, 두 달 만에 누적 3만 부", sub="반면 '케토 식단과 비슷, 공감한다'는 독자도").save(O / "c06.jpg", quality=95)

frame(("세무사 수석 'AI 안경' 논란 뒤 엑스에선", "\"공부법이 '당 끊기, 계단'?\""),
      quote("엑스 이용자 글", ["원래 수능 7등급", "→ AI 안경 나온 26년 수능으로 서울대 치대", "→ 점수 향상 추세가 안경 성능 향상", "    추세랑 비슷함", "→ 공부법이 >당끊기,", "    계단 오르내리기<"], "X @itwillbe_sage · 11월 12일"),
      "그래서 19일, 수능 국어 생중계로 증명", sub="11시부터 80분, 편집 없이 원테이크 (본인 예고)").save(O / "c07.jpg", quality=95)
print("ok")
