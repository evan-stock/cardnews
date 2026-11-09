"""수사 보드 모션그래픽 릴스 틀 (2026.11.09 첫 적용: 중국 미인계 간첩작전).

어두운 코르크 보드 한가운데 '배후' 카드가 있고, 장면마다 표적 사진 카드가 꽂히며
빨간 실이 배후 카드로 이어지고 '표적' 도장이 찍힌다. 마지막 정리 장면에서 실이 모두 빛난다.
위 고정: today.worthy 로고 → 노란 꼬리표 → 굵은 제목 2줄. 아래: 작은 줄 + 굵은 2줄 자막.

사용: python3 scripts/board_reel/build.py <spec.json> [--shots]   (--shots: 장면별 확인용 사진만)
결과: media/<id>/board_reel.mp4, media/<id>/board_reel_cover.jpg(첫 장면 완성 프레임)
"""
import json, math, random, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
FB = "assets/fonts/Pretendard-Black.otf"
FM = "assets/fonts/Pretendard-Medium.otf"
FX = "assets/fonts/Pretendard-ExtraBold.otf"
LOGO = "brand/logo_typo_A.png"
YEL = (255, 216, 77)
RED = (226, 32, 38)
WHITE = (255, 255, 255)

BOARD = (40, 470, 1040, 1420)  # 보드 영역
CENTER = (540, 945)
SLOTS = [(255, 690), (825, 690), (255, 1200), (825, 1200)]  # 카드 중심
CARD_W, PHOTO_H = 330, 250


def font(p, s):
    return ImageFont.truetype(p, s)


def ease_out(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3


def ease_back(t):
    t = max(0, min(1, t))
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


# ---------- 정적 배경 ----------
def make_background():
    random.seed(7)
    bg = Image.new("RGB", (W, H), (12, 11, 10))
    # 코르크 질감: 갈색 잡음 + 블러
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    noise = Image.effect_noise((bw, bh), 60).convert("L")
    cork = ImageOps.colorize(noise, (52, 36, 24), (104, 76, 50)).filter(ImageFilter.GaussianBlur(1.1))
    speck = Image.effect_noise((bw, bh), 90).convert("L").point(lambda v: 255 if v > 215 else 0).filter(ImageFilter.GaussianBlur(0.6))
    cork.paste((40, 28, 18), (0, 0), speck.point(lambda v: v // 2))
    # 비네팅
    vig = Image.new("L", (bw, bh), 0)
    dv = ImageDraw.Draw(vig)
    for i in range(60):
        dv.rectangle((i * 3, i * 3, bw - i * 3, bh - i * 3), outline=int(255 * (i / 60) ** 1.6))
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGB", (bw, bh), (8, 6, 5))
    cork = Image.composite(cork, dark, vig)
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=26, fill=255)
    bg.paste(cork, BOARD[:2], mask)
    # 나무 테두리
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle(BOARD, radius=26, outline=(70, 50, 34), width=10)
    return bg.convert("RGBA")


def make_header(spec):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    lg = Image.open(LOGO).convert("RGBA")
    lh = 40
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    ov.alpha_composite(lg, (70, 110))
    tf = font(FX, 34)
    tag = spec["tag"]
    tw = d.textlength(tag, font=tf) + 36
    d.rounded_rectangle((70, 180, 70 + tw, 234), radius=10, fill=YEL)
    d.text((70 + 18, 207), tag, font=tf, fill=(15, 15, 15), anchor="lm")
    f = font(FB, 84)
    l1, l2 = spec["title"]
    draw_rich(d, (70, 330), l1, f, WHITE)
    draw_rich(d, (70, 432), l2, f, YEL, hi=YEL)
    return ov


def fit_font(d, text, path, size, maxw):
    s = size
    while s > 40:
        f = font(path, s)
        if d.textlength(text.replace("'", ""), font=f) <= maxw:
            return f
        s -= 2
    return font(path, s)


def draw_rich(d, xy, text, f, base, hi=YEL):
    """'작은따옴표' 안은 노랑. 따옴표는 지운다."""
    x, y = xy
    parts = text.split("'")
    for i, p in enumerate(parts):
        col = hi if i % 2 == 1 else base
        d.text((x, y), p, font=f, fill=col, anchor="ls")
        x += d.textlength(p, font=f)


def subtitle_layer(b, alpha):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha <= 0:
        return ov
    d = ImageDraw.Draw(ov)
    # 아래 어둡게
    for y in range(1430, H):
        t = min(1, (y - 1430) / 120)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(200 * t)))
    ctx = b.get("ctx", "")
    if ctx:
        fc = fit_font(d, ctx, FM, 38, 940)
        d.text((70, 1530), ctx, font=fc, fill=(200, 200, 200), anchor="ls")
    f1 = fit_font(d, b["l1"], FB, 70, 940)
    f2 = fit_font(d, b["l2"], FB, 70, 940)
    draw_rich(d, (70, 1630), b["l1"], f1, WHITE)
    draw_rich(d, (70, 1725), b["l2"], f2, YEL, hi=YEL)
    if alpha < 1:
        a = ov.getchannel("A").point(lambda v: int(v * alpha))
        ov.putalpha(a)
    return ov


