"""20261122-dannycho: 대니초가 로스트파티3에서 과즙세연에게 한 농담 논란. 공용 틀(frame)·카드 만들기."""
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


def fit(name, w=940, h=700, c=(.5, .5), crop=None):
    im = Image.open(O / name).convert("RGB")
    if crop: im = im.crop(crop)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=c)
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))


if __name__ == "__main__":
    # 3장: 엑스 원글 캡처(캡처 카드)
    spec = {"out": str(O / "c03.jpg"), "sub": "엑스 @KKOZSOM · 2026.11.21",
            "title": "펀치라인스 공식 클립\n엑스에서만 '조회 119만'",
            "cap": str(O / "xembed.jpg"), "cap_crop": [0, 0, 860, 1070], "cap_max_h": 620,
            "caption": "엑스 게시물 캡처 (조회수는 11.22 오전 기준)", "label": "퍼진 곳",
            "lines": ["펨코 등 커뮤니티 인기글로도 번지며", "'과즙세연 면전 돌직구' 영상으로 화제"]}
    json.dump([spec], open(O / "cap_spec.json", "w"), ensure_ascii=False)
    subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
    # 4장: 주최 측 설명 + 유튜브 썸네일
    frame(("주최 측이 풀영상에 단 설명", "\"로스트는 '상호 합의' 하에 놀리는 장르\""),
          fit("yt_thumb.jpg", 940, 560),
          "과즙세연도 '정식 출연진'이었다", "펀치라인스 유튜브 '로스트파티3' 풀버전(11.21 공개) · 8.15 출연진 공지").save(O / "c04.jpg", quality=93)
    # 5장: 반응
    frame(("풀영상 공개 하루, 댓글 반응은", "\"성희롱에 다 같이 웃는 '기묘한' 광경\""),
          fit("f10.jpg", 940, 720),
          "\"로스트도 웃겨야지, 이건 그냥 '불쾌'\"", "펀치라인스 유튜브·에펨코리아 댓글(11.21~22)").save(O / "c05.jpg", quality=93)
    print("ok")
