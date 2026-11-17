"""20261117-check2(최종): 17일 오후 총리 대국민 담화 반영 — 응시 제한 10년·소급, 형사 고발, 입학 취소, 재난문자로 숨긴 폰 적발, 단추 스티커.
표지·CTA lay one + 2~6장 검은 바탕 틀(frame). 사진: 파이낸셜뉴스(담화)·세계일보(초소형 카메라)."""
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


frame(("17일 오후 총리 대국민 담화", "응시 제한 1년→'10년'"), fit(op("press06.jpg"), 940, 640, (.5, .35)),
      "올해 수능부터 '소급 적용' 추진", "\"바로 국회와 협의하겠다\"").save(O / "c02.jpg", quality=93)
frame(("시험 무효로 '안 끝난다'", "걸리면 이렇게 된다"),
      panel([("형사 고발", "위계에 의한 공무집행방해 '5년 이하 징역'"), ("이미 붙었다면", "'입학 취소'"), ("대학 재학 중 재수생", "'퇴학' 조치"), ("그 뒤로", "'10년'간 입학 금지(대교협 협의)")]),
      "끝나고 들켜도 '끝까지 추적'", "통신 기록으로 AI 접속 '사후 추적'").save(O / "c03.jpg", quality=93)
frame(("모레(19일) 시험장에서는", "이렇게 '검사'한다"),
      panel([("1교시 전", "모든 전자기기 '제출', 안 내면 부정행위"), ("시험 시작 전", "'재난문자' 보내 숨긴 휴대폰 적발"), ("안경·시계", "1교시 전 '전수 점검'"), ("옷 단추", "'스티커' 붙인다"), ("가방", "시험실 밖 '복도' 보관")], gap=118),
      "평소 쓰던 안경도 '점검 대상'", "총리 담화·정부 발표(11.17)").save(O / "c04.jpg", quality=93)
frame(("이런 걸 잡겠다는 것", "지퍼에 숨긴 '초소형 카메라'"), fit(op("cam.jpg"), 940, 640),
      "맨눈으로는 구분이 어렵다", "사진: 세계일보").save(O / "c05.jpg", quality=93)
frame(("정부가 동시에 하는 것", "'비상근무' 돌입"),
      panel([("감독관", "7만 5천여 명에 '8,400명' 추가"), ("청와대", "AI 부정행위 '비상대책 TF'"), ("네이버·당근", "AI 안경·카메라 '거래 관리'"), ("국가자격시험", "감시 예산 '182억' 증액 추진"), ("전파 차단", "법적·기술적 한계로 '안 한다'")], gap=118),
      "수능 '이틀 전' 나온 총력전", "JTBC·연합뉴스·파이낸셜뉴스(11.17)").save(O / "c06.jpg", quality=93)
fit(op("press06.jpg"), W, H, (.55, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
