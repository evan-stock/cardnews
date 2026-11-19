"""오쓸 3D 그래픽: 빙하기 호수 점토(버터 같은 흙) 위의 집 — 단면 + 물이 스며들면 점토가 흘러 집이 기운다
본보기 anim3d_liquefy.py 를 복사해 장면을 새로 짬(2026.11.18, 20261118-clay).
사용: python3 scripts/story_shorts/anim3d_clay.py --out /tmp/f_clay --start 0 --end 105 --scale 75 --samples 12
  0~1.2초: 집 가까이(창문 불빛) → 카메라가 뒤로 빠지며 땅 단면(흙·줄무늬 회색 점토·암반)이 드러남
  1.2초~: 파란 물줄기가 점토로 스며듦 → 점토 윗면이 집 아래에서 꺼지며 옆으로 흘러나감 → 집이 기울며 가라앉음
"""
import argparse, math, random, os, sys
import bpy, bmesh
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="frames")
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--end", type=int, default=105)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--samples", type=int, default=24)
ap.add_argument("--engine", default="CYCLES")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, rgb, emit=0.0, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


M = {
    "grass": mat("grass", hexc("#6f7f5a")),
    "soil": mat("soil", hexc("#7a5a40")),
    "clay": mat("clay", hexc("#4c5a68"), rough=0.35),
    "varve": mat("varve", hexc("#3f4850"), rough=0.35),
    "rock": mat("rock", hexc("#2a2d3a")),
    "far": mat("far", hexc("#4a5a44")),
    "hill": mat("hill", hexc("#4a4566")),
    "hill2": mat("hill2", hexc("#38344f")),
    "tree": mat("tree", hexc("#26352c")),
    "wall": mat("wall", hexc("#d8cbb4")),
    "roof": mat("roof", hexc("#8a3b32")),
    "window": mat("window", hexc("#ffc46b"), emit=6.0, rough=0.3),
    "water": mat("water", hexc("#3aa0ff"), emit=2.5, rough=0.2),
    "lake": mat("lake", hexc("#6d8fb0"), rough=0.15),
}
clay_bsdf = M["clay"].node_tree.nodes["Principled BSDF"]

# ---------------- ground ----------------
X0, X1, Y0, Y1 = -8.0, 8.0, 0.0, 12.0
NX, NY = 64, 36
HX, HY = 0.0, 3.0          # 집 위치
noise = {}


def nz(i, j, k, s):
    if (i, j, k) not in noise:
        noise[i, j, k] = random.uniform(-s, s)
    return noise[i, j, k]


def gx(i): return X0 + (X1 - X0) * i / NX
def gy(j): return Y0 + (Y1 - Y0) * j / NY


def dip(x, y):            # 집 아래 꺼짐 모양
    return math.exp(-((x - HX) ** 2 / (2 * 1.9 ** 2) + (y - HY) ** 2 / (2 * 2.4 ** 2)))


def bulge(x, y):          # 옆(오른쪽)으로 밀려 나온 점토
    return math.exp(-((x - 3.6) ** 2 / (2 * 1.3 ** 2) + (y - HY) ** 2 / (2 * 2.6 ** 2)))


# 경계: (기본 z, 잡음, 꺼짐 비율, 부풂 비율)
BOUNDS = [(0.0, 0.05, 1.0, 0.7), (-0.55, 0.04, 1.0, 0.75), (-3.3, 0.03, 0.15, 0.0), (-7.0, 0.0, 0.0, 0.0)]
LAYERS = [("grass_soil", 0, 1), ("clay", 1, 2), ("rock", 2, 3)]
DEPTH = 1.6   # 최대 꺼짐


def zb(k, i, j, x, y, s):
    base, ns, fd, fb = BOUNDS[k]
    return base + nz(i, j, k, ns) - s * DEPTH * dip(x, y) * fd + s * 0.55 * bulge(x, y) * fb


objs = {}


def build(name, mats):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(M[m])
    objs[name] = ob


build("grass_soil", ["soil", "grass"])
build("clay", ["clay"])
build("rock", ["rock"])


