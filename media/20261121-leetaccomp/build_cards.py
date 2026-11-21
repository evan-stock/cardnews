"""20261121-leetaccomp: 리트 만점자 패러글라이딩 일화 거짓 의혹(커뮤니티 주장) + (패러글라이딩 중심으로 다시 만듦). leetjail/build_cards.py 복사.
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




frame(("본인이 밝혀온 '각성' 계기", "단양 '패러글라이딩' 안내문"),
      panel([("본인 설명", "친구들과 '3주 전국일주' 떠난 첫날 폰 분실"),
             ("그 뒤", "3주간 휴대전화 없이 '디지털 디톡스'"),
             ("충북 단양에서", "'패러글라이딩 안내문'을 읽다가"),
             ("본인 표현", "\"글이 '선명하게' 머릿속에 들어왔다\"")], h=640),
      "이 경험 뒤 성적이 '급상승'했다는 이야기", "주간경향(11.18)·생전 인터뷰").save(O / "c02.jpg", quality=93)
frame(("커뮤니티에 퍼진 주장", "\"패러글라이딩 일화도 '거짓'\""),
      panel([("인증 사진", "3주 여행인데 사진이 '한 장도 없다'"),
             ("휴대전화 분실", "증거가 안 남는 '설정' 아니냐"),
             ("처분 이력(보도)", "2022년 9월 공갈 등 '징역 6개월' 실형"),
             ("누리꾼 결론", "\"그 시기엔 '수감 중' 아니었나\"")], h=640),
      "본인 해명은 들을 수 없게 됐다", "온라인 커뮤니티 게시글 주장").save(O / "c03.jpg", quality=93)
frame(("날짜를 맞춰 보면", "일화 시기 '엇갈려'"),
      panel([("2022년 9월", "공갈 등 혐의 '징역 6개월' 선고(보도)"),
             ("2022년 말", "본인이 말했다는 '3주 전국일주' 시기"),
             ("2023년", "주간경향 보도 속 '도보 전국일주' 시기"),
             ("2023년 11월", "수능 응시, 뒤이어 '고려대 합격'")], h=640),
      "2022년 말이면 '수감 기간'과 겹칠 수 있다", "출소 시점은 '확인 안 돼'").save(O / "c04.jpg", quality=93)
fit(op("lee_photo.jpg"), W, H, (.5, .2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
