# 댓글로 키우는 아이 — 3D 등장인물·소품 (2026.10.23). life_3d.py(아기)와 같은 조명·질감.
# 사용: python3 scripts/story_shorts/life_3d2.py <출력폴더> [이름들...]
#   이름: tod_o tod_blink tod_proud dad dad_blink mom mom_blink pencil money mic
import os, sys, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from life_3d import norm, sd_ellip, sd_sph, smin, HEAD, HR, EYE_X, EYE_Y, CURL

INK = np.array([0.23, 0.15, 0.12])

def sd_capsule(p, a, b, r):
    pa = p - a; ba = np.asarray(b) - a
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
    return np.linalg.norm(pa - h[:, None] * ba, axis=-1) - r

def sd_cyl_x(p, c, h, r):  # x축 원기둥(반길이 h)
    q = p - c; d0 = np.linalg.norm(q[:, 1:], axis=-1) - r; d1 = np.abs(q[:, 0]) - h
    return np.minimum(np.maximum(d0, d1), 0) + np.linalg.norm(np.stack([d0.clip(0), d1.clip(0)], -1), axis=-1)

def sd_rbox(p, c, b, r):
    q = np.abs(p - c) - (np.asarray(b) - r)
    return np.linalg.norm(q.clip(0), axis=-1) + np.minimum(q.max(-1), 0) - r

def sd_torus_z(p, c, R, r):
    q = p - c; a = np.linalg.norm(q[:, :2], axis=-1) - R
    return np.sqrt(a ** 2 + q[:, 2] ** 2) - r

def rot(p, c, ax, ang):  # 점들을 c 기준으로 회전(역변환용)
    q = p - c; ca, sa = np.cos(ang), np.sin(ang)
    i, j = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[ax]
    out = q.copy(); out[:, i] = ca * q[:, i] - sa * q[:, j]; out[:, j] = sa * q[:, i] + ca * q[:, j]
    return out + c

def far(p): return np.full(len(p), 9.0)

class Char:
    """공통 머리(김댓글 가족 얼굴형) + 몸. 재질 이름별 색·광택."""
    PAL = {"skin": (1.0, 0.84, 0.74), "eye": (0.09, 0.06, 0.06), "hair": (0.33, 0.22, 0.16), "tear": (0.55, 0.82, 1.0)}
    GLOSS = {"eye": (120, 1.6), "tear": (80, 1.0), "glass": (60, 0.8)}

    def __init__(self, expr, kind):
        self.expr, self.kind = expr, kind
        self.mats = ["skin", "eye", "hair", "tear"] + self.body_mats()

    def body_mats(self): return []
    def body(self, p): return []

    def head(self, p):
        e = self.expr
        head = sd_ellip(p, HEAD, HR)
        ears = np.minimum(sd_sph(p, HEAD + [1.0, -0.02, 0], 0.22), sd_sph(p, HEAD + [-1.0, -0.02, 0], 0.22))
        skin = smin(head, ears, 0.08)
        if e in ("happy", "o", "proud"):
            eyes = np.minimum(sd_ellip(p, HEAD + [EYE_X, EYE_Y, 0.86], np.array([0.12, 0.155, 0.08])),
                              sd_ellip(p, HEAD + [-EYE_X, EYE_Y, 0.86], np.array([0.12, 0.155, 0.08])))
        else: eyes = far(p)
        hair = self.hair(p)
        return [skin, eyes, hair, far(p)]

    def hair(self, p):
        h = far(p)
        for c in CURL: h = np.minimum(h, sd_sph(p, c, 0.062))
        return h

    def sdf(self, p):
        D = np.stack(self.head(p) + self.body(p)); return D.min(0), D.argmin(0)
    def d(self, p): return self.sdf(p)[0]

    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        return col

    def paint_face(self, p, col):
        q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]; front = z > 0.3
        for sx in (1, -1):
            dd = np.sqrt((x - sx * 0.58) ** 2 + ((y + 0.17) / 0.65) ** 2)
            w = (np.clip(1 - dd / 0.2, 0, 1) ** 1.5 * front)[:, None]
            col = col * (1 - 0.55 * w) + np.array([1.0, 0.45, 0.5]) * (0.55 * w)
        def st(m, c=INK):
            nonlocal col; col = np.where(m[:, None], c, col)
        e = self.expr
        if e in ("happy", "blink"):
            r = np.sqrt(x ** 2 + (y + 0.12) ** 2); st(front & (np.abs(r - 0.15) < 0.024) & (y < -0.16))
        if e == "o": st(front & (((x / 0.075) ** 2 + ((y + 0.3) / 0.095) ** 2) < 1), np.array([0.45, 0.16, 0.18]))
        if e == "proud":
            m = (((x / 0.17) ** 2 + ((y + 0.2) / 0.16) ** 2) < 1) & (y < -0.2); st(front & m, np.array([0.62, 0.18, 0.22]))
            st(front & (((x / 0.09) ** 2 + ((y + 0.31) / 0.04) ** 2) < 1), np.array([1.0, 0.5, 0.52]))
        if e == "blink":
            for sx in (1, -1):
                r = np.sqrt((x - sx * EYE_X) ** 2 + (y - 0.12) ** 2); st(front & (np.abs(r - 0.13) < 0.024) & (y < 0.06))
        return col

