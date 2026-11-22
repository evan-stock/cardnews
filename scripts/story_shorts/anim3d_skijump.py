"""오쓸 3D 그래픽: 스키점프 출발 트랙(인런)과 송풍기 — 2026.11.23, 20261123-skijump
공통 틀(로우폴리·노을 하늘·낮은 태양·조명탑 광원·카메라 TRACK_TO)은 anim3d_vortex.py 를 따르고 장면은 새로 짬.
사용: python3 scripts/story_shorts/anim3d_skijump.py --scene a --out /tmp/f_sa --start 0 --end 90 --step 2 --scale 60 --samples 10
  scene a: 얼음 홈(스키가 지나가는 길) 위 눈 부스러기 클로즈업 → 송풍기 바람에 날아감 → 카메라가 빠지며 트랙 옆 송풍기 줄
  scene b: 선수가 얼음 홈을 따라 빠르게 내려오다 남은 눈 한 덩이를 밟음 → 눈이 튀고 몸이 흔들림
"""
import argparse, math, random, os, sys
import bpy, bmesh
from mathutils import Vector, Matrix

ap = argparse.ArgumentParser()
ap.add_argument("--scene", default="a")
ap.add_argument("--out", default="frames")
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--end", type=int, default=90)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--samples", type=int, default=12)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
random.seed(11)
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
    "snow": mat("snow", "#e6ecf5", rough=0.9),
    "ice": mat("ice", "#8fd3ff", emit=1.2, rough=0.08),
    "wall": mat("wall", "#2c3852", rough=0.7),
    "rail": mat("rail", "#9aa3b5", rough=0.4),
    "walk": mat("walk", "#4b5263", rough=0.8),
    "jacket": mat("jacket", "#3f5b3c"),
    "skin": mat("skin", "#d9a77f"),
    "cap": mat("cap", "#1d2430"),
    "pack": mat("pack", "#ff7a1a", emit=0.4, rough=0.5),
    "tube": mat("tube", "#22262e", rough=0.5),
    "jet": mat("jet", "#c9ecff", emit=1.6, rough=0.9),
    "bit": mat("bit", "#ffffff", emit=0.9, rough=0.9),
    "flag": mat("flag", "#ff2d2d", emit=2.0),
    "suit": mat("suit", "#24366e", rough=0.5),
    "bib": mat("bib", "#f2f2f2", rough=0.6),
    "helmet": mat("helmet", "#e9e9ee", rough=0.3),
    "ski": mat("ski", "#1a1c22", rough=0.4),
    "skitip": mat("skitip", "#ffd23f", emit=1.5),
    "ring": mat("ring", "#ff3b30", emit=14),
    "lamp": mat("lamp", "#fff4d6", emit=40),
    "pole": mat("pole", "#555d6e"),
    "tree": mat("tree", "#22332b"),
    "hill": mat("hill", "#cfd8e8", rough=0.95),
    "hill2": mat("hill2", "#4a4566"),
}


def link(ob, parent=None, m=None):
    if m:
        ob.data.materials.append(M[m])
    if parent:
        ob.parent = parent
    return ob


