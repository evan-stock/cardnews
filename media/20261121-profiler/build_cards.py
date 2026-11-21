"""20261121-profiler: 배상훈 프로파일러가 본 리트 만점자 이진우(팟빵 CRIME 11.20, 뉴시스·파이낸셜 11.19~20, 위키트리/SBS 성적). 자살보도 권고기준: 방법·장소·현장 사진 없음, 109 표기."""
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

def strip(name, boxes, w=940):
    ims=[Image.open(O / name).convert("RGB").crop(b) for b in boxes]
    c=Image.new("RGB",(ims[0].width,sum(i.height for i in ims)),"white"); y=0
    for i in ims: c.paste(i,(0,y)); y+=i.height
    return c.resize((w, round(c.height*w/c.width)), Image.LANCZOS)


def stack(parts, w=940, pad=28):
    ims=[]
    for n,b in parts:
        im=Image.open(O / n).convert("RGB").crop(b); ims.append(im.resize((w-2*pad, round(im.height*(w-2*pad)/im.width)), Image.LANCZOS))
    c=Image.new("RGB",(w,sum(i.height for i in ims)+pad*(len(ims)+1)),"white"); y=pad
    for i in ims: c.paste(i,(pad,y)); y+=i.height+pad
    return c


def yt_card():
    t = strip("yt.jpg", [(0, 570, 860, 790)])
    b = Image.open(O / "yt_thumb.jpg").convert("RGB").crop((1000, 225, 1280, 720))
    b = b.resize((round(b.width * 520 / b.height), 520), Image.LANCZOS)
    c = Image.new("RGB", (940, t.height + 520), (18, 18, 22)); c.paste(t, (0, 0)); c.paste(b, ((940 - b.width) // 2, t.height))
    return c


frame(("구독 56만 유튜브 '팟빵 CRIME'", "배상훈 \"이 사람은 '리플리 증후군'\""),
      yt_card(),
      "거짓말을 반복하다 '자기도' 믿게 된다", "유튜브 [팟빵] CRIME(11.20) · 조회 126만").save(O / "c02.jpg", quality=93)
frame(("패러글라이딩 '뇌 각성' 스토리", "\"사실은 '각성제' 경험일 것\""),
      strip("newsis.jpg", [(0, 235, 860, 470), (0, 560, 860, 650)]),
      "\"모든 거짓엔 '진실'이 조금 섞여 있다\"", "뉴시스(11.19) · 팟빵 CRIME(11.20) 배상훈 프로파일러 주장").save(O / "c03.jpg", quality=93)
frame(("프로파일러가 짚은 해, 2018학년도 수능", "국어 7등급인데 수학만 '1등급'"),
      strip("wikitree.jpg", [(0, 1135, 860, 1625)]),
      "\"그때부터가 '최초' 시점일 것\"", "이진우 씨 공개 성적 · SBS 정리 / 팟빵 CRIME(11.20)").save(O / "c04.jpg", quality=93)
frame(("배상훈이 끝까지 강조한 것", "\"'공범·브로커'가 있었을 것\""),
      stack([("newsis_chrome.png",(0, 0, 1568, 180)),("newsis_p2.png",(0,0,978,412))]),
      "\"죽었다고 끝이 아니다, 2018년부터 다시 봐야\"", "뉴시스(11.19) · 유튜브 [팟빵] CRIME(11.20)").save(O / "c05.jpg", quality=93)
_c = stack([("newsis_chrome.png",(0, 0, 1568, 180)),("newsis_p1_hl.png",(0,0,978,464)),("newsis_p2_hl.png",(0,0,978,412))], pad=22)
if _c.height > 740: _c = _c.resize((round(_c.width*740/_c.height), 740), Image.LANCZOS)
frame(("배상훈이 짚은 두 가지", "'각성제' 과대망상, 입시 '부정' 가능성"),
      _c, "\"약물 검사·대리시험 의혹까지 다 봐야\"", "뉴시스(11.19) · 배상훈 프로파일러 유튜브 분석").save(O / "c03n.jpg", quality=93)
p = Image.open(R / "media/20261121-leetpara/cand/lee_photo.jpg").convert("RGB")
pass
print("ok")