# ---------- 돌복 입은 아이 ----------
class Toddler(Char):
    def body_mats(self): return ["jeo", "chima", "sleeve", "hand"]
    def body(self, p):
        top = sd_ellip(p, np.array([0, -0.38, -0.02]), np.array([0.78, 0.5, 0.66]))
        low = sd_ellip(p, np.array([0, -0.95, -0.02]), np.array([0.95, 0.55, 0.8]))
        arms = np.minimum(sd_capsule(p, np.array([0.62, -0.35, 0]), np.array([0.62, -0.85, 0.42]), 0.17),
                          sd_capsule(p, np.array([-0.62, -0.35, 0]), np.array([-0.62, -0.85, 0.42]), 0.17))
        hands = np.minimum(sd_sph(p, np.array([0.62, -0.95, 0.55]), 0.15), sd_sph(p, np.array([-0.62, -0.95, 0.55]), 0.15))
        return [top, low, arms, hands]
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "jeo":
            x, y, z = p[:, 0], p[:, 1], p[:, 2]
            col = np.where(((np.abs(np.abs(x) - (y + 0.15) * -0.55) < 0.03) & (z > 0) & (y > -0.75))[:, None], np.array([0.85, 0.6, 0.3]), col)
            ribbon = (((x + 0.12) ** 2 + (y + 0.62) ** 2) < 0.06 ** 2) | ((np.abs(x + 0.05 - (y + 0.62) * -0.3) < 0.035) & (y < -0.62) & (y > -0.9) & (x > -0.25))
            return np.where((ribbon & (z > 0))[:, None], np.array([0.92, 0.25, 0.35]), col)
        if name == "sleeve":
            cols = np.array([[1, .42, .42], [1, .82, .4], [.35, .82, .6], [.35, .66, .9], [.78, .5, 1]])
            k = (np.floor((p[:, 1] + 0.3) / -0.11).astype(int)).clip(0, 4)
            return cols[k]
        return col