def box(loc, scl, m, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = scl
    return link(o, parent, m)


def ico(loc, r, m, parent=None, sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    return link(bpy.context.active_object, parent, m)


def rod(a, b, r, m, parent=None, verts=6):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return link(o, parent, m)


# ---------------- 트랙(로컬: X 가로, -Y 내리막, Z 위) — ramp 가 30도 기울임 ----------------
ramp = bpy.data.objects.new("ramp", None)
scene.collection.objects.link(ramp)
ramp.rotation_euler = (math.radians(30), 0, 0)

GX = 0.30                                   # 두 얼음 홈의 x
box((0, -20, -0.2), (3.2, 70, 0.4), "snow", ramp)
for sx in (1, -1):
    box((GX * sx, -20, 0.004), (0.17, 70, 0.012), "ice", ramp)
    box((1.75 * sx, -20, 0.35), (0.22, 70, 0.9), "wall", ramp)          # 옆벽
    box((1.75 * sx, -20, 0.85), (0.08, 70, 0.08), "rail", ramp)          # 난간
box((2.55, -20, 0.05), (1.3, 70, 0.1), "walk", ramp)                    # 오른쪽 요원 통로

# 요원(송풍기) 줄 — 오른쪽 통로
crew = []
for k in range(22):
    y = 3.0 - k * 1.55
    x0 = 2.45
    body = box((x0, y, 0.55), (0.34, 0.26, 0.72), "jacket", ramp)
    ico((x0, y, 1.05), 0.15, "skin", ramp)
    box((x0, y, 1.17), (0.3, 0.3, 0.08), "cap", ramp)
    box((x0 + 0.2, y, 0.62), (0.16, 0.3, 0.42), "pack", ramp)
    noz = Vector((0.95, y - 0.55, 0.28))
    rod((x0 - 0.1, y, 0.62), noz, 0.05, "tube", ramp)
    # 바람 줄기(원뿔) — 노즐에서 트랙 쪽으로
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.02, radius2=0.14, depth=1.0)
    jet = link(bpy.context.active_object, ramp, "jet")
    jdir = Vector((-0.55, -1.0, -0.18)).normalized()
    jet.rotation_mode = "QUATERNION"
    jet.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(jdir)
    crew.append((noz, jdir, jet))
# 빨간 깃발 요원(맨 위)
box((1.3, 4.6, 0.55), (0.32, 0.26, 0.7), "jacket", ramp)
ico((1.3, 4.6, 1.02), 0.15, "skin", ramp)
rod((1.15, 4.6, 0.8), (0.75, 4.2, 0.85), 0.03, "tube", ramp)
flag = box((0.62, 4.1, 0.85), (0.25, 0.02, 0.18), "flag", ramp)


def place_jet(noz, jdir, jet, s):
    L = 1.6 * s
    jet.scale = (max(s, 0.001),) * 2 + (max(L, 0.001),)
    jet.location = noz + jdir * (L / 2)
    jet.hide_render = s < 0.03


# 눈 부스러기
bits = []
for k in range(170):
    gx = random.choice((GX, -GX, random.uniform(-1.2, 1.2)))
    y = random.uniform(-11, 3)
    p = Vector((gx + random.uniform(-0.09, 0.09), y, 0.03))
    o = ico(p, random.uniform(0.025, 0.06), "bit", ramp)
    tb = 0.45 + (3 - y) * 0.035 + random.uniform(0, 0.35)
    v = Vector((random.uniform(-1.6, -0.4), random.uniform(-4.5, -2.0), random.uniform(0.6, 1.8)))
    bits.append((o, p, tb, v, o.scale.copy()))

# 장면 b 용: 남은 눈 한 덩이 + 선수
LUMP_Y = -14.0
lump = []
for k in range(34):
    p = Vector((GX + random.uniform(-0.13, 0.13), LUMP_Y + random.uniform(-0.2, 0.2), 0.05 + random.uniform(0, 0.12)))
    o = ico(p, random.uniform(0.06, 0.11), "bit", ramp)
    v = Vector((random.uniform(-0.6, 1.4), random.uniform(-3.5, 0.5), random.uniform(1.0, 2.6)))
    lump.append((o, p, v))

skier = bpy.data.objects.new("skier", None)
scene.collection.objects.link(skier)
skier.parent = ramp
for sx in (1, -1):
    box((GX * sx, -0.2, 0.03), (0.09, 2.5, 0.03), "ski", skier)
    box((GX * sx, -1.42, 0.05), (0.09, 0.12, 0.03), "skitip", skier)
    box((GX * sx * 0.9, 0.0, 0.14), (0.12, 0.24, 0.16), "cap", skier)                  # 부츠
    rod((GX * sx * 0.9, 0.0, 0.2), (GX * sx * 0.7, -0.25, 0.55), 0.08, "suit", skier)   # 정강이
    rod((GX * sx * 0.7, -0.25, 0.55), (GX * sx * 0.55, 0.25, 0.75), 0.09, "suit", skier)  # 허벅지
    rod((0.22 * sx, -0.25, 0.95), (0.2 * sx, 0.45, 0.6), 0.05, "suit", skier)           # 팔(뒤로)
rod((0, 0.25, 0.75), (0, -0.4, 1.0), 0.2, "suit", skier, verts=8)                      # 몸통(앞으로 숙임)
box((0, -0.12, 0.92), (0.3, 0.34, 0.2), "bib", skier, rot=(math.radians(-20), 0, 0))
ico((0, -0.62, 1.06), 0.14, "helmet", skier)
for ch in skier.children:
    ch.hide_render = args.scene != "b"

bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.03, location=(GX, LUMP_Y, 0.1))
ring = link(bpy.context.active_object, ramp, "ring")

# ---------------- 배경: 조명탑(빛나는 광원)·눈 언덕·나무 ----------------
for (x, y) in ((-7, -3), (-7, -17), (8.5, -10)):
    rod((x, y, 0), (x, y, 7.5), 0.12, "pole", ramp)
    box((x, y, 7.7), (1.2, 0.3, 0.6), "lamp", ramp)
    bpy.ops.object.light_add(type="SPOT", location=(x, y, 7.4))
    L = bpy.context.active_object
    L.parent = ramp
    L.data.energy = 2500; L.data.spot_size = math.radians(70); L.data.color = hexc("#fff1d0")
    L.rotation_mode = "QUATERNION"
    L.rotation_quaternion = Vector((0, 0, -1)).rotation_difference((Vector((0, y - 4, 0)) - Vector((x, y, 7.4))).normalized())
