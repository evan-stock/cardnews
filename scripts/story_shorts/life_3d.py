# 댓글로 키우는 아이 — 동글 아기(A안)를 3D로 렌더 (2026.10.23). 외부 3D 프로그램 없이 numpy 레이마칭.
# 사용: python3 scripts/story_shorts/life_3d.py <출력폴더> [가로px]
# 표정별 스프라이트(PNG, 투명 배경)를 만든다 → 애니메이션은 기존처럼 스프라이트를 움직여서 만든다.
import os, sys, time
import numpy as np
from PIL import Image

def norm(v): return v / np.linalg.norm(v, axis=-1, keepdims=True).clip(1e-9)

def sd_ellip(p, c, r):
    q = (p - c) / r; k0 = np.linalg.norm(q, axis=-1); k1 = np.linalg.norm(q / r, axis=-1)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-9)

def sd_sph(p, c, r): return np.linalg.norm(p - c, axis=-1) - r

def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)

HEAD = np.array([0, 0.55, 0.0]); HR = np.array([1.05, 0.97, 0.95])
BODY = np.array([0, -0.62, -0.02]); BR = np.array([0.92, 0.78, 0.78])
EYE_X, EYE_Y = 0.36, 0.06

def curl_pts():  # 정수리 한 가닥: 머리에서 솟아 안쪽으로 말리는 나선
    pts = []
    for i in range(40):
        t = i / 39
        if t < 0.3:
            a = t / 0.3; pts.append((0.0 + 0.03 * a, 1.40 + 0.30 * a, 0.0))
        else:
            a = (t - 0.3) / 0.7; ang = np.pi + a * 1.9 * np.pi; r = 0.17 * (1 - 0.45 * a)
            pts.append((0.03 + 0.17 + r * np.cos(ang), 1.70 + r * np.sin(ang) * -1, 0.0))
    return np.array(pts)
CURL = curl_pts()

class Scene:
    def __init__(self, expr):
        self.expr = expr

    def sdf(self, p):
        e = self.expr
        head = sd_ellip(p, HEAD, HR)
        ears = np.minimum(sd_sph(p, HEAD + [1.0, -0.02, 0], 0.22), sd_sph(p, HEAD + [-1.0, -0.02, 0], 0.22))
        skin = smin(head, ears, 0.08)
        body = sd_ellip(p, BODY, BR)
        hands = np.minimum(sd_sph(p, BODY + [0.33, 0.08, 0.72], 0.13), sd_sph(p, BODY + [-0.33, 0.08, 0.72], 0.13))
        hair = np.full(len(p), 9.0)
        for c in CURL: hair = np.minimum(hair, sd_sph(p, c, 0.062))
        ds = [skin, body, hair, hands]
        if e in ("happy", "o"):
            eyes = np.minimum(sd_ellip(p, HEAD + [EYE_X, EYE_Y, 0.86], np.array([0.12, 0.155, 0.08])),
                              sd_ellip(p, HEAD + [-EYE_X, EYE_Y, 0.86], np.array([0.12, 0.155, 0.08])))
        else:
            eyes = np.full(len(p), 9.0)
        ds.append(eyes)
        if e == "cry":
            tears = np.minimum(sd_ellip(p, HEAD + [0.42, -0.22, 0.86], np.array([0.06, 0.1, 0.05])),
                               sd_ellip(p, HEAD + [-0.42, -0.22, 0.86], np.array([0.06, 0.1, 0.05])))
        else:
            tears = np.full(len(p), 9.0)
        ds.append(tears)
        D = np.stack(ds)  # 0 skin 1 body 2 hair 3 hands 4 eyes 5 tears
        return D.min(0), D.argmin(0)

    def d(self, p): return self.sdf(p)[0]

    def normal(self, p):
        e = 1e-3; ex = np.array([e, 0, 0]); ey = np.array([0, e, 0]); ez = np.array([0, 0, e])
        n = np.stack([self.d(p + ex) - self.d(p - ex), self.d(p + ey) - self.d(p - ey), self.d(p + ez) - self.d(p - ez)], -1)
        return norm(n)

    # 얼굴에 그리는 무늬(볼터치·입·감은 눈)
    def paint_skin(self, p, base):
        col = base.copy(); q = p - HEAD; x, y, z = q[:, 0], q[:, 1], q[:, 2]
        front = z > 0.3
        for sx in (1, -1):  # 볼터치(부드럽게)
            dd = np.sqrt(((x - sx * 0.58) / 1.0) ** 2 + ((y + 0.17) / 0.65) ** 2)
            w = np.clip(1 - dd / 0.2, 0, 1) ** 1.5 * front
            col = col * (1 - 0.55 * w[:, None]) + np.array([1.0, 0.45, 0.5]) * (0.55 * w[:, None])
        ink = np.array([0.23, 0.15, 0.12]); e = self.expr
        def stroke(mask, c=ink):
            nonlocal col
            col = np.where(mask[:, None], c, col)
        if e in ("happy", "blink"):  # 웃는 입
            r = np.sqrt(x ** 2 + (y + 0.12) ** 2)
            stroke(front & (np.abs(r - 0.15) < 0.024) & (y < -0.16))
        if e == "o":
            stroke(front & (((x / 0.075) ** 2 + ((y + 0.3) / 0.095) ** 2) < 1), np.array([0.45, 0.16, 0.18]))
        if e == "blink":
            for sx in (1, -1):
                r = np.sqrt((x - sx * EYE_X) ** 2 + (y - 0.12) ** 2)
                stroke(front & (np.abs(r - 0.13) < 0.024) & (y < 0.06))
        if e == "cry":
            for sx in (1, -1):  # > < 눈
                xx = (x - sx * EYE_X) * -sx; yy = y - EYE_Y
                m = (np.abs(np.abs(yy) - (0.1 - xx * 0.85)) < 0.03) & (xx > -0.11) & (xx < 0.12)
                stroke(front & m)
            mouth = ((x / 0.2) ** 2 + ((y + 0.3) / 0.15) ** 2) < 1
            stroke(front & mouth, np.array([0.62, 0.18, 0.22]))
            tongue = ((x / 0.11) ** 2 + ((y + 0.4) / 0.06) ** 2) < 1
            stroke(front & tongue, np.array([1.0, 0.5, 0.52]))
        return col

    def paint_body(self, p, base):
        q = p - BODY; col = base.copy()
        fold = np.abs(q[:, 1] - (0.22 - 0.25 * q[:, 0] ** 2)) < 0.03
        col = np.where((fold & (q[:, 2] > 0))[:, None], base * 0.82, col)
        rng = ((np.sin(q[:, 0] * 23) * np.sin(q[:, 1] * 19) > 0.93) & (q[:, 1] < 0.1))  # 별 무늬 점
        return np.where(rng[:, None], np.array([1, 1, 1.0]), col)