# ---------- 아빠·엄마 ----------
class Adult(Char):
    def body_mats(self): return ["suit", "glass"] if self.kind == "dad" else ["suit", "hairB"]
    def hair(self, p):
        q = p - HEAD; cap = sd_ellip(p, HEAD + [0, 0.03, -0.02], HR * 1.045)
        line = 0.36 - 0.6 * np.maximum(0, -q[:, 2]) - (0.12 * np.cos(q[:, 0] * 3) if self.kind == "dad" else 0)
        hair = np.maximum(cap, line - q[:, 1])
        if self.kind == "mom":
            hair = np.minimum(hair, sd_sph(p, HEAD + [0.55, 0.92, -0.3], 0.3))
        return hair
    def body(self, p):
        b = sd_ellip(p, np.array([0, -1.05, -0.05]), np.array([0.98, 1.0, 0.72]))
        if self.kind == "dad":
            g = np.minimum(sd_torus_z(p, HEAD + [EYE_X, EYE_Y, 0.95], 0.2, 0.025), sd_torus_z(p, HEAD + [-EYE_X, EYE_Y, 0.95], 0.2, 0.025))
            g = np.minimum(g, sd_capsule(p, HEAD + [-0.16, EYE_Y + 0.04, 0.99], HEAD + [0.16, EYE_Y + 0.04, 0.99], 0.022))
            return [b, g]
        bob = sd_ellip(p, HEAD + [0, -0.05, -0.12], np.array([1.14, 1.0, 0.98]))
        q = p - HEAD; bob = np.maximum(bob, q[:, 2] - 0.35)  # 얼굴 앞은 비움
        bob = np.maximum(bob, -(q[:, 1] + 0.55))
        return [b, bob]
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "suit":
            x, y, z = p[:, 0], p[:, 1], p[:, 2]; fr = z > 0.2
            if self.kind == "dad":
                shirt = (np.abs(x) < (y + 0.75) * 0.0 + 0.32 * ((y + 0.3) / -0.65).clip(0, 1) * -1 + 0.32) & (y > -0.95)
                shirt = (np.abs(x) < 0.32 - 0.32 * ((-0.15 - y) / 0.8).clip(0, 1)) & (y < -0.12)
                col = np.where((shirt & fr)[:, None], np.array([0.97, 0.97, 0.97]), col)
                tie = (np.abs(x) < 0.07 + 0.04 * ((-0.3 - y) / 0.6).clip(0, 1)) & (y < -0.2) & (y > -0.95)
                col = np.where((tie & fr)[:, None], np.array([0.88, 0.25, 0.32]), col)
            else:
                apron = (np.abs(x) < 0.5) & (y < -0.55)
                col = np.where((apron & fr)[:, None], np.array([0.98, 0.97, 0.95]), col)
                hx, hy = x / 0.11, (y + 1.05) / 0.11
                heart = (hx ** 2 + (hy - 0.2 - np.sqrt(np.abs(hx)) * 0.6) ** 2) < 1.1
                col = np.where((heart & fr)[:, None], np.array([0.92, 0.27, 0.37]), col)
            return col
        return col

Adult.PAL = dict(Char.PAL)

