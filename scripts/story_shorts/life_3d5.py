# 인생 댓글로 정함 4화용 3D 추가분 (2026.10.26): 영어유치원 원복 입은 세 살 김댓글(엄지 척·아래 가리키기 포즈), 방송 PD.
# 사용: python3 scripts/story_shorts/life_3d5.py <출력폴더> [이름들...]
#   이름: kidu_happy kidu_blink kidu_proud kidu_o kidu_frown kidut_proud kidut_blink(주먹 번쩍) kidup_happy kidup_blink pd_o pd_happy pd_blink
#   kidu*/kidut*/kidup* 는 잘라내지 않은 같은 캔버스(700x900)로 저장 → 애니에서 같은 상자로 함께 잘라 쓰면 위치가 맞는다.
import inspect, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import life_3d2
from life_3d import sd_ellip, sd_sph, smin, HEAD, HR, EYE_X, EYE_Y
from life_3d2 import Char, Adult, INK, sd_capsule, sd_torus_z, far, render
from life_3d3 import Kid
from life_3d4 import KidA

# 잘라내지 않는 render (같은 카메라·캔버스로 포즈끼리 위치를 맞추기 위해)
_src = inspect.getsource(life_3d2.render).replace("def render(", "def render_nc(").replace("return im.crop(im.getbbox())", "return im")
exec(_src, life_3d2.__dict__); render_nc = life_3d2.render_nc

NAVY = np.array([0.2, 0.25, 0.47]); WHITE = np.array([0.97, 0.97, 0.97]); TIE = np.array([1.0, 0.78, 0.22])

class KidU(KidA):
    """영어유치원 원복: 남색 재킷(반팔) + 흰 셔츠 + 노란 넥타이 + 회색 반바지. expr: happy blink proud o frown"""
    def body_mats(self): return ["jacket", "pants", "limb", "shoe"]
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "jacket":
            x, y, z = p[:, 0], p[:, 1], p[:, 2]; fr = z > 0.15
            v = (np.abs(x) < 0.24 * ((y + 0.62) / 0.62).clip(0, 1)) & (y > -0.62)  # 흰 셔츠 V
            col = np.where((v & fr)[:, None], WHITE, col)
            tie = (np.abs(x) < 0.045 + 0.05 * ((-0.12 - y) / 0.45).clip(0, 1)) & (y < -0.04) & (y > -0.6)
            col = np.where((tie & fr)[:, None], TIE, col)
            badge = ((x - 0.4) ** 2 + (y + 0.4) ** 2) < 0.075 ** 2  # 가슴 노란 배지
            return np.where((badge & fr)[:, None], TIE, col)
        return col

def _legs(p):
    return np.minimum(sd_capsule(p, np.array([0.3, -1.05, 0]), np.array([0.3, -1.4, 0.02]), 0.17),
                      sd_capsule(p, np.array([-0.3, -1.05, 0]), np.array([-0.3, -1.4, 0.02]), 0.17))
def _left(p):
    a = sd_capsule(p, np.array([-0.7, -0.35, 0.05]), np.array([-0.78, -0.82, 0.25]), 0.14)
    return np.minimum(a, sd_sph(p, np.array([-0.8, -0.9, 0.3]), 0.15))

class KidUT(KidU):
    """오른손 주먹 번쩍(화이팅). 손가락 하나만 세우면 오해 소지 → 주먹만"""
    def body(self, p):
        torso, shorts, limbs, shoes = Kid.body(self, p)
        r = sd_capsule(p, np.array([0.66, -0.3, 0.05]), np.array([0.92, 0.05, 0.45]), 0.14)
        r = np.minimum(r, sd_ellip(p, np.array([0.97, 0.13, 0.52]), np.array([0.17, 0.15, 0.15])))
        return [torso, shorts, np.minimum(np.minimum(_left(p), r), _legs(p)), shoes]

class KidUP(KidU):
    """오른손 검지로 아래(댓글창)를 콕 가리킴"""
    def body(self, p):
        torso, shorts, limbs, shoes = Kid.body(self, p)
        r = sd_capsule(p, np.array([0.64, -0.32, 0.08]), np.array([0.82, -0.62, 0.62]), 0.14)
        r = np.minimum(r, sd_sph(p, np.array([0.86, -0.72, 0.7]), 0.14))
        r = np.minimum(r, sd_capsule(p, np.array([0.87, -0.8, 0.78]), np.array([0.9, -1.12, 0.9]), 0.055))
        return [torso, shorts, np.minimum(np.minimum(_left(p), r), _legs(p)), shoes]

