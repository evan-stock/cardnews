"""오쓸 3D 그래픽: 날개 끝 소용돌이(익단 와류) — 2026.11.20, 20261120-vortex
본보기 anim3d_clay.py 의 공통 틀(로우폴리·노을 하늘·낮은 태양·카메라 TRACK_TO)을 쓰고 장면은 새로 짬.
사용: python3 scripts/story_shorts/anim3d_vortex.py --scene a --out /tmp/f_va --start 0 --end 105 --scale 75 --samples 12
  scene a: 오른쪽 날개 끝 바로 뒤 → 아래(높은 압력) 공기가 날개 끝을 돌아 위로 말려 올라가는 빨간 화살표
           → 카메라가 옆으로 빠지며 두 날개 끝에서 하얀 소용돌이 띠가 뒤로 길게 끌려 나옴
  scene b: 넓게 — 큰 여객기 뒤로 소용돌이 두 줄, 뒤따르던 작은 비행기가 그 속에 들어가 확 기울어짐
"""
import argparse, math, random, os, sys
import bpy, bmesh
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--scene", default="a")
ap.add_argument("--out", default="frames")
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--end", type=int, default=105)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--samples", type=int, default=24)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat(name, hx, emit=0.0, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*hexc(hx), 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*hexc(hx), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


M = {
    "body": mat("body", "#dfe3ea", rough=0.5),
    "wing": mat("wing", "#c3c9d4", rough=0.5),
    "engine": mat("engine", "#8e97a8", rough=0.5),
    "tail": mat("tail", "#33507f", rough=0.5),
    "glass": mat("glass", "#1c2433", rough=0.2),
    "land": mat("land", "#fff1c9", emit=25),
    "red": mat("red", "#ff3b30", emit=18),
    "green": mat("green", "#3bff7a", emit=18),
    "strobe": mat("strobe", "#ffffff", emit=30),
    "arrow": mat("arrow", "#ff6a3d", emit=4, rough=0.4),
    "arrow_b": mat("arrow_b", "#5ab8ff", emit=4, rough=0.4),
    "mist": mat("mist", "#eef4ff", emit=1.6, rough=0.9),
    "grass": mat("grass", "#56664a"),
    "runway": mat("runway", "#3a3d48"),
    "dash": mat("dash", "#f4f4f4", emit=1.2),
    "rlight": mat("rlight", "#ffb347", emit=14),
    "tree": mat("tree", "#26352c"),
    "hill": mat("hill", "#4a4566"),
    "hill2": mat("hill2", "#38344f"),
    "river": mat("river", "#6d8fb0", rough=0.15),
}
mist_bsdf = M["mist"].node_tree.nodes["Principled BSDF"]


def link(ob, parent=None, m=None):
    if m:
        ob.data.materials.append(M[m])
    if parent:
        ob.parent = parent
    return ob


def mesh_obj(name, verts, faces, m, parent=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return link(ob, parent, m)


# ---------------- 로우폴리 여객기 (기수 +Y, 날개 X, 위 Z) ----------------
TIP = Vector((7.0, -2.8, 0.35))      # 오른쪽 날개 끝(비행기 좌표)


def make_plane(scale=1.0, lights=True):
    root = bpy.data.objects.new("plane", None)
    scene.collection.objects.link(root)
    root.scale = (scale, scale, scale)
    # 동체
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.75, depth=11, rotation=(math.radians(90), 0, 0))
    link(bpy.context.active_object, root, "body")
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.75, radius2=0.1, depth=2.0, location=(0, 6.5, -0.1),
                                    rotation=(math.radians(-90), 0, 0))
    link(bpy.context.active_object, root, "body")
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.75, radius2=0.18, depth=2.6, location=(0, -6.8, 0.25),
                                    rotation=(math.radians(90), 0, 0))
    link(bpy.context.active_object, root, "body")
    # 조종실 창
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 6.4, 0.35))
    o = bpy.context.active_object; o.scale = (0.9, 0.5, 0.18); link(o, root, "glass")
    # 날개(뒤로 젖힘·끝이 살짝 위로)
    for sx in (1, -1):
        rle, rte = (0.6 * sx, 1.3, -0.35), (0.6 * sx, -2.0, -0.35)
        tle, tte = (TIP.x * sx, -2.2, TIP.z), (TIP.x * sx, -3.3, TIP.z)
        th_r, th_t = 0.16, 0.06
        v = [(*rle[:2], rle[2] + th_r), (*rte[:2], rte[2] + th_r * 0.4), (*tte[:2], tte[2] + th_t * 0.4), (*tle[:2], tle[2] + th_t),
             (*rle[:2], rle[2] - th_r), (*rte[:2], rte[2] - th_r * 0.4), (*tte[:2], tte[2] - th_t * 0.4), (*tle[:2], tle[2] - th_t)]
        f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 3, 7, 4), (1, 5, 6, 2), (3, 2, 6, 7), (0, 4, 5, 1)]
        if sx < 0:
            f = [tuple(reversed(x)) for x in f]
        mesh_obj("wing", v, f, "wing", root)
        # 엔진
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.48, depth=2.0, location=(2.6 * sx, 1.0, -0.95),
                                            rotation=(math.radians(90), 0, 0))
        link(bpy.context.active_object, root, "engine")
        # 수평 꼬리날개
        v = [(0.3 * sx, -5.6, 0.45), (0.3 * sx, -7.0, 0.45), (2.7 * sx, -7.6, 0.6), (2.7 * sx, -7.0, 0.6)]
        v = v + [(x, y, z - 0.08) for x, y, z in v]
        f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 3, 7, 4), (1, 5, 6, 2), (3, 2, 6, 7), (0, 4, 5, 1)]
        if sx < 0:
            f = [tuple(reversed(x)) for x in f]
        mesh_obj("hstab", v, f, "wing", root)
    # 수직 꼬리날개
    v = [(0.08, -5.2, 0.6), (0.08, -7.4, 0.6), (0.08, -8.0, 3.2), (0.08, -7.0, 3.2)]
    v = v + [(-x, y, z) for x, y, z in v]
    mesh_obj("fin", v, [(0, 1, 2, 3), (4, 7, 6, 5), (0, 3, 7, 4), (1, 5, 6, 2), (3, 2, 6, 7)], "tail", root)
    if lights:
        for sx, m in ((1, "green"), (-1, "red")):        # 날개 끝 항법등(오른쪽 초록, 왼쪽 빨강)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.11, location=(TIP.x * sx, -2.6, TIP.z + 0.03))
            link(bpy.context.active_object, root, m)
            bpy.ops.object.light_add(type="POINT", location=(TIP.x * sx, -2.5, TIP.z + 0.1))
            L = bpy.context.active_object; L.data.energy = 25; L.data.color = hexc("#3bff7a" if sx > 0 else "#ff3b30")
            L.parent = root
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.13, location=(1.4 * sx, 1.4, -0.5))  # 착륙등
            link(bpy.context.active_object, root, "land")
            bpy.ops.object.light_add(type="SPOT", location=(1.4 * sx, 1.6, -0.6), rotation=(math.radians(-80), 0, 0))
            L = bpy.context.active_object; L.data.energy = 900; L.data.spot_size = math.radians(30)
            L.data.color = hexc("#fff1c9"); L.parent = root
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.12, location=(0, -8.0, 3.25))   # 꼬리 섬광등
        link(bpy.context.active_object, root, "strobe")
    return root


