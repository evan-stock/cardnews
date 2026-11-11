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


def rows(d, y, items, hl_last=False):
    for i, (lab, v) in enumerate(items):
        hl = hl_last and i == len(items) - 1
        d.rounded_rectangle((P, y, W - P, y + 120), 18, fill=(60, 52, 20) if hl else BOX, outline=YE if hl else None, width=3)
        d.text((P + 36, y + 76), lab, font=F("SemiBold", 38), fill=YE if hl else FG, anchor="ls")
        d.text((W - P - 36, y + 80), v, font=F("Black", 56), fill=YE if hl else FG, anchor="rs")
        y += 140
    return y

def quote(d, y, lines, who):
    d.rounded_rectangle((P, y, W - P, y + 90 + 64 * len(lines)), 22, fill=BOX)
    d.rectangle((P, y, P + 8, y + 90 + 64 * len(lines)), fill=YE)
    for j, ln in enumerate(lines):
        rich(d, P + 44, y + 78 + j * 64, ln, F("Black", 50), FG)
    d.text((P + 44, y + 78 + len(lines) * 64), who, font=F("Medium", 28), fill=MU, anchor="ls")

# 2장
im, d, y = base("뉴욕타임스 · 2026.11.11 보도", "직속 부하 임원과\n'두 번째' 불륜")
y += 30
rows(d, y, [("상대", "킴벌리 파월(48)"), ("직책", "헬스케어 부사장"), ("관계", "젠슨 황 '직속'"), ("근거", "전·현직 직원 5명")])
body(d, ["엔비디아·젠슨 황·파월 모두 사실을 확인하지 않았습니다.", "앞서 중국 스파이 의심 인물과의 불륜은 본인이 인정했습니다."])
finish(im, "c02")

# 3장
im, d, y = base("3월 GTC 기간 · 산호세 호텔", "애정 표현 찍히자\n경호팀이 '격리'")
y += 30
steps = [("목격", "두 사람의 애정 표현을 휴대전화로 촬영"), ("격리", "경호팀이 촬영한 사람을 따로 분리"), ("제안", "'비밀유지계약(NDA)' 서명 제안")]
for i, (k, v) in enumerate(steps):
    yy = y + 40 + i * 120; last = i == len(steps) - 1; col = YE if last else FG
    d.ellipse((P, yy - 14, P + 28, yy + 14), fill=col)
    if not last: d.line((P + 14, yy + 18, P + 14, yy + 102), fill=LN, width=4)
    d.text((P + 60, yy - 18), k, font=F("SemiBold", 28), fill=YE if last else MU, anchor="ls")
    rich(d, P + 60, yy + 32, v, F("Black", 40), col)
body(d, ["보고받은 관계자 3명의 말을 NYT가 전했습니다.", "다만 NYT는 영상 자체는 검증하지 못했다고 밝혔습니다."])
finish(im, "c03")

# 4장
im, d, y = base("NYT가 전화로 묻자", "젠슨 황은\n전화를 '끊었다'")
y += 40
quote(d, y, ["\"저와 직접 얘기하시면", "안 될 것 같네요\""], "젠슨 황, NYT 통화에서 (뉴욕타임스 보도)")
body(d, ["엔비디아는 입장을 내지 않았고,", "파월 부사장은 바로 응답하지 않았습니다."])
finish(im, "c04")

# 5장
im, d, y = base("킴벌리 파월은 누구", "2008년 입사,\n의료 AI 이끄는 '부사장'")
y += 30
rows(d, y, [("입사", "2008년"), ("직책", "헬스케어 부사장"), ("보고 라인", "CEO 직속")])
body(d, ["한 전직 직원은 CNBC에 \"보건·과학 배경이 없어", "두 사람 관계 소문이 수년간 돌았다\"고 말했습니다."])
finish(im, "c05")

# 6장
im, d, y = base("월스트리트저널 · 같은 날 몇 분 뒤", "이사회, 젠슨 황\n'해임' 준비")
y += 40
quote(d, y, ["\"이사회가 젠슨 황을", "'내보낼' 준비를 하고 있다\""], "월스트리트저널, 소식통 인용")
body(d, ["두 번의 불륜(그중 하나는 중국 스파이 의심 인물)이 이유입니다.", "이사회는 이르면 현지시간 11일 회의를 열어 거취를 정합니다."])
finish(im, "c06")

# 7장
im, d, y = base("시장 반응 · 11일(현지)", "시간외 '8%' 급락,\n52주 최저")
y += 30
rows(d, y, [("정규장 종가", "173.73달러 (+2.9%)"), ("시간외", "159.59달러 (-8.1%)"), ("불륜 보도 후 1주", "-13% 넘게")], hl_last=True)
body(d, ["같은 시간 AMD는 3.75%, 브로드컴은 2.7% 올랐습니다."])
finish(im, "c07")
