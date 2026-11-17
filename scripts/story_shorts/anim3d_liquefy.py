"""오쓸 3D 그래픽 본보기(2026.11.18 사용자 확정 방식): 숨 쉬는 자갈 바닥 단면 — 로우폴리 + 해 질 녘 조명 + 카메라 이동
준비: pip install --break-system-packages bpy  (Blender 5.x 파이썬 모듈, 약 430MB, Python 3.13)
사용: python3 scripts/story_shorts/anim3d_liquefy.py --out /tmp/f_liq --start 0 --end 90 --scale 75 --samples 12
      (Cycles CPU, 2코어에서 3초 90프레임 약 9분) → gfx3d_post.py 로 1080x780 mp4
새 장면은 이 파일을 복사해 anim3d_<이름>.py 로 만든다: 재질(mat/hexc), 지형 메시 갱신, 로우폴리 돌(ico sphere 1단계),
배경(원뿔 나무·언덕), 하늘 그라데이션, 해 질 녘 태양+보조광+면광, 카메라 TRACK_TO 이동(ease), 프레임마다 위치 갱신 후 렌더.
"""
import argparse, math, random, os, sys
import bpy, bmesh
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="frames")
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--end", type=int, default=90)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--samples", type=int, default=24)
ap.add_argument("--engine", default="CYCLES")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------- materials ----------------
def mat(name, rgb, emit=0.0, rough=0.85, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m

def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

M = {
    "surface": mat("surface", hexc("#a39886")),
    "gravel": mat("gravel", hexc("#7a6a58")),
    "sand": mat("sand", hexc("#c9a46b")),
    "clay": mat("clay", hexc("#7a4636")),
    "water": mat("water", hexc("#1f5fc4"), emit=0.6, rough=0.3),
    "rock": mat("rock", hexc("#262a38")),
    "far": mat("far", hexc("#3d4a3c")),
    "hill": mat("hill", hexc("#4a4566")),
    "hill2": mat("hill2", hexc("#38344f")),
    "tree": mat("tree", hexc("#26352c")),
    "arrow": mat("arrow", hexc("#8fe3ff"), emit=2.0, rough=0.4),
    "bubble": mat("bubble", hexc("#6cc8ff"), emit=1.5, rough=0.2),
}
stone_mats = [mat(f"st{i}", hexc(c)) for i, c in enumerate(
    ["#8d8478", "#6f665c", "#b2a998", "#5e5a55", "#9c8a72", "#cfc6b4"])]

# ---------------- ground model ----------------
X0, X1, Y0, Y1 = -8.0, 8.0, 0.0, 14.0
NX, NY = 56, 40
BX, BY, SIG = 0.0, 1.0, 1.7   # 들썩이는 중심(앞 단면 근처)
PERIOD = 1.5                 # 1.5초에 한 번 숨쉬기 → 3초에 두 번
AMP = 0.55

def bump(x, y):
    return math.exp(-((x - BX) ** 2 + (y - BY) ** 2) / (2 * SIG ** 2))

def breath(t):
    return AMP * (0.5 - 0.5 * math.cos(2 * math.pi * t / PERIOD))

noise = {}
def nz(i, j, k, s):
    key = (i, j, k)
    if key not in noise:
        noise[key] = random.uniform(-s, s)
    return noise[key]

# 층 경계: (이름, 기본 z, 잡음, 들썩임 비율)
BOUNDS = [
    ("top", 0.0, 0.07, 1.0),
    ("g", -0.75, 0.06, 1.0),
    ("s", -1.55, 0.05, 0.92),
    ("c", -1.95, 0.03, 0.82),
    ("w", -2.75, 0.04, 0.0),
    ("r", -5.0, 0.0, 0.0),
]
LAYERS = [("gravel", 0, 1), ("sand", 1, 2), ("clay", 2, 3), ("water", 3, 4), ("rock", 4, 5)]

def zb(k, i, j, x, y, h):
    _, base, ns, f = BOUNDS[k]
    edge = 1.0 if (0 < i < NX and j < NY) else 1.0
    return base + nz(i, j, k, ns) * edge + h * bump(x, y) * f

def gx(i): return X0 + (X1 - X0) * i / NX
def gy(j): return Y0 + (Y1 - Y0) * j / NY

layer_objs = {}
def build_layer(name):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    ob.data.materials.append(M[name])
    if name == "gravel":
        ob.data.materials.append(M["surface"])
    layer_objs[name] = ob
    return ob

def update_layer(name, ka, kb, h):
    ob = layer_objs[name]
    bm = bmesh.new()
    top = {}; bot = {}
    for i in range(NX + 1):
        for j in range(NY + 1):
            x, y = gx(i), gy(j)
            zt = zb(ka, i, j, x, y, h); zbb = zb(kb, i, j, x, y, h)
            top[i, j] = bm.verts.new((x, y, zt))
            bot[i, j] = bm.verts.new((x, y, min(zbb, zt - 0.02)))
    def f(vs, mi=0):
        face = bm.faces.new(vs); face.material_index = mi; return face
    for i in range(NX):
        for j in range(NY):
            # 삼각형으로 나눠 로우폴리 면 느낌
            mi = 1 if name == "gravel" else 0
            f((top[i, j], top[i + 1, j], top[i + 1, j + 1]), mi)
            f((top[i, j], top[i + 1, j + 1], top[i, j + 1]), mi)
            f((bot[i, j], bot[i + 1, j + 1], bot[i + 1, j]))
            f((bot[i, j], bot[i, j + 1], bot[i + 1, j + 1]))
    for i in range(NX):  # 앞 단면(y=0)과 뒷면
        f((top[i, 0], bot[i, 0], bot[i + 1, 0], top[i + 1, 0]))
        f((top[i, NY], top[i + 1, NY], bot[i + 1, NY], bot[i, NY]))
    for j in range(NY):
        f((top[0, j], top[0, j + 1], bot[0, j + 1], bot[0, j]))
        f((top[NX, j], bot[NX, j], bot[NX, j + 1], top[NX, j + 1]))
    bm.normal_update()
    bm.to_mesh(ob.data); bm.free()
    ob.data.update()

for name, ka, kb in LAYERS:
    build_layer(name)

def surf_z(x, y, h):
    i = min(max(round((x - X0) / (X1 - X0) * NX), 0), NX)
    j = min(max(round((y - Y0) / (Y1 - Y0) * NY), 0), NY)
    return zb(0, i, j, x, y, h)

# ---------------- stones ----------------
def stone(r, m, sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co *= random.uniform(0.82, 1.15)
    o.data.materials.append(m)
    return o

surface_stones = []
for _ in range(260):
    x = random.uniform(-7.5, 7.5); y = random.uniform(0.25, 9.0)
    r = random.uniform(0.07, 0.22) * (1.0 if y < 4 else 0.8)
    o = stone(r, random.choice(stone_mats))
    o.scale = (1, random.uniform(0.8, 1.2), random.uniform(0.45, 0.7))
    o.rotation_euler = (0, 0, random.uniform(0, 6.28))
    surface_stones.append((o, x, y, r * 0.35))

face_stones = []  # 단면에 박힌 자갈
for _ in range(150):
    x = random.uniform(-7.8, 7.8); z = random.uniform(-0.7, -0.08)
    r = random.uniform(0.06, 0.16)
    o = stone(r, random.choice(stone_mats[:4]))
    o.scale = (1, 0.5, 0.75)
    face_stones.append((o, x, z, 1.0))
for _ in range(60):  # 모래층 작은 알갱이
    x = random.uniform(-7.8, 7.8); z = random.uniform(-1.5, -0.8)
    o = stone(random.uniform(0.03, 0.06), stone_mats[5])
    o.scale = (1, 0.5, 1)
    face_stones.append((o, x, z, 0.92))

# ---------------- pressure arrows & bubbles ----------------
arrows = []
for k, x in enumerate([-2.4, -1.2, 0.0, 1.2, 2.4]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=0.42)
    shaft = bpy.context.active_object
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.2, depth=0.26, location=(0, 0, 0.33))
    head = bpy.context.active_object
    shaft.select_set(True); head.select_set(True)
    bpy.context.view_layer.objects.active = shaft
    bpy.ops.object.join()
    shaft.data.materials.clear(); shaft.data.materials.append(M["arrow"])
    arrows.append((shaft, x, k))

bubbles = []
for k in range(16):
    o = stone(random.uniform(0.04, 0.07), M["bubble"], sub=1)
    bubbles.append((o, random.uniform(-2.0, 2.0), random.uniform(0, 1)))

# ---------------- background ----------------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 70, -0.05))
far = bpy.context.active_object; far.scale = (220, 112, 1)
far.data.materials.append(M["far"])
for k in range(9):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    h = bpy.context.active_object
    h.location = (random.uniform(-60, 60), random.uniform(55, 90), -2)
    h.scale = (random.uniform(14, 26), random.uniform(6, 10), random.uniform(5, 11))
    h.data.materials.append(M["hill"] if k % 2 else M["hill2"])
for _ in range(70):
    x = random.uniform(-30, 30); y = random.uniform(17, 45)
    if abs(x) < 3 and y < 22: continue
    s = random.uniform(0.7, 1.6)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.45 * s, depth=1.9 * s, location=(x, y, 0.9 * s))
    bpy.context.active_object.data.materials.append(M["tree"])