# ---------------- 소용돌이(하얀 김 알갱이) ----------------
def vortex_points(t, tip_w, sink, spin, n=1400, v=9.0, life=3.4, seed=0):
    """날개 끝(tip_w: 월드 좌표)에서 뒤(-Y)로 끌려가며 도는 알갱이들. 오른쪽 날개 기준, 왼쪽은 x 반전."""
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        birth = -life + (k / n) * (life + 4.0) + rnd.uniform(-0.02, 0.02)
        age = t - birth
        if age < 0 or age > life:
            continue
        a0 = rnd.randrange(3) * 2 * math.pi / 3 + rnd.uniform(-0.45, 0.45)   # 3가닥 나선 + 흩어짐
        r = (0.08 + 0.34 * min(age / 0.8, 1.0)) * rnd.uniform(0.55, 1.1)
        ang = a0 + spin * 2 * math.pi * 2.6 * age
        cx = tip_w.x - 0.35
        cz = tip_w.z - sink * age
        y = tip_w.y - 0.3 - v * age + rnd.uniform(-0.15, 0.15)
        fade = min(age / 0.25, 1.0) * min((life - age) / 0.6, 1.0)
        pts.append(((cx + r * math.cos(ang), y, cz + r * math.sin(ang)), fade * rnd.uniform(0.6, 1.0)))
    return pts


