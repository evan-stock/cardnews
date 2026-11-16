# 인생 댓글로 정함 3화용 3D 추가분 (2026.10.25): 앞치마 두른 세 살 김댓글(정색 표정 포함), 크레용 쥔 김댓글, 미안한 엄마.
# 사용: python3 scripts/story_shorts/life_3d4.py <출력폴더> [이름들...]
#   이름: kida_happy kida_blink kida_proud kida_o kida_frown kidc_proud kidc_blink mom_sad
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from life_3d import sd_ellip, sd_sph, HEAD, EYE_X, EYE_Y
from life_3d2 import Char, INK, sd_capsule, far, render
from life_3d3 import Kid, AdultX  # Kid 재질(shirt 등)을 Char.PAL 에 등록함

APRON = np.array([0.98, 0.97, 0.95]); APRON_RED = np.array([0.92, 0.27, 0.37])

class KidA(Kid):
    """앞치마 두른 세 살 김댓글. expr: happy blink proud o frown(정색)"""
    def head(self, p):
        D = Char.head(self, p)
        if self.expr == "frown":  # 반쯤 감은 눈(시큰둥)
            D[1] = np.minimum(sd_ellip(p, HEAD + [EYE_X, EYE_Y - 0.02, 0.86], np.array([0.12, 0.085, 0.07])),
                              sd_ellip(p, HEAD + [-EYE_X, EYE_Y - 0.02, 0.86], np.array([0.12, 0.085, 0.07])))
        return D
    def paint_face(self, p, col):
        if self.expr != "frown": return Char.paint_face(self, p, col)
        col = Char.paint_face(self, p, col)
        q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]; front = z > 0.3
        for sx in (1, -1):  # 안쪽으로 내려간 눈썹
            xx = x - sx * EYE_X; yy = y - (0.27 - 0.09 * (sx * xx < 0) * 0 - 0.08 * (-sx * xx) / 0.14)
            m = front & (np.abs(xx) < 0.15) & (np.abs(y - (0.26 + 0.07 * sx * xx / 0.15)) < 0.028)
            col = np.where(m[:, None], INK, col)
        m = front & (np.abs(x) < 0.12) & (np.abs(y + 0.25) < 0.022)  # 일자 입
        return np.where(m[:, None], INK, col)
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "shirt":
            x, y, z = p[:, 0], p[:, 1], p[:, 2]; fr = z > 0.15
            bib = (np.abs(x) < 0.34) & (y < -0.12) & fr
            col = np.where(bib[:, None], APRON, col)
            strap = (np.abs(np.abs(x) - 0.3) < 0.05) & (y >= -0.12) & fr
            col = np.where(strap[:, None], APRON, col)
            hx, hy = x / 0.09, (y + 0.45) / 0.09  # 엄마 앞치마와 같은 빨간 하트
            heart = (hx ** 2 + (hy - 0.2 - np.sqrt(np.abs(hx)) * 0.6) ** 2) < 1.1
            return np.where((heart & fr)[:, None], APRON_RED, col)
        if name == "shorts":  # 앞치마 아랫단이 반바지를 덮음
            x, z = p[:, 0], p[:, 2]
            return np.where(((np.abs(x) < 0.5) & (z > 0.15))[:, None], APRON, col)
        return col

class KidC(KidA):
    """크레용을 번쩍 든 앞치마 김댓글(오른팔 + 크레용 한 덩어리)"""
    def body_mats(self): return ["shirt", "shorts", "limb", "shoe", "cray", "crayP"]
    def body(self, p):
        torso, shorts, limbs, shoes = Kid.body(self, p)
        left = sd_capsule(p, np.array([-0.7, -0.35, 0.05]), np.array([-0.78, -0.82, 0.25]), 0.14)
        left = np.minimum(left, sd_sph(p, np.array([-0.8, -0.9, 0.3]), 0.15))
        right = sd_capsule(p, np.array([0.68, -0.3, 0.05]), np.array([0.95, 0.12, 0.38]), 0.14)
        right = np.minimum(right, sd_sph(p, np.array([1.0, 0.2, 0.42]), 0.16))
        legs = np.minimum(sd_capsule(p, np.array([0.3, -1.05, 0]), np.array([0.3, -1.4, 0.02]), 0.17),
                          sd_capsule(p, np.array([-0.3, -1.05, 0]), np.array([-0.3, -1.4, 0.02]), 0.17))
        a = np.array([0.98, 0.02, 0.44]); b = np.array([1.2, 0.95, 0.46]); ba = b - a; L = np.linalg.norm(ba); u = ba / L
        pa = p - a; h = pa @ u; rad = np.linalg.norm(pa - h[:, None] * u, axis=-1); hb = h / L
        rr = np.where(hb < 0.85, 0.1, 0.1 * (1 - (hb - 0.85) / 0.15).clip(0.2, 1))
        cr = np.maximum(rad - rr, np.maximum(-h, h - L))
        paper = np.where((hb > 0.2) & (hb < 0.7), np.maximum(rad - 0.108, np.maximum(-h, h - L)), 9.0)
        return [torso, shorts, np.minimum(np.minimum(left, right), legs), shoes, cr, paper]

for k, v in {"cray": (0.92, 0.22, 0.25), "crayP": (1.0, 0.95, 0.85)}.items(): Char.PAL[k] = v

class AdultS(AdultX):
    """미안한 엄마: 질끈 감은 눈 + 시무룩한 입"""
    def paint_face(self, p, col):
        if self.expr != "sad": return super().paint_face(p, col)
        col = Char.paint_face(self, p, col)
        q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]; front = z > 0.3
        for sx in (1, -1):  # 처진 눈(바깥쪽이 내려감)
            xx = x - sx * EYE_X
            m = front & (np.abs(xx) < 0.13) & (np.abs(y - (0.05 - 0.06 * sx * xx / 0.13)) < 0.026)
            col = np.where(m[:, None], INK, col)
        r = np.sqrt(x ** 2 + (y + 0.42) ** 2)
        m = front & (np.abs(r - 0.14) < 0.024) & (y > -0.33)  # ∩ 입
        return np.where(m[:, None], INK, col)

def kid(sc): return render(sc, 600, 840, look_y=0.05, dist=6.4)

JOBS = {
    "kida_happy": lambda: kid(KidA("happy", "kid")), "kida_blink": lambda: kid(KidA("blink", "kid")),
    "kida_proud": lambda: kid(KidA("proud", "kid")), "kida_o": lambda: kid(KidA("o", "kid")),
    "kida_frown": lambda: kid(KidA("frown", "kid")),
    "kidc_proud": lambda: render(KidC("proud", "kid"), 700, 840, look_y=0.05, dist=6.4),
    "kidc_blink": lambda: render(KidC("blink", "kid"), 700, 840, look_y=0.05, dist=6.4),
    "mom_sad": lambda: render(AdultS("sad", "mom"), 600, 900, look_y=-0.1, dist=7.0),
}

if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(JOBS); os.makedirs(out, exist_ok=True)
    for nm in names:
        t0 = time.time(); JOBS[nm]().save(f"{out}/{nm}.png"); print(nm, round(time.time() - t0, 1), "s", flush=True)