# ---------- 카드 ----------
def photo_fit(path, w, h, fx=0.5, fy=0.4):
    im = Image.open(path).convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * r)), max(h, int(im.height * r))), Image.LANCZOS)
    x = int((im.width - w) * fx)
    y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def make_card(c, base):
    """폴라로이드식 카드 + 압정. 반환: RGBA, 압정 위치(카드 기준)."""
    pad = 14
    cap_h = 92
    cw, ch = CARD_W, PHOTO_H + pad + cap_h
    card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((24, 26, 24 + cw, 26 + ch), fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    card.alpha_composite(sh)
    d = ImageDraw.Draw(card)
    d.rectangle((20, 20, 20 + cw, 20 + ch), fill=(238, 233, 222))
    if c.get("img"):
        ph = photo_fit(base / c["img"], cw - 2 * pad, PHOTO_H - pad, c.get("fx", 0.5), c.get("fy", 0.35))
    else:
        ph = c["_drawn"]
    ph = ImageOps.grayscale(ph).convert("RGB") if c.get("gray") else ph
    card.paste(ph, (20 + pad, 20 + pad))
    f = fit_font(d, c["cap"], FB, 34, cw - 2 * pad)
    d.text((20 + pad, 20 + PHOTO_H + 46), c["cap"], font=f, fill=(20, 20, 20), anchor="ls")
    if c.get("credit"):
        fc = font(FM, 19)
        d.text((20 + cw - pad, 20 + PHOTO_H + 80), c["credit"], font=fc, fill=(110, 105, 98), anchor="rs")
    pin = (20 + cw // 2, 26)
    # 압정
    d.ellipse((pin[0] - 15, pin[1] - 15, pin[0] + 15, pin[1] + 15), fill=(150, 14, 18))
    d.ellipse((pin[0] - 11, pin[1] - 13, pin[0] + 7, pin[1] + 3), fill=(235, 60, 60))
    return card, pin


def make_center(spec):
    cw, ch = 360, 190
    card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((24, 26, 24 + cw, 26 + ch), fill=(0, 0, 0, 200))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(card)
    d.rectangle((20, 20, 20 + cw, 20 + ch), fill=(20, 18, 18), outline=RED, width=6)
    l1, l2 = spec["center"]
    cx = 20 + cw // 2
    if spec.get("center_img"):
        em = Image.open(Path("media") / spec["id"] / spec["center_img"]).convert("RGB")
        m = Image.new("L", em.size, 0)
        ImageDraw.Draw(m).ellipse((0, 0, em.width - 1, em.height - 1), fill=255)
        em.putalpha(m)
        em = em.resize((118, 118), Image.LANCZOS)
        card.alpha_composite(em, (20 + 22, 20 + (ch - 118) // 2 + 6))
        cx = 20 + 140 + (cw - 140) // 2
    d.text((cx, 20 + 98), l1, font=fit_font(d, l1, FB, 50, cw - 160 if spec.get("center_img") else cw - 30), fill=WHITE, anchor="ms")
    d.text((cx, 20 + 150), l2, font=fit_font(d, l2, FM, 28, cw - 160 if spec.get("center_img") else cw - 30), fill=(235, 90, 90), anchor="ms")
    pin = (20 + cw // 2, 30)
    d.ellipse((pin[0] - 15, pin[1] - 15, pin[0] + 15, pin[1] + 15), fill=(150, 14, 18))
    d.ellipse((pin[0] - 11, pin[1] - 13, pin[0] + 7, pin[1] + 3), fill=(235, 60, 60))
    return card


def make_stamp(text):
    s = Image.new("RGBA", (300, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((8, 8, 292, 142), radius=14, outline=RED + (235,), width=10)
    d.text((150, 108), text, font=font(FB, 86), fill=RED + (235,), anchor="ms")
    # 거친 질감
    random.seed(3)
    n = Image.effect_noise((300, 150), 80).convert("L").point(lambda v: 0 if v > 170 else 255)
    a = Image.composite(s.getchannel("A"), Image.new("L", s.size, 0), n)
    s.putalpha(a)
    return s.rotate(-12, expand=True, resample=Image.BICUBIC)


def string_pts(a, b, sag=60, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t + sag * math.sin(math.pi * t)
        pts.append((x, y))
    return pts


def draw_string(d, a, b, prog, glow=0.0):
    pts = string_pts(a, b)
    k = max(1, int(len(pts) * prog))
    seg = pts[:k + 1] if prog < 1 else pts
    if len(seg) < 2:
        return
    if glow > 0:
        d.line(seg, fill=(255, 60, 60, int(110 * glow)), width=16, joint="curve")
    d.line(seg, fill=(120, 8, 10, 255), width=7, joint="curve")
    d.line(seg, fill=(225, 30, 34, 255), width=4, joint="curve")


# ---------- 그리기 ----------
def build(spec_path, shots_only=False):
    spec = json.loads(Path(spec_path).read_text())
    base = Path("media") / spec["id"]
    out_dir = base
    work = Path("/tmp/board_reel") / spec["id"]
    work.mkdir(parents=True, exist_ok=True)

    bgimg = make_background()
    header = make_header(spec)
    center = make_center(spec)
    stamp = make_stamp(spec.get("stamp", "표적"))
    cards = []
    for i, sc in enumerate(spec["scenes"]):
        c = sc["card"]
        if c.get("drawn"):
            c["_drawn"] = Image.open(base / c["drawn"]).convert("RGB").resize((CARD_W - 28, PHOTO_H - 14), Image.LANCZOS)
        im, pin = make_card(c, base)
        cards.append((im, pin, SLOTS[i]))

    seg = spec.get("scene_len", 3.6)
    intro = spec.get("intro_len", 0.7)
    recap_len = spec.get("recap_len", 3.4)
    cta_len = spec.get("cta_len", 2.6)
    n = len(cards)
    total = intro + n * seg + recap_len + cta_len
    nf = int(total * FPS)
    rot = [-4, 3, 3.5, -3]

    center_xy = (CENTER[0] - center.width // 2, CENTER[1] - center.height // 2)
    center_pin = (CENTER[0], center_xy[1] + 30)

    def frame(t):
        fr = bgimg.copy()
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # 정리 장면 줌
        t_recap = intro + n * seg
        glow = 0.0
        if t >= t_recap:
            glow = 0.6 + 0.4 * math.sin((t - t_recap) * 6)
        # 실 (카드 아래 레이어)
        sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sl)
        placed = []
        for i, (im, pin, slot) in enumerate(cards):
            t0 = intro + i * seg
            if t < t0:
                continue
            lt = t - t0
            drop = ease_back(lt / 0.45)
            sc = 1.25 - 0.25 * drop if lt < 0.45 else 1.0
            alpha = min(1, lt / 0.2)
            imr = im.rotate(rot[i], expand=True, resample=Image.BICUBIC)
            if sc != 1.0:
                imr = imr.resize((int(imr.width * sc), int(imr.height * sc)), Image.BICUBIC)
            x = slot[0] - imr.width // 2
            y = slot[1] - imr.height // 2 - int(40 * (1 - ease_out(lt / 0.45)))
            # 압정 위치(회전 근사)
            px = slot[0] + (pin[0] - im.width / 2)
            py = slot[1] + (pin[1] - im.height / 2)
            sprog = ease_out((lt - 0.45) / 0.6)
            if lt > 0.45:
                draw_string(sd, (px, py), center_pin, sprog, glow)
            placed.append((imr, x, y, alpha, lt, slot, i))
        fr.alpha_composite(center, center_xy)
        fr.alpha_composite(sl)
        for imr, x, y, alpha, lt, slot, i in placed:
            if alpha < 1:
                a = imr.getchannel("A").point(lambda v: int(v * alpha))
                imr = imr.copy()
                imr.putalpha(a)
            fr.alpha_composite(imr, (int(x), int(y)))
            # 도장
            st0 = 1.15
            if lt > st0:
                k = min(1, (lt - st0) / 0.18)
                s = 1.8 - 0.8 * ease_out(k)
                stp = stamp.resize((int(stamp.width * s * 0.72), int(stamp.height * s * 0.72)), Image.BICUBIC)
                if k < 1:
                    a = stp.getchannel("A").point(lambda v: int(v * k))
                    stp.putalpha(a)
                fr.alpha_composite(stp, (slot[0] - stp.width // 2 + 70, slot[1] - stp.height // 2 - 20))
        # 배후 카드 위에 실 끝 매듭이 보이게 다시 압정
        d = ImageDraw.Draw(fr)
        if any(t >= intro + i * seg + 1.05 for i in range(n)):
            d.ellipse((center_pin[0] - 15, center_pin[1] - 15, center_pin[0] + 15, center_pin[1] + 15), fill=(150, 14, 18))
            d.ellipse((center_pin[0] - 11, center_pin[1] - 13, center_pin[0] + 7, center_pin[1] + 3), fill=(235, 60, 60))
        # 정리 장면: 살짝 확대 + 빨간 빛
        if t >= t_recap:
            k = ease_out((t - t_recap) / 1.2)
            z = 1 + 0.06 * k
            box = (int(W * (1 - 1 / z) / 2), int(H * (1 - 1 / z) / 2), int(W - W * (1 - 1 / z) / 2), int(H - H * (1 - 1 / z) / 2))
            fr = fr.crop(box).resize((W, H), Image.BICUBIC)
            red = Image.new("RGBA", (W, H), (180, 0, 0, int(40 * glow)))
            fr.alpha_composite(red)
        fr.alpha_composite(header)
        # 자막
        if t < intro:
            b, a = spec["scenes"][0]["b"], 0
        elif t < t_recap:
            i = int((t - intro) // seg)
            lt = t - intro - i * seg
            b, a = spec["scenes"][i]["b"], min(1, lt / 0.25)
        else:
            b, a = spec["recap"], min(1, (t - t_recap) / 0.3)
        fr.alpha_composite(subtitle_layer(b, a))
        # CTA
        t_cta = t_recap + recap_len
        if t >= t_cta:
            k = min(1, (t - t_cta) / 0.35)
            fr.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(215 * k))))
            ct = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dc = ImageDraw.Draw(ct)
            l0, l1, l2 = spec["cta"]
            dc.text((W // 2, 840), l0, font=font(FM, 44), fill=(220, 220, 220), anchor="ms")
            dc.text((W // 2, 950), l1, font=fit_font(dc, l1, FB, 82, 960), fill=WHITE, anchor="ms")
            dc.text((W // 2, 1050), l2, font=fit_font(dc, l2, FB, 82, 960), fill=YEL, anchor="ms")
            bt = "＋ 팔로우 @today.worthy"
            bf = font(FX, 40)
            bw = dc.textlength(bt, font=bf) + 70
            dc.rounded_rectangle((W // 2 - bw // 2, 1140, W // 2 + bw // 2, 1230), radius=45, outline=WHITE, width=4)
            dc.text((W // 2, 1186), bt, font=bf, fill=WHITE, anchor="mm")
            if k < 1:
                ct.putalpha(ct.getchannel("A").point(lambda v: int(v * k)))
            fr.alpha_composite(ct)
        return fr.convert("RGB")

    if shots_only:
        times = [intro + i * seg + seg - 0.3 for i in range(n)] + [intro + n * seg + recap_len - 0.3, total - 0.2]
        for k, tt in enumerate(times):
            frame(tt).save(work / f"shot{k}.jpg", quality=88)
        print("shots:", work)
        return
    # 커버 = 첫 장면 완성 프레임
    frame(intro + seg - 0.3).save(out_dir / "board_reel_cover.jpg", quality=93)
    silent = work / "silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    for i in range(nf):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    out = out_dir / "board_reel.mp4"
    bgm = spec.get("bgm")
    if bgm:
        st, vol = bgm.get("start", 0), bgm.get("vol", 0.5)
        af = f"volume={vol},afade=t=in:st=0:d=0.3,afade=t=out:st={total - 1.5:.2f}:d=1.5"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-ss", str(st), "-t", f"{total:.2f}", "-i", bgm["file"],
                        "-af", af, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)], check=True)
    else:
        silent.replace(out)
    print("done:", out, f"{total:.1f}s")


if __name__ == "__main__":
    build(sys.argv[1], "--shots" in sys.argv)