# ---------------- world & light ----------------
world = bpy.data.worlds.new("sky"); scene.world = world
world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], ramp.inputs[0])
nt.links.new(ramp.outputs[0], bg.inputs[0])
nt.links.new(bg.outputs[0], out.inputs[0])
cr = ramp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = (*hexc("#f2a65a"), 1)
e = cr.elements.new(0.12); e.color = (*hexc("#c76b8a"), 1)
e = cr.elements.new(0.3); e.color = (*hexc("#4a3f7a"), 1)
cr.elements[-1].position = 0.7; cr.elements[-1].color = (*hexc("#141a3a"), 1)
bg.inputs[1].default_value = 0.7

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(72), 0, math.radians(-35)))
sun = bpy.context.active_object; sun.data.energy = 3.2
sun.data.color = hexc("#ffb27a"); sun.data.angle = math.radians(3)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(160)))
fill = bpy.context.active_object; fill.data.energy = 0.9; fill.data.color = hexc("#8aa0ff")
bpy.ops.object.light_add(type="AREA", location=(0, -6, 1.5), rotation=(math.radians(90), 0, 0))
key = bpy.context.active_object; key.data.energy = 260; key.data.size = 10
key.data.color = hexc("#ffd9b8")

# ---------------- camera ----------------
bpy.ops.object.empty_add(location=(0, 1.2, 0.1)); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 32; scene.camera = cam
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt
tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"

