"""4번 양식의 커뮤니티 캡처판(kind "community"): 흰 바탕 커뮤니티 캡처 카드 (2026-11-28 사용자 확정, 참고 @bythepulse 느낌).
흰 바탕 + 그림자 진 캡처 카드(가로 940, 최대 높이 760) + 오른쪽 아래 회색 출처
+ 검은 굵은 한 줄(t1, ExtraBold 50) + 노란 형광펜 핵심 줄(t2, Black 66) + 하단 가운데 검은 로고.
사용: python3 scripts/white_cap_card.py spec.json  (cap/out 은 저장소 기준 경로)
예시: media/20261128-sam7/white.json"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = Path(__file__).resolve().parents[1]
W, H = 1080, 1350
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
YE = (255, 216, 77)
D = R


def card(s):
    dark = s.get("theme", "dark") == "dark"  # 2026-11-28: 기본 검은 바탕
    im = Image.new("RGB", (W, H), (12, 12, 14) if dark else (255, 255, 255))
    cap = Image.open(D / s["cap"]).convert("RGB")
    if s.get("crop"):
        cap = cap.crop(s["crop"])
    bw = s.get("w", 940)
    cap = cap.resize((bw, round(cap.height * bw / cap.width)), Image.LANCZOS)
    mh = s.get("max_h", 760)
    if cap.height > mh:
        k = mh / cap.height
        cap = cap.resize((round(cap.width * k), mh), Image.LANCZOS)
    cw, ch = cap.size
    l1, l2 = s["t1"], s["t2"]
    f1, f2 = F("ExtraBold", 50), F("Black", 66)
    gap, th = 70, 62 + 18 + 84
    total = ch + gap + th
    y0 = max(70, round((H - 110 - total) / 2))
    x0 = (W - cw) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if dark:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((x0 - 2, y0 + 6, x0 + cw + 2, y0 + ch + 10), fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(sh, (0, 0), sh)
    im.paste(cap, (x0, y0))
    ImageDraw.Draw(im).rectangle((x0, y0, x0 + cw - 1, y0 + ch - 1), outline=(60, 62, 68) if dark else (228, 228, 228), width=2)
    d = ImageDraw.Draw(im)
    ty = y0 + ch + gap
    d.text((W // 2, ty), l1, font=f1, fill=(255, 255, 255) if dark else (20, 20, 20), anchor="mt")
    ty2 = ty + 62 + 18
    tw = d.textlength(l2, font=f2)
    # 형광펜 안 씀(2026-11-28 사용자): 핵심 줄은 노란 글씨. 흰 바탕일 땐 검은 외곽선으로 읽히게.
    d.text((W // 2, ty2), l2, font=f2, fill=YE, anchor="mt",
           stroke_width=0 if dark else 3, stroke_fill=(20, 20, 20))
    if s.get("src"):
        d.text((x0 + cw, y0 + ch + 14), s["src"], font=F("Medium", 26), fill=(150, 150, 150), anchor="rt")
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")
    lh = 40
    lg = lg.resize((round(lg.width * lh / lg.height), lh), Image.LANCZOS)
    # 흰 바탕용: 흰 글자는 검게
    px = lg.load()
    for yy in range(lg.height):
        for xx in range(lg.width):
            r, g, b, a = px[xx, yy]
            if not dark and a and r > 200 and g > 200 and b > 200:
                px[xx, yy] = (20, 20, 20, a)
    im.paste(lg, ((W - lg.width) // 2, H - 80), lg)
    im.save(D / s["out"], quality=95)


if __name__ == "__main__":
    for s in json.load(open(sys.argv[1])):
        card(s)
        print(s["out"])
