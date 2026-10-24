# 인생 댓글로 정함 2화용 3D 추가분 (2026.10.24): 세 살 김댓글, 우는 아빠, 놀란 엄마, 갈림길 소품.
# 사용: python3 scripts/story_shorts/life_3d3.py <출력폴더> [이름들...]
#   이름: kid_happy kid_blink kid_proud kid_o dad_cry mom_wow cap bag bowl
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from life_3d import sd_ellip, sd_sph, smin, HEAD, EYE_X, EYE_Y
from life_3d2 import Char, Adult, Item, INK, sd_capsule, sd_cyl_x, sd_rbox, sd_torus_z, rot, far, render

# ---------- 세 살 김댓글(노란 티셔츠 + 남색 반바지) ----------
class Kid(Char):
    def body_mats(self): return ["shirt", "shorts", "limb", "shoe"]
    def body(self, p):
        torso = sd_ellip(p, np.array([0, -0.42, -0.02]), np.array([0.7, 0.52, 0.6]))
        shorts = sd_ellip(p, np.array([0, -0.92, -0.02]), np.array([0.72, 0.32, 0.6]))
        sleeves = np.minimum(sd_sph(p, np.array([0.62, -0.25, 0]), 0.24), sd_sph(p, np.array([-0.62, -0.25, 0]), 0.24))
        torso = smin(torso, sleeves, 0.08)
        arms = np.minimum(sd_capsule(p, np.array([0.7, -0.35, 0.05]), np.array([0.78, -0.82, 0.25]), 0.14),
                          sd_capsule(p, np.array([-0.7, -0.35, 0.05]), np.array([-0.78, -0.82, 0.25]), 0.14))
        arms = np.minimum(arms, np.minimum(sd_sph(p, np.array([0.8, -0.9, 0.3]), 0.15), sd_sph(p, np.array([-0.8, -0.9, 0.3]), 0.15)))
        legs = np.minimum(sd_capsule(p, np.array([0.3, -1.05, 0]), np.array([0.3, -1.4, 0.02]), 0.17),
                          sd_capsule(p, np.array([-0.3, -1.05, 0]), np.array([-0.3, -1.4, 0.02]), 0.17))
        shoes = np.minimum(sd_ellip(p, np.array([0.31, -1.52, 0.1]), np.array([0.2, 0.12, 0.27])),
                           sd_ellip(p, np.array([-0.31, -1.52, 0.1]), np.array([0.2, 0.12, 0.27])))
        return [torso, shorts, np.minimum(arms, legs), shoes]
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "shirt":  # 가슴에 빨간 별 하나
            x, y, z = p[:, 0], p[:, 1] + 0.45, p[:, 2]
            a = np.arctan2(y, x); r = np.sqrt(x ** 2 + y ** 2)
            star = r < 0.16 * (0.62 + 0.38 * np.cos(5 * (a - np.pi / 2)))
            return np.where((star & (z > 0.3))[:, None], np.array([0.95, 0.32, 0.36]), col)
        return col

KPAL = {"shirt": (1.0, 0.82, 0.32), "shorts": (0.28, 0.36, 0.62), "limb": (1.0, 0.84, 0.74), "shoe": (1.0, 0.45, 0.45)}

# ---------- 우는 아빠 / 놀란 엄마 ----------
class AdultX(Adult):
    def head(self, p):
        D = super().head(p)
        if self.expr == "cry":  # 눈물 줄기(양쪽)
            t = np.minimum(sd_capsule(p, HEAD + [0.38, -0.08, 0.9], HEAD + [0.42, -0.42, 0.84], 0.055),
                           sd_capsule(p, HEAD + [-0.38, -0.08, 0.9], HEAD + [-0.42, -0.42, 0.84], 0.055))
            D[3] = t
        return D
    def paint_face(self, p, col):
        col = super().paint_face(p, col)
        if self.expr != "cry": return col
        q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]; front = z > 0.3
        for sx in (1, -1):  # 꽉 감은 눈(∩)
            r = np.sqrt((x - sx * EYE_X) ** 2 + (y - 0.0) ** 2)
            m = front & (np.abs(r - 0.12) < 0.026) & (y > 0.02)
            col = np.where(m[:, None], INK, col)
        m = front & (((x / 0.2) ** 2 + ((y + 0.3) / 0.1) ** 2) < 1)  # 엉엉 벌린 입
        col = np.where(m[:, None], np.array([0.55, 0.16, 0.2]), col)
        return col

