"""20261119-sunungcheat: 2027 수능 부정행위 총정리(재난문자 35명·용인 초소형카메라·서초 깔창폰). 교육부·제주의소리·뉴스1·SBS·MBC·싱글리스트(11.19)."""
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


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p


PH = json.loads((D / "photos.json").read_text()) if (D / "photos.json").exists() else {}


def ph(key, h, rows):
    """사진이 있으면 사진, 없으면 정리 상자."""
    if key in PH:
        name, c = PH[key]["f"], tuple(PH[key].get("c", (.5, .5)))
        return fit(name, 940, h, c)
    return panel(rows, h=h)


frame(("수능 사상 첫 '위급재난문자'", "폰 숨긴 수험생 '35명' 걸렸다"),
      panel([("1차 · 오전 8시 30분 (시험 직전)", "'22명' 적발 · 9개 시·도"),
             ("2차 · 오후 2시 21분 (3교시 직후)", "'10명' 추가 적발"),
             ("3차 · 오후 2시 57분 (한국사 시험 중)", "'3명' 또 걸렸다"),
             ("원리", "전원 '켜진' 폰만 경보음이 울린다")], h=640),
      "올해부터 '갖고만 있어도' 부정행위", "교육부 발표·제주의소리(11.19)").save(O / "c02.jpg", quality=93)

frame(("용인 시험장, 재수생 소지품에서", "'초소형 카메라'·이어폰 나왔다"),
      ph("yongin", 640, [("언제", "시험 전 '소지품 확인' 중 발견"),
                         ("누구", "'재수생' 수험생 1명"),
                         ("조치", "즉시 '퇴실' · 경찰 수사 예정"),
                         ("아직 모르는 것", "실제로 '썼는지'는 미확인")]),
      "실제로 '썼는지'는 경찰이 가린다", "뉴스1·SBS·경기도교육청(11.19)").save(O / "c03.jpg", quality=93)

frame(("서초구 시험장, 2교시 도중", "'신발 깔창' 속에서 벨이 울렸다"),
      ph("seocho", 640, [("어디서", "서울 서초구 한 고교 시험장"),
                         ("들킨 이유", "시험 중 폰 '벨 소리'"),
                         ("신고", "학교 관계자 112 \"'중대 부정행위'\""),
                         ("지금", "경찰, 숨긴 경위·사용 여부 조사")]),
      "경찰이 시험장 '안까지' 들어왔다", "MBC·싱글리스트(11.19)").save(O / "c04.jpg", quality=93)

frame(("올해 수능이 이렇게까지 한 이유", "감독관 코앞 'AI 커닝'"),
      panel([("발단", "세무사 수석이 'AI 부정행위' 자수"),
             ("수능 대책", "옷깃·단추에 '스티커', 안경 전수 검사"),
             ("가방", "교실 밖 '복도'에 따로 보관"),
             ("처벌", "응시 제한 1년 → '10년' 추진")], h=640),
      "작년 수능 부정행위 '279건', 역대 최다", "국무총리 담화(11.17)·허프포스트코리아").save(O / "c05.jpg", quality=93)

if "cover" in PH:
    c = PH["cover"]; fit(c["f"], W, H, tuple(c.get("c", (.5, .4)))).save(O / "cover_bg.jpg", quality=95)
print("ok")
