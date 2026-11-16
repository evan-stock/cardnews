"""20261116-mimiminu: 미미미누 '수능 무조건 연기해야' (세무사 수석 AI 자수 후속).
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


# ---------- 표지 배경 (영상 캡처, 자막 위까지) ----------
src = Image.open(O / "yt_thumb.jpg").convert("RGB").crop((367, 40, 911, 720))
cov = src.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 80, 2))
cov = ImageEnhance.Contrast(cov).enhance(1.08)
cov.save(O / "cover_bg.jpg", quality=95)

# 2장: 미미미누 영상
frame(("수능 사흘 앞두고 올라온 영상", "\"수험생·학부모 '불안감에 떨고 있다'\""), fit("press03.jpg", 940, 640, crop=(60, 0, 1000, 600), c=(.5, .3)),
      "\"월요일까지 '구체적 대책' 내놔라\"", sub="유튜브 미미미누 15일 라이브·16일 영상").save(O / "f02.jpg", quality=95)

# 3장: 발단
frame(("발단은 세무사 시험 '수석' 합격자", "\"초소형 카메라+AI로 풀었다\" 자수"), fit("press35.jpg", 940, 640, crop=(180, 40, 1180, 720)),
      "감독관 '바로 앞자리'에서도 못 잡았다", sub="11월 15일 유튜브 이돈호 변호사 채널 영상").save(O / "f03.jpg", quality=95)

# 4장: 수법
frame(("미미미누가 짚은 수법", "\"단추·팔찌에 달면 'AI가 푼다'\""), fit("press17.jpg", 940, 705),
      "\"지금은 AI 안경을 '아득히' 넘어섰다\"", sub="15일 라이브 · \"기출문제는 단시간에 정답\"").save(O / "f04.jpg", quality=95)

# 5장: 정부 대책 vs 사흘 (패널)
pw, ph = 940, 620
panel = Image.new("RGB", (pw, ph), (24, 24, 30)); d = ImageDraw.Draw(panel)
d.text((40, 36), "정부가 15일 내놓은 수능 대책", font=F("Black", 36), fill=YE)
rows = ["시험장 1,312곳마다 'AI 기기 판단' 전담 인력",
        "전체 수험생 대상 AI 기기 점검 절차",
        "감독관·수험생 교육 강화",
        "휴대폰·스마트안경·스마트워치·블루투스 이어폰 반입 금지"]
y = 112
for r in rows:
    d.ellipse((44, y + 14, 56, y + 26), fill=YE); rich(d, 78, y, r, F("SemiBold", 33)); y += 66
d.line((40, y + 14, pw - 40, y + 14), fill=(60, 60, 70), width=2); y += 44
d.text((40, y), "미미미누의 질문", font=F("Black", 32), fill=(200, 200, 208)); y += 54
rich(d, 40, y, "\"수능까지 '사흘'인데, 교육이 현실적으로 되나\"", F("SemiBold", 34))
y += 56
rich(d, 40, y, "귓속 초소형 이어폰·단추 카메라는 '눈으로' 잡기 어렵다", F("Medium", 30), (170, 170, 180))
frame(("남은 시간은 단 '사흘'", "대책은 결국 '사람 눈'"), panel,
      "\"하루 전에라도 미룰 수 있다\"", sub="미미미누 15일 라이브 · 정부 대책은 청와대 긴급회의 발표").save(O / "f05.jpg", quality=95)

# 6장: 평가원 게시판 (캡처 카드)
specs = [{"out": str(O / "c06.jpg"), "sub": "한국교육과정평가원 '수능 묻고 답하기' 게시판 · 11월 16일",
          "title": "\"수능 연기 아니면\n'인터넷을 끊어주세요'\"", "cap": str(O / "press34.jpg"),
          "cap_crop": [0, 0, 1200, 678], "cap_max_h": 470, "box_bg": [255, 255, 255],
          "caption": "평가원 게시판 캡처 (16일 오전, 작성자 가림)", "label": "16일 하루 게시판",
          "lines": ["\"일주일이든, 이주일이든, 한 달이든 어떻게든\"", "제목마다 '연기'와 '대책'이 줄줄이 올라왔습니다"]}]
sp = Path("/tmp/mm_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 7장: 전례
frame(("실제로 미룬 적 있다", "2017년 포항 지진, 수능 '하루 전' 1주일 연기"), fit("press28.jpg", 940, 640),
      "2020년엔 코로나로 '2주' 미뤄 12월에", sub="사진: 2017년 연기 발표 다음 날, 버린 문제집 다시 찾는 수험생").save(O / "f07.jpg", quality=95)
print("ok")
