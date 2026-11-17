"""20261117-jensenback: 2~6장 검은 바탕 frame 틀 (20261113-kress build_cards.py의 frame() 복사)."""
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

def frame(top, photo, bottom, body=(), src=None, focus=(.5, .5), ph=560):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    pw = 940; p = fit(photo, pw, ph, focus)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 88
    rich_center(d, y, bottom, F("Black", 46), YE); y += 66
    for ln in body:
        fs = 35
        while d.textlength(ln.replace("'", ""), font=F("Medium", fs)) > 960: fs -= 1
        rich_center(d, y, ln, F("Medium", fs), (235, 235, 240)); y += 50
    if src: rich_center(d, y + 10, src, F("Medium", 27), (150, 150, 158))
    logo(im); return im

frame(("젠슨 황을 끌어내린 '스파이설'", "트럼프도 \"스파이였는지 '모르겠다'\""), O / "alice.jpg",
      "백악관 자문 색스 \"스파이 의혹 무너지는 중\"",
      ["백악관 과학기술자문위 공동의장 색스는", "미 정보기관끼리도 판단이 엇갈린다고 했습니다.", "다만 FBI 수사는 아직 계속되고 있습니다."],
      "블록미디어·시대일보 11월 17일 · 사진: 젠슨 황과 앨리스 황", focus=(.5, .4)).save(O / "f02.jpg", quality=95)
frame(("애초에 앞뒤가 안 맞았다", "정작 중국은 엔비디아 칩 '막는 중'"), O / "chip.jpg",
      "H200 60만 개, 중국 승인 못 받아 홍콩에 묶여",
      ["중국은 작년 알리바바 등에 엔비디아 주문을", "취소하라고 명령했습니다. 칩을 막는 나라가", "칩 들여오려 '미인계'? 앞뒤가 반대입니다."],
      "로이터 11월 5일 · FT·블룸버그(2025년 9월)", focus=(.5, .35)).save(O / "f03.jpg", quality=95)
frame(("그러자 쏟아진 복귀론", "\"젠슨 돌려내라\" '18만 명' 서명"), O / "trump.jpg",
      "트럼프 \"복귀, 전혀 개의치 않는다\"",
      ["청원은 \"독립 조사 동안 젠슨을 복귀시키라\"고", "요구합니다. 머스크·팀 스위니가 서명했고, 대주주들은", "복귀를 포함한 '모든 선택지'를 검토하라고 했습니다."],
      "대만 타이베이101엔 'Taiwan Loves Jensen' 불빛 · 로이터·CNBC", focus=(.5, .3)).save(O / "f04.jpg", quality=95)
frame(("하지만 걸림돌 ①", "불륜은 '본인이 인정'했다"), O / "stern.jpg",
      "임원에게 '물병' 던졌다는 증언까지",
      ["올해 2월 임원 30여 명이 모인 회의에서 폭언하고", "고위 임원에게 물병을 던졌다는 참석자 증언입니다.", "사임 당일엔 사내 '세 번째' 여성 의혹도 나왔습니다."],
      "뉴욕포스트 11월 14일·로이터 11월 12일 · 황 측 논평 거부", focus=(.5, .3)).save(O / "f05.jpg", quality=95)
frame(("걸림돌 ② 결정권 쥔 이사회는", "\"젠슨 복귀 '검토 안 해'\""), O / "hq_old.jpg",
      "복귀 확률 18% → '7%' 뚝",
      ["예측시장 칼시의 복귀 확률은 한때 18%까지 올랐다가", "이사회 '검토 안 해' 보도 뒤 7%로 떨어졌습니다.", "FT는 이사회가 ARM CEO 르네 하스와 접촉했다고 보도했습니다."],
      "로이터·CNBC 11월 16일 · 파이낸셜뉴스(칼시) · FT", focus=(.5, .5)).save(O / "f06.jpg", quality=95)
print("ok")
