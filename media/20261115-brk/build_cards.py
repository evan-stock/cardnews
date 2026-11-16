"""20261113-kress: 참고 게시물(@peakon.mag DfpWK1dn2Lr) 구성 — 표지(말풍선) → 사임 사실+사진 → 임시 CEO 크레스 → 머스크 X → 팔로우.
2~4장은 검은 바탕 '위 문구 + 가운데 사진 + 아래 노란 한 줄' 틀로 직접 그림. 표지 배경에도 말풍선을 그려 둠."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = Path("/home/claude/cardnews/media/20261115-brk"); R = Path("/home/claude/cardnews"); O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
PEN = lambda s: ImageFont.truetype(str(R / "assets/fonts/HiMelody-Regular.ttf"), s)


def bubble(im, cx, cy, text, w=380, h=170, tail="bl", fs=50):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    tx = {"bl": (x0 + w * .28, y1 - 10, x0 + w * .12, y1 + 60, x0 + w * .42, y1 - 18),
          "br": (x1 - w * .28, y1 - 10, x1 - w * .12, y1 + 60, x1 - w * .42, y1 - 18)}[tail]
    d.polygon([(tx[0], tx[1]), (tx[2], tx[3]), (tx[4], tx[5])], fill="white", outline="black")
    d.ellipse((x0, y0, x1, y1), fill="white", outline="black", width=4)
    d.polygon([(tx[0], tx[1] - 6), (tx[2] + 4, tx[3] - 8), (tx[4], tx[5] - 4)], fill="white")
    lines = text.split("\n"); lh = fs + 6; y = cy - lh * len(lines) / 2 + fs * .5
    for ln in lines:
        d.text((cx, y), ln, font=PEN(fs), fill="black", anchor="mm"); y += lh


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


def frame(top, photo, bottom, sub=None, focus=(.5, .5), bub=None, ph=760):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    pw = 940; p = fit(photo, pw, ph, focus) if isinstance(photo, (str, Path)) else photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    if bub: bubble(im, *bub)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


frame(("11월 15일 본인 영상에서", "\"생성형 AI를 이용해 '부정행위'를 했습니다\""), O / "v2_mask.jpg",
      "수석 합격은 '정당한 노력'이 아니었다", sub="마스크 쓰고 직접 출연 (유튜브 '이돈호 변호사')", focus=(.5, .32)).save(O / "f02.jpg", quality=95)
frame(("알려진 'AI 안경'이 아니라", "'초소형 카메라'로 찍어 AI에 보냈다"), O / "v2_stand.jpg",
      "답은 스마트폰으로 확인", sub="구체적 과정은 모방 우려로 공개하지 않음", focus=(.5, .3)).save(O / "f03.jpg", quality=95)
frame(("14일엔 \"공부를 왜 하겠느냐\"더니", "'하루 만에' 자수"), O / "note_cover.jpg",
      "\"그 당시에는 숨겨야겠다는 생각이 들어서\"", sub="14일 인터뷰에선 \"AI 안경으로 이걸 맞힐 수 있으면\" 반문", focus=(.5, .25)).save(O / "f04.jpg", quality=95)
frame(("세무사 1·2차만이 아니었다", "공인회계사 1차도 '같은 방식'"), O / "yt_lawyer.jpg",
      "수법은 수사기관에 그대로 설명하기로", sub="이돈호 변호사 (법무법인 노바)", focus=(.6, .3), ph=760).save(O / "f06.jpg", quality=95)
print("ok")
