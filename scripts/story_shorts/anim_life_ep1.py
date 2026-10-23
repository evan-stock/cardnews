# 댓글로 키우는 아이 1화 — 코드로 그린 캐릭터 시험판 (2026.10.23)
# 사용: python3 scripts/story_shorts/anim_life_ep1.py <출력폴더>
# 결과: <출력>/s1~s5.mp4 (띠 아래 영역 1080x1490, 파이프라인 scenes[].video 용)
#       <출력>/preview.mp4 (1080x1920, 제목 띠 + 자막 + 효과음, 내레이션 없음)
import math, os, random, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(ROOT, "assets/fonts/Jua-Regular.ttf")
SFX = os.path.join(ROOT, "assets/sfx")
W, H, BAND, FH, FPS = 1080, 1490, 430, 1920, 30
F = lambda s: ImageFont.truetype(FONT, s)

YEL = (255, 212, 59); WHT = (255, 255, 255); INK = (40, 32, 30)
SKIN = (255, 222, 196); CHEEK = (255, 150, 150); HAIR = (60, 42, 32)
MINT = (150, 220, 200); CREAM = (255, 246, 230)

ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
def back(t):  # 튕기며 등장
    if t <= 0: return 0
    if t >= 1: return 1
    c = 1.9; t -= 1
    return 1 + (c + 1) * t ** 3 + c * t ** 2

# ---------------- 대본 ----------------
SCENES = [
    dict(id="s1", say="방금 한 아이가 태어났습니다. 이 아이의 인생은 이제, 여러분 댓글이 정합니다.",
         sfx=[("pop", 0.5)]),
    dict(id="s2", say="이름은 김댓글. 키 오십 센티, 몸무게 삼 점 이 킬로그램입니다.",
         sub="이름은 김댓글. 키 50센티, 몸무게 3.2kg입니다.", sfx=[]),
    dict(id="s3", say="아빠는 평범한 회사원, 엄마는 분식집 사장님. 통장 잔고는 팔십칠만 원입니다.",
         sub="아빠는 평범한 회사원, 엄마는 분식집 사장님. 통장 잔고는 87만 원입니다.", sfx=[("ding", 5.2)]),
    dict(id="s4", say="그리고 첫 번째 갈림길, 돌잡이입니다. 이 아이는 무엇을 잡을까요?",
         sfx=[("question", 3.4)]),
    dict(id="s5", say="댓글 일등이 이 아이의 미래가 됩니다. 결과는 다음 화에서 공개합니다.",
         sub="댓글 1등이 이 아이의 미래가 됩니다. 결과는 다음 화에서 공개합니다.", sfx=[("tada", 0.3)]),
]
HOOK = ["댓글로 키우는 아이 1화", "인생은 '댓글'이 정한다"]

def syl(s): return sum(1 for c in s if '가' <= c <= '힣' or c.isalnum())
for sc in SCENES:  # 필재 1.1배 기준 초당 약 6.3음절 + 여유
    sc["dur"] = round(syl(sc["say"]) / 6.3 + 0.6, 2) + float(os.environ.get("LIFE_HOLD", 0))
# LIFE_HOLD: 파이프라인용 장면 영상은 목소리보다 길게(여유 초) 만든다. 실제 길이는 목소리에 맞춰 잘린다.

# ---------------- 그리기 도구 ----------------
def bg(top=(255, 244, 222), bot=(255, 228, 205)):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))
    r = random.Random(1)
    for _ in range(60):
        x, y, s = r.randrange(W), r.randrange(H), r.choice([6, 8, 10])
        d.ellipse((x, y, x + s, y + s), fill=(255, 255, 255))
    return im

