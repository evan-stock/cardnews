"""20261112-taxglass2: healing.zip 게시물 사진(블로그 수기·댓글·노트 캡처)으로 만든 안쪽 장. 디자인 v2 색·글꼴."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R = Path(__file__).resolve().parents[2]; O = Path(__file__).parent / "cand"
W, H, P = 1080, 1350, 90
BG, FG, YE = (12, 12, 14), (255, 255, 255), (255, 216, 77)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
src = lambda i: Image.open(O / f"src{i}.jpg").convert("RGB")

# 표지 배경: 원본 글자(아래쪽) 위까지만 쓰고 아래는 어둡게 이어 붙임
s1 = src(1); top = s1.crop((0, 0, 1080, 815))
cov = Image.new("RGB", (W, H), BG); cov.paste(top, (0, 0))
fade = Image.new("L", (W, 260), 0)
for y in range(260): ImageDraw.Draw(fade).line((0, y, W, y), fill=int(255 * y / 259))
cov.paste(Image.new("RGB", (W, 260), BG), (0, 815 - 260), fade)
cov.save(O / "cover_bg.jpg", quality=95)
BGIMG = O / "cover_bg.jpg"

def rich(d, x, y, text, font, base, anchor="ls"):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'") if hl else p
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor=anchor); x += d.textlength(p, font=font)

def card(name, sub, t, cap, body, maxw=900):
    b = Image.open(BGIMG).convert("RGB").filter(ImageFilter.GaussianBlur(18))
    im = ImageEnhance.Brightness(b).enhance(.15); d = ImageDraw.Draw(im); y = 160
    d.text((P, y), sub, font=F("SemiBold", 36), fill=YE, anchor="ls"); y += 30
    for ln in t.split("\n"):
        y += 92; rich(d, P, y, ln, F("Black", 76), FG)
    y += 50
    yb = H - 150 - 50 * len(body)
    avail = yb - 40 - y
    k = min(maxw / cap.width, avail / cap.height); cw, ch = int(cap.width * k), int(cap.height * k)
    c = cap.resize((cw, ch), Image.LANCZOS)
    m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), 22, fill=255)
    im.paste(c, ((W - cw) // 2, y + (avail - ch) // 2), m)
    for i, ln in enumerate(body):
        rich(d, P, yb + i * 50, ln, F("Medium", 34), (225, 225, 230))
    logo = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); h = 40; w = int(logo.width * h / logo.height)
    logo = logo.resize((w, h), Image.LANCZOS); logo.putalpha(logo.split()[3].point(lambda v: int(v * .75)))
    im.paste(logo, ((W - w) // 2, H - 62 - h), logo); im.save(O / f"{name}.jpg", quality=95); print(name, cw, ch)

# 성적 캡처: 이름 줄은 잘라내고, 얼굴은 한 번 더 흐림
s7 = src(7).crop((0, 375, 1080, 1350))
face = (98, 0, 614, 1047 - 375); fr = s7.crop(face).filter(ImageFilter.GaussianBlur(14)); s7.paste(fr, face[:2])

card("c02", "논란의 시작 · 수석 합격자 블로그 합격수기", "\"의지는 누구보다\n'있었습니다'\"", src(2).crop((0, 0, 1080, 1255)),
     ["새벽 운동 뒤 학원에 갔지만, 잠이 모자라", "수업 중 졸았다고 적었습니다."])
card("c03", "수기 속 문제의 대목", "\"머리가 좋아진 게 아니라,\n'전원이 들어온 겁니다'\"", src(3),
     ["20분도 못 버티던 집중이 한 번 앉으면", "90분씩 이어졌다는 설명입니다."])
card("c04", "수기가 퍼지자 · 블로그 댓글 73개", "'세무사' 이름 단 계정들이\n줄줄이 찾아왔다", src(4).crop((0, 0, 1080, 1210)),
     ["\"성지순례 왔습니다\" \"흥미진진하네요\"", "현직 의견을 묻는 댓글까지 달렸습니다."])
card("c05", "같은 블로그 댓글", "\"설마 이대로\n'합격' 주는 건가\"", src(5).crop((0, 0, 1080, 1330)),
     ["\"원청징수라니 세상에나…\"라는 댓글도", "달렸습니다. 무슨 뜻인지는 다음 장에."])
card("c06", "합격수기에 공개된 필기 노트", "'원천징수'가 아니라\n'원청징수'?", src(8).crop((0, 248, 1080, 990)),
     ["세법 기본 용어가 노트에 다르게 적혀 있어", "온라인에서 도마에 올랐습니다."])
card("c07", "수석 합격자 성적 · 합격수기 공개분", "1차 400점 만점에\n'397.5점'", s7,
     ["2차는 회계학 192·190점(200점 만점)인데", "세법학1부만 114점이라 의심이 쏠렸습니다."])
card("c08", "온라인 커뮤니티 반응", "\"올림픽 100m에서\n'8초' 나온 격\"", src(9).crop((30, 300, 1050, 1030)),
     ["세무사를 준비했던 친구의 말이라며 퍼진 글입니다.", "점수만 보고 나온 온라인 주장입니다."])
