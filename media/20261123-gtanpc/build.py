"""20261123-gtanpc: GTA6 '자기가 게임 속에 있다고 믿는 NPC' 이스터에그(IGN·Dexerto·Complex·LADbible 11.20~22). 게임 장면만 잘라 쓰고 글은 우리 문구."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
BOX = {1: (8, 445, 225, 1135), 2: (20, 214, 1095, 1080), 3: (20, 162, 1085, 1053), 4: (20, 200, 1080, 1104),
       5: (20, 186, 1095, 1077), 6: (20, 186, 1080, 1062), 7: (20, 243, 1085, 1111), 8: (20, 375, 1035, 1342)}
op = lambda i: Image.open(O / f"p1_{i}.jpg").convert("RGB").crop(BOX[i])


def rc(d, y, t, f, base):
    parts = re.split(r"('[^']*')", t); tw = sum(d.textlength(p.strip("'"), font=f) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=f, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=f)


def frame(top, ph, bottom, sub, out, maxh=700):
    ph = ImageOps.fit(ph, (940, min(maxh, round(ph.height * 940 / ph.width))), Image.LANCZOS)
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rc(d, 168, top[0], F("Medium", 46), FG); rc(d, 236, top[1], F("Black", 54), FG)
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), 18, fill=255)
    im.paste(ph, ((W - ph.width) // 2, 300), m); d = ImageDraw.Draw(im); y = 300 + ph.height + 92
    rc(d, y, bottom, F("Black", 44), YE); rc(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
    im.save(O / out, quality=93)


S = "GTA6 게임 화면"
frame(("어느 집 차고 안에 숨겨진", "'음모론 게시판'"), op(2), "\"IT’S A SIMULATION\" 여긴 '가짜 세상'이다", S, "c02.jpg")
frame(("첫 번째 의심", "\"아이들은 다 어디 갔지?\""), op(3), "게임 속엔 아이가 '한 명도' 안 나온다", S, "c03.jpg")
frame(("두 번째 의심", "\"똑같이 생긴 사람들\""), op(4), "서로 모르는 사람이 '같은 얼굴'", "NPC 캐릭터 모델 재사용을 꼬집은 것", "c04.jpg")
frame(("세 번째 의심", "\"차들이 '사라진다'\""), op(5), "돌아보면 없어지는 차, 게임 속 '그 현상'", S, "c05.jpg")
frame(("그리고 깨달았다", "\"왜 나는 '못 떠나지'?\""), op(6), "게임 무대 '레오니다'를 벗어날 수 없다", "\"로스산토스 가는 표를 사려 했는데\"", "c06.jpg")
frame(("마지막 가설", "\"J와 L만 '자유의지'가 있다\""), op(7), "J·L = 주인공 '제이슨·루시아'", S, "c07.jpg")
frame(("이 집, 5년 전에 이미 나왔다", "2021년 'GTA 산안드레아스' 리메이크"), op(8), "UFO 사진 속 그 집이 GTA6 '첫 단서'였다", "Dexerto·Complex 보도", "c08.jpg")
ImageOps.fit(op(2), (W, H), Image.LANCZOS, centering=(.3, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
