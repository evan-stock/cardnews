"""20261121-riemann: 앤트로픽 수학자 알푀게 'Claude와 리만가설 증명' 주장(11.20). 근거: PANews·체인캐처·크립토브리핑·MLQ·포위크MBA·사이언티픽 아메리칸 보도. 검증 전 '주장'으로만 쓴다."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p



# 표지 배경: 리만 초상(위키미디어, 퍼블릭 도메인)
fit(op(O / "press12.jpg"), W, H, (.5, .25)).save(O / "cover_bg.jpg", quality=95)

# 2장 무슨 일
frame(("11월 20일, 앤트로픽 수학자", "\"Claude와 함께 '증명'했다\""),
      fit(op(O / "alpoge.jpg"), 940, 640, (.62, .4)),
      "레벤트 알푀게, 개인 웹사이트에 '4쪽 메모'", "\"리만가설 증명을 발견했다고 믿는다\" · 일반화 리만가설까지").save(O / "c02.jpg", quality=93)

# 3장 리만가설이 뭐길래
frame(("리만가설이 뭐길래", "'160년' 넘게 아무도 못 풀었다"),
      panel([("제기", "1859년 독일 수학자 '리만'"),
             ("내용", "소수가 흩어진 방식에 숨은 '규칙'"),
             ("지위", "밀레니엄 7대 난제 · 상금 '100만 달러'"),
             ("연결", "인터넷 '암호'를 떠받치는 소수 이론")], h=640),
      "수학계 '최대 난제'로 꼽힌다", "클레이수학연구소").save(O / "c03.jpg", quality=93)

# 4장 왜 진지하게 보나
frame(("이번엔 왜 '진지하게' 보나", "논문 대신 '검사 가능한 코드'"),
      panel([("증명 방식", "컴퓨터가 한 줄씩 검사하는 'Lean'"),
             ("공개", "압축 파일 '14개'로 통째 공개"),
             ("이력", "7월 Claude로 '야코비안 추측' 반례"),
             ("본인 설명", "마지막 단계는 'Claude 기여'가 더 컸다")], h=640),
      "AI가 '증명의 주역'이 된 첫 사례?", "PANews·체인캐처·크립토브리핑 보도").save(O / "c04.jpg", quality=93)

# 5장 아직은 주장
frame(("하지만 아직은 '주장'", "확인해야 할 것들"),
      panel([("논문", "아직 '없음' · 단순화 후 쓸 계획"),
             ("외부 검증", "독립 검증 '아직 없음'"),
             ("핵심 쟁점", "코드 속 정리가 진짜 '리만가설'인가"),
             ("상금 조건", "학술지 게재 후 '2년' 학계 인정")], h=640),
      "검증되면 'AI 수학' 역사상 최대 사건", "사이언티픽 아메리칸·포위크MBA 보도").save(O / "c05.jpg", quality=93)
print("ok")
