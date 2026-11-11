"""20261112-taxglass 안쪽 장(2~7) 생성. 디자인 v2 색·글꼴. 사용: python build_cards.py [배경사진]"""
import sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R = Path(__file__).resolve().parents[2]; O = Path(__file__).parent / "cand"
W, H, P = 1080, 1350, 90
BG, FG, MU, YE, LN, BOX = (12,12,14), (255,255,255), (165,165,172), (255,216,77), (52,52,58), (30,30,34)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
BGIMG = sys.argv[1] if len(sys.argv) > 1 else None

def rich(d, x, y, text, font, base, anchor="ls"):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'") if hl else p
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor=anchor); x += d.textlength(p, font=font)
    return x

def base(sub, t):
    im = Image.new("RGB", (W, H), BG)
    if BGIMG:
        b = Image.open(BGIMG).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(18))
        im = ImageEnhance.Brightness(b).enhance(.15)
    d = ImageDraw.Draw(im); y = 160
    d.text((P, y), sub, font=F("SemiBold", 36), fill=YE, anchor="ls"); y += 30
    for ln in t.split("\n"):
        y += 92; rich(d, P, y, ln, F("Black", 76), FG)
    return im, d, y + 60

def body(d, lines, y=None):
    y = y or H - 150 - 50 * len(lines)
    for i, ln in enumerate(lines):
        rich(d, P, y + i * 50, ln, F("Medium", 34), (225, 225, 230))

