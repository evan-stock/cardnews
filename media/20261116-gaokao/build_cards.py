"""20261116-gaokao: 중국 가오카오 vs 한국 수능 AI 부정행위 대책 비교. 검은 바탕 틀(frame) + 비교표."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

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


def fit(src, w, h, focus=(.5, .5)):
    return ImageOps.fit(Image.open(src).convert("RGB"), (w, h), Image.LANCZOS, centering=focus)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)



def frame(top, photo, bottom, sub=None, focus=(.5, .5), ph=760):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    pw = 940; p = fit(photo, pw, ph, focus) if isinstance(photo, (str, Path)) else photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


S = R / "media/20261116-sage/cand"
ai = Image.open(O / "press10.jpg").convert("RGB").crop((200, 0, 1200, 640)); ai.save(O / "ai_cam.jpg", quality=95)
cv = Image.open(O / "press10.jpg").convert("RGB").crop((668, 0, 1188, 650)).resize((1080, 1350), Image.LANCZOS)
cv.save(O / "cover_ai.jpg", quality=95)
dr = Image.open(S / "url12.jpg").convert("RGB"); dr.crop((0, 626, 1179, 1406)).save(O / "drone.jpg", quality=95)

frame(("중국 대입 '가오카오' 시험실 카메라엔", "'AI 감독관'이 붙어 있다"), O / "ai_cam.jpg",
      "이상 행동 40가지, 0.5초 만에 경고", sub="두리번·귓속말·너무 빨리 답하기까지 잡는다 (후베이성)").save(O / "c02.jpg", quality=95)
frame(("시험장 들어가기 전엔", "'안경'까지 벗어 영상 앞에서 검사"), O / "press05.jpg",
      "스마트 보안문 + 금속탐지 '무음 입장'", sub="광둥성은 안경 쓴 수험생 전원 · 허난성 보안문 (2026)",
      focus=(.1, .5)).save(O / "c03.jpg", quality=95)
frame(("시험장 위 하늘엔", "전파 잡는 '드론'까지 띄웠다"), O / "drone.jpg",
      "500m 상공에서 무선 신호 추적", sub="2015년 허난성 뤄양 · 지금은 전 시험장 전파 차단").save(O / "c04.jpg", quality=95)

rows = [("응시 인원", "1,290만 명", "55만 명"),
        ("안경 검사", "전원, 영상 앞에서", "의심될 때만"),
        ("입장 검색", "스마트 보안문", "복도 금속탐지기"),
        ("전파", "전 시험장 차단", "탐지기 없음"),
        ("시험 중 감시", "AI 카메라", "감독관 '눈'")]
tb = Image.new("RGB", (940, 760), (24, 24, 28)); d = ImageDraw.Draw(tb)
cx = (165, 460, 785)
d.rectangle((0, 0, 940, 110), fill=(40, 40, 46))
for x, h, c in zip(cx, ("", "중국 가오카오", "한국 수능"), (FG, FG, YE)):
    d.text((x, 55), h, font=F("Black", 42), fill=c, anchor="mm")
for i, (a, b, c) in enumerate(rows):
    y = 110 + i * 130 + 65
    if i: d.line((30, y - 65, 910, y - 65), fill=(62, 62, 70), width=2)
    d.text((cx[0], y), a, font=F("Medium", 36), fill=(170, 170, 180), anchor="mm")
    d.text((cx[1], y), b, font=F("Black", 38), fill=FG, anchor="mm")
    d.text((cx[2], y), c.replace("'", ""), font=F("Black", 38), fill=YE, anchor="mm")
frame(("같은 'AI 커닝' 걱정인데", "대책은 이만큼 다르다"), tb,
      "한국 전파탐지기는 '내년부터 검토'", sub="중국 2026 가오카오 / 한국 2027학년도 수능 교육부 대책").save(O / "c05.jpg", quality=95)
fit(O / "cover_ai.jpg", 1080, 1350).save(O / "cta_bg.jpg", quality=95)
print("ok")


# ===== v2: 엑스 글타래 흐름대로 재구성 =====
def panel(rows, title=None, h=760, num=False, fs=40):
    tb = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(tb); y0 = 0
    if title:
        d.rectangle((0, 0, 940, 100), fill=(40, 40, 46)); d.text((470, 50), title, font=F("Black", 40), fill=YE, anchor="mm"); y0 = 100
    rh = (h - y0) / len(rows)
    for i, r in enumerate(rows):
        y = y0 + rh * i + rh / 2
        if i: d.line((40, y - rh / 2, 900, y - rh / 2), fill=(62, 62, 70), width=2)
        if isinstance(r, tuple):
            d.text((60, y), r[0], font=F("Black", fs), fill=YE, anchor="lm")
            d.text((880, y), r[1], font=F("Medium", fs - 4), fill=FG, anchor="rm")
        else:
            d.text((60, y), r.replace("'", ""), font=F("Black", fs), fill=FG, anchor="lm")
    return tb


# 표지 배경: 자수 영상 장면 세로 크롭(자막 포함)
fit(O / "yt_fool.jpg", 1080, 1350, (.5, .5)).save(O / "cover_ys.jpg", quality=95)

frame(("세무사 수석이 자백한 방법은", "'AI 안경'이 아니었다"), O / "yt_fool.jpg",
      "초소형 카메라 → AI → 스마트폰으로 답 확인", sub="감독관 4명 \"특이사항 없었다\" · 공인회계사 1차도 같은 방식",
      focus=(.5, .45)).save(O / "v2_02.jpg", quality=95)

frame(("부정행위의 핵심은", "'세 가지' 조합이다"),
      panel(["① 문제를 찍는 '카메라'", "② 답을 내는 'AI'", "③ 답을 받는 '장치'"], fs=50),
      "안경은 그중 '하나'일 뿐", sub="장비값이 싸지면서 개인도 쉽게 갖추게 됐다는 지적").save(O / "v2_03.jpg", quality=95)

frame(("올해 국내에서만", "이만큼 '걸렸다'"),
      panel([("토익", "스마트안경 · 4년 응시 제한"), ("소방설비·전기산업기사", "AI 안경 착용 적발"),
             ("가스기능사", "AI 안경 착용 확인"), ("연세대·서울시립대 논술", "스마트안경 적발"),
             ("중·고교 내신", "스마트안경 4건"), ("세무사·회계사", "카메라+AI, 본인 자수")], fs=36),
      "그럼 '안 걸린' 사람은 몇 명일까", sub="2026년 5~11월 보도 기준").save(O / "v2_04.jpg", quality=95)

frame(("\"전파만 끊으면 되잖아?\"", "한국에선 '안 된다'"),
      panel(["전파는 사방으로 퍼져 시험장만 못 끊는다", "전파법상 안보 상황 아니면 차단 금지",
             "2004년 수능 휴대폰 부정 뒤에도 '무산'"], fs=38),
      "인도는 인터넷 끊었더니 '블루투스 슬리퍼'", sub="2021 라자스탄 교사시험 · 한 켤레 60만 루피에 팔렸다").save(O / "v2_05.jpg", quality=95)

frame(("시험장 하늘엔 전파 잡는 '드론',", "입구엔 '스마트 보안문'"), O / "drone.jpg",
      "중국은 전 시험장 전파 차단", sub="2015 허난성 뤄양 드론 · 2026 광둥성 안경 전원 검사").save(O / "v2_07.jpg", quality=95)

frame(("시험 시간엔", "중국 AI도 '문제 풀이'를 멈춘다"), O / "press11.jpg",
      "\"시험 기간 문답 기능 일시 중단\"", sub="더우바오·위안바오 등 · 시험 시간에만 문제 촬영·풀이 차단").save(O / "v2_08.jpg", quality=95)
print("v2 ok")
