"""20261117-yundoyoung: 과학 강사 윤도영 AI 부정행위 입장 (수능 이틀 앞).
원본 헤더: 20261116-mimiminu: 미미미누 '수능 무조건 연기해야' (세무사 수석 AI 자수 후속).
표지·CTA lay one(렌더러) · 2~7장 검은 바탕 틀 / 캡처 카드."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
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


def fit(name, w=940, h=700, c=(.5, .5), crop=None):
    im = Image.open(O / name).convert("RGB")
    if crop: im = im.crop(crop)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=c)
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))



# ---------- 표지 배경 (유튜브 썸네일 오른쪽, 제목 글자 빼고) ----------
src = Image.open(O / "yt_thumb.jpg").convert("RGB").crop((784, 16, 1280, 636))
cov = src.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 80, 2))
cov = ImageEnhance.Contrast(cov).enhance(1.06)
cov.save(O / "cover_bg.jpg", quality=95)

# 2장: 영상 화면 캡처 (엑스에 올라온 유튜브 화면)
specs = [{"out": str(O / "c02.jpg"), "sub": "11월 16일 유튜브 '윤도영통합과학시스템'",
          "title": "\"솜방망이 처벌이면\n'기댓값이 양수'다\"", "cap": str(O / "xshot.jpg"),
          "cap_crop": [36, 10, 1284, 1075], "cap_max_h": 560, "box_bg": [255, 255, 255],
          "caption": "영상 화면 캡처 (엑스 @donstop4886 게시 · 조회 26만)", "label": "통합과학 강사 윤도영의 진단",
          "lines": ["도덕적 기준이 없다면 '시도 안 할 이유가 없다'", "\"과학 기술로 생긴 문제는 '과학 기술로' 막아야\""]}]
sp = Path("/tmp/yd_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 3장: 수능 연기론 (패널)
pw, ph = 940, 640
panel = Image.new("RGB", (pw, ph), (24, 24, 30)); d = ImageDraw.Draw(panel)
d.text((40, 36), "윤도영의 '수능 연기' 계산", font=F("Black", 36), fill=YE)
rows = [("1년 연기하면?", "\"대학 정원 '2배', 국민이 받아들일까\""),
        ("내년 3월 입학 거꾸로 세면", "아무리 늘려도 '최대 2주'"),
        ("그 이상 미루면", "3월 입학 자체가 '불가능'")]
y = 108
for a, b in rows:
    d.ellipse((44, y + 14, 56, y + 26), fill=YE); d.text((78, y), a, font=F("Medium", 30), fill=(190, 190, 200))
    rich(d, 78, y + 44, b, F("SemiBold", 36)); y += 128
d.line((40, y + 6, pw - 40, y + 6), fill=(60, 60, 70), width=2); y += 34
rich(d, 40, y, "\"일단 연기하고 대책은 나중에? '글쎄'\"", F("SemiBold", 34))
frame(("수능 연기론에 대한 답", "미룬다면 '확실한 방안'이 먼저"), panel,
      "\"연기는 대책을 위한 '시간'일 때만\"", sub="윤도영 16일 영상 · 이투데이 11.16 보도").save(O / "f03.jpg", quality=95)

# 4장: 정부 대책 직격 (썸네일 전체)
frame(("정부 대책을 향한 직격", "\"올해 수능은 대부분 '백지상태'\""), fit("yt_thumb.jpg", 940, 560),
      "대통령의 심각성 인식에 '의구심'", sub="\"국가 역량 집중, 말은 좋지만 '내년 수능' 기준\"").save(O / "f04.jpg", quality=95)

# 5장: 대통령에게 요구한 것 vs 교육부 (패널)
pw, ph = 940, 660
panel = Image.new("RGB", (pw, ph), (24, 24, 30)); d = ImageDraw.Draw(panel)
d.text((40, 36), "윤도영이 대통령에게 요구한 것", font=F("Black", 36), fill=YE)
rows = ["수능 당일 대책을 대통령이 '직접' 발표",
        "구속수사·'무관용' 엄벌 방침 선포",
        "공공기관 유휴 금속탐지기 '총동원'",
        "국회·법원도: 전파 관련 법, 솜방망이 처벌"]
y = 112
for r in rows:
    d.ellipse((44, y + 14, 56, y + 26), fill=YE); rich(d, 78, y, r, F("SemiBold", 33)); y += 66
d.line((40, y + 14, pw - 40, y + 14), fill=(60, 60, 70), width=2); y += 44
d.text((40, y), "같은 날 교육부 브리핑", font=F("Black", 32), fill=(200, 200, 208)); y += 54
rich(d, 40, y, "\"수능 연기는 '고려하지 않는다'\"", F("SemiBold", 34)); y += 56
rich(d, 40, y, "초소형 카메라 추가 대책은 17일 발표 예정", F("Medium", 30), (170, 170, 180))
frame(("\"불안을 잠재우기엔 '턱없이' 부족\"", "대통령이 '직접' 말하라"), panel,
      "수능까지 남은 시간은 '이틀'", sub="윤도영 16일 영상 · 교육부 16일 정례 브리핑").save(O / "f05.jpg", quality=95)

# 6장: 수험생에게
frame(("수험생에게 남긴 말", "\"중요한 시험은 '90%가 멘탈 싸움'\""), fit("exam_room.jpg", 940, 640, c=(.6, .5)),
      "\"차분히, 남은 시간 '최선'을\"", sub="사진: 2025.11.13 수능 고사장(사진공동취재단)").save(O / "f06.jpg", quality=95)
print("ok")