# ---------- 갈림길 소품 ----------
class Prop(Item):
    PALS = {"board": (0.16, 0.16, 0.22), "tassel": (1.0, 0.8, 0.3), "bagY": (1.0, 0.8, 0.22), "flap": (1.0, 0.66, 0.2),
            "strap": (0.95, 0.45, 0.35), "bowl": (0.95, 0.95, 0.97), "sauce": (0.9, 0.22, 0.15), "tteok": (1.0, 0.45, 0.28)}
    GLOSS = {"sauce": (60, 0.9), "tteok": (50, 0.7), "bowl": (40, 0.5)}
    @property
    def mats(self):
        return {"cap": ["board", "tassel"], "bag": ["bagY", "flap", "strap"], "bowl": ["bowl", "sauce", "tteok"]}[self.kind]
    def sdf(self, p):
        k = self.kind; c = np.array([0, 0.0, 0.0])
        if k == "cap":
            q = rot(p, c, "y", 0.6)
            board = sd_rbox(q, c + [0, 0.25, 0], (0.85, 0.04, 0.85), 0.02)
            skull = sd_ellip(p, c + [0, 0.05, 0], np.array([0.55, 0.3, 0.55]))
            skull = np.maximum(skull, p[:, 1] - 0.24)
            t = np.minimum(sd_capsule(p, c + [0, 0.3, 0], c + [0.62, 0.3, 0.3], 0.03), sd_capsule(p, c + [0.62, 0.3, 0.3], c + [0.66, -0.2, 0.34], 0.03))
            t = np.minimum(t, sd_ellip(p, c + [0.66, -0.28, 0.34], np.array([0.07, 0.14, 0.07])))
            t = np.minimum(t, sd_sph(p, c + [0, 0.31, 0], 0.07))
            D = [np.minimum(board, skull), t]
        elif k == "bag":
            body = sd_rbox(p, c, (0.72, 0.62, 0.32), 0.22)
            flap = sd_rbox(p, c + [0, 0.25, 0.2], (0.74, 0.4, 0.16), 0.16)
            flap = np.maximum(flap, -(p[:, 2] - 0.2))
            strap = sd_torus_z(p, c + [0, 0.62, 0], 0.4, 0.07); strap = np.maximum(strap, -(p[:, 1] - 0.62))
            btn = sd_sph(p, c + [0, -0.1, 0.36], 0.08)
            D = [body, flap, np.minimum(strap, btn)]
        else:
            shell = np.abs(sd_sph(p, c + [0, 0.35, 0], 0.85)) - 0.05; shell = np.maximum(shell, p[:, 1] - 0.3)
            sauce = np.maximum(sd_sph(p, c + [0, 0.35, 0], 0.8), p[:, 1] - 0.1)
            tt = far(p)
            for (x, z, a) in ((-0.3, 0.1, 0.4), (0.15, 0.25, -0.5), (0.3, -0.15, 0.9), (-0.1, -0.3, -0.2), (0.0, 0.0, 1.5)):
                d = np.array([np.cos(a), 0, np.sin(a)]) * 0.28
                tt = np.minimum(tt, sd_capsule(p, c + [x, 0.15, z] - d, c + [x, 0.15, z] + d, 0.1))
            D = [shell, sauce, tt]
        D = np.stack(D); return D.min(0), D.argmin(0)
    def paint(self, name, p, col):
        if name == "bowl":  # 그릇 테두리 파란 줄
            m = np.abs(p[:, 1] - 0.18) < 0.03
            col = np.where(m[:, None], np.array([0.35, 0.55, 0.9]), col)
        return col

def kid(e): sc = Kid(e, "kid"); return render(sc, 600, 840, look_y=0.05, dist=6.4)
# render() 팔레트에 새 재질 추가
for k, v in KPAL.items(): Char.PAL[k] = v

JOBS = {
    "kid_happy": lambda: kid("happy"), "kid_blink": lambda: kid("blink"), "kid_proud": lambda: kid("proud"), "kid_o": lambda: kid("o"),
    "dad_cry": lambda: render(AdultX("cry", "dad"), 600, 900, look_y=-0.1, dist=7.0),
    "mom_wow": lambda: render(AdultX("o", "mom"), 600, 900, look_y=-0.1, dist=7.0),
    "cap": lambda: render(Prop("cap"), 420, 360, look_y=0.05, dist=3.6, pitch=0.45),
    "bag": lambda: render(Prop("bag"), 420, 420, look_y=0.05, dist=4.2, pitch=0.15),
    "bowl": lambda: render(Prop("bowl"), 440, 340, look_y=0.0, dist=3.6, pitch=0.6),
}

if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(JOBS); os.makedirs(out, exist_ok=True)
    for nm in names:
        t0 = time.time(); JOBS[nm]().save(f"{out}/{nm}.png"); print(nm, round(time.time() - t0, 1), "s", flush=True)
