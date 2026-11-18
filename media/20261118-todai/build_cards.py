"""20261118-todai: 도쿄대 의대(理三) 모의고사 1등 한국인 수험생 jocho — 부정·AI 의심 → 실력이었다(반전형).
근거: 엑스 원글(@poongkawaii 11.18), 일본 수험생 엑스(@mogami_effort 실전 348/440, @Action_4everl 본레 3위 334, @ippou_sonokorou 부정 의심 반론),
jocho 공개 답안. 일반인이라 닉네임만, 실명·얼굴 안 씀."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; V = D / "video"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p


def bars(h=640):
    """우리 편집 장: 만점 440 기준 평균·전국 3위·jocho 막대."""
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p)
    d.text((56, 40), "도신 10월 도쿄대 본시험레벨 모의고사 · 이과 · 440점 만점", font=F("Medium", 28), fill=(190, 190, 198))
    rows = [("응시자 평균", 177.1, (110, 110, 118)), ("전국 3위", 334, (170, 170, 178)), ("jocho", 401, YE)]
    x0, x1 = 56, 884
    for i, (k, v, c) in enumerate(rows):
        y = 130 + i * 160
        d.text((x0, y), k, font=F("Black", 40), fill=YE if k == "jocho" else FG)
        d.rounded_rectangle((x0, y + 62, x1, y + 112), 12, fill=(40, 40, 46))
        d.rounded_rectangle((x0, y + 62, x0 + (x1 - x0) * v / 440, y + 112), 12, fill=c)
        s = f"{v:g}점"; tw = d.textlength(s, font=F("Black", 40))
        d.text((x1 - tw, y), s, font=F("Black", 40), fill=YE if k == "jocho" else FG)
    return p


# 2장: 손글씨 답안
ans = op(V / "p1_4.jpg")
frame(("2007년생 한국인 수험생 'jocho'", "도쿄대 의대 모의고사 '연속 1등'"),
      fit(ans, 940, 700, (.5, .18)),
      "고친 흔적 하나 없는 '손글씨 답안'", "jocho가 엑스에 공개한 모의고사 답안").save(O / "c02.jpg", quality=93)

# 3장: 성적 정리
frame(("일본 대형 입시학원 도쿄대 모의고사", "나가는 시험마다 '1위'"),
      panel([("8월 · 순다이 도쿄대 실전 모의고사", "전국 '1위' · 348점 / 440"),
             ("8월 · 가와이주쿠 도쿄대 입시 오픈", "한·중·일 1등 경쟁 '최상위'"),
             ("10월 · 도신 도쿄대 본시험레벨", "'401점' / 440"),
             ], h=640, gap=190),
      "외국인이 '리산' 모의고사를 휩쓸었다", "일본 수험생 엑스 게시물 종합").save(O / "c03.jpg", quality=93)

# 막대 비교(미사용)
frame(("같은 시험, 전국 3위가 334점", "1등과 '67점' 차이"),
      bars(640),
      "3위 수험생: \"jocho와의 차이는 '가늠이 안 된다'\"", "전국 3위 수험생이 공개한 성적표 기준(@Action_4everl)").save(O / "c04.jpg", quality=93)

# 5장·6장: 캡처 카드
spec = [
    {"out": str(O / "c05.jpg"), "sub": "10월 20일 · 일본 수험생 엑스", "title": "\"401점은 '부정' 아니냐\"\n돌아온 반론은…",
     "cap": str(O / "cap_fusei.jpg"), "cap_crop": [40, 20, 770, 420], "caption": "@ippou_sonokorou 게시물 캡처(엑스 자동 번역)",
     "label": "\"부정해도 이런 점수는 못 받는다\"",
     "lines": ["의심이 나오자 일본 수험생들이 먼저 '반박'했습니다.", "그의 공개 답안을 따라 쓰며 공부한다는 글까지."]},
    {"out": str(O / "c06.jpg"), "sub": "10월 19일 · 전국 3위 수험생 성적표", "title": "만점 440점, 평균 177점\n3위가 '334점'",
     "cap": str(O / "cap_3rd.jpg"), "cap_crop": [0, 315, 800, 545], "caption": "도신 도쿄대 본시험레벨 모의고사 성적표 캡처(@Action_4everl)",
     "label": "jocho는 같은 시험 '401점'",
     "lines": ["2,200명이 본 시험에서 3위와도 67점 차이입니다."]},
    {"out": str(O / "c08.jpg"), "sub": "11월 18일 · 국내 엑스 반응", "title": "한국은 '반반'\n\"혹시 챗GPT??\"",
     "cap": str(O / "cap_kr.jpg"), "caption": "엑스 인용 게시물 캡처(실명 가림)",
     "label": "세무냥이·리트냥이 이어 \"도쿄냥이\"?",
     "lines": ["\"AI가 풀이 과정까지 서술형으로 써?\" 반문도 나왔습니다."]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)

# 7장: 왜 '진짜'인가 — 시험 방식
frame(("AI·커닝으로 안 되는 이유", "도쿄대 2차 시험은 '전부 서술형'"),
      panel([("수학", "150분 동안 단 '6문제'"),
             ("채점", "정답보다 '풀이 과정'"),
             ("답만 맞히면", "과정이 부실하면 '감점'"),
             ("jocho 답안", "빈칸 없이 '끝까지' 채웠다")], h=640),
      "답을 외워선 못 받는 점수", "본시험은 내년 2월 말").save(O / "c07.jpg", quality=93)

# 표지 배경: 손글씨 답안(어둡게는 렌더러가)
bg = op(V / "p1_3.jpg")
bg = ImageEnhance.Brightness(ImageEnhance.Contrast(bg).enhance(1.15)).enhance(0.8)
fit(bg, W, H, (.5, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
