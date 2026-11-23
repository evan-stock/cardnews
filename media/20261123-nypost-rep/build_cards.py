"""20261123-nypost-rep: 뉴욕시장 행사 '랩틸리언' 눈 영상 당사자(조던 라이트 뉴욕주 하원의원) 해명 — 뉴욕포스트(11.22). 본문은 실제 기사 캡처(로고·제목 포함 한 화면 그대로).
leetnews/build_cards.py 복사."""
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




nyp = op("nyp.jpg")
def shot(box, w=940):
    im = nyp.crop(box); return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
# 2장(2026.11.23 사용자 지시): 자료화면 캡처 대신 '눈 바뀌는 영상'. 틀(png)을 만들고 영상은 ffmpeg로 사진 자리에 얹음
VW, VH = 448, 560
frame(("11월 20일 뉴욕시장 기자회견", "뒤에 선 남성 눈이 '하얗게'"), Image.new("RGB", (VW, VH), (0, 0, 0)),
      "엑스에선 \"이게 '도마뱀'이 눈 깜박이는 방식\"", "영상: 뉴욕시장실 행사(엑스 재편집본)").save(O / "c02.jpg", quality=93)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(O / "c02.jpg"), "-stream_loop", "2", "-i", str(O / "eye_clip.mp4"),
                "-filter_complex", f"[1:v]scale={VW}:{VH},setsar=1[v];[0:v][v]overlay={(W - VW) // 2}:300:shortest=1,format=yuv420p",
                "-r", "30", "-c:v", "libx264", "-crf", "18", "-an", str(O / "eye_slide.mp4")], check=True)
frame(("뉴욕포스트 취재에", "당사자는 '뉴욕주 하원의원'"), shot((0, 0, 860, 760), 760),
      "할렘 지역구 조던 라이트(32) 의원", "뉴욕포스트(11.22) 기사 화면").save(O / "c03.jpg", quality=93)
frame(("본인 해명", "\"분명히 저는 '인간'입니다\""), shot((0, 7205, 860, 7745), 940),
      "\"파충류나 외계인에 대해선 '할 말 없다'\"", "\"영상 속에서 무슨 일이 있었는지 나도 모르겠다\"").save(O / "c04.jpg", quality=93)
# 표지(2026.11.23 사용자 지시): 기자회견 장면(눈 하얗게 바뀌는 순간) 꽉 채우고, 의원 공식 사진은 동그라미 안에 작게. 겹쳐 합성하지 않음
import os
bgsrc = "eye_up.png" if os.path.exists(O / "eye_up.png") else "eye_center.png"  # eye_up.png = 사용자가 화질 올린 사진
bg = ImageOps.fit(op(bgsrc), (W, H), Image.LANCZOS, centering=(.5, .5))
rt = op("rt1.png"); face = rt.crop((1090 - 200, 40, 1090 + 200, 440)).resize((300, 300), Image.LANCZOS)
D0 = 300; mk = Image.new("L", (D0, D0), 0); ImageDraw.Draw(mk).ellipse((0, 0, D0 - 1, D0 - 1), fill=255)
x0, y0 = W - D0 - 60, 90
# 동그라미 프로필은 2026.11.23 사용자 지시로 뺌
if bgsrc == "eye_up.png":  # 사용자가 준 AI 합성 이미지(눈만 파충류 눈으로 바꿈) → 실제 사진으로 오해 없게 표시
    d = ImageDraw.Draw(bg); f = F("SemiBold", 34); t = "AI 합성 이미지"; tw = d.textlength(t, font=f)
    d.text((62, 132), t, font=f, fill=(0, 0, 0), anchor="lm"); d.text((60, 130), t, font=f, fill=(255, 255, 255), anchor="lm")  # 검은 상자 없이(2026.11.23 사용자 지시), 옅은 그림자만
bg.save(O / "cover_bg.jpg", quality=95)
print("ok")