mist_me = bpy.data.meshes.new("mist")
mist_ob = bpy.data.objects.new("mist", mist_me)
scene.collection.objects.link(mist_ob)
mist_ob.data.materials.append(M["mist"])
OCTA = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
OF = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]


def update_mist(points, size):
    bm = bmesh.new()
    for (x, y, z), w in points:
        s = size * w
        if s < 0.004:
            continue
        vs = [bm.verts.new((x + s * a, y + s * b * 1.8, z + s * c)) for a, b, c in OCTA]
        for f in OF:
            bm.faces.new([vs[i] for i in f])
    bm.to_mesh(mist_me); bm.free(); mist_me.update()


# ---------------- 휘는 화살표(날개 끝을 돌아 말려 올라가는 공기) ----------------
arrow_me = bpy.data.meshes.new("arrow")
arrow_ob = bpy.data.objects.new("arrow", arrow_me)
scene.collection.objects.link(arrow_ob)
arrow_ob.data.materials.append(M["arrow"])


def update_arrow(center, rad, a_start, a_end, frac, y, thick=0.07):
    bm = bmesh.new()
    if frac > 0.01:
        a1 = a_start + (a_end - a_start) * frac
        N = max(int(40 * frac), 2)
        rings = []
        for i in range(N + 1):
            a = a_start + (a1 - a_start) * i / N
            c = Vector((center.x + rad * math.cos(a), y, center.z + rad * math.sin(a)))
            nrm = Vector((math.cos(a), 0, math.sin(a)))
            ring = []
            for j in range(6):
                b = 2 * math.pi * j / 6
                off = nrm * math.cos(b) * thick + Vector((0, 1, 0)) * math.sin(b) * thick
                ring.append(bm.verts.new(c + off))
            rings.append(ring)
        for i in range(N):
            for j in range(6):
                bm.faces.new((rings[i][j], rings[i][(j + 1) % 6], rings[i + 1][(j + 1) % 6], rings[i + 1][j]))
        # 화살촉
        tang = Vector((-math.sin(a1), 0, math.cos(a1)))
        tipc = Vector((center.x + rad * math.cos(a1), y, center.z + rad * math.sin(a1)))
        nrm = Vector((math.cos(a1), 0, math.sin(a1)))
        base = [bm.verts.new(tipc + (nrm * math.cos(2 * math.pi * j / 6) + Vector((0, 1, 0)) * math.sin(2 * math.pi * j / 6)) * thick * 2.6)
                for j in range(6)]
        apex = bm.verts.new(tipc + tang * 0.35)
        for j in range(6):
            bm.faces.new((base[j], base[(j + 1) % 6], apex))
        bm.faces.new(list(reversed(base)))
    bm.normal_update(); bm.to_mesh(arrow_me); bm.free(); arrow_me.update()


# ---------------- 땅(활주로·나무·강) — 비행기 대신 땅이 뒤로 흐름 ----------------
ground = bpy.data.objects.new("ground", None)
scene.collection.objects.link(ground)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 100, 0))
o = bpy.context.active_object; o.scale = (500, 700, 1); link(o, ground, "grass")
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 120, 0.02))
o = bpy.context.active_object; o.scale = (9, 500, 1); link(o, ground, "runway")
for k in range(70):
    yy = -120 + k * 7
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, yy, 0.04))
    o = bpy.context.active_object; o.scale = (0.35, 3.0, 1); link(o, ground, "dash")
    for sx in (1, -1):
        bpy.ops.mesh.primitive_cube_add(size=0.25, location=(5.0 * sx, yy, 0.12))
        link(bpy.context.active_object, ground, "rlight")
bpy.ops.mesh.primitive_plane_add(size=1, location=(-60, 60, 0.03))
o = bpy.context.active_object; o.scale = (40, 600, 1); link(o, ground, "river")
for _ in range(260):
    x = random.uniform(-160, 160); y = random.uniform(-150, 500)
    if abs(x) < 14 or -82 < x < -38:
        continue
    s_ = random.uniform(1.2, 3.2)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.6 * s_, depth=2.4 * s_, location=(x, y, 1.1 * s_))
    link(bpy.context.active_object, ground, "tree")
for k in range(12):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    hh = bpy.context.active_object
    hh.location = (random.uniform(-400, 400), random.uniform(500, 700), -5)
    hh.scale = (random.uniform(60, 120), random.uniform(25, 40), random.uniform(25, 55))
    link(hh, None, "hill" if k % 2 else "hill2")