for k, v in {"jacket": tuple(NAVY), "pants": (0.55, 0.57, 0.63)}.items(): Char.PAL[k] = v

# ---------- 방송 PD: 빨간 모자 + 헤드셋 + 검정 티 ----------
class PD(Adult):
    def body_mats(self): return ["suit", "capR", "phones"]
    def hair(self, p):
        q = p - HEAD; cap = sd_ellip(p, HEAD + [0, 0.03, -0.02], HR * 1.045)
        return np.maximum(cap, 0.3 - 0.6 * np.maximum(0, -q[:, 2]) - q[:, 1])
    def body(self, p):
        b = sd_ellip(p, np.array([0, -1.05, -0.05]), np.array([0.98, 1.0, 0.72]))
        q = p - HEAD
        cap = np.maximum(sd_ellip(p, HEAD + [0, 0.12, -0.02], HR * 1.08), 0.42 - q[:, 1])
        brim = sd_ellip(p, HEAD + [0, 0.48, 0.82], np.array([0.62, 0.06, 0.48]))
        band = np.maximum(sd_torus_z(p, HEAD + [0, 0.05, 0], 1.14, 0.06), -(q[:, 1] - 0.05))
        cups = np.minimum(sd_ellip(p, HEAD + [1.08, -0.02, 0], np.array([0.12, 0.22, 0.2])), sd_ellip(p, HEAD + [-1.08, -0.02, 0], np.array([0.12, 0.22, 0.2])))
        boom = np.minimum(sd_capsule(p, HEAD + [-1.08, -0.1, 0.1], HEAD + [-0.42, -0.36, 0.86], 0.035), sd_sph(p, HEAD + [-0.38, -0.37, 0.9], 0.07))
        return [b, np.minimum(cap, brim), np.minimum(np.minimum(band, cups), boom)]
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "suit":  # 목에 건 노란 출입증 줄 + 카드
            x, y, z = p[:, 0], p[:, 1], p[:, 2]; fr = z > 0.2
            strap = (np.abs(np.abs(x) - 0.2 * ((y + 0.95) / 0.75).clip(0, 1) - 0.0) < 0.035) & (y > -0.95) & (y < -0.2)
            col = np.where((strap & fr)[:, None], TIE, col)
            card = (np.abs(x) < 0.17) & (y < -0.95) & (y > -1.3)
            return np.where((card & fr)[:, None], WHITE, col)
        return col

PD_PAL = {"capR": (0.92, 0.3, 0.33), "phones": (0.16, 0.16, 0.2)}
for k, v in PD_PAL.items(): Char.PAL[k] = v

def pd(e):
    sc = PD(e, "pd")
    # render() 는 kind 가 dad 가 아니면 suit 를 살구색으로 칠함 → PALS 로 검정 티 지정
    pal = {**Char.PAL, "hand": (1.0, 0.82, 0.72), "suit": (0.2, 0.2, 0.24), "glass": (0.18, 0.14, 0.14), "hairB": (0.33, 0.22, 0.16)}
    sc.PALS = pal
    return render(sc, 600, 900, look_y=-0.1, dist=7.0)

def kidu(cls, e): return render_nc(cls(e, "kid"), 700, 900, look_y=0.05, dist=6.4)

JOBS = {
    "kidu_happy": lambda: kidu(KidU, "happy"), "kidu_blink": lambda: kidu(KidU, "blink"), "kidu_proud": lambda: kidu(KidU, "proud"),
    "kidu_o": lambda: kidu(KidU, "o"), "kidu_frown": lambda: kidu(KidU, "frown"),
    "kidut_proud": lambda: kidu(KidUT, "proud"), "kidut_blink": lambda: kidu(KidUT, "blink"),
    "kidup_happy": lambda: kidu(KidUP, "happy"), "kidup_blink": lambda: kidu(KidUP, "blink"),
    "pd_o": lambda: pd("o"), "pd_happy": lambda: pd("happy"), "pd_blink": lambda: pd("blink"),
}