def render(expr, Wp=600, Hp=800, yaw=0.0):
    sc = Scene(expr); ss = 2; W, H = Wp * ss, Hp * ss
    cam = np.array([6.2 * np.sin(yaw), 0.35, 6.2 * np.cos(yaw)]); look = np.array([0, 0.25, 0])
    fw = norm(look - cam); rt = norm(np.cross(fw, [0, 1, 0])); up = np.cross(rt, fw)
    fov = 0.40; asp = W / H
    xs = (np.arange(W) + 0.5) / W * 2 - 1; ys = 1 - (np.arange(H) + 0.5) / H * 2
    X, Y = np.meshgrid(xs * fov * asp, ys * fov)
    dirs = norm(fw + X[..., None] * rt + Y[..., None] * up).reshape(-1, 3)
    N = len(dirs); t = np.full(N, 3.5); hit = np.zeros(N, bool); alive = np.ones(N, bool)
    for _ in range(90):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0: break
        p = cam + dirs[idx] * t[idx, None]; dd = sc.d(p)
        t[idx] += dd * 0.9
        h = dd < 1e-3; hit[idx[h]] = True; alive[idx[h]] = False
        far = t[idx] > 9; alive[idx[far]] = False
    out = np.zeros((N, 4))
    idx = np.nonzero(hit)[0]; p = cam + dirs[idx] * t[idx, None]
    _, mat = sc.sdf(p); n = sc.normal(p); v = -dirs[idx]
    pal = np.array([[1.0, 0.84, 0.74], [0.62, 0.88, 0.80], [0.33, 0.22, 0.16], [1.0, 0.82, 0.72], [0.09, 0.06, 0.06], [0.55, 0.82, 1.0]])
    base = pal[mat]
    sk = mat == 0; base[sk] = sc.paint_skin(p[sk], base[sk])
    bd = mat == 1; base[bd] = sc.paint_body(p[bd], base[bd])
    L = norm(np.array([-0.6, 0.8, 0.9])); L2 = norm(np.array([0.9, 0.2, -0.4]))
    ndl = (n @ L); diff = np.clip(ndl * 0.6 + 0.4, 0, 1) ** 1.3  # 감싸는 빛(부드러운 점토 느낌)
    # 앰비언트 오클루전
    ao = np.ones(len(idx))
    for k in range(1, 5):
        h = 0.06 * k; ao -= (h - sc.d(p + n * h)).clip(0) * (0.9 / k)
    ao = ao.clip(0.35, 1)
    sky = 0.55 + 0.45 * n[:, 1]
    amb = np.array([0.95, 0.92, 1.0]) * (0.28 + 0.14 * sky[:, None])
    col = base * (diff[:, None] * np.array([1.0, 0.96, 0.9]) * 0.85 + amb) * ao[:, None]
    # 피부 속 빛(서브서피스 흉내): 그늘진 피부가 붉게
    col += (mat == 0)[:, None] * (1 - diff)[:, None] * np.array([0.10, 0.02, 0.0])
    rim = (1 - np.clip((n * v).sum(1), 0, 1)) ** 3 * np.clip(n @ L2 * 0.5 + 0.5, 0, 1)
    col += rim[:, None] * 0.35 * np.array([1.0, 0.95, 0.9])
    hv = norm(L + v); spec = np.clip((n * hv).sum(1), 0, 1)
    shin = np.where(mat == 4, 120, np.where(mat == 5, 80, 25)); ks = np.where(mat == 4, 1.6, np.where(mat == 5, 1.0, 0.12))
    col += (spec ** shin * ks)[:, None]
    if (mat == 4).any():  # 눈 속 두 번째 반짝임
        e4 = mat == 4; q = p[e4] - HEAD
        for sx in (1, -1):
            m2 = ((q[:, 0] - sx * EYE_X - 0.045) ** 2 + (q[:, 1] - EYE_Y + 0.07) ** 2) < 0.03 ** 2
            tmp = col[e4]; tmp[m2] = 0.95; col[e4] = tmp
    col = col ** (1 / 1.1)
    out[idx, :3] = col.clip(0, 1); out[idx, 3] = 1
    img = (out.reshape(H, W, 4) * 255).astype(np.uint8)
    im = Image.fromarray(img, "RGBA").resize((Wp, Hp), Image.LANCZOS)
    return im.crop(im.getbbox())

if __name__ == "__main__":
    out = sys.argv[1]; Wp = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    os.makedirs(out, exist_ok=True)
    for e in ("happy", "blink", "cry", "o"):
        t0 = time.time(); render(e, Wp, int(Wp * 4 / 3)).save(f"{out}/baby3d_{e}.png"); print(e, round(time.time() - t0, 1), "s")