for k in range(60):
    x = random.choice((-1, 1)) * random.uniform(5, 30); y = random.uniform(-60, 20)
    s_ = random.uniform(0.8, 2.2)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.6 * s_, depth=2.6 * s_, location=(x, y, 1.0 * s_))
    link(bpy.context.active_object, ramp, "tree")
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -40, -26))
gp = link(bpy.context.active_object, None, "hill"); gp.scale = (400, 400, 1)

# ---------------- 하늘·빛 ----------------
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
rmp = nt.nodes.new("ShaderNodeValToRGB"); bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], rmp.inputs[0])
nt.links.new(rmp.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
cr = rmp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = (*hexc("#f2a65a"), 1)
e = cr.elements.new(0.12); e.color = (*hexc("#c76b8a"), 1)
e = cr.elements.new(0.3); e.color = (*hexc("#4a3f7a"), 1)
cr.elements[-1].position = 0.7; cr.elements[-1].color = (*hexc("#141a3a"), 1)
bg.inputs[1].default_value = 0.8

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(76), 0, math.radians(140)))
sun = bpy.context.active_object; sun.data.energy = 2.6; sun.data.color = hexc("#ffb27a"); sun.data.angle = math.radians(3)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(45), 0, math.radians(-40)))
fill = bpy.context.active_object; fill.data.energy = 0.9; fill.data.color = hexc("#8aa0ff")

bpy.ops.object.empty_add(); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 28; scene.camera = cam
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
bpy.context.view_layer.update()
RW = ramp.matrix_world.copy()


def W(v):
    return RW @ Vector(v)


def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


# ---------------- 렌더 ----------------
r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS; r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
r.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = args.samples
scene.cycles.use_denoising = True; scene.cycles.max_bounces = 4; r.use_persistent_data = True

os.makedirs(args.out, exist_ok=True)
for fr in range(args.start, args.end, args.step):
    t = fr / FPS
    if args.scene == "a":
        js = ease((t - 0.25) / 0.35) * (0.85 + 0.15 * math.sin(t * 23))
        for noz, jdir, jet in crew:
            place_jet(noz, jdir, jet, js)
        for o, p, tb, v, s0 in bits:
            u = max(t - tb, 0)
            o.location = p + Vector((v.x * u, v.y * u, v.z * u - 2.2 * u * u))
            o.scale = s0 * max(1 - u / 0.9, 0)
            o.hide_render = u > 0.9
        for o, p, v in lump:
            o.hide_render = True
        ring.hide_render = True
        flag.rotation_euler = (0, math.radians(12 * math.sin(t * 8)), 0)
        u = ease((t - 1.0) / 1.8)
        CA, TA = Vector((0.75, 1.6, 0.42)), Vector((0.15, -2.8, 0.03))
        CB, TB = Vector((-3.6, 6.5, 4.6)), Vector((1.0, -6.5, 0.2))
        cam.location = W(CA.lerp(CB, u)); tgt.location = W(TA.lerp(TB, u))
    else:
        for noz, jdir, jet in crew:
            place_jet(noz, jdir, jet, 0)
        for o, p, tb, v, s0 in bits:
            o.hide_render = True
        flag.rotation_euler = (0, 0, 0)
        T_HIT = 1.5
        y0, v1, v2 = 2.0, -10.6, -8.2                     # 맞은 뒤 느려짐
        sy = y0 + v1 * min(t, T_HIT) + v2 * max(t - T_HIT, 0)
        k = max(t - T_HIT, 0)
        wob = math.radians(14) * math.exp(-k * 2.2) * math.sin(k * 14) if t > T_HIT else 0
        skier.location = (0.05 * math.sin(k * 14) * math.exp(-k * 2) if t > T_HIT else 0, sy, 0)
        skier.rotation_euler = (0, wob, wob * 0.4)
        for o, p, v in lump:
            u = max(t - T_HIT, 0)
            o.location = p + Vector((v.x * u, v.y * u, v.z * u - 3.0 * u * u))
            o.hide_render = u > 1.0
        ring.hide_render = not (T_HIT <= t < T_HIT + 0.5)
        rs = 0.3 + 4.0 * max(t - T_HIT, 0)
        ring.scale = (rs, rs, rs)
        ring.location = (GX, LUMP_Y, 0.1)
        # 카메라: 선수 옆 앞쪽에서 함께 내려가다(0~1.5초) 맞는 순간 앞에서 멈춰 지나가는 걸 봄
        cy = sy
        cam.location = W((-1.25, cy + 2.6, 2.4)); tgt.location = W((0.35, cy - 3.6, 0.0))
    scene.frame_set(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