def update_layer(name, ka, kb, s):
    ob = objs[name]
    bm = bmesh.new()
    top, bot = {}, {}
    for i in range(NX + 1):
        for j in range(NY + 1):
            x, y = gx(i), gy(j)
            zt = zb(ka, i, j, x, y, s)
            top[i, j] = bm.verts.new((x, y, zt))
            bot[i, j] = bm.verts.new((x, y, min(zb(kb, i, j, x, y, s), zt - 0.03)))

    def f(vs, mi=0):
        fc = bm.faces.new(vs); fc.material_index = mi

    mi_top = 1 if name == "grass_soil" else 0
    for i in range(NX):
        for j in range(NY):
            f((top[i, j], top[i + 1, j], top[i + 1, j + 1]), mi_top)
            f((top[i, j], top[i + 1, j + 1], top[i, j + 1]), mi_top)
            f((bot[i, j], bot[i + 1, j + 1], bot[i + 1, j]))
            f((bot[i, j], bot[i, j + 1], bot[i + 1, j + 1]))
    for i in range(NX):
        f((top[i, 0], bot[i, 0], bot[i + 1, 0], top[i + 1, 0]))
        f((top[i, NY], top[i + 1, NY], bot[i + 1, NY], bot[i, NY]))
    for j in range(NY):
        f((top[0, j], top[0, j + 1], bot[0, j + 1], bot[0, j]))
        f((top[NX, j], bot[NX, j], bot[NX, j + 1], top[NX, j + 1]))
    bm.normal_update(); bm.to_mesh(ob.data); bm.free(); ob.data.update()


# 점토 단면의 줄무늬(호수 바닥에 해마다 쌓인 층) — 앞 단면에 얇은 띠
VARVES = [-0.9, -1.25, -1.55, -1.9, -2.2, -2.55, -2.9]
varve_objs = []
for zv in VARVES:
    me = bpy.data.meshes.new("v"); ob = bpy.data.objects.new("v", me)
    scene.collection.objects.link(ob); ob.data.materials.append(M["varve"])
    varve_objs.append((ob, zv))


def update_varve(ob, zv, s):
    bm = bmesh.new(); prev = None
    rows = []
    for i in range(NX + 1):
        x = gx(i)
        wob = 0.03 * math.sin(x * 2.3 + zv * 5)
        frac = (zv + 0.55) / (-3.3 + 0.55)          # 0(위)~1(아래)
        zz = zv + wob - s * DEPTH * dip(x, 0) * (1 - 0.85 * frac) + s * 0.55 * bulge(x, 0) * (1 - frac)
        a = bm.verts.new((x, -0.012, zz + 0.045)); b = bm.verts.new((x, -0.012, zz - 0.045))
        rows.append((a, b))
    for i in range(NX):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    bm.normal_update(); bm.to_mesh(ob.data); bm.free(); ob.data.update()


def surf_z(x, y, s):
    i = min(max(round((x - X0) / (X1 - X0) * NX), 0), NX)
    j = min(max(round((y - Y0) / (Y1 - Y0) * NY), 0), NY)
    return zb(0, i, j, x, y, s)


# ---------------- house (로우폴리) ----------------
bpy.ops.object.empty_add(location=(HX, HY, 0)); house = bpy.context.active_object
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75)); w = bpy.context.active_object
w.scale = (2.2, 1.8, 1.5); w.data.materials.append(M["wall"]); w.parent = house
rme = bpy.data.meshes.new("roof"); rf = bpy.data.objects.new("roof", rme); scene.collection.objects.link(rf)
rb = bmesh.new()
pts = [rb.verts.new(v) for v in [(-1.3, -1.1, 1.5), (1.3, -1.1, 1.5), (1.3, 1.1, 1.5), (-1.3, 1.1, 1.5), (-1.3, 0, 2.5), (1.3, 0, 2.5)]]
for fc in [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]:
    rb.faces.new([pts[k] for k in fc])
rb.normal_update(); rb.to_mesh(rme); rb.free()
rf.data.materials.append(M["roof"]); rf.parent = house
for wx in (-0.55, 0.55):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, -0.91, 0.85))
    wd = bpy.context.active_object; wd.scale = (0.45, 0.04, 0.5); wd.data.materials.append(M["window"]); wd.parent = house
bpy.ops.object.light_add(type="POINT", location=(0, -1.4, 0.9)); wl = bpy.context.active_object
wl.data.energy = 60; wl.data.color = hexc("#ffb85c"); wl.parent = house

# ---------------- water streaks ----------------
drops = []
for k in range(26):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=0.45)
    o = bpy.context.active_object; o.data.materials.append(M["water"])
    drops.append((o, random.uniform(-2.6, 2.6), random.uniform(0, 1)))

