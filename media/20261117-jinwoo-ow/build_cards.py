"""20261117-jinwoo-ow: 실명은 쓰지 않음(변호사 캡처 속 이름도 가림). 리트 만점자('리트냥이' 의혹), 공부법은 추상적인데 오버워치 해설은 '일타강사급' + 변호사 '풀이 대답' 조언.
여자 행세·주작·스토킹 등 확인 안 된 주장은 다루지 않음. 댓글 계정명·프로필은 가림, 본인 계정 여부는 '추정'으로만 씀.
표지 lay one(왼쪽 지금백지연 인터뷰 화면, 오른쪽 오버워치 2 정커퀸 공식 트레일러 화면) + 2~5장 검은 바탕 틀 + CTA.
"""
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



def contain(name, w=940, h=660, bg=(255, 255, 255), blur_boxes=(), crop=None):
    im = Image.open(O / name).convert("RGB")
    for b in blur_boxes:
        r = im.crop(b).filter(ImageFilter.GaussianBlur(14)); im.paste(r, b[:2])
    if crop: im = im.crop(crop)
    s = min((w - 40) / im.width, (h - 40) / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = Image.new("RGB", (w, h), bg); p.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return p


frame(("지금백지연 인터뷰에서 밝힌 만점 비결", "'생활 습관' 이야기"),
      panel([("비결로 꼽은 것", "'디지털 디톡스'·'설탕 끊기'·'걷기'"), ("본인 설명", "\"3주 동안 '완벽하게' 지켜졌다\""), ("다른 인터뷰", "도보 '전국일주' 뒤 \"다른 사람 됐다\"")], h=560),
      "온라인 반응: 공부법은 '추상적'", "영상: 유튜브 '지금백지연'·뉴시스(11.16)").save(O / "c02.jpg", quality=93)
frame(("본인 계정으로 '추정'되는 유튜브 댓글", "정커퀸 운영법은 '디테일'"), contain("cap_ow_raw.jpg", bg=(18, 18, 18), blur_boxes=[(60, 50, 490, 145)], crop=(66, 40, 1940, 1035)),
      "상대 동선·스킬 타이밍·'개선점'까지", "오버워치 영상 댓글 캡처(계정명 가림) · 본인 계정인지는 확인 안 됨").save(O / "c03.jpg", quality=93)
frame(("한 변호사가 스레드에 남긴 조언", "\"수능·LEET도 '풀이 대답'해야\""), contain("cap_lawyer.jpg", blur_boxes=[(305, 368, 535, 462)]),
      "\"판단 과정을 '직접' 보여준다면\"", "시험을 둘러싼 의혹에 답하는 데 도움이 될 수 있다는 것").save(O / "c04.jpg", quality=93)
frame(("지금까지 나온 의혹과 해명", "'목요일'에 풀이 공개"),
      panel([("MBC 보도", "언어이해 25~29번 답 '연달아 수정'"), ("처음 고른 답", "바로 앞 24~28번 정답과 '일치'"), ("본인 해명", "후반 집중력 저하로 '잔실수'"), ("예고", "19일(목) 수능 국어 '풀이 공개'")]),
      "부정행위는 '확인된 사실 아님'", "MBC(11.16)·TV리포트(11.17)").save(O / "c05.jpg", quality=93)
print("ok")
# 표지 배경(사용자 지정): 왼쪽 리트 만점자 프로필 사진(나무위키)(사용자 제공), 오른쪽 정커퀸 — 가운데 경계는 페이드
lee = Image.open(O / "lee_photo.jpg"); s = H / lee.height; lee = lee.resize((round(lee.width * s), H), Image.LANCZOS)
Lc = Image.new("RGB", (W, H), (235, 238, 242)); Lc.paste(lee, (round(330 - 480 * s), 0))
jq = ImageOps.fit(Image.open(O / "jq_hd.jpg").convert("RGB").crop((0, 0, 560, 720)), (620, H), Image.LANCZOS, centering=(.4, .3))  # 사용자 제공 고화질(오버워치 2 애니메이션 단편 썸네일), 로고 글자 빼고 자름
Rc = Image.new("RGB", (W, H)); Rc.paste(jq, (W - 620, 0))
row = Image.new("L", (W, 1)); row.putdata([0 if x < 500 else 255 if x > 680 else int(255 * (x - 500) / 180) for x in range(W)])
mask = row.resize((W, H))
Image.composite(Rc, Lc, mask).save(O / "cover_bg.jpg", quality=95)