# ---------- 소품 ----------
class Item:
    GLOSS = {"metal": (50, 0.9), "lead": (30, 0.4)}
    def __init__(self, kind): self.kind = kind; self.expr = None
    @property
    def mats(self):
        return {"pencil": ["wood", "yellow", "pink", "metal", "lead"], "money": ["bill", "bill2"], "mic": ["metal", "black", "gold"]}[self.kind]
    def sdf(self, p):
        k = self.kind; c = np.array([0, 0.2, 0.0])
        if k == "pencil":
            q = rot(rot(p, c, "z", 0.25), c, "y", -0.35)
            body = sd_cyl_x(q, c + [-0.05, 0, 0], 0.95, 0.2)
            tip_t = (q[:, 0] - 0.9) / 0.5; r = 0.2 * (1 - tip_t.clip(0, 1))
            cone = np.maximum(np.linalg.norm((q - c)[:, 1:], axis=-1) - r, np.maximum(0.9 - q[:, 0], q[:, 0] - 1.4))
            lead = np.where(tip_t > 0.65, cone, 9.0); cone = np.where(tip_t <= 0.65, cone, np.maximum(cone, 9.0))
            eraser = sd_cyl_x(q, c + [-1.12, 0, 0], 0.16, 0.19); band = sd_cyl_x(q, c + [-0.96, 0, 0], 0.06, 0.215)
            D = [cone, body, eraser, band, lead]
        elif k == "money":
            bills = []
            for dy, ang in ((0.0, 0.12), (0.12, -0.08), (0.24, 0.04)):
                q = rot(p, c + [0, dy, 0], "y", ang)
                bills.append(sd_rbox(q, c + [0, dy - 0.3, 0], (1.1, 0.05, 0.55), 0.04))
            D = [np.minimum(bills[0], bills[1]), bills[2]]
        else:
            q = rot(p, c, "z", -0.35)
            head = sd_sph(q, c + [0, 0.55, 0], 0.48); handle = sd_capsule(q, c + [0, -0.1, 0], c + [0, -1.3, 0], 0.17)
            ring = sd_cyl_x(rot(q, c + [0, -0.02, 0], "z", np.pi / 2), c + [0, -0.02, 0], 0.08, 0.24)
            D = [head, handle, ring]
        D = np.stack(D); return D.min(0), D.argmin(0)
    def d(self, p): return self.sdf(p)[0]
    PALS = {"wood": (0.96, 0.82, 0.64), "yellow": (1.0, 0.78, 0.25), "pink": (1.0, 0.6, 0.68), "metal": (0.78, 0.8, 0.86),
            "lead": (0.2, 0.18, 0.2), "bill": (0.6, 0.85, 0.58), "bill2": (0.66, 0.9, 0.62), "black": (0.2, 0.2, 0.26), "gold": (1.0, 0.8, 0.35)}
    def paint(self, name, p, col):
        if name == "bill2":
            q = p - np.array([0, 0.14, 0.0]); r = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2)
            col = np.where((np.abs(r - 0.2) < 0.025)[:, None], np.array([0.3, 0.6, 0.35]), col)
            border = (np.abs(np.abs(q[:, 0]) - 0.92) < 0.025) & (np.abs(q[:, 2]) < 0.4) | (np.abs(np.abs(q[:, 2]) - 0.4) < 0.025) & (np.abs(q[:, 0]) < 0.92)
            col = np.where(border[:, None], np.array([0.35, 0.65, 0.4]), col)
        if name == "metal" and self.kind == "mic":
            q = rot(p, np.array([0, 0.2, 0]), "z", -0.35) - np.array([0, 0.75, 0])
            grid = (np.abs(np.sin(q[:, 0] * 30)) < 0.18) | (np.abs(np.sin(q[:, 1] * 30)) < 0.18)
            col = np.where(grid[:, None], col * 0.7, col)
        return col