# ---------------- background ----------------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 60, -0.06))
fr_ = bpy.context.active_object; fr_.scale = (220, 96, 1); fr_.data.materials.append(M["far"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(-6, 30, -0.04))
lk = bpy.context.active_object; lk.scale = (40, 14, 1); lk.data.materials.append(M["lake"])
for k in range(9):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    hh = bpy.context.active_object
    hh.location = (random.uniform(-60, 60), random.uniform(55, 90), -2)
    hh.scale = (random.uniform(14, 26), random.uniform(6, 10), random.uniform(5, 11))
    hh.data.materials.append(M["hill"] if k % 2 else M["hill2"])
for _ in range(60):
    x = random.uniform(-30, 30); y = random.uniform(14, 42)
    if abs(x) < 4 and y < 20:
        continue
    s_ = random.uniform(0.7, 1.6)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.45 * s_, depth=1.9 * s_, location=(x, y, 0.9 * s_))
    bpy.context.active_object.data.materials.append(M["tree"])

# ---------------- world & light ----------------
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB"); bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], ramp.inputs[0])
nt.links.new(ramp.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
cr = ramp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = (*hexc("#f2a65a"), 1)
e = cr.elements.new(0.12); e.color = (*hexc("#c76b8a"), 1)
e = cr.elements.new(0.3); e.color = (*hexc("#4a3f7a"), 1)
cr.elements[-1].position = 0.7; cr.elements[-1].color = (*hexc("#141a3a"), 1)
bg.inputs[1].default_value = 0.7

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(72), 0, math.radians(-35)))
sun = bpy.context.active_object; sun.data.energy = 3.0; sun.data.color = hexc("#ffb27a"); sun.data.angle = math.radians(3)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(160)))
fill = bpy.context.active_object; fill.data.energy = 0.9; fill.data.color = hexc("#8aa0ff")
bpy.ops.object.light_add(type="AREA", location=(0, -7, 0.5), rotation=(math.radians(90), 0, 0))
key = bpy.context.active_object; key.data.energy = 320; key.data.size = 12; key.data.color = hexc("#ffd9b8")

# ---------------- camera ----------------
bpy.ops.object.empty_add(location=(0, 3, 1)); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 32; scene.camera = cam
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"


def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u


CAM_A, TGT_A = Vector((3.0, -2.6, 1.9)), Vector((0.0, 3.0, 1.1))
CAM_B, TGT_B = Vector((0.0, -8.6, 0.9)), Vector((0.0, 2.0, -1.2))

# ---------------- render ----------------
r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS; r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
if args.engine == "CYCLES":
    r.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True; scene.cycles.max_bounces = 4; r.use_persistent_data = True
else:
    r.engine = args.engine

os.makedirs(args.out, exist_ok=True)
for fr in range(args.start, args.end, args.step):
    t = fr / FPS
    wet = ease((t - 1.0) / 1.0)          # 물이 스며듦
    s = ease((t - 1.6) / 1.6)            # 점토가 흐름(0→1)
    for name, ka, kb in LAYERS:
        update_layer(name, ka, kb, s)
    for ob, zv in varve_objs:
        update_varve(ob, zv, s)
    # 점토가 젖으며 더 밝고 번들거림
    clay_bsdf.inputs["Base Color"].default_value = (*[lerp(a, b, wet) for a, b in zip(hexc("#4c5a68"), hexc("#6a7f92"))], 1)
    clay_bsdf.inputs["Roughness"].default_value = lerp(0.45, 0.12, wet)
    # 집: 꺼진 땅을 따라 내려앉고 오른쪽으로 기움
    house.location = (HX + 0.25 * s, HY, surf_z(HX, HY, s) + 0.02)
    house.rotation_euler = (0, math.radians(14) * s, 0)
    # 물줄기: 땅 위에서 점토층 안으로 내려감
    for o, x, ph in drops:
        u = (t / 0.9 + ph) % 1.0
        vis = wet if t > 0.9 else 0.0
        z0 = surf_z(x, 0.0, s) - 0.1; z1 = -2.4 - s * DEPTH * dip(x, 0) * 0.3
        o.location = (x, -0.05, lerp(z0, z1, u))
        sc = vis * math.sin(math.pi * u)
        o.scale = (sc, sc, sc)
    u = ease(t / 1.6)
    cam.location = CAM_A.lerp(CAM_B, u); tgt.location = TGT_A.lerp(TGT_B, u)
    scene.frame_set(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
