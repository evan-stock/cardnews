# 댓글로 키우는 아이 1화 v3 — 3D 렌더 캐릭터(life_3d·life_3d2) 버전 (2026.10.23)
# 사용: python3 scripts/story_shorts/anim_life_ep1_v3.py <출력폴더> <3D스프라이트폴더>
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter
SPR3 = sys.argv.pop(2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_life_ep1 as V1
import anim_life_ep1_v2 as V2
from anim_life_ep1 import W, H, ease, back, blink

S = V2.S

def with_shadow(im, k=0.1):
    pad = int(im.height * k); out = Image.new("RGBA", (im.width + 40, im.height + pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    cx, cy = out.width / 2, im.height + pad * 0.25
    d.ellipse((cx - im.width * 0.38, cy - pad * 0.28, cx + im.width * 0.38, cy + pad * 0.28), fill=(110, 60, 30, 85))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(pad * 0.25)))
    out.alpha_composite(im, (20, 0)); return out

def load(key, file, match=None, width=None, shadow=True):
    im = Image.open(os.path.join(SPR3, file)).convert("RGBA")
    w = width or S[match or key].width
    im = im.resize((int(w), int(im.height * w / im.width)), Image.LANCZOS)
    S[key] = with_shadow(im) if shadow else im

for e in ("happy", "blink", "cry", "o"): load(f"baby_{e}", f"baby3d_{e}.png", "baby_happy", 400)
for k in ("tod_o", "tod_blink", "tod_proud"): load(k, f"{k}.png", width=400)
for k in ("dad", "dad_blink", "mom", "mom_blink"): load(k, f"{k}.png", width=380)
load("pencil", "pencil.png", width=250, shadow=False); load("money", "money.png", width=250, shadow=False); load("mic", "mic.png", width=150, shadow=False)
for k in ("bg_nursery", "bg_living", "bg_dol", "bg_vote"):  # 배경은 살짝 흐리게 → 3D 캐릭터가 도드라짐
    S[k] = S[k].filter(ImageFilter.GaussianBlur(3))

put, txt, label, pill = V2.put, V2.txt, V2.label, V2.pill
INK = V2.INK; ITEM_X = V2.ITEM_X; ITEMS = V2.ITEMS

def s4(t, dur):
    im = S["bg_dol"].copy(); d = ImageDraw.Draw(im)
    ph = max(0, t - 0.9); tgt = 1 + math.sin(ph * 2.0) if t < dur - 0.5 else 1  # 0~2: 고민하며 좌우로
    lean = (tgt - 1)
    tk = "tod_blink" if blink(t, 0.4) < 1 else "tod_o"
    put(im, tk, 540 + lean * 45, 320, 0.92 * V2.breathe(t), -lean * 8)
    im.alpha_composite(S["table"], (20, 500)); d = ImageDraw.Draw(im)
    near = int(round(tgt)) if t > 0.9 else -1
    for i, (key, name, col) in enumerate(ITEMS):
        k = back((t - 0.4 - i * 0.3) / 0.35)
        if k <= 0: continue
        hot = i == near
        if hot:
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
            gd.ellipse((ITEM_X[i] - 140, 470, ITEM_X[i] + 140, 650), fill=(255, 230, 120, 150))
            im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22))); d = ImageDraw.Draw(im)
        bob = (14 if hot else 5) * math.sin(t * (7 if hot else 4) + i)
        put(im, key, ITEM_X[i], 560 + bob, k * (1.12 if hot else 1.0)); d = ImageDraw.Draw(im)
        d.ellipse((ITEM_X[i] + 70, 470, ITEM_X[i] + 130, 530), fill=col, outline=INK, width=5)
        txt(d, ITEM_X[i] + 100, 502, str(i + 1), 44, (255, 255, 255), stroke=3)
    if t > 3.2:
        b = 16 * abs(math.sin((t - 3.2) * 6)); txt(d, 800, 150 - b, "?", 150, (255, 95, 110), stroke=9)
    a = ease((t - 0.2) / 0.4)
    label(d, 1230 + (1 - a) * 60, "첫 번째 갈림길", 104)
    if a > 0: pill(d, W / 2, 1370, "돌잡이로 미래가 정해진다", 52)
    return im

V1.FUNCS = dict(V1.FUNCS); V1.FUNCS["s4"] = s4
if __name__ == "__main__":
    V1.main()