# ---------------- 하늘·빛 ----------------
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
bg.inputs[1].default_value = 0.8

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(78), 0, math.radians(150)))
sun = bpy.context.active_object; sun.data.energy = 3.2; sun.data.color = hexc("#ffb27a"); sun.data.angle = math.radians(3)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(-30)))
fill = bpy.context.active_object; fill.data.energy = 0.9; fill.data.color = hexc("#8aa0ff")

# ---------------- 장면 배치 ----------------
ALT = 9.0
plane = make_plane(1.0)
plane.location = (0, 0, ALT)
tipR = Vector((TIP.x, TIP.y, TIP.z + ALT))
small = None
if args.scene == "b":
    small = make_plane(0.42, lights=True)

bpy.ops.object.empty_add(location=(0, 0, ALT)); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 30; scene.camera = cam
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"


def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u


# ---------------- 렌더 ----------------
r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS; r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
r.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = args.samples
scene.cycles.use_denoising = True; scene.cycles.max_bounces = 4; r.use_persistent_data = True

VC = Vector((tipR.x - 0.35, tipR.y + 0.4, tipR.z))   # 화살표 회전 중심(날개 끝 바로 안쪽)
os.makedirs(args.out, exist_ok=True)
for fr in range(args.start, args.end, args.step):
    t = fr / FPS
    ground.location = (0, -22.0 * t, 0)      # 땅이 뒤로 흐름 = 비행 중
    plane.rotation_euler = (math.radians(1.5 * math.sin(t * 1.3)), math.radians(0.8 * math.sin(t * 0.9)), 0)
    if args.scene == "a":
        # 0~1.3초: 빨간 화살표가 날개 아래에서 끝을 돌아 위로 말려 올라감
        update_arrow(VC, 0.85, math.radians(-160), math.radians(175), ease((t - 0.15) / 1.0), VC.y)
        arrow_ob.hide_render = t > 2.2
        # 1.0초~: 하얀 김 소용돌이가 생겨 뒤로 끌려감
        cond = ease((t - 0.9) / 0.8)
        pts = vortex_points(t, tipR, 0.12, 1, seed=1)
        pts += [((-x, y, z), w) for (x, y, z), w in vortex_points(t, tipR, 0.12, 1, seed=2)]
        update_mist(pts, 0.085 * cond)
        u = ease((t - 1.1) / 2.0)
        CA, TA = Vector((10.2, -8.0, ALT + 1.3)), Vector((6.3, -2.2, ALT + 0.2))
        CB, TB = Vector((17.0, -19.0, ALT + 4.0)), Vector((2.0, -9.0, ALT - 0.3))
        cam.location = CA.lerp(CB, u); tgt.location = TA.lerp(TB, u)
    else:
        update_arrow(VC, 0.85, 0, 0, 0, VC.y)
        pts = vortex_points(t, tipR, 0.16, 1, n=1700, life=4.4, seed=1)
        pts += [((-x, y, z), w) for (x, y, z), w in vortex_points(t, tipR, 0.16, 1, n=1700, life=4.4, seed=2)]
        update_mist(pts, 0.1)
        # 작은 비행기: 오른쪽 소용돌이 줄을 따라 다가오다 들어가는 순간 확 기울어짐
        sy = lerp(-46.0, -30.0, t / 3.5)
        age = (tipR.y - 0.3 - sy) / 9.0
        sz = tipR.z - 0.16 * age + 0.1
        roll = ease((t - 1.5) / 0.7) * math.radians(62) + math.radians(7) * math.sin(t * 9) * ease((t - 1.5) / 0.4)
        small.location = (tipR.x - 0.35 - 0.25 * ease((t - 1.5) / 1.0), sy, sz - 0.6 * ease((t - 1.6) / 1.4))
        small.rotation_euler = (math.radians(-6) * ease((t - 1.8) / 1.0), roll, math.radians(-8) * ease((t - 1.8) / 1.0))
        u = ease(t / 2.2)
        CA, TA = Vector((20.0, -50.0, ALT + 5.0)), Vector((3.0, -24.0, ALT - 0.5))
        CB, TB = Vector((15.0, -46.0, ALT + 2.5)), Vector((5.5, -31.0, ALT - 0.3))
        cam.location = CA.lerp(CB, u); tgt.location = TA.lerp(TB, u)
    scene.frame_set(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