def ctext(d, x, y, s, size, fill=INK, stroke=0, sfill=(0, 0, 0), anchor="mm"):
    d.text((x, y), s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

def blink(t, seed=0):
    p = (t + seed) % 3.1
    return 0.15 if p < 0.12 else 1.0

def head(d, cx, cy, r, t, expr="smile", seed=0, hair="baby"):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SKIN, outline=INK, width=max(3, int(r * 0.06)))
    if hair == "baby":  # 정수리 머리카락 한 가닥 = 김댓글 트레이드마크
        d.arc((cx - r * 0.25, cy - r * 1.35, cx + r * 0.35, cy - r * 0.75), 160, 360, fill=INK, width=max(3, int(r * 0.07)))
    elif hair == "dad":
        d.chord((cx - r, cy - r, cx + r, cy + r * 0.2), 180, 360, fill=HAIR)
    elif hair == "mom":
        d.ellipse((cx - r * 1.05, cy - r * 1.05, cx + r * 1.05, cy + r * 0.3), fill=HAIR)
        d.ellipse((cx + r * 0.55, cy - r * 1.25, cx + r * 1.15, cy - r * 0.65), fill=HAIR)  # 똥머리
        d.ellipse((cx - r * 0.85, cy - r * 0.55, cx + r * 0.85, cy + r * 0.95), fill=SKIN)
    ey, ex, er = cy + r * 0.05, r * 0.36, r * 0.11
    if expr == "cry":
        for s in (-1, 1):
            d.line([(cx + s * ex - er * 1.3, ey - er), (cx + s * ex + er * 1.3, ey + er * 0.3)], fill=INK, width=max(3, int(r * 0.06)))
        d.ellipse((cx - r * 0.2, cy + r * 0.32, cx + r * 0.2, cy + r * 0.7), fill=(180, 60, 70), outline=INK, width=3)
    else:
        k = blink(t, seed)
        for s in (-1, 1):
            d.ellipse((cx + s * ex - er, ey - er * k, cx + s * ex + er, ey + er * k), fill=INK)
        if expr == "smile":
            d.arc((cx - r * 0.2, cy + r * 0.2, cx + r * 0.2, cy + r * 0.52), 20, 160, fill=INK, width=max(3, int(r * 0.06)))
        elif expr == "o":
            d.ellipse((cx - r * 0.09, cy + r * 0.32, cx + r * 0.09, cy + r * 0.52), fill=INK)
    for s in (-1, 1):
        d.ellipse((cx + s * r * 0.6 - r * 0.15, cy + r * 0.25, cx + s * r * 0.6 + r * 0.15, cy + r * 0.42), fill=CHEEK)

def baby(d, cx, cy, sc, t, expr="smile"):
    r = 95 * sc
    d.rounded_rectangle((cx - r * 0.95, cy + r * 0.55, cx + r * 0.95, cy + r * 2.1), radius=int(r * 0.7), fill=MINT, outline=INK, width=max(3, int(r * 0.06)))
    head(d, cx, cy, r, t, expr)

def toddler(d, cx, cy, sc, t, expr="o", arm=0.0):
    r = 85 * sc
    d.rounded_rectangle((cx - r * 0.8, cy + r * 0.8, cx + r * 0.8, cy + r * 2.0), radius=int(r * 0.4), fill=(255, 190, 90), outline=INK, width=4)
    # 앞으로 뻗는 팔(arm: -1 왼쪽 ~ 1 오른쪽)
    hx, hy = cx + arm * 260 * sc, cy + r * 2.35
    d.line([(cx + r * 0.5, cy + r * 1.1), (hx, hy)], fill=SKIN, width=int(r * 0.28))
    d.ellipse((hx - r * 0.2, hy - r * 0.2, hx + r * 0.2, hy + r * 0.2), fill=SKIN, outline=INK, width=3)
    head(d, cx, cy, r, t, expr)

def adult(d, cx, cy, sc, t, who):
    r = 80 * sc
    body = (90, 110, 160) if who == "dad" else (240, 140, 120)
    d.rounded_rectangle((cx - r * 0.95, cy + r * 0.85, cx + r * 0.95, cy + r * 2.9), radius=int(r * 0.45), fill=body, outline=INK, width=4)
    if who == "dad":
        d.polygon([(cx, cy + r * 0.95), (cx - r * 0.15, cy + r * 1.2), (cx, cy + r * 2.0), (cx + r * 0.15, cy + r * 1.2)], fill=(220, 60, 60))
    else:
        d.rounded_rectangle((cx - r * 0.6, cy + r * 1.4, cx + r * 0.6, cy + r * 2.7), radius=12, fill=WHT, outline=INK, width=3)
    head(d, cx, cy, r, t, "smile", seed=1.3 if who == "dad" else 0.7, hair=who)