def finish(im, name):
    logo = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); h = 40; w = int(logo.width * h / logo.height)
    logo = logo.resize((w, h), Image.LANCZOS); logo.putalpha(logo.split()[3].point(lambda v: int(v * .75)))
    im.paste(logo, ((W - w) // 2, H - 62 - h), logo); im.save(O / f"{name}.jpg", quality=95); print(name)

def bars(d, y, rows, maxv, unit="점", bw=470, gap=112):
    for lab, v, hl in rows:
        d.text((P, y + 40), lab, font=F("SemiBold", 34), fill=YE if hl else FG, anchor="ls")
        x0 = 320; L = max(6, int(bw * v / maxv))
        d.rounded_rectangle((x0, y, x0 + bw, y + 54), 10, fill=BOX)
        d.rounded_rectangle((x0, y, x0 + L, y + 54), 10, fill=YE if hl else (205, 205, 212))
        d.text((x0 + bw + 20, y + 42), f"{v:g}{unit}", font=F("Black", 44), fill=YE if hl else FG, anchor="ls")
        y += gap
    return y

# 2장: 수석 스펙
im, d, y = base("제63회 세무사 시험 수석은 누구", "대기업 엔지니어 출신\n'1·2차 동차 수석'")
y += 10
steps = [("1992년생", "만 34세"), ("대학", "서울과기대 기계공학과"), ("2012년~ 약 10년", "현대중공업 근무"),
         ("코로나 시기", "요식업 자영업 → 폐업"), ("2026년", "1·2차 '동차' 수석 합격")]
gap = 104
for i, (when, what) in enumerate(steps):
    yy = y + 40 + i * gap; last = i == len(steps) - 1; col = YE if last else FG
    d.ellipse((P, yy - 14, P + 28, yy + 14), fill=col)
    if not last: d.line((P + 14, yy + 18, P + 14, yy + gap - 18), fill=LN, width=4)
    d.text((P + 60, yy - 18), when, font=F("SemiBold", 28), fill=YE if last else MU, anchor="ls")
    rich(d, P + 60, yy + 32, what, F("Black", 44), col)
body(d, ["인터뷰에서 매일 새벽 3시 50분에 일어나", "백지 복습으로 공부했다고 밝혔습니다."])
finish(im, "c02a")

# 2장: 과목별 점수표
im, d, y = base("제63회 세무사 시험 수석 성적", "'AI 글라스' 사용\n의혹 논란"); y += 40
for title, rows in [("1차 · 객관식 (100점 만점)", [("재정학", "97.5", 0), ("세법학개론", "100", 0), ("회계학개론", "100", 0), ("상법", "100", 0)]),
                    ("2차 · 서술형 (100점 환산)", [("회계학1부", "96", 0), ("회계학2부", "95", 0), ("세법학2부", "83.5", 0), ("세법학1부", "57", 1)])]:
    d.text((P, y), title, font=F("SemiBold", 32), fill=MU, anchor="ls"); y += 22
    cw = (W - 2 * P) // 4
    for i, (lab, v, hl) in enumerate(rows):
        x = P + i * cw
        d.rounded_rectangle((x + 4, y, x + cw - 8, y + 150), 16, fill=(60, 52, 20) if hl else BOX, outline=YE if hl else None, width=3)
        d.text((x + cw // 2 - 2, y + 48), lab, font=F("Medium", 28), fill=YE if hl else MU, anchor="ms")
        d.text((x + cw // 2 - 2, y + 122), v, font=F("Black", 58), fill=YE if hl else FG, anchor="ms")
    y += 210
body(d, ["거의 만점인 과목들 사이에서 세법학1부만 낮은 점수가", "온라인에서 의심을 불렀습니다. 기기를 썼다는 근거나", "적발 사실은 확인되지 않았습니다."])
finish(im, "c02")

# 3장: 1차 세법 분포
im, d, y = base("1차 세법, 합격자 3,050명 중", "90점대 '0명',\n그런데 혼자 '100점'")
y += 30
for lab, v, hl in [("100점", "1명", 1), ("90점대", "0명", 0), ("80점대", "1명", 0)]:
    d.rounded_rectangle((P, y, W - P, y + 130), 18, fill=(60, 52, 20) if hl else BOX, outline=YE if hl else None, width=3)
    d.text((P + 40, y + 84), lab, font=F("SemiBold", 44), fill=YE if hl else FG, anchor="ls")
    d.text((W - P - 40, y + 90), v, font=F("Black", 72), fill=YE if hl else FG, anchor="rs")
    y += 155
d.text((P, y + 10), "※ 현직 세무사(@seedtax) 정리 기준", font=F("Medium", 28), fill=MU, anchor="ls")
body(d, ["80분에 두 과목 80문제, 문제당 1분꼴인 시험입니다.", "올해 세법은 응시자 '74%'가 과락한 '불시험'이었습니다."])
finish(im, "c03_old")

# 4장: 온라인 의심 논리
im, d, y = base("온라인이 의심하는 논리", "계산은 만점,\n'판례 서술'만 57점")
y += 40
bars(d, y, [("회계학1부", 96, 0), ("회계학2부", 95, 0), ("세법학2부", 83.5, 0), ("세법학1부", 57, 1)], 100)
body(d, ["\"AI가 잘 푸는 계산은 만점인데, 판례를 직접 써야 하는", "과목에서만 무너졌다\"는 주장입니다.", "점수만 보고 한 추측입니다."])
finish(im, "c04_old")

# 5장: 반대로 보면
im, d, y = base("반대로 보면", "57점도 작년 평균보다\n'23점' 높다")
y += 60
bars(d, y, [("작년 평균", 33.82, 0), ("수석", 57, 1)], 100, gap=130)
body(d, ["지난해(제62회) 세법학1부 평균은 33.82점,", "과락률은 65.62%였습니다.", "57점도 상위권 점수라는 반론이 나오는 이유입니다."])
finish(im, "c05")

# 6장: 현직 반응 (실제 댓글 캡처 3장)
im, d, y = base("현직 세무사들 반응 · 수석 합격자 블로그 댓글", "\"돈을 건다면,\n'사람이 할 수 없다'에\"")
y += 0
for f in ["cap_c1.png", "cap_c2.png", "cap_c3.png"]:
    c = Image.open(O / f).convert("RGB"); bw = 750; ch = round(c.height * bw / c.width)
    c = c.resize((bw, ch), Image.LANCZOS)
    m = Image.new("L", (bw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, bw - 1, ch - 1), 22, fill=255)
    im.paste(c, ((W - bw) // 2, y), m); y += ch + 16
print("c06 bottom", y)
finish(im, "c06")

# 7장: AI 안경 9건
im, d, y = base("남의 일이 아닌 이유", "AI 안경, 올해만\n'9건' 적발")
y += 30
for lab, v in [("국가기술자격시험", "5건"), ("중·고교 시험", "4건")]:
    d.rounded_rectangle((P, y, W - P, y + 130), 18, fill=BOX)
    d.text((P + 40, y + 84), lab, font=F("SemiBold", 44), fill=FG, anchor="ls")
    d.text((W - P - 40, y + 90), v, font=F("Black", 72), fill=YE, anchor="rs")
    y += 155
body(d, ["시험장은 여전히 감독관 눈에 의존합니다.", "산업인력공단은 스마트안경 전담 감독", "'AI 인스펙터' 도입을 예고했습니다."])
finish(im, "c07")
