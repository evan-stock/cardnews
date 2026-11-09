"""수사 보드 모션그래픽 릴스 틀 (2026.11.09 첫 적용: 중국 미인계 간첩작전).

어두운 코르크 보드 한가운데 '배후' 카드가 있고, 장면마다 카메라가 표적 자리로 확대해 들어가
사진 카드가 꽂히고 '표적' 도장이 찍힌 뒤, 다시 빠지면서 빨간 실이 배후 카드로 이어진다.
마지막 정리 장면에서 실이 모두 빛난다. (2026.11.09 사용자: "확대해서 보여주는 방식")
위 고정: today.worthy 로고 → 노란 꼬리표 → 굵은 제목 2줄. 아래: 작은 줄 + 굵은 2줄 자막.

사용: python3 scripts/board_reel/build.py <spec.json> [--shots]   (--shots: 장면별 확인용 사진만)
결과: media/<id>/board_reel.mp4 (bgm 있으면 음악 포함), board_reel_nomusic.mp4, board_reel_cover.jpg
원고 예: drafts/board_reel/20261109-honeytrap.json
"""
import json, math, random, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
SS = 2  # 카드는 2배 해상도로 만들어 확대해도 선명하게
FB = "assets/fonts/Pretendard-Black.otf"
FM = "assets/fonts/Pretendard-Medium.otf"
FX = "assets/fonts/Pretendard-ExtraBold.otf"
LOGO = "brand/logo_typo_A.png"
YEL = (255, 216, 77)
RED = (226, 32, 38)
WHITE = (255, 255, 255)

BOARD = (40, 470, 1040, 1420)
C = (540, 945)  # 화면 기준 보드 중심(카메라 초점이 오는 자리)
SLOTS = [(255, 690), (825, 690), (255, 1200), (825, 1200)]
CARD_W, PHOTO_H = 330, 250
ZOOM = 1.85


def font(p, s):
    return ImageFont.truetype(p, int(s))


def ease_out(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def ease_back(t):
    t = max(0, min(1, t))
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def fit_font(d, text, path, size, maxw):
    s = size
    while s > 20:
        f = font(path, s)
        if d.textlength(text.replace("'", ""), font=f) <= maxw:
            return f
        s -= 2
    return font(path, s)


def draw_rich(d, xy, text, f, base, hi=YEL):
    x, y = xy
    for i, p in enumerate(text.split("'")):
        d.text((x, y), p, font=f, fill=hi if i % 2 else base, anchor="ls")
        x += d.textlength(p, font=f)


def pin(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 14, 18))
    d.ellipse((x - r * 0.73, y - r * 0.87, x + r * 0.47, y + r * 0.2), fill=(235, 60, 60))