def bubble(d, x, y, s, size, a=1.0, fill=WHT):
    ft = F(size); w = d.textlength(s, font=ft); pad = size * 0.45
    box = (x - w / 2 - pad, y - size * 0.75, x + w / 2 + pad, y + size * 0.75)
    d.rounded_rectangle(box, radius=int(size * 0.6), fill=fill, outline=INK, width=5)
    d.polygon([(x - 30, box[3] - 3), (x + 10, box[3] - 3), (x - 40, box[3] + 40)], fill=fill, outline=INK)
    d.line([(x - 28, box[3] - 3), (x + 8, box[3] - 3)], fill=fill, width=8)
    d.text((x, y), s, font=ft, fill=INK, anchor="mm")

def scaled(layer_fn, cx, cy, k):
    """layer_fn(d) 로 그린 투명 레이어를 (cx,cy) 기준으로 k배"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer_fn(ImageDraw.Draw(lay))
    if k >= 0.999: return lay
    k = max(k, 0.01); w, h = int(W * k), int(H * k)
    sm = lay.resize((w, h), Image.LANCZOS); out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sm, (int(cx - cx * k), int(cy - cy * k))); return out

def label(d, y, s, size=88, fill=YEL):
    ctext(d, W / 2, y, s, size, fill, stroke=8, sfill=INK)

# 자막 자리(띠 아래 기준 약 y 780~1050)는 비워 둔다.
ITEMS = [("연필", (90, 170, 240)), ("돈", (90, 190, 110)), ("마이크", (240, 110, 140))]

def draw_item(d, kind, cx, cy, s=1.0):
    if kind == "연필":
        d.polygon([(cx - 90 * s, cy - 18 * s), (cx + 60 * s, cy - 18 * s), (cx + 100 * s, cy), (cx + 60 * s, cy + 18 * s), (cx - 90 * s, cy + 18 * s)], fill=(255, 200, 60), outline=INK)
        d.polygon([(cx + 60 * s, cy - 18 * s), (cx + 100 * s, cy), (cx + 60 * s, cy + 18 * s)], fill=(240, 210, 170), outline=INK)
        d.rectangle((cx - 105 * s, cy - 18 * s, cx - 90 * s, cy + 18 * s), fill=(250, 150, 170), outline=INK)
    elif kind == "돈":
        d.rounded_rectangle((cx - 85 * s, cy - 45 * s, cx + 85 * s, cy + 45 * s), radius=8, fill=(170, 220, 160), outline=INK, width=4)
        d.ellipse((cx - 25 * s, cy - 25 * s, cx + 25 * s, cy + 25 * s), outline=INK, width=4)
    else:
        d.ellipse((cx - 38 * s, cy - 75 * s, cx + 38 * s, cy + 1 * s), fill=(150, 150, 160), outline=INK, width=4)
        d.rounded_rectangle((cx - 16 * s, cy - 5 * s, cx + 16 * s, cy + 75 * s), radius=8, fill=(50, 50, 60), outline=INK, width=3)

# ---------------- 장면 ----------------
BASE = bg()

def s1(t, dur):
    im = BASE.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    for i in range(10):  # 반짝이
        a = (t * 0.8 + i * 0.37) % 1; x = 540 + 380 * math.cos(i * 0.63 + t * 0.4); y = 380 + 260 * math.sin(i * 1.1 + t * 0.3)
        r = 10 * math.sin(a * math.pi); d.polygon([(x, y - r * 2), (x + r, y), (x, y + r * 2), (x - r, y)], fill=YEL)
    k = back(t / 0.5)
    im.alpha_composite(scaled(lambda dd: baby(dd, 540, 330, 1.7, t, "cry" if 0.5 < t < 2.4 else "smile"), 540, 450, k))
    d = ImageDraw.Draw(im)
    if 0.5 < t < 2.4:
        j = 6 * math.sin(t * 40)
        bubble(d, 790 + j, 140, "응애!!", 80)
    a = ease((t - 2.6) / 0.4)
    if a > 0:
        label(d, 1180 + (1 - a) * 80, "D+0 탄생", 110)
        ctext(d, W / 2, 1330, "인생 결정권: 여러분", 64, INK)
    return im

def s2(t, dur):
    im = BASE.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    baby(d, 250, 300, 1.05, t, "smile")
    x0 = 1080 - ease(t / 0.5) * 640  # 출생 카드 미끄러져 들어옴
    d.rounded_rectangle((x0, 120, x0 + 600, 660), radius=30, fill=WHT, outline=INK, width=6)
    d.rounded_rectangle((x0, 120, x0 + 600, 220), radius=30, fill=(255, 120, 120), outline=INK, width=6)
    d.rectangle((x0 + 4, 180, x0 + 596, 220), fill=(255, 120, 120))
    ctext(d, x0 + 300, 172, "출생 카드", 60, WHT, stroke=4, sfill=INK)
    rows = [("이름", "김댓글", 0.6), ("키", "50cm", 1.7), ("몸무게", "3.2kg", 2.6)]
    for i, (k, v, at) in enumerate(rows):
        a = back((t - at) / 0.35)
        if a <= 0: continue
        y = 300 + i * 120
        ctext(d, x0 + 60, y, k, 54, (130, 120, 115), anchor="lm")
        ctext(d, x0 + 540, y, v, int(72 * min(a, 1.2)), INK, anchor="rm")
        d.line([(x0 + 50, y + 55), (x0 + 550, y + 55)], fill=(230, 220, 210), width=3)
    a = ease((t - 0.8) / 0.4)
    if a > 0: label(d, 1200 + (1 - a) * 60, "주인공: 김댓글", 100)
    return im

def s3(t, dur):
    im = BASE.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    for who, x, at, lab in (("dad", 230, 0.0, "아빠: 회사원"), ("mom", 850, 1.3, "엄마: 분식집 사장")):
        k = back((t - at) / 0.45)
        if k > 0:
            im.alpha_composite(scaled(lambda dd, w=who, xx=x: adult(dd, xx, 230, 1.15, t, w), x, 450, k))
            d = ImageDraw.Draw(im)
            if k > 0.9: ctext(d, x, 640, lab, 52, INK, stroke=0)
    baby(d, 540, 420, 0.75, t, "smile")
    if t > 2.6:  # 통장 잔고 카운터
        p = ease((t - 2.6) / 2.4); won = int(870000 * p / 1000) * 1000
        d.rounded_rectangle((170, 1090, 910, 1400), radius=26, fill=(60, 120, 200), outline=INK, width=6)
        ctext(d, 540, 1150, "통장 잔고", 56, WHT)
        ctext(d, 540, 1280, f"{won:,}원", 120, YEL, stroke=6, sfill=INK)
    return im

def s4(t, dur):
    im = BASE.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    a = ease(t / 0.4)
    label(d, 90 - (1 - a) * 60, "첫 번째 갈림길: 돌잡이", 92)
    # 아이: 팔이 아이템 사이를 오간다
    arm = math.sin(max(0, t - 0.8) * 2.2) if t < dur - 0.6 else 0
    toddler(d, 540, 275, 1.1, t, "o", arm)
    # 돌상
    d.rounded_rectangle((60, 560, 1020, 740), radius=24, fill=(205, 140, 90), outline=INK, width=6)
    d.rectangle((110, 740, 150, 780), fill=(160, 100, 60)); d.rectangle((930, 740, 970, 780), fill=(160, 100, 60))
    for i, (name, col) in enumerate(ITEMS):
        cx = 220 + i * 320; k = back((t - 0.5 - i * 0.35) / 0.35)
        if k <= 0: continue
        im.alpha_composite(scaled(lambda dd, n=name, c=cx: draw_item(dd, n, c, 640, 1.0), cx, 640, k)); d = ImageDraw.Draw(im)
        d.ellipse((cx - 34, 1100 - 34, cx + 34, 1100 + 34), fill=col, outline=INK, width=5)
        ctext(d, cx, 1100, str(i + 1), 52, WHT, stroke=3, sfill=INK)
        ctext(d, cx, 1190, name, 72, INK)
    if t > 3.4:
        b = 14 * abs(math.sin((t - 3.4) * 6))
        ctext(d, 840, 210 - b, "?", 150, (255, 90, 90), stroke=8, sfill=INK)
    return im

def s5(t, dur):
    im = BASE.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    baby(d, 540, 250, 1.1, t, "o")
    label(d, 620, "댓글로 골라주세요", 100)
    for i, (name, col) in enumerate(ITEMS):
        x = 200 + i * 340; pul = 1 + 0.06 * math.sin(t * 5 + i * 1.3)
        w2, h2 = 140 * pul, 110 * pul
        d.rounded_rectangle((x - w2, 1250 - h2, x + w2, 1250 + h2), radius=30, fill=col, outline=INK, width=6)
        ctext(d, x, 1210, f"{i + 1}번", 56, WHT, stroke=4, sfill=INK)
        ctext(d, x, 1290, name, 74, WHT, stroke=5, sfill=INK)
    a = ease((t - 2.0) / 0.4)
    if a > 0: ctext(d, W / 2, 1430, "댓글 1등이 다음 화의 운명", 54, INK)
    return im

FUNCS = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5)

# ---------------- 자막·제목 ----------------
def chunks(text, n=8):
    out = []
    for sent in re.split(r"(?<=[.,?!])\s+", text):  # 문장·쉼표에서 먼저 끊고 8자 단위로
        cur = ""
        for w in sent.split():
            cand = (cur + " " + w).strip()
            if cur and len(cand.replace(" ", "")) > n: out.append(cur); cur = w
            else: cur = cand
        if cur: out.append(cur)
    return out

def title_band():
    band = Image.new("RGBA", (W, BAND), (0, 0, 0, 255)); d = ImageDraw.Draw(band)
    for i, line in enumerate(HOOK):
        y = 150 + i * 135; ft = F(96)
        parts = line.split("'"); total = sum(d.textlength(p, font=ft) for p in parts); x = (W - total) / 2
        for j, p in enumerate(parts):
            col = YEL if (i == 0 or j % 2 == 1) else WHT
            d.text((x, y), p, font=ft, fill=col, anchor="lm"); x += d.textlength(p, font=ft)
    return band

def ffw(path, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)

def main():
    band = title_band(); sub_ft = F(116)
    full = ffw(f"{OUT}/_preview_noaudio.mp4", W, FH)
    t0 = 0.0; sfx_events = []
    for sc in SCENES:
        dur = sc["dur"]; n = int(round(dur * FPS))
        cl = ffw(f"{OUT}/{sc['id']}.mp4", W, H)
        subs = chunks(sc.get("sub", sc["say"]))
        lens = [max(1, len(s.replace(" ", ""))) for s in subs]; tot = sum(lens)
        speak = dur - 0.5; edges = [0.15]
        for L in lens: edges.append(edges[-1] + speak * L / tot)
        for f, at in sc["sfx"]: sfx_events.append((f, t0 + at))
        for i in range(n):
            t = i / FPS; im = FUNCS[sc["id"]](t, dur).convert("RGB")
            cl.stdin.write(im.tobytes())
            fr = Image.new("RGB", (W, FH)); fr.paste(band.convert("RGB"), (0, 0)); fr.paste(im, (0, BAND))
            d = ImageDraw.Draw(fr)
            for k, s in enumerate(subs):
                if edges[k] <= t < edges[k + 1] or (k == len(subs) - 1 and t >= edges[k]):
                    d.text((W / 2, int(FH * 0.68)), s, font=sub_ft, fill=WHT, stroke_width=10, stroke_fill=(0, 0, 0), anchor="mm")
            full.stdin.write(fr.tobytes())
        cl.stdin.close(); cl.wait(); t0 += dur
    full.stdin.close(); full.wait()
    # 효과음 섞기
    total = t0; ins = ["-i", f"{OUT}/_preview_noaudio.mp4", "-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=44100:cl=stereo"]
    flt = []; tags = ["[1:a]"]
    for k, (f, at) in enumerate(sfx_events):
        ins += ["-i", f"{SFX}/{f}.mp3"]; ms = int(at * 1000)
        flt.append(f"[{k + 2}:a]adelay={ms}|{ms},volume=1.6[a{k}]"); tags.append(f"[a{k}]")
    flt.append("".join(tags) + f"amix=inputs={len(tags)}:normalize=0:duration=first[aout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-shortest", f"{OUT}/preview.mp4"], check=True)
    os.remove(f"{OUT}/_preview_noaudio.mp4")
    print("total", round(total, 1), "s", [(s["id"], s["dur"]) for s in SCENES])

if __name__ == "__main__":
    main()
