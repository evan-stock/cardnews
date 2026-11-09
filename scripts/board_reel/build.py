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
    hook = spec.get("hook")  # 첫 장면 사진을 화면 가득 보여준 뒤 카드로 줄어들며 꽂힘
    hook_len = 1.0 if hook else 0.0
    shrink = 0.45 if hook else 0.0
    intro = hook_len + shrink if hook else spec.get("intro_len", 0.6)
    recap_len = spec.get("recap_len", 3.4)
    cta_len = spec.get("cta_len", 2.6)
    n = len(cards)
    t_recap = intro + n * seg
    t_cta = t_recap + recap_len
    total = t_cta + cta_len
    nf = int(total * FPS)

    # ---- 미리 만들어 두는 것들 ----
    # 스포트라이트(가운데 밝고 바깥 어둡게)
    yy, xx = [], []
    spot = Image.radial_gradient("L").resize((1400, 1400), Image.BILINEAR)  # 가운데 0 → 바깥 255
    def spot_layer(strength):
        a = spot.point(lambda v: int(min(255, max(0, (v - 60) * 1.6)) * strength))
        lay = Image.new("RGBA", spot.size, (0, 0, 0, 255))
        lay.putalpha(a)
        out = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * strength * 0.9)))
        out.paste(lay, (C[0] - 700, C[1] - 700))
        return out
    spots = [spot_layer(k / 10) for k in range(11)]
    # 필름 그레인(6장 돌려 쓰기)
    grains = []
    for g in range(6):
        nz = Image.effect_noise((W // 2, H // 2), 40).resize((W, H), Image.NEAREST)
        gl = Image.new("RGBA", (W, H), (128, 128, 128, 0))
        gl.putalpha(nz.point(lambda v: int(abs(v - 128) * 0.28)))
        gl = Image.merge("RGBA", (nz, nz, nz, gl.getchannel("A")))
        grains.append(gl)
    # 색보정(어두운 곳 살짝 청록, 밝은 곳 살짝 주황)
    def lut(ch):
        out = []
        for v in range(256):
            x = v / 255
            if ch == 0:
                y = x + 0.04 * x * x - 0.02 * (1 - x) * (1 - x)
            elif ch == 1:
                y = x + 0.006 * (1 - x) * (1 - x)
            else:
                y = x + 0.018 * (1 - x) * (1 - x) - 0.05 * x * x
            y = (y - 0.5) * 1.06 + 0.5 - 0.012
            out.append(int(max(0, min(1, y)) * 255))
        return out
    LUT = lut(0) + lut(1) + lut(2)
    # 훅 사진(첫 카드와 같은 구도)
    if hook:
        c0 = spec["scenes"][0]["card"]
        src = Image.open(base / hook.get("img", c0.get("img"))).convert("RGB")
        hook_img = photo_fit(src, 1302, 1018, c0.get("fx", 0.5), c0.get("fy", 0.35))  # 302:236 비율

    def scene_k(lt, i):
        if lt < 0.55:
            return 1.0 if (hook and i == 0) else ease_io(lt / 0.55)
        if lt < 2.55:
            return 1.0
        if lt < 3.25:
            return 1 - ease_io((lt - 2.55) / 0.7)
        return 0.0

    def camera(t):
        """(z, fx, fy, zoomk): 보드 좌표 f가 화면 C에 오도록 z배."""
        if hook and t < intro:
            sx, sy = SLOTS[0]
            return ZOOM, sx, sy, 1.0
        if intro <= t < t_recap:
            i = int((t - intro) // seg)
            lt = t - intro - i * seg
            sx, sy = SLOTS[i]
            k = scene_k(lt, i)
            return 1 + (ZOOM - 1) * k, C[0] + (sx - C[0]) * k, C[1] + (sy - C[1]) * k, k
        if t >= t_recap:
            k = ease_out((t - t_recap) / 1.2)
            return 1 + 0.06 * k, C[0], C[1], 0.0
        return 1.0, C[0], C[1], 0.0

    def shake(t):
        """핸드헬드 흔들림 + 도장 찍힐 때 쿵."""
        dx = 2.6 * math.sin(t * 1.3) + 1.4 * math.sin(t * 2.9 + 1)
        dy = 2.2 * math.sin(t * 1.1 + 2) + 1.2 * math.sin(t * 3.3)
        for i in range(n):
            st = t - (intro + i * seg + 0.15 + (0.6 if hook and i == 0 else 0.85))
            if 0 <= st < 0.3:
                a = 14 * (1 - st / 0.3)
                dx += a * math.sin(st * 90)
                dy += a * math.cos(st * 77)
        return dx, dy

    def string_sag(t, i):
        done = intro + i * seg + 0.7 + 2.4
        if t < done:
            return 60
        u = t - done
        return 60 + 22 * math.sin(u * 14) * math.exp(-u * 4)

    def paste_sprite(canvas, sprite, center_xy, scale, alpha=1.0):
        w, h = max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))
        sp = sprite.resize((w, h), Image.BICUBIC if scale < 1 else Image.LANCZOS)
        if alpha < 1:
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
        canvas.alpha_composite(sp, (round(center_xy[0] - w / 2), round(center_xy[1] - h / 2)))

    def subtitle(b, lt):
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if lt < 0:
            return ov
        d = ImageDraw.Draw(ov)
        rows = []
        if b.get("ctx"):
            rows.append(("ctx", b["ctx"], 1530))
        rows += [("l1", b["l1"], 1630), ("l2", b["l2"], 1725)]
        for r, (kind, text, y) in enumerate(rows):
            u = (lt - r * 0.1) / 0.32
            if u <= 0:
                continue
            a = min(1, u)
            off = int(28 * (1 - ease_out(u)))
            lay = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            base_y = 100
            if kind == "ctx":
                dl.text((70, base_y), text, font=fit_font(dl, text, FM, 38, 940), fill=(200, 200, 200), anchor="ls")
            elif kind == "l2":
                draw_rich(dl, (70, base_y), text, fit_font(dl, text, FB, 70, 940), YEL, hi=YEL)
            else:
                f = fit_font(dl, text, FB, 70, 940)
                x = 70
                wipe = ease_out((lt - 0.45) / 0.3)
                for i2, part in enumerate(text.split("'")):
                    w2 = dl.textlength(part, font=f)
                    if i2 % 2 and wipe > 0:
                        dl.rectangle((x - 6, base_y - 62, x - 6 + (w2 + 12) * wipe, base_y + 12), fill=YEL)
                        dl.text((x, base_y), part, font=f, fill=(15, 15, 15) if wipe > 0.5 else WHITE, anchor="ls")
                    else:
                        dl.text((x, base_y), part, font=f, fill=WHITE, anchor="ls")
                    x += w2
            if a < 1:
                lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * a)))
            ov.alpha_composite(lay, (0, y - base_y + off))
        return ov

    def frame(t, fi=0):
        z, fx, fy, zk = camera(t)
        sx_, sy_ = shake(t)
        Cs = (C[0] + sx_, C[1] + sy_)

        def T(p):
            return ((p[0] - fx) * z + Cs[0], (p[1] - fy) * z + Cs[1])

        glow = 0.6 + 0.4 * math.sin((t - t_recap) * 6) if t >= t_recap else 0.0
        board = Image.new("RGBA", (W, H), (12, 11, 10, 255))
        x0 = (0 - Cs[0]) / z + fx - cork_xy[0]
        y0 = (0 - Cs[1]) / z + fy - cork_xy[1]
        bg = cork.crop((round(x0), round(y0), round(x0 + W / z), round(y0 + H / z))).resize((W, H), Image.BILINEAR)
        if zk > 0.05:
            bg = bg.filter(ImageFilter.GaussianBlur(3.2 * zk))
        board.paste(bg, (0, 0))
        sl = ImageDraw.Draw(board)
        for i in range(n):
            t0 = intro + i * seg
            if t < t0 + 0.7:
                continue
            prog = ease_out((t - t0 - 0.7) / 2.4) if t < t0 + 3.1 else 1
            pts = [T(p) for p in string_pts(pins[i], center_pin, sag=string_sag(t, i))]
            k = max(2, int(len(pts) * prog) + 1)
            seg_pts = pts[:k]
            if glow:
                sl.line(seg_pts, fill=(255, 60, 60, int(110 * glow)), width=round(16 * z), joint="curve")
            sl.line(seg_pts, fill=(120, 8, 10, 255), width=round(7 * z), joint="curve")
            sl.line(seg_pts, fill=(225, 30, 34, 255), width=round(4 * z), joint="curve")
        paste_sprite(board, center, T(C), z / SS)
        dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dust)
        for i, (im, slot) in enumerate(cards):
            t0 = intro + i * seg
            first = hook and i == 0
            if t < t0 + (0 if first else 0.15):
                continue
            lt = t - t0 - (0 if first else 0.15)
            if first:
                sc, dy, al = 1.0, 0, 1.0
            else:
                drop = ease_back(lt / 0.45)
                sc = (1.3 - 0.3 * drop) if lt < 0.45 else 1.0
                dy, al = 40 * (1 - ease_out(lt / 0.45)), min(1, lt / 0.2)
            paste_sprite(board, im, T((slot[0], slot[1] - dy)), z * sc / SS, al)
            st = lt - (0.6 if first else 0.85)
            if st > 0:
                k = min(1, st / 0.18)
                s = 1.8 - 0.8 * ease_out(k)
                sp = T((slot[0] + 85, slot[1] + 30))
                paste_sprite(board, stamps[i], sp, z * s * 0.72 / SS, k)
                if 0.15 < st < 0.75:
                    u = (st - 0.15) / 0.6
                    rnd = random.Random(i * 31)
                    for q in range(16):
                        ang = rnd.uniform(0, 2 * math.pi)
                        dist = rnd.uniform(60, 170) * z * ease_out(u)
                        r = rnd.uniform(2, 5) * z
                        px, py = sp[0] + math.cos(ang) * dist, sp[1] + math.sin(ang) * dist + 30 * u * u * z
                        dd.ellipse((px - r, py - r, px + r, py + r), fill=(230, 215, 190, int(200 * (1 - u))))
        board.alpha_composite(dust)
        if any(t >= intro + i * seg + 0.7 for i in range(n)):
            cp = T(center_pin)
            pin(ImageDraw.Draw(board), cp[0], cp[1], 15 * z)
        if glow:
            board.alpha_composite(Image.new("RGBA", (W, H), (180, 0, 0, int(40 * glow))))
        # 스포트라이트: 확대할수록 바깥이 더 어둡게
        board.alpha_composite(spots[min(10, round((0.25 + 0.5 * zk) * 10))])
        win = board.crop(BOARD)
        win.alpha_composite(shade)
        fr = Image.new("RGBA", (W, H), (12, 11, 10, 255))
        fr.paste(win, BOARD[:2], bmask)
        # 훅: 사진이 화면 가득 → 첫 카드 사진 자리로 줄어듦
        if hook and t < intro:
            tz = ZOOM
            target_c = (C[0] + sx_, C[1] - 46 * tz + sy_)
            tw, th = 302 * tz, 236 * tz
            if t < hook_len:
                u = t / hook_len
                cw, ch = 1080 * (1.08 - 0.06 * u), 844 * (1.08 - 0.06 * u)
                cx, cy = C[0], C[1]
                fr.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)))
            else:
                u = ease_io((t - hook_len) / shrink)
                cw = 1080 * 1.02 + (tw - 1080 * 1.02) * u
                ch = 844 * 1.02 + (th - 844 * 1.02) * u
                cx = C[0] + (target_c[0] - C[0]) * u
                cy = C[1] + (target_c[1] - C[1]) * u
                fr.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - u)))))
            hp = hook_img.resize((round(cw), round(ch)), Image.BICUBIC).convert("RGBA")
            fr.alpha_composite(hp, (round(cx - cw / 2), round(cy - ch / 2)))
        fr = fr.convert("RGB").point(LUT).convert("RGBA")
        fr.alpha_composite(grains[fi % 6])
        fr.alpha_composite(header)
        # 자막
        if t < t_recap:
            i = max(0, int((t - intro) // seg)) if t >= intro else 0
            lt = (t - intro - i * seg) if t >= intro else t
            if i == 0:
                lt = t  # 첫 자막은 처음부터
            fr.alpha_composite(subtitle(spec["scenes"][i]["b"], lt))
        else:
            fr.alpha_composite(subtitle(spec["recap"], t - t_recap))
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
        times = [0.3, hook_len + shrink * 0.5] if hook else []
        for i in range(n):
            times += [intro + i * seg + 1.0, intro + i * seg + seg - 0.2]
        times += [t_cta - 0.3, total - 0.2]
        for k, tt in enumerate(times):
            frame(tt, k).save(work / f"shot{k:02d}.jpg", quality=88)
        print("shots:", work, len(times))
        return
    silent = base / "board_reel_nomusic.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    for i in range(nf):
        p.stdin.write(frame(i / FPS, i).tobytes())
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