# ---------- 4화 대안 '가짜 김댓글' (10.26): 옆집 애(가르마 + 동그란 안경, 원복), 감기 걸린 김댓글(이불 + 콧물) ----------
class Neighbor(KidU):
    """옆집 애: 정수리 컬 대신 2:8 가르마 머리 + 동그란 안경"""
    def body_mats(self): return ["jacket", "pants", "limb", "shoe", "glass"]
    def hair(self, p):
        q = p - HEAD; cap = sd_ellip(p, HEAD + [0, 0.04, -0.02], HR * 1.05)
        line = 0.3 - 0.6 * np.maximum(0, -q[:, 2]) + 0.08 * np.clip(q[:, 0], -1, 1)
        return np.maximum(cap, line - q[:, 1])
    def body(self, p):
        g = np.minimum(sd_torus_z(p, HEAD + [EYE_X, EYE_Y, 0.95], 0.2, 0.028), sd_torus_z(p, HEAD + [-EYE_X, EYE_Y, 0.95], 0.2, 0.028))
        g = np.minimum(g, sd_capsule(p, HEAD + [-0.16, EYE_Y + 0.04, 0.99], HEAD + [0.16, EYE_Y + 0.04, 0.99], 0.024))
        return Kid.body(self, p) + [g]
    def paint(self, name, p, col):
        if name == "hair":  # 가르마 선
            q = p - HEAD
            return np.where(((np.abs(q[:, 0] + 0.42) < 0.035) & (q[:, 1] > 0.5))[:, None], np.array([0.2, 0.13, 0.1]), col)
        return KidU.paint(self, name, p, col)

class Sick(KidU):
    """감기 김댓글: 이불(민트) 두른 몸 + 반쯤 감은 눈 + 콧물. expr: frown(반눈) / blink"""
    def body_mats(self): return ["mint", "pants", "limb", "shoe"]
    def body(self, p):
        torso, shorts, limbs, shoes = Kid.body(self, p)
        blanket = sd_ellip(p, np.array([0, -0.75, 0.0]), np.array([1.0, 0.85, 0.82]))
        blanket = smin(blanket, sd_ellip(p, np.array([0, -0.1, -0.15]), np.array([1.05, 0.35, 0.75])), 0.2)
        return [blanket, far(p), far(p), shoes]
    def head(self, p):
        D = KidA.head(self, p)
        snot = np.minimum(sd_capsule(p, HEAD + [0.07, -0.1, 0.96], HEAD + [0.075, -0.19, 0.95], 0.045), sd_sph(p, HEAD + [0.075, -0.22, 0.94], 0.065))
        D[3] = snot
        return D
    def paint_face(self, p, col):
        col = Char.paint_face(self, p, col)
        q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]; front = z > 0.3
        if self.expr == "frown":
            for sx in (1, -1):  # 처진 눈썹(안쪽이 올라감)
                xx = x - sx * EYE_X
                m = front & (np.abs(xx) < 0.13) & (np.abs(y - (0.27 - 0.06 * sx * xx / 0.13)) < 0.024)
                col = np.where(m[:, None], INK, col)
        r = np.sqrt(x ** 2 + (y + 0.44) ** 2)
        col = np.where((front & (np.abs(r - 0.12) < 0.022) & (y > -0.36))[:, None], INK, col)  # ∩ 입
        red = (((x / 0.12) ** 2 + ((y + 0.1) / 0.08) ** 2) < 1) & (z > 0.8)  # 빨간 코
        return np.where(red[:, None], np.array([1.0, 0.5, 0.5]), col)
    def paint(self, name, p, col):
        if name == "skin": return self.paint_face(p, col)
        if name == "mint":  # 이불 물방울 무늬
            x, y = p[:, 0], p[:, 1]
            dots = ((np.mod(x * 4, 1) - 0.5) ** 2 + (np.mod(y * 4 + 0.5 * np.floor(x * 4), 1) - 0.5) ** 2) < 0.04
            return np.where(dots[:, None], np.array([1.0, 1.0, 1.0]), col)
        return col

def nb(e): return render_nc(Neighbor(e, "kid"), 700, 900, look_y=0.05, dist=6.4)
def sick(e): return render_nc(Sick(e, "kid"), 700, 900, look_y=0.05, dist=6.4)
JOBS.update({"nb_happy": lambda: nb("happy"), "nb_blink": lambda: nb("blink"), "nb_proud": lambda: nb("proud"),
             "sick_frown": lambda: sick("frown"), "sick_blink": lambda: sick("blink")})

if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(JOBS); os.makedirs(out, exist_ok=True)
    for nm in names:
        t0 = time.time(); JOBS[nm]().save(f"{out}/{nm}.png"); print(nm, round(time.time() - t0, 1), "s", flush=True)
