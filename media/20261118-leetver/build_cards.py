"""20261118-leetver: 내일 리트 만점자 수능 국어 공개 검증 방식(IDA 공식 공지 + 디일렉·MTN·이데일리·위키트리)."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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



# 4장 시험 조건
frame(("일반 수험생보다 '불리하게'", "15분 덜 받고, '11문항' 더 푼다"),
      panel([("일반 수험생", "80분 · 45문항"),
             ("리트 만점자", "'65분' · '56문항'"),
             ("문항", "공통 34 + 화작 11 + 언매 11 '전부'"),
             ("시험지", "평가원 공개 즉시 '현장 인쇄'")], h=640),
      "오전 11시 15분 시작 → 낮 12시 20분 종료", "IDA입시연구소 공지·이데일리(11.18)").save(O / "c04.jpg", quality=93)

# 5장 시험 중·후
frame(("시험 중에도, 끝나고도", "빠져나갈 '틈'이 없다"),
      panel([("화장실", "감독관 동행, 복귀하면 '재검사'"),
             ("자리 이탈", "시험 중 원칙적으로 '금지'"),
             ("시험 직후", "시험지 회수 · 탑뷰 영상과 '흔적 대조'"),
             ("마지막 관문", "강사가 3~5문항 골라 \"'왜 이 답?'\"")], h=640),
      "정답 근거·오답 제외 이유를 '직접' 설명해야", "IDA입시연구소 공식 공지").save(O / "c05.jpg", quality=93)

# 6장 한계
frame(("그런데 만점을 받아도", "'끝'이 아니다"),
      panel([("주관사 IDA", "과거 리트 의혹은 '확정 못 한다'"),
             ("신경외과 전문의", "내시경으론 체내 기기 '못 찾는다'"),
             ("수학 강사", "생중계는 '물타기'라는 주장"),
             ("전파탐지 업체", "즉시 중단 여부는 '협의' 사항")], h=640),
      "내일 증명하는 건 '오늘의 실력'뿐", "IDA 공지·위키트리·키자드·이데일리").save(O / "c06.jpg", quality=93)

spec = [
    {"out": str(O / "c02.jpg"), "sub": "IDA입시연구소 유튜브 공식 공지", "title": "수능 당일 '전 과정' 생중계\n내일 오전 8시",
     "cap": str(O / "yt_top.jpg"), "cap_crop": [95, 15, 695, 265], "caption": "IDA입시연구소 유튜브 커뮤니티 게시물 캡처",
     "label": "\"결백을 보증하는 자리가 아니다\"",
     "lines": ["주관사도 처음부터 선을 그었습니다.", "검사부터 채점·기자 질의까지 모두 공개합니다."]},
    {"out": str(O / "c03.jpg"), "sub": "공개 검증 진행 방식 ①", "title": "시험 전 검사만 '6단계'",
     "cap": str(O / "yt_step1.jpg"), "cap_crop": [140, 15, 640, 235], "cap_max_h": 520, "caption": "IDA입시연구소 공지 캡처",
     "label": "보안기업 전파탐지 장비까지 투입",
     "lines": ["무선 보안 기업 지슨이 탐지 장비 2종 설치", "주머니 없는 지정 복장 + 귀 내시경 검사"]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
bg = ImageEnhance.Brightness(op(O / "lee_photo.jpg")).enhance(0.95)
#fit(bg, W, H, (.5, .15)).save(O / "cover_bg.jpg", quality=95)
print("ok")
