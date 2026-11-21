"""20261121-leetaccomp: 리트 만점자 패러글라이딩 일화 거짓 의혹(커뮤니티 주장) + 공범·외부 조력 의혹(경찰 수사·고발인). leetjail/build_cards.py 복사.
원래: 20261119-leetjail(속보): JTBC(11.19 09:08) 리트 만점자 구치소 수감 재소자 증언·개명 전 이름·생년월일 일치 공갈 판결문. 실명·개명 전 이름 안 씀.
근거: 사용자 제공 JTBC 기사 캡처(제목·요약·첫 문단). 따옴표는 기사에 실린 증언만. sidae/build_cards.py 복사."""
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






fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda n: Image.open(O / n).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




yt = op("press01.jpg").crop((560, 20, 1280, 430))  # 초소형 카메라 부분만(로고·자막 빼고)
frame(("숨졌지만 수사는 계속", "남은 의문 '공범 있었나'"), fit(yt, 940, 560, (.5, .5)),
      "경찰, 외부 조력자·공범 여부 '수사 중'", "사진: 초소형 카메라(YTN 화면)").save(O / "c02.jpg", quality=93)
frame(("커뮤니티에 퍼진 주장", "\"패러글라이딩 일화도 '거짓'\""),
      panel([("본인이 밝혀온 각성 계기", "전국일주 중 '단양 패러글라이딩' 안내문"),
             ("본인 설명", "\"글이 '선명하게' 머릿속에 들어왔다\""),
             ("누리꾼 주장", "인증 사진 '0장', 첫날 폰 분실 설정도 의문"),
             ("보도된 처분 이력", "2022년 9월 공갈 등 '징역 6개월' 실형")], h=640),
      "\"그 시기엔 '수감 중' 아니었나\"", "일화 시기 2022년 말(본인 언급 전언)·2023년(주간경향) 엇갈림").save(O / "c03.jpg", quality=93)
frame(("공범 의혹 근거로 거론되는 것", "리트 답 '한 칸씩 밀림'"),
      panel([("리트 25~29번", "지운 답이 '바로 앞 문항 정답'과 일치"),
             ("제기된 의혹", "불러준 답을 '밀려 받아 적은' 것 아니냐"),
             ("2023년 수능 당시", "생성형 AI 정답률 '지금보다 낮아'"),
             ("경찰 판단", "외부 조력자 개입 '배제 안 해'")], h=640),
      "본인은 생전 의혹 '부인'", "파이낸셜뉴스·주간경향(11.18~20)").save(O / "c04.jpg", quality=93)
frame(("'공소권 없음'으로 끝날까", "경찰 \"실체 규명 계속\""),
      panel([("광역수사단 금융범죄수사대", "\"사망에도 '수사 계속'\""),
             ("증거", "2026학년도 수능 시험지 '증거보전'"),
             ("고발인 변호사", "종결되면 '성명불상 공범' 추가 고발"),
             ("부검 결과", "타살 정황 '없어'")], h=640),
      "공범 존재 여부는 '아직 확인 안 돼'", "네이트·파이낸셜뉴스(11.19~20)").save(O / "c05.jpg", quality=93)
fit(op("lee_photo.jpg"), W, H, (.5, .2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
