# 인생 댓글로 정함 5화용 3D 추가분 (2026.10.27): 게임기를 두 손으로 내미는 원복 김댓글, 게임기 단독 소품.
# 사용: python3 scripts/story_shorts/life_3d6.py <출력폴더> [이름들...]
#   이름: kidug_proud kidug_blink kidug_o (life_3d5 kidu_* 와 같은 캔버스 700x900, 잘라내지 않음) console
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from life_3d import sd_sph
from life_3d2 import Char, Item, sd_capsule, sd_rbox, rot, render
from life_3d3 import Kid
from life_3d5 import KidU, kidu, _legs

CON_C = np.array([0.0, -0.5, 0.86])  # 게임기 중심(배 앞)

def sd_console(p, c=CON_C, tilt=-0.35):
    q = rot(p, c, "x", tilt)
    body = sd_rbox(q, c, (0.62, 0.27, 0.07), 0.07)
    return body

def paint_console(p, col, c=CON_C, tilt=-0.35):
    q = rot(p, c, "x", tilt) - c; x, y, z = q[:, 0], q[:, 1], q[:, 2]; fr = z > 0.05
    scr = fr & (np.abs(x) < 0.3) & (np.abs(y) < 0.2)
    col = np.where(scr[:, None], np.array([0.55, 0.85, 1.0]), col)
    star = fr & (np.abs(x) < 0.07) & (np.abs(y) < 0.07)  # 화면 속 노란 별(캐릭터)
    col = np.where(star[:, None], np.array([1.0, 0.85, 0.3]), col)
    dpad = fr & (((np.abs(x + 0.47) < 0.07) & (np.abs(y) < 0.025)) | ((np.abs(x + 0.47) < 0.025) & (np.abs(y) < 0.07)))
    col = np.where(dpad[:, None], np.array([0.1, 0.1, 0.12]), col)
    for bx, by, bc in ((0.45, 0.05, (0.95, 0.3, 0.35)), (0.52, -0.05, (0.3, 0.6, 0.95))):
        b = fr & (((x - bx) ** 2 + (y - by) ** 2) < 0.035 ** 2)
        col = np.where(b[:, None], np.array(bc), col)
    return col

class KidUG(KidU):
    """두 손으로 게임기를 앞으로 내밈(게임기와 손을 함께 렌더 → 소품만 따로 움직이지 않음)"""
    def body_mats(self): return ["jacket", "pants", "limb", "shoe", "conB"]
    def body(self, p):
        torso, shorts, limbs, shoes = Kid.body(self, p)
        r = sd_capsule(p, np.array([0.64, -0.32, 0.05]), np.array([0.62, -0.5, 0.78]), 0.14)
        l = sd_capsule(p, np.array([-0.64, -0.32, 0.05]), np.array([-0.62, -0.5, 0.78]), 0.14)
        hands = np.minimum(sd_sph(p, np.array([0.62, -0.5, 0.86]), 0.15), sd_sph(p, np.array([-0.62, -0.5, 0.86]), 0.15))
        arms = np.minimum(np.minimum(r, l), hands)
        return [torso, shorts, np.minimum(arms, _legs(p)), shoes, sd_console(p)]
    def paint(self, name, p, col):
        if name == "conB": return paint_console(p, col)
        return KidU.paint(self, name, p, col)

Char.PAL["conB"] = (0.3, 0.3, 0.36)
Char.GLOSS["conB"] = (40, 0.4)

class Console(Item):
    def __init__(self): super().__init__("console")
    @property
    def mats(self): return ["conB"]
    def sdf(self, p):
        c = np.array([0, 0.0, 0.0]); d = sd_console(p, c, 0.0); return d, np.zeros(len(p), int)
    PALS = {"conB": (0.3, 0.3, 0.36)}
    GLOSS = {"conB": (40, 0.4)}
    def paint(self, name, p, col): return paint_console(p, col, np.array([0, 0.0, 0.0]), 0.0)

JOBS = {"kidug_proud": lambda: kidu(KidUG, "proud"), "kidug_blink": lambda: kidu(KidUG, "blink"), "kidug_o": lambda: kidu(KidUG, "o"),
        "console": lambda: render(Console(), 520, 300, look_y=0.0, dist=2.6, pitch=0.25)}

if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(JOBS); os.makedirs(out, exist_ok=True)
    for nm in names:
        t0 = time.time(); JOBS[nm]().save(f"{out}/{nm}.png"); print(nm, round(time.time() - t0, 1), "s", flush=True)
