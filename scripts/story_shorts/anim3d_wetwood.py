"""오쓸 3D 그래픽: 나무 속 가스(세균성 습심재 wetwood) — 2026.11.21, 20261121-wetwood
본보기 anim3d_liquefy.py 의 공통 틀(로우폴리·노을 하늘·낮은 태양·카메라 TRACK_TO)을 쓰고 장면은 새로 짬.
사용: python3 scripts/story_shorts/anim3d_wetwood.py --scene a --out /tmp/f_wa --start 0 --end 105 --step 2 --scale 60 --samples 10
  scene a: 케이크처럼 4분의 1을 잘라 낸 줄기 단면 — 젖은 심재 속 세균(초록 점)이 늘고 가스 방울이 차오르며
           바깥으로 미는 화살표가 커짐 → 카메라가 빠지며 해 질 녘 숲 속 나무 전체가 드러남(발밑 랜턴)
  scene b: 같은 나무 — 톱날이 들어가 틈이 나자 가스(하얀 김)가 한꺼번에 뿜어지고 갈색 거품이 껍질을 타고 흐름
근거: Illinois IPM RPD 656(가스 메탄 45~60%, 최대 60psi), Wikipedia Slime flux, NPR 2019(미루나무 가스에 불 붙임).
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
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat(name, h, emit=0.0, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*hexc(h), 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*hexc(h), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


M = {
    "bark": mat("bark", "#4b3a2e"),
    "bark2": mat("bark2", "#5d4837"),
    "sap": mat("sap", "#d9b98a"),
    "heart": mat("heart", "#6b3a1e", emit=0.25, rough=0.35),   # 젖은 심재(번들거림)
    "ring": mat("ring", "#b8935f"),
    "ground": mat("ground", "#4d4a3a"),
    "leaf": mat("leaf", "#2f2a22"),
    "tree": mat("tree", "#26352c"),
    "tree2": mat("tree2", "#1f2b27"),
    "hill": mat("hill", "#4a4566"),
    "hill2": mat("hill2", "#38344f"),
    "bact": mat("bact", "#7dff8a", emit=3.0, rough=0.4),
    "gas": mat("gas", "#d8f1ff", emit=0.9, rough=0.2),
    "arrow": mat("arrow", "#ff5a3c", emit=2.2, rough=0.4),
    "foam": mat("foam", "#5a3018", emit=0.05, rough=0.25),
    "saw": mat("saw", "#e8792b"),
    "bar": mat("bar", "#9aa0a8", rough=0.3),
    "dark": mat("dark", "#22252b"),
    "lamp": mat("lamp", "#ffcf7a", emit=8.0),
    "stone": mat("stone", "#6f665c"),
}

R_HEART, R_SAP, R_BARK = 0.62, 1.0, 1.16
H = 4.2
CUT = (math.radians(-110), math.radians(15))   # 잘라 낸 쐐기(카메라 쪽, +x -y 사분면)


def sector(name, r0, r1, a0, a1, z0, z1, m, n=10, caps=True, wobble=0.0):
    """r0~r1 고리를 a0~a1 각도만큼 각지게 만든 기둥(로우폴리). 양 끝 단면(caps)이 '케이크 단면'."""
    bm = bmesh.new()
    rows = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        w = 1 + (random.uniform(-wobble, wobble) if 0 < k < n else 0)
        ca, sa = math.cos(a), math.sin(a)
        rows.append([bm.verts.new((r * w * ca, r * w * sa, z)) for r, z in
                     ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for k in range(n):
        a, b = rows[k], rows[k + 1]
        bm.faces.new((a[1], b[1], b[2], a[2]))           # 바깥
        bm.faces.new((a[2], b[2], b[3], a[3]))           # 위
        bm.faces.new((a[0], a[1], b[1], b[0]))           # 아래
        if r0 > 0.001:
            bm.faces.new((a[0], a[3], b[3], b[0]))       # 안
    if caps:
        for row, flip in ((rows[0], False), (rows[-1], True)):
            vs = [row[0], row[3], row[2], row[1]] if not flip else [row[0], row[1], row[2], row[3]]
            if r0 <= 0.001:
                vs = [vs[0], vs[1], vs[2], vs[3]]
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


cutaway = args.scene == "a"
if cutaway:
    a0, a1 = CUT[1], CUT[0] + 2 * math.pi       # 쐐기를 뺀 나머지 270도
    sector("heart", 0.0, R_HEART, a0, a1, 0, H, M["heart"], n=18)
    sector("sap", R_HEART, R_SAP, a0, a1, 0, H, M["sap"], n=18)
    sector("bark", R_SAP, R_BARK, a0, a1, 0, H, M["bark"], n=18, wobble=0.04)
else:
    sector("heart", 0.0, R_HEART, 0, 2 * math.pi, 0, H, M["heart"], n=24, caps=False)
    sector("sap", R_HEART, R_SAP, 0, 2 * math.pi, 0, H, M["sap"], n=24, caps=False)
    sector("bark", R_SAP, R_BARK, 0, 2 * math.pi, 0, H, M["bark"], n=24, caps=False, wobble=0.04)
# 위쪽 줄기(잘리지 않은 부분, 껍질 결)와 가지
sector("trunk_up", 0.0, R_BARK * 0.97, 0, 2 * math.pi, H, H + 5.5, M["bark2"], n=12, caps=False, wobble=0.05)
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=R_BARK * 0.97, radius2=0.25, depth=3, location=(0, 0, H + 7))
bpy.context.active_object.data.materials.append(M["bark2"])
for k, (ang, z) in enumerate([(0.6, 7.2), (2.6, 8.4), (4.3, 7.8)]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.22, depth=3.2,
                                        location=(1.4 * math.cos(ang), 1.4 * math.sin(ang), z + 0.8),
                                        rotation=(0, math.radians(55), ang))
    bpy.context.active_object.data.materials.append(M["bark2"])

# 단면 위 나이테 선(얇은 고리 몇 개)
ring_objs = []
if cutaway:
    for rr in (0.25, 0.45, 0.78, 0.9):
        for a in CUT:
            ca, sa = math.cos(a), math.sin(a)
            bpy.ops.mesh.primitive_cube_add(size=1)
            o = bpy.context.active_object
            o.scale = (0.012, 0.012, H * 0.5)
            nx, ny = -sa, ca
            o.location = (rr * ca + nx * 0.004 * (1 if a == CUT[1] else -1), rr * sa + ny * 0.004 * (1 if a == CUT[1] else -1), H / 2)
            o.data.materials.append(M["ring"])

# ---------------- ground & forest ----------------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=30, y_subdivisions=30, size=60, location=(0, 10, 0))
g = bpy.context.active_object
for v in g.data.vertices:
    d = math.hypot(v.co.x, v.co.y - 0)
    v.co.z = random.uniform(-0.12, 0.12) + (0 if d < 3 else random.uniform(0, 0.25))
g.data.materials.append(M["ground"])
for _ in range(90):
    x = random.uniform(-6, 6); y = random.uniform(-5, 6)
    if math.hypot(x, y) < 1.5: continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.08, 0.22),
                                          location=(x, y, 0.02))
    o = bpy.context.active_object; o.scale.z = 0.4
    o.data.materials.append(M["leaf"] if random.random() < 0.6 else M["stone"])
for _ in range(80):
    x = random.uniform(-32, 32); y = random.uniform(5, 45)
    if abs(x) < 4 and y < 9: continue
    s = random.uniform(1.0, 2.4)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.55 * s, depth=3.2 * s, location=(x, y, 1.5 * s))
    bpy.context.active_object.data.materials.append(M["tree"] if random.random() < 0.5 else M["tree2"])
for k in range(8):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    h = bpy.context.active_object
    h.location = (random.uniform(-60, 60), random.uniform(60, 90), -2)
    h.scale = (random.uniform(14, 26), random.uniform(6, 10), random.uniform(6, 12))
    h.data.materials.append(M["hill"] if k % 2 else M["hill2"])

# 발밑 랜턴(장면 안 광원)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.13, depth=0.32, location=(1.5, -1.6, 0.18))
bpy.context.active_object.data.materials.append(M["lamp"])
bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.17, depth=0.14, location=(1.5, -1.6, 0.41))
bpy.context.active_object.data.materials.append(M["dark"])
bpy.ops.object.light_add(type="POINT", location=(1.5, -1.6, 0.45))
lamp = bpy.context.active_object; lamp.data.energy = 90; lamp.data.color = hexc("#ffb85c")
lamp.data.shadow_soft_size = 0.3

# ---------------- scene a: bacteria, gas bubbles, arrows on cut faces ----------------
def on_face(a, r, z, off=0.03):
    """단면(각도 a 의 평면) 위 점. off 만큼 카메라 쪽으로 띄움."""
    ca, sa = math.cos(a), math.sin(a)
    nx, ny = (sa, -ca) if a == CUT[1] else (-sa, ca)
    return Vector((r * ca + nx * off, r * sa + ny * off, z))


bacts, bubbles, arrows = [], [], []
if cutaway:
    for _ in range(70):
        a = random.choice(CUT); r = R_HEART * math.sqrt(random.random()) * 0.95
        z = random.uniform(0.3, H - 0.3)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.035)
        o = bpy.context.active_object; o.data.materials.append(M["bact"])
        bacts.append((o, a, r, z, random.uniform(0, 1)))
    for _ in range(26):
        a = random.choice(CUT); r = R_HEART * math.sqrt(random.random()) * 0.85
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
        o = bpy.context.active_object; o.data.materials.append(M["gas"])
        bubbles.append((o, a, r, random.uniform(0.2, H - 0.8), random.uniform(0.05, 0.13), random.uniform(0, 1)))
    for a in CUT:
        for z in (1.0, 2.1, 3.2):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.045, depth=0.34)
            shaft = bpy.context.active_object
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.12, depth=0.2, location=(0, 0, 0.26))
            head = bpy.context.active_object
            shaft.select_set(True); head.select_set(True)
            bpy.context.view_layer.objects.active = shaft
            bpy.ops.object.join()
            shaft.data.materials.clear(); shaft.data.materials.append(M["arrow"])
            arrows.append((shaft, a, z))

# ---------------- scene b: saw, gas jet, foam ----------------
saw_parts, jets, foams = [], [], []
CUT_Z = 1.25
if not cutaway:
    bpy.ops.mesh.primitive_cube_add(size=1); body = bpy.context.active_object
    body.scale = (0.5, 0.26, 0.3); body.data.materials.append(M["saw"])
    bpy.ops.mesh.primitive_cube_add(size=1); bar = bpy.context.active_object
    bar.scale = (1.4, 0.035, 0.12); bar.data.materials.append(M["bar"])
    bpy.ops.mesh.primitive_cube_add(size=1); handle = bpy.context.active_object
    handle.scale = (0.06, 0.32, 0.24); handle.data.materials.append(M["dark"])
    saw_parts = [(body, Vector((0.7 + 1.4 - 0.1, 0, 0.06))), (bar, Vector((0.7, 0, 0))), (handle, Vector((1.95, 0, 0.3)))]
    # 톱자국(어두운 틈) — 톱이 들어간 만큼 길어짐
    bpy.ops.mesh.primitive_cube_add(size=1); kerf = bpy.context.active_object
    kerf.data.materials.append(M["dark"])
    for _ in range(170):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
        o = bpy.context.active_object; o.data.materials.append(M["gas"])
        jets.append((o, random.uniform(0, 1), random.uniform(-0.35, 0.35), random.uniform(-0.25, 0.25)))
    for _ in range(45):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
        o = bpy.context.active_object; o.data.materials.append(M["foam"])
        ang = random.uniform(math.radians(-80), math.radians(-10))
        foams.append((o, ang, random.uniform(0, 0.8), random.uniform(0.05, 0.1)))

# ---------------- world & light ----------------
world = bpy.data.worlds.new("sky"); scene.world = world
world.use_nodes = True
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

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(74), 0, math.radians(-40)))
sun = bpy.context.active_object; sun.data.energy = 3.0
sun.data.color = hexc("#ffb27a"); sun.data.angle = math.radians(3)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(160)))
fill = bpy.context.active_object; fill.data.energy = 0.8; fill.data.color = hexc("#8aa0ff")
bpy.ops.object.light_add(type="AREA", location=(3.5, -4.5, 2.5), rotation=(math.radians(70), 0, math.radians(38)))
key = bpy.context.active_object; key.data.energy = 220; key.data.size = 6
key.data.color = hexc("#ffd9b8")

# ---------------- camera ----------------
bpy.ops.object.empty_add(location=(0, 0, 2)); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 32; scene.camera = cam
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt
tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"


def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u


if cutaway:
    CAM_A, TGT_A = Vector((1.55, -1.55, 2.35)), Vector((0.0, 0.0, 2.05))
    CAM_B, TGT_B = Vector((4.3, -5.6, 3.0)), Vector((0.0, 0.0, 2.7))
else:
    CAM_A, TGT_A = Vector((2.6, -4.6, 1.9)), Vector((0.4, -0.4, 1.35))
    CAM_B, TGT_B = Vector((3.4, -5.6, 2.1)), Vector((0.2, -0.6, 1.45))

# ---------------- render settings ----------------
r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS
r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
r.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
r.use_persistent_data = True

os.makedirs(args.out, exist_ok=True)
heart_bsdf = M["heart"].node_tree.nodes["Principled BSDF"]
SAW_DIR = Vector((-math.cos(math.radians(-45)), -math.sin(math.radians(-45)), 0))  # 바깥(+x-y) → 안쪽
for fr in range(args.start, args.end, args.step):
    t = fr / FPS
    if cutaway:
        grow = ease(t / 2.4)                     # 세균·가스가 차오름
        for o, a, rr, z, ph in bacts:
            vis = 1.0 if ph < 0.35 + 0.65 * grow else 0.0
            o.location = on_face(a, rr, z + 0.03 * math.sin(7 * t + ph * 9), 0.02)
            s = vis * (0.8 + 0.3 * math.sin(9 * t + ph * 12)); o.scale = (s, s, s)
        for o, a, rr, z0, rad, ph in bubbles:
            show = ease((grow - ph * 0.6) / 0.4)
            z = z0 + 0.35 * ((t * 0.25 + ph) % 1.0)
            o.location = on_face(a, rr, z, 0.035)
            s = rad * show * (0.85 + 0.15 * math.sin(6 * t + ph * 8)); o.scale = (s, s, s * 0.9)
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t / 0.9)
        for o, a, z in arrows:
            rr = R_HEART * (0.55 + 0.25 * grow)
            o.location = on_face(a, rr, z, 0.05)
            ca, sa = math.cos(a), math.sin(a)
            o.rotation_euler = (0, math.radians(90), math.atan2(sa, ca))
            s = (0.3 + 1.0 * grow) * (0.85 + 0.2 * pulse); o.scale = (s, s, s)
        heart_bsdf.inputs["Emission Strength"].default_value = 0.2 + 0.25 * grow
        u = ease((t - 1.3) / 2.0)
    else:
        push = ease((t - 0.1) / 0.9)             # 톱이 0.1~1.0초에 들어감
        pull = ease((t - 1.25) / 0.6)             # 가스가 터지자 1.25초부터 톱을 뺌
        depth = 0.55 * push - 6.0 * pull          # 껍질+변재를 지나 심재에 닿음 → 뒤로 빠짐
        tip = Vector((R_BARK * math.cos(math.radians(-45)), R_BARK * math.sin(math.radians(-45)), CUT_Z)) + SAW_DIR * depth
        ang = math.atan2(-SAW_DIR.y, -SAW_DIR.x)
        for o, off in saw_parts:
            loc = Vector((off.x * math.cos(ang) - off.y * math.sin(ang), off.x * math.sin(ang) + off.y * math.cos(ang), off.z))
            o.location = tip + loc
            o.rotation_euler = (0, 0, ang)
            o.location.z += 0.01 * math.sin(90 * t) + 2.5 * pull    # 톱 떨림, 뺄 때 위로
        kerf.location = Vector((R_BARK * math.cos(math.radians(-45)), R_BARK * math.sin(math.radians(-45)), CUT_Z)) + SAW_DIR * (depth / 2 - 0.05)
        kerf.rotation_euler = (0, 0, ang)
        kd = 0.55 * push
        kerf.location = Vector((R_BARK * math.cos(math.radians(-45)), R_BARK * math.sin(math.radians(-45)), CUT_Z)) + SAW_DIR * (kd / 2 - 0.05)
        kerf.scale = (max(kd, 0.01) + 0.1, 0.9, 0.06)
        burst = ease((t - 1.0) / 0.35)            # 심재에 닿는 순간 가스가 터짐
        mouth = Vector((R_BARK * math.cos(math.radians(-45)), R_BARK * math.sin(math.radians(-45)), CUT_Z))
        out_dir = Vector((math.cos(math.radians(-80)), math.sin(math.radians(-80)), 0.35)).normalized()
        side = Vector((-out_dir.y, out_dir.x, 0))
        for o, ph, sx, sz in jets:
            u = (t * 1.6 + ph) % 1.0
            d = 0.15 + 3.2 * u * burst
            p = mouth + out_dir * d + side * (sx * u * 1.6 + 0.6 * u) + Vector((0, 0, sz * u * 1.4))
            o.location = p
            s = burst * (0.025 + 0.1 * u) * (1 - 0.5 * u); o.scale = (s, s, s)
        for o, ang2, ph, rad in foams:
            u = ease((t - 1.15 - ph) / 1.3)
            rr = R_BARK + 0.03
            a = math.radians(-45) + (ang2 - math.radians(-45)) * 0.5
            o.location = (rr * math.cos(a), rr * math.sin(a), CUT_Z - 0.05 - 1.0 * u)
            s = rad * min(u * 4, 1); o.scale = (s, s * 0.7, s * 1.3)
        u = ease(t / 3.0)
    cam.location = CAM_A.lerp(CAM_B, u)
    tgt.location = TGT_A.lerp(TGT_B, u)
    scene.frame_set(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