# ---------- 정적 그림 ----------
def make_cork():
    random.seed(7)
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    # 확대해도 버틸 수 있게 보드보다 넓게(바깥 여백 포함) 만든다
    pad = 600
    cw, ch = bw + pad * 2, bh + pad * 2
    noise = Image.effect_noise((cw, ch), 60).convert("L")
    cork = ImageOps.colorize(noise, (52, 36, 24), (104, 76, 50)).filter(ImageFilter.GaussianBlur(1.1))
    speck = Image.effect_noise((cw, ch), 90).convert("L").point(lambda v: 255 if v > 215 else 0).filter(ImageFilter.GaussianBlur(0.6))
    cork.paste((40, 28, 18), (0, 0), speck.point(lambda v: v // 2))
    return cork, (BOARD[0] - pad, BOARD[1] - pad)


def make_vignette():
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    vig = Image.new("L", (bw, bh), 255)
    dv = ImageDraw.Draw(vig)
    for i in range(60):
        dv.rectangle((i * 3, i * 3, bw - i * 3, bh - i * 3), outline=int(255 * (i / 60) ** 1.6))
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    shade = Image.new("RGBA", (bw, bh), (8, 6, 5, 0))
    shade.putalpha(vig.point(lambda v: 255 - v))
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=26, fill=255)
    return shade, mask


def make_header(spec):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    lg = Image.open(LOGO).convert("RGBA")
    lh = 40
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    ov.alpha_composite(lg, (70, 110))
    tf = font(FX, 34)
    tw = d.textlength(spec["tag"], font=tf) + 36
    d.rounded_rectangle((70, 180, 70 + tw, 234), radius=10, fill=YEL)
    d.text((88, 207), spec["tag"], font=tf, fill=(15, 15, 15), anchor="lm")
    f = font(FB, 84)
    l1, l2 = spec["title"]
    draw_rich(d, (70, 330), l1, f, WHITE)
    draw_rich(d, (70, 432), l2, f, YEL, hi=YEL)
    d.rounded_rectangle(BOARD, radius=26, outline=(70, 50, 34), width=10)
    return ov


def subtitle_layer(b, alpha):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha <= 0:
        return ov
    d = ImageDraw.Draw(ov)
    if b.get("ctx"):
        d.text((70, 1530), b["ctx"], font=fit_font(d, b["ctx"], FM, 38, 940), fill=(200, 200, 200), anchor="ls")
    draw_rich(d, (70, 1630), b["l1"], fit_font(d, b["l1"], FB, 70, 940), WHITE)
    draw_rich(d, (70, 1725), b["l2"], fit_font(d, b["l2"], FB, 70, 940), YEL, hi=YEL)
    if alpha < 1:
        ov.putalpha(ov.getchannel("A").point(lambda v: int(v * alpha)))
    return ov


def photo_fit(im, w, h, fx=0.5, fy=0.4):
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    x = int((im.width - w) * fx)
    y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def make_card(c, base):
    """폴라로이드 카드(SS배 해상도). 반환: 이미지, 압정 위치(카드 기준, SS배)."""
    S = SS
    pad, cap_h, m = 14 * S, 92 * S, 20 * S
    cw, ch = CARD_W * S, PHOTO_H * S + pad + cap_h
    card = Image.new("RGBA", (cw + 2 * m, ch + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((m + 4 * S, m + 6 * S, m + 4 * S + cw, m + 6 * S + ch), fill=(0, 0, 0, 170))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)))
    d = ImageDraw.Draw(card)
    d.rectangle((m, m, m + cw, m + ch), fill=(238, 233, 222))
    src = Image.open(base / (c.get("img") or c.get("drawn"))).convert("RGB")
    ph = photo_fit(src, cw - 2 * pad, PHOTO_H * S - pad, c.get("fx", 0.5), c.get("fy", 0.35))
    if c.get("gray"):
        ph = ImageOps.grayscale(ph).convert("RGB")
    card.paste(ph, (m + pad, m + pad))
    f = fit_font(d, c["cap"], FB, 34 * S, cw - 2 * pad)
    d.text((m + pad, m + PHOTO_H * S + 46 * S), c["cap"], font=f, fill=(20, 20, 20), anchor="ls")
    if c.get("credit"):
        d.text((m + cw - pad, m + PHOTO_H * S + 80 * S), c["credit"], font=font(FM, 19 * S), fill=(110, 105, 98), anchor="rs")
    pp = (m + cw // 2, m + 6 * S)
    pin(d, pp[0], pp[1], 15 * S)
    return card, pp


def make_center(spec):
    S = SS
    cw, ch, m = 360 * S, 190 * S, 20 * S
    card = Image.new("RGBA", (cw + 2 * m, ch + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((m + 4 * S, m + 6 * S, m + 4 * S + cw, m + 6 * S + ch), fill=(0, 0, 0, 200))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * S)))
    d = ImageDraw.Draw(card)
    d.rectangle((m, m, m + cw, m + ch), fill=(20, 18, 18), outline=RED, width=6 * S)
    l1, l2 = spec["center"]
    cx, tw = m + cw // 2, cw - 30 * S
    if spec.get("center_img"):
        em = Image.open(Path("media") / spec["id"] / spec["center_img"]).convert("RGB").resize((118 * S, 118 * S), Image.LANCZOS)
        mk = Image.new("L", em.size, 0)
        ImageDraw.Draw(mk).ellipse((0, 0, em.width - 1, em.height - 1), fill=255)
        em.putalpha(mk)
        card.alpha_composite(em, (m + 22 * S, m + (ch - 118 * S) // 2 + 6 * S))
        cx, tw = m + 140 * S + (cw - 140 * S) // 2, cw - 160 * S
    d.text((cx, m + 98 * S), l1, font=fit_font(d, l1, FB, 50 * S, tw), fill=WHITE, anchor="ms")
    d.text((cx, m + 150 * S), l2, font=fit_font(d, l2, FM, 28 * S, tw), fill=(235, 90, 90), anchor="ms")
    pp = (m + cw // 2, m + 10 * S)
    pin(d, pp[0], pp[1], 15 * S)
    return card, pp


def make_stamp(text):
    S = SS
    s = Image.new("RGBA", (300 * S, 150 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((8 * S, 8 * S, 292 * S, 142 * S), radius=14 * S, outline=RED + (235,), width=10 * S)
    d.text((150 * S, 108 * S), text, font=fit_font(d, text, FB, 86 * S, 250 * S), fill=RED + (235,), anchor="ms")
    random.seed(3)
    n = Image.effect_noise(s.size, 80).convert("L").point(lambda v: 0 if v > 170 else 255)
    s.putalpha(Image.composite(s.getchannel("A"), Image.new("L", s.size, 0), n))
    return s.rotate(-12, expand=True, resample=Image.BICUBIC)


def string_pts(a, b, sag=60, n=40):
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n + sag * math.sin(math.pi * i / n)) for i in range(n + 1)]


# ---------- 렌더 ----------
def build(spec_path, shots_only=False):
    spec = json.loads(Path(spec_path).read_text())
    base = Path("media") / spec["id"]
    work = Path("/tmp/board_reel") / spec["id"]
    work.mkdir(parents=True, exist_ok=True)

    cork, cork_xy = make_cork()
    shade, bmask = make_vignette()
    header = make_header(spec)
    center, cpin = make_center(spec)
    stamp = make_stamp(spec.get("stamp", "표적"))
    stamps = [make_stamp(sc["stamp"]) if sc.get("stamp") else stamp for sc in spec["scenes"]]
    rot = [-4, 3, 3.5, -3]
    cards = []
    for i, sc in enumerate(spec["scenes"]):
        im, pp = make_card(sc["card"], base)
        im = im.rotate(rot[i % 4], expand=True, resample=Image.BICUBIC)
        # 회전 뒤 압정 위치(카드 중심 기준 회전)
        ang = math.radians(-rot[i % 4])
        ox, oy = pp[0] - (im.width - 0) / 2, pp[1] - im.height / 2
        cards.append((im, SLOTS[i]))
    # 압정의 보드 좌표(1배): 카드 위쪽 가운데
    card_h1 = (PHOTO_H * SS + 14 * SS + 92 * SS) / SS
    pins = [(sx, sy - card_h1 / 2 + 6) for sx, sy in SLOTS]
    center_pin = (C[0], C[1] - 190 / 2 + 10)

    seg = spec.get("scene_len", 3.8)
    intro = spec.get("intro_len", 0.6)
    recap_len = spec.get("recap_len", 3.4)
    cta_len = spec.get("cta_len", 2.6)
    n = len(cards)
    t_recap = intro + n * seg
    t_cta = t_recap + recap_len
    total = t_cta + cta_len
    nf = int(total * FPS)

    def camera(t):
        """(z, fx, fy): 보드 좌표 f가 화면 C에 오도록 z배."""
        if intro <= t < t_recap:
            i = int((t - intro) // seg)
            lt = t - intro - i * seg
            sx, sy = SLOTS[i]
            if lt < 0.55:
                k = ease_io(lt / 0.55)
            elif lt < 2.55:
                k = 1
            elif lt < 3.25:
                k = 1 - ease_io((lt - 2.55) / 0.7)
            else:
                k = 0
            z = 1 + (ZOOM - 1) * k
            return z, C[0] + (sx - C[0]) * k, C[1] + (sy - C[1]) * k
        if t >= t_recap:
            k = ease_out((t - t_recap) / 1.2)
            return 1 + 0.06 * k, C[0], C[1]
        return 1.0, C[0], C[1]

    def T(p, cam):
        z, fx, fy = cam
        return ((p[0] - fx) * z + C[0], (p[1] - fy) * z + C[1])

    def paste_sprite(canvas, sprite, center_xy, scale, alpha=1.0):
        w, h = max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))
        sp = sprite.resize((w, h), Image.BICUBIC if scale < 1 else Image.LANCZOS)
        if alpha < 1:
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
        canvas.alpha_composite(sp, (round(center_xy[0] - w / 2), round(center_xy[1] - h / 2)))

    def frame(t):
        cam = camera(t)
        z = cam[0]
        glow = 0.6 + 0.4 * math.sin((t - t_recap) * 6) if t >= t_recap else 0.0
        board = Image.new("RGBA", (W, H), (12, 11, 10, 255))
        # 코르크: 화면 → 보드 좌표 역변환해서 잘라 확대
        x0 = (0 - C[0]) / z + cam[1] - cork_xy[0]
        y0 = (0 - C[1]) / z + cam[2] - cork_xy[1]
        bg = cork.crop((round(x0), round(y0), round(x0 + W / z), round(y0 + H / z))).resize((W, H), Image.BILINEAR)
        board.paste(bg, (0, 0))
        # 실
        sl = ImageDraw.Draw(board)
        for i in range(n):
            t0 = intro + i * seg
            if t < t0 + 0.7:
                continue
            prog = ease_out((t - t0 - 0.7) / 2.4) if t < t0 + 3.1 else 1
            pts = [T(p, cam) for p in string_pts(pins[i], center_pin)]
            k = max(2, int(len(pts) * prog) + 1)
            seg_pts = pts[:k]
            if glow:
                sl.line(seg_pts, fill=(255, 60, 60, int(110 * glow)), width=round(16 * z), joint="curve")
            sl.line(seg_pts, fill=(120, 8, 10, 255), width=round(7 * z), joint="curve")
            sl.line(seg_pts, fill=(225, 30, 34, 255), width=round(4 * z), joint="curve")
        # 배후 카드
        paste_sprite(board, center, T(C, cam), z / SS)
        # 표적 카드 + 도장
        for i, (im, slot) in enumerate(cards):
            t0 = intro + i * seg
            if t < t0 + 0.15:
                continue
            lt = t - t0 - 0.15
            drop = ease_back(lt / 0.45)
            sc = (1.3 - 0.3 * drop) if lt < 0.45 else 1.0
            pos = T((slot[0], slot[1] - 40 * (1 - ease_out(lt / 0.45))), cam)
            paste_sprite(board, im, pos, z * sc / SS, min(1, lt / 0.2))
            st = lt - 0.85
            if st > 0:
                k = min(1, st / 0.18)
                s = 1.8 - 0.8 * ease_out(k)
                paste_sprite(board, stamps[i], T((slot[0] + 85, slot[1] + 30), cam), z * s * 0.72 / SS, k)
        if any(t >= intro + i * seg + 0.7 for i in range(n)):
            cp = T(center_pin, cam)
            pin(ImageDraw.Draw(board), cp[0], cp[1], 15 * z)
        if glow:
            board.alpha_composite(Image.new("RGBA", (W, H), (180, 0, 0, int(40 * glow))))
        # 보드 창(viewport)만 남기기
        bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
        win = board.crop(BOARD)
        win.alpha_composite(shade)
        fr = Image.new("RGBA", (W, H), (12, 11, 10, 255))
        fr.paste(win, BOARD[:2], bmask)
        fr.alpha_composite(header)
        # 자막
        if t < intro:
            b, a = spec["scenes"][0]["b"], 0
        elif t < t_recap:
            i = int((t - intro) // seg)
            b, a = spec["scenes"][i]["b"], min(1, (t - intro - i * seg) / 0.25)
        else:
            b, a = spec["recap"], min(1, (t - t_recap) / 0.3)
        fr.alpha_composite(subtitle_layer(b, a))
        # CTA
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
            bwid = dc.textlength(bt, font=bf) + 70
            dc.rounded_rectangle((W // 2 - bwid // 2, 1140, W // 2 + bwid // 2, 1230), radius=45, outline=WHITE, width=4)
            dc.text((W // 2, 1186), bt, font=bf, fill=WHITE, anchor="mm")
            if k < 1:
                ct.putalpha(ct.getchannel("A").point(lambda v: int(v * k)))
            fr.alpha_composite(ct)
        return fr.convert("RGB")

    if shots_only:
        times = []
        for i in range(n):
            times += [intro + i * seg + 1.6, intro + i * seg + seg - 0.2]
        times += [t_cta - 0.3, total - 0.2]
        for k, tt in enumerate(times):
            frame(tt).save(work / f"shot{k:02d}.jpg", quality=88)
        print("shots:", work, len(times))
        return
    frame(intro + 1.6).save(base / "board_reel_cover.jpg", quality=93)
    silent = base / "board_reel_nomusic.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    for i in range(nf):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    bgm = spec.get("bgm")
    if bgm:
        af = f"volume={bgm.get('vol', 0.5)},afade=t=in:st=0:d=0.3,afade=t=out:st={total - 1.5:.2f}:d=1.5"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-ss", str(bgm.get("start", 0)), "-t", f"{total:.2f}", "-i", bgm["file"],
                        "-af", af, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(base / "board_reel.mp4")], check=True)
    print("done:", base, f"{total:.1f}s")


if __name__ == "__main__":
    build(sys.argv[1], "--shots" in sys.argv)
