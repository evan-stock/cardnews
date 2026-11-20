"""20261120-distrust: 세무냥이 사태가 남긴 불신(세무사 최연소·미트냥이·감평냥이 해명, 냥이 리스트). 리트냥이 제외(사용자 지시). 개인정보 가림."""
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

op = lambda n: Image.open(O / n).convert("RGB")


def cap(name, box, blur=(), mark=(), w=940, maxh=760):
    im = op(name)
    for b in blur:  # 이름·생년월일 등 가리기(원본 좌표)
        im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(14)), b[:2])
    im = im.crop(box)
    if mark:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
        for m in mark: dd.rectangle(m, fill=(255, 216, 77, 90))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    h = round(im.height * w / im.width)
    if h > maxh: im = im.crop((0, 0, im.width, round(maxh * im.width / w))); h = maxh
    return im.resize((w, h), Image.LANCZOS)


def mosaic(name, out, boxes, k=14):
    im = op(name)
    for b in boxes:
        r = im.crop(b); w, h = r.size
        im.paste(r.resize((max(1, w // k), max(1, h // k)), Image.NEAREST).resize((w, h), Image.NEAREST), b[:2])
    im.save(O / out, quality=95)


mosaic("press02.jpg", "press02m.jpg", [(855, 80, 975, 220), (36, 540, 132, 578)])  # 세무사 최연소 얼굴
mosaic("m1.jpg", "m1m.jpg", [(745, 140, 850, 270)])  # 미트냥이 얼굴


def stack(a, b, gap=16):
    im = Image.new("RGB", (940, a.height + gap + b.height), (10, 10, 12)); im.paste(a, (0, 0)); im.paste(b, (0, a.height + gap)); return im


# 냥이 리스트(리트냥이 줄 가림)
frame(("세무냥이 자수 뒤 온라인에 돈", "'고양이 목록'"),
      cap("press30.jpg", (0, 0, 689, 395), blur=[(0, 120, 689, 162)], mark=[(0, 162, 689, 200), (0, 238, 689, 276)]),
      "고득점·단기 합격만으로 '냥이' 딱지", "온라인 커뮤니티 게시물(더팩트 보도 갈무리)").save(O / "c02.jpg", quality=93)
# 세무사 최연소
frame(("세무사 최연소 합격자(21)는", "\"AI 안경 썼지?\" '악플'"),
      stack(cap("press02m.jpg", (0, 0, 1276, 715)), cap("press04.jpg", (0, 200, 1282, 560), maxh=200)),
      "공부한 교재 수십 권 들고 직접 '반박'", "518등·과락 겨우 면한 성적 · MBC 뉴스데스크 화면").save(O / "c03.jpg", quality=93)
# 미트냥이 1: 6년 성적 변화(이름·생년월일·수험번호 가림)
frame(("MDEET 전국 1등 '미트냥이'", "\"1년이 아니라 '6년' 준비했다\""),
      stack(cap("m2.jpg", (130, 800, 740, 1060), blur=[(135, 905, 560, 942)], maxh=340),
            cap("m6.jpg", (15, 320, 630, 560), blur=[(25, 400, 450, 436)], maxh=340)),
      "2020년 첫 시험(위) → 2025년 전국 1등(아래)", "본인 공개 MDEET 성적통지표 · 위키트리 보도(11.20)").save(O / "c04.jpg", quality=93)
# 미트냥이 2: '1년' 오해
frame(("'1년 만에 수석'은 어디서 나왔나", "\"강의 들은 기간이 '1년'\""),
      stack(cap("m9.jpg", (15, 40, 1075, 200), mark=[(0, 60, 1060, 160)]), cap("m1m.jpg", (0, 0, 910, 512), maxh=470)),
      "유튜브 촬영 때 강사와 의사소통 '오해'", "본인 공개 해명문 / 아래: 문제의 강의 영상").save(O / "c05.jpg", quality=93)
# 미트냥이 3: TEPS 때문에 두 번 탈락
frame(("MDEET 합격권 넘고도", "영어 410점에 1차 '두 번' 탈락"),
      cap("m3.jpg", (45, 75, 665, 570), maxh=620),
      "3년 영어만 파서 496점 → 2026년 치전원 입학", "본인 공개 TEPS 성적(2021년 촬영) · 해명문").save(O / "c06.jpg", quality=93)
# 미트냥이 4: 시험지 사진 + 해명 이유
frame(("시험 날 찍은 시험지 사진까지", "\"가족들까지 '상처'받아서\""),
      stack(stack(cap("m9.jpg", (15, 780, 1075, 880), mark=[(0, 0, 1060, 95)]), cap("m7.jpg", (27, 215, 663, 520), maxh=300)), cap("m7.jpg", (27, 945, 663, 1060), maxh=170)),
      "\"결코 어떤 시험도 부정한 방법으로 치지 않았다\"", "2025.8.11 촬영 기록 · 본인 공개 해명문").save(O / "c07.jpg", quality=93)
# 감평냥이 1: 학력
frame(("6개월 만에 붙은 이유", "서울대 학사·'도시계획' 석사"),
      cap("g5.jpg", (40, 1030, 920, 1590), mark=[(0, 26, 880, 196)]),
      "국토계획법·도시정비법 등 시험과 '겹치는' 전공", "본인 2차 해명문 중 '3. 베이스 관련'").save(O / "c08.jpg", quality=93)
# 감평냥이 2: 6개월 표현 사과
frame(("'6개월'이라는 표현은", "\"부적절했다\" 먼저 '사과'"),
      cap("g6.jpg", (40, 1150, 920, 1850), mark=[(0, 520, 880, 650)]),
      "\"이전 지식의 영향을 '간과'했다\"", "본인 2차 해명문 캡처").save(O / "c09.jpg", quality=93)
# 감평냥이 3: 공부 증거 공개
frame(("AI 커닝 의심엔", "공부한 '증거'로 답했다"),
      stack(cap("g2.jpg", (60, 1250, 880, 1392), maxh=220), cap("g4.jpg", (90, 250, 840, 1000), maxh=470)),
      "학원 수강 확인서·손으로 쓴 연습 답안 '공개'", "본인 2차 해명문 캡처").save(O / "c10.jpg", quality=93)
# 감평냥이 4: 마지막 말 + 공부 사진
frame(("해명문의 마지막 말", "\"정당한 노고가 '무시당하지' 않기를\""),
      stack(cap("g9.jpg", (40, 690, 920, 1000), mark=[(0, 196, 880, 292)]), cap("g8.jpg", (69, 900, 872, 1460), maxh=400)),
      "성적은 189명 중 150등, 부정행위 증거는 '없다'", "본인 2차 해명문 캡처 / 한국경제(11.18)").save(O / "c11.jpg", quality=93)
print("ok")

# 표지 후보: X=MBC 화면 / Z=해명 자료 4분할
_b = op("press30.jpg"); _b.paste(_b.crop((0, 120, 689, 162)).filter(ImageFilter.GaussianBlur(14)), (0, 120)); _b.save(O / "press30b.jpg", quality=95)
fit("press02.jpg", W, H, (.6, .5), crop=(380, 70, 1100, 545)).save(O / "cvX.jpg", quality=95)
q = [ImageOps.fit(op(n).crop(b), (540, 675), Image.LANCZOS) for n, b in
     [("press02.jpg", (640, 60, 1276, 560)), ("m6.jpg", (15, 440, 630, 560)), ("g8.jpg", (69, 900, 872, 1460)), ("press30b.jpg", (0, 0, 689, 300))]]
Z = Image.new("RGB", (W, H))
for i, t in enumerate(q): Z.paste(t, ((i % 2) * 540, (i // 2) * 675))
Z.save(O / "cvZ.jpg", quality=95)

for k, (n, c, cr) in {"P": ("press06.jpg", (.5, .5), None), "Q": ("press22.jpg", (.45, .5), (0, 0, 560, 335)),
                       "R": ("press24.jpg", (.5, .5), None), "T": ("press18.jpg", (.5, .5), None)}.items():
    fit(n, W, H, c, crop=cr).save(O / f"cv{k}.jpg", quality=95)


# 표지(2026.11.17 스토킹 표지 양식): 미트냥이 사진 크게 + 눈만 가림 + 해명문 캡처 카드 띄우기
def eyes(im, box, k=10):
    r = im.crop(box); w, h = r.size
    im.paste(r.resize((max(1, w // k), max(1, h // k)), Image.NEAREST).resize((w, h), Image.NEAREST), box[:2]); return im


def floatcard(base, img, x, y, w, ang, pad=14, rad=22):
    img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    c = Image.new("RGBA", (w + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), rad, fill=255)
    bg = Image.new("RGBA", c.size, (255, 255, 255, 255)); bg.paste(img, (pad, pad)); c.paste(bg, (0, 0), m)
    sh = Image.new("RGBA", (c.width + 80, c.height + 80), (0, 0, 0, 0))
    sm = Image.new("L", c.size, 0); ImageDraw.Draw(sm).rounded_rectangle((0, 0, c.width - 1, c.height - 1), rad, fill=150)
    sh.paste((0, 0, 0, 255), (40, 52), sm); sh = sh.filter(ImageFilter.GaussianBlur(18))
    sh.alpha_composite(c, (40, 40)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (x - 40, y - 40))


src = eyes(op("m1.jpg"), (754, 189, 846, 216), k=6)
person = src.crop((712, 70, 910, 512))
ph = H; pw = round(person.width * ph / person.height)
pimg = person.resize((pw, ph), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2)).convert("RGBA")
gm = Image.new("L", (pw, ph), 255); gd = ImageDraw.Draw(gm)
for x in range(220):  # 오른쪽 끝 220px 부드럽게 사라짐
    gd.line((pw - 220 + x, 0, pw - 220 + x, ph), fill=int(255 * (1 - x / 220)))
pimg.putalpha(gm)
cv = Image.new("RGBA", (W, H), (18, 18, 22, 255)); cv.alpha_composite(pimg, (-20, 0))
q1 = op("m9.jpg").crop((20, 281, 1000, 318))
q2 = op("g5.jpg").crop((40, 1030, 920, 1220))
ov = Image.new("RGBA", q2.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rectangle((0, 26, 880, 190), fill=(255, 216, 77, 110))
q2 = Image.alpha_composite(q2.convert("RGBA"), ov).convert("RGB")
floatcard(cv, q1, 400, 170, 640, 2)
floatcard(cv, q2, 440, 330, 590, -3)
cv.convert("RGB").save(O / "cover_bg.jpg", quality=95)
print("cover ok")