def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
CAM_A, TGT_A = Vector((1.2, -2.2, 1.35)), Vector((0.1, 1.6, -0.05))
CAM_B, TGT_B = Vector((0.0, -8.2, 0.75)), Vector((0.0, 2.0, -1.55))

# ---------------- render settings ----------------
r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS
r.image_settings.file_format = "PNG"
r.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
if args.engine == "CYCLES":
    r.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    r.use_persistent_data = True
else:
    r.engine = args.engine

os.makedirs(args.out, exist_ok=True)
water_bsdf = M["water"].node_tree.nodes["Principled BSDF"]
for fr in range(args.start, args.end, args.step):
    t = fr / FPS
    h = breath(t)
    for name, ka, kb in LAYERS:
        update_layer(name, ka, kb, h)
    for o, x, y, sink in surface_stones:
        o.location = (x, y, surf_z(x, y, h) + sink * 0.4)
    for o, x, z, f in face_stones:
        o.location = (x, -0.01, z + h * bump(x, 0) * f)
    pulse = h / AMP
    for o, x, k in arrows:
        zc = -2.45 + 0.12 * pulse + h * bump(x, 0) * 0.4
        o.location = (x, -0.12, zc)
        s = 0.75 + 0.45 * pulse
        o.scale = (s, s, s)
    for o, x, ph in bubbles:
        u = (t / 1.2 + ph) % 1.0
        z0 = -1.9 + h * bump(x, 0) * 0.8
        z1 = surf_z(x, 0.0, h) - 0.05
        o.location = (x + 0.08 * math.sin(6 * u + ph * 9), -0.06, lerp(z0, z1, u))
        sc = math.sin(math.pi * u) * (0.6 + 0.6 * pulse)
        o.scale = (sc, sc, sc)
    water_bsdf.inputs["Emission Strength"].default_value = 0.15 + 0.55 * pulse
    u = ease(t / 2.6)
    cam.location = CAM_A.lerp(CAM_B, u)
    tgt.location = TGT_A.lerp(TGT_B, u)
    scene.frame_set(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