def render(sc, Wp=600, Hp=800, cam_y=0.35, look_y=0.25, dist=6.2, fov=0.40, ss=2, pitch=0.0):
    W, H = Wp * ss, Hp * ss
    cam = np.array([0, cam_y + dist * np.sin(pitch), dist * np.cos(pitch)]); look = np.array([0, look_y, 0])
    fw = norm(look - cam); rt = norm(np.cross(fw, [0, 1, 0])); up = np.cross(rt, fw); asp = W / H
    xs = (np.arange(W) + 0.5) / W * 2 - 1; ys = 1 - (np.arange(H) + 0.5) / H * 2
    X, Y = np.meshgrid(xs * fov * asp, ys * fov)
    dirs = norm(fw + X[..., None] * rt + Y[..., None] * up).reshape(-1, 3)
    N = len(dirs); t = np.full(N, 2.5); hit = np.zeros(N, bool); alive = np.ones(N, bool)
    for _ in range(110):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0: break
        p = cam + dirs[idx] * t[idx, None]; dd = sc.d(p); t[idx] += dd * 0.9
        h = dd < 1e-3; hit[idx[h]] = True; alive[idx[h]] = False
        alive[idx[t[idx] > 10]] = False
    out = np.zeros((N, 4)); idx = np.nonzero(hit)[0]; p = cam + dirs[idx] * t[idx, None]
    _, mat = sc.sdf(p)
    e = 1e-3; E = np.eye(3) * e
    n = norm(np.stack([sc.d(p + E[i]) - sc.d(p - E[i]) for i in range(3)], -1)); v = -dirs[idx]
    pal = getattr(sc, "PALS", None) or {**Char.PAL, "jeo": (1.0, 0.88, 0.45), "chima": (1.0, 0.5, 0.65), "sleeve": (1, 1, 1),
                                         "hand": (1.0, 0.82, 0.72), "suit": (0.3, 0.42, 0.7) if getattr(sc, "kind", "") == "dad" else (1.0, 0.58, 0.48),
                                         "glass": (0.18, 0.14, 0.14), "hairB": (0.33, 0.22, 0.16), "mint": (0.62, 0.88, 0.8)}
    names = sc.mats; base = np.zeros((len(idx), 3)); shin = np.full(len(idx), 25.0); ks = np.full(len(idx), 0.12)
    gl = {**Char.GLOSS, **getattr(sc, "GLOSS", {})}
    for i, nm in enumerate(names):
        m = mat == i
        if not m.any(): continue
        base[m] = np.array(pal[nm]); base[m] = sc.paint(nm, p[m], base[m])
        if nm in gl: shin[m], ks[m] = gl[nm]
    L = norm(np.array([-0.6, 0.8, 0.9])); L2 = norm(np.array([0.9, 0.2, -0.4]))
    diff = np.clip((n @ L) * 0.6 + 0.4, 0, 1) ** 1.3
    ao = np.ones(len(idx))
    for k in range(1, 5):
        h = 0.06 * k; ao -= (h - sc.d(p + n * h)).clip(0) * (0.9 / k)
    ao = ao.clip(0.35, 1); sky = 0.55 + 0.45 * n[:, 1]
    amb = np.array([0.95, 0.92, 1.0]) * (0.28 + 0.14 * sky[:, None])
    col = base * (diff[:, None] * np.array([1.0, 0.96, 0.9]) * 0.85 + amb) * ao[:, None]
    if "skin" in names:
        col += (mat == names.index("skin"))[:, None] * (1 - diff)[:, None] * np.array([0.10, 0.02, 0.0])
    rim = (1 - np.clip((n * v).sum(1), 0, 1)) ** 3 * np.clip(n @ L2 * 0.5 + 0.5, 0, 1)
    col += rim[:, None] * 0.35 * np.array([1.0, 0.95, 0.9])
    hv = norm(L + v); spec = np.clip((n * hv).sum(1), 0, 1); col += (spec ** shin * ks)[:, None]
    if "eye" in names:
        ei = mat == names.index("eye"); q = p[ei] - HEAD; tmp = col[ei]
        for sx in (1, -1):
            tmp[((q[:, 0] - sx * EYE_X - 0.045) ** 2 + (q[:, 1] - EYE_Y + 0.07) ** 2) < 0.03 ** 2] = 0.95
        col[ei] = tmp
    col = col ** (1 / 1.1); out[idx, :3] = col.clip(0, 1); out[idx, 3] = 1
    im = Image.fromarray((out.reshape(H, W, 4) * 255).astype(np.uint8), "RGBA").resize((Wp, Hp), Image.LANCZOS)
    return im.crop(im.getbbox())

JOBS = {
    "tod_o": lambda: render(Toddler("o", "tod")), "tod_blink": lambda: render(Toddler("blink", "tod")),
    "tod_proud": lambda: render(Toddler("proud", "tod")),
    "dad": lambda: render(Adult("happy", "dad"), 600, 900, look_y=-0.1, dist=7.0), "dad_blink": lambda: render(Adult("blink", "dad"), 600, 900, look_y=-0.1, dist=7.0),
    "mom": lambda: render(Adult("happy", "mom"), 600, 900, look_y=-0.1, dist=7.0), "mom_blink": lambda: render(Adult("blink", "mom"), 600, 900, look_y=-0.1, dist=7.0),
    "pencil": lambda: render(Item("pencil"), 500, 300, look_y=0.2, dist=3.4, pitch=0.5),
    "money": lambda: render(Item("money"), 500, 320, look_y=-0.05, dist=3.0, pitch=0.7),
    "mic": lambda: render(Item("mic"), 360, 500, look_y=0.0, dist=3.6, pitch=0.2),
}

if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(JOBS); os.makedirs(out, exist_ok=True)
    for nm in names:
        t0 = time.time(); JOBS[nm]().save(f"{out}/{nm}.png"); print(nm, round(time.time() - t0, 1), "s", flush=True)
