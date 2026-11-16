"""20261105-musklaser 2장: 머스크 X 게시물 실제 캡처 + 9시간 뒤 본인 댓글 사진 + 번역 + 팔로우 CTA. 1080x1350."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 1080, 1350
F = "assets/fonts/"
BLACK, MED, SEMI = F + "Pretendard-Black.otf", F + "Pretendard-Medium.otf", F + "Pretendard-SemiBold.otf"
YEL = (255, 216, 77)
from PIL import ImageFont


def font(p, s):
    return ImageFont.truetype(p, s)


def framed(im, w, radius=28, border=(70, 74, 80)):
    im = im.convert("RGB").resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, outline=border, width=3)
    return out


def segs_draw(d, x, y, segs, f):
    for part, col in segs:
        d.text((x, y), part, font=f, fill=col)
        x += d.textlength(part, font=f)


def main(bg_path, tweet_path, reply_path, out):
    bg = ImageOps.fit(Image.open(bg_path).convert("RGB"), (W, H))
    bg = Image.blend(bg.filter(ImageFilter.GaussianBlur(28)), Image.new("RGB", (W, H), (0, 0, 0)), 0.8)
    d = ImageDraw.Draw(bg)
    f_t = font(BLACK, 58)
    segs_draw(d, 90, 120, [("\"이번엔 내 ", "white"), ("'선거 개입용", YEL)], f_t)
    segs_draw(d, 90, 196, [("우주 레이저'", YEL), ("가 안 먹혔나 보네\"", "white")], f_t)

    tw = framed(Image.open(tweet_path), 900)
    bg.paste(tw, (90, 310), tw)
    y = 310 + tw.height + 34

    d.text((90, y), "9시간 뒤 본인 댓글로 올린 사진", font=font(MED, 30), fill=(160, 166, 172))
    y += 52
    rp = framed(Image.open(reply_path), 440, radius=20, border=(90, 94, 100))
    bg.paste(rp, (90, y), rp)
    d.text((90 + 440 + 30, y + 40), "옛날 TV", font=font(MED, 30), fill=(200, 200, 200))
    d.text((90 + 440 + 30, y + 82), "송출 중단 화면:", font=font(MED, 30), fill=(200, 200, 200))
    d.text((90 + 440 + 30, y + 124), "\"죄송합니다,", font=font(SEMI, 30), fill="white")
    d.text((90 + 440 + 30, y + 166), "기술적 문제가", font=font(SEMI, 30), fill="white")
    d.text((90 + 440 + 30, y + 208), "발생했습니다\"", font=font(SEMI, 30), fill="white")
    y += rp.height + 40

    print("본문 끝 y =", y)

    f_btn = font(SEMI, 32)
    label = "＋ 팔로우 @today.worthy"
    tl = d.textlength(label, font=f_btn)
    bx0, by0 = (W - tl) / 2 - 40, H - 200
    d.rounded_rectangle((bx0, by0, bx0 + tl + 80, by0 + 64), 32, outline="white", width=3)
    d.text((bx0 + 40, by0 + 12), label, font=f_btn, fill="white")
    logo = Image.open("brand/logo_typo_A.png").convert("RGBA")
    lw = int(logo.width * 50 / logo.height)
    logo = logo.resize((lw, 50))
    bg.paste(logo, ((W - lw) // 2, H - 104), logo)
    bg.save(out, quality=95)


if __name__ == "__main__":
    main(*sys.argv[1:5])
