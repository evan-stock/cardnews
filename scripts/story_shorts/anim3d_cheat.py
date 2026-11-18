"""오쓸 3D 그래픽: 세무사 수석 AI 부정행위 수법 시뮬레이션(경향신문 2026.11.18 단독 보도 내용 그대로)
본보기 anim3d_clay.py 를 복사해 장면을 새로 짬(2026.11.18, 20261118-cheat3d).
  수정테이프에 붙인 초소형 카메라로 시험지 촬영 → 무선 키보드처럼 개조한 계산기로 명령 입력
  → 휴대전화 → 자택 노트북의 AI가 풀이 → 다시 시험장으로 → 초소형 모니터로 답 확인
사용: python3 scripts/story_shorts/anim3d_cheat.py --out /tmp/f_cheat --start 0 --end 210 --scale 60 --samples 10
      --labels out.json 을 주면 이름표 위치(1080x780 기준)를 계산해 저장하고 렌더는 하지 않음
"""
import argparse, json, math, random, os, sys
import bpy, bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="frames")
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--end", type=int, default=210)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--samples", type=int, default=24)
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--labels", default="")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
random.seed(5)
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


def bsdf(m): return m.node_tree.nodes["Principled BSDF"]


M = {
    "desk": mat("desk", "#b07a4a", rough=0.6), "floor": mat("floor", "#5d6470"), "ground": mat("ground", "#3b4a3a"),
    "paper": mat("paper", "#f4f1e8", rough=0.9), "ink": mat("ink", "#3a3a44"),
    "tape": mat("tape", "#dfe8f2", rough=0.4), "tape2": mat("tape2", "#3d7bd9", rough=0.4),
    "lens": mat("lens", "#111111", rough=0.2), "rec": mat("rec", "#ff3b3b", emit=6.0),
    "beam": mat("beam", "#ff6b6b", emit=3.0),
    "calc": mat("calc", "#2b2f3a", rough=0.5), "key": mat("key", "#596070", rough=0.6),
    "keyon": mat("keyon", "#ffd84d", emit=5.0), "lcd": mat("lcd", "#9fb89a", emit=0.6),
    "phone": mat("phone", "#16181d", rough=0.3), "pscreen": mat("pscreen", "#5ab0ff", emit=2.5),
    "mon": mat("mon", "#1a1c22", rough=0.4), "mscreen": mat("mscreen", "#0c1410", emit=0.3),
    "mline": mat("mline", "#5dff8a", emit=6.0),
    "wall": mat("wall", "#d8cbb4"), "roof": mat("roof", "#8a3b32"), "window": mat("window", "#ffc46b", emit=6.0),
    "laptop": mat("laptop", "#8c919c", rough=0.4), "lscreen": mat("lscreen", "#7d5cff", emit=4.0),
    "packet": mat("packet", "#8fe3ff", emit=9.0, rough=0.3), "packet2": mat("packet2", "#5dff8a", emit=9.0, rough=0.3),
    "line": mat("line", "#8fe3ff", emit=1.2), "hill": mat("hill", "#4a4566"), "hill2": mat("hill2", "#38344f"),
    "tree": mat("tree", "#26352c"),
}


def box(loc, size, m, parent=None, name="b"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = size; o.data.materials.append(M[m] if isinstance(m, str) else m)
    if parent: o.parent = parent
    return o


def cyl(loc, r, d, m, rot=(0, 0, 0), v=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.data.materials.append(M[m]); return o


def rod(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a
    o = cyl((a + b) / 2, r, d.length, m, v=6)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o


# ---------------- 시험장 책상 ----------------
box((0, 0, -0.62), (9, 7, 0.1), "floor")                       # 교실 바닥 섬
box((0, 0, -0.15), (6.4, 4.2, 0.3), "desk")
for lx in (-2.9, 2.9):
    for ly in (-1.8, 1.8):
        box((lx, ly, -0.38), (0.2, 0.2, 0.45), "desk")
PAPER = Vector((-0.9, 0.3, 0.005))
box(PAPER, (2.2, 3.0, 0.01), "paper")
for k in range(11):                                               # 시험지 글줄
    w = random.uniform(1.0, 1.8)
    box((PAPER.x - 0.9 + w / 2, PAPER.y + 1.25 - k * 0.24, 0.013), (w, 0.05, 0.004), "ink")

# 수정테이프 + 초소형 카메라(렌즈가 시험지를 향함)
TAPE = Vector((1.15, 1.25, 0.13))
tp = box(TAPE, (0.75, 0.32, 0.24), "tape", name="tape")
box(TAPE + Vector((0.18, 0, 0.0)), (0.3, 0.33, 0.25), "tape2")
lens = cyl(TAPE + Vector((-0.38, 0, 0.04)), 0.055, 0.04, "lens", rot=(0, math.radians(90), 0))
rec = cyl(TAPE + Vector((-0.4, 0, 0.04)), 0.025, 0.02, "rec", rot=(0, math.radians(90), 0))
LENS = TAPE + Vector((-0.42, 0, 0.04))
beam = [rod(LENS, PAPER + Vector((dx, dy, 0.02)), 0.008, "beam") for dx, dy in ((-1.0, 1.4), (1.0, 1.4), (-1.0, -1.4), (1.0, -1.4))]

# 계산기(무선 키보드처럼 개조) — 버튼 = 단축 명령어
CALC = Vector((1.55, -0.75, 0.07))
box(CALC, (1.0, 1.5, 0.14), "calc")
box(CALC + Vector((0, 0.5, 0.075)), (0.8, 0.32, 0.01), "lcd")
keys = []
for r in range(5):
    for c in range(4):
        keys.append(box(CALC + Vector((-0.33 + c * 0.22, 0.18 - r * 0.2, 0.085)), (0.16, 0.14, 0.04), M["key"].copy()))
KEYSEQ = [3, 9, 14, 6, 17, 1, 11]

# 초소형 모니터(손 옆, 답 확인)
MON = Vector((0.55, -1.35, 0.16))
mon = box(MON, (0.42, 0.06, 0.3), "mon")
mon.rotation_euler = (math.radians(-18), 0, 0)
msc = box(MON + Vector((0, -0.035, 0.01)), (0.36, 0.01, 0.24), "mscreen"); msc.rotation_euler = mon.rotation_euler
mlines = []
for k in range(4):
    o = box(MON + Vector((-0.12 + 0.04 * (k % 2), -0.045, 0.08 - k * 0.055)), (0.18 - 0.03 * (k % 3), 0.006, 0.022), "mline")
    o.rotation_euler = mon.rotation_euler; mlines.append(o)

# 휴대전화(책상 아래 주머니 쪽)
PHONE = Vector((2.6, -2.5, -0.55))
ph = box(PHONE, (0.42, 0.8, 0.06), "phone")
box(PHONE + Vector((0, 0, 0.035)), (0.36, 0.7, 0.01), "pscreen")

# ---------------- 자택(멀리) + 노트북 AI ----------------
HOME = Vector((10.0, 15.0, -0.6))
box(HOME + Vector((0, 0, -0.1)), (9, 7, 0.2), "ground")
box(HOME + Vector((0, 1.2, 0.75)), (2.4, 1.9, 1.5), "wall")
rme = bpy.data.meshes.new("roof"); rf = bpy.data.objects.new("roof", rme); scene.collection.objects.link(rf)
rb = bmesh.new(); o = HOME + Vector((0, 1.2, 0))
pts = [rb.verts.new(o + Vector(v)) for v in [(-1.4, -1.15, 1.5), (1.4, -1.15, 1.5), (1.4, 1.15, 1.5), (-1.4, 1.15, 1.5), (-1.4, 0, 2.5), (1.4, 0, 2.5)]]
for fc in [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]:
    rb.faces.new([pts[k] for k in fc])
rb.normal_update(); rb.to_mesh(rme); rb.free(); rf.data.materials.append(M["roof"])
for wx in (-0.6, 0.6):
    box(HOME + Vector((wx, 0.24, 0.85)), (0.45, 0.04, 0.5), "window")
LAP = HOME + Vector((0, -1.6, 0.0))
box(LAP + Vector((0, 0, 0.35)), (1.8, 1.0, 0.7), "desk")                     # 작은 탁자
box(LAP + Vector((0, 0, 0.73)), (1.1, 0.75, 0.05), "laptop")
lid = box(LAP + Vector((0, 0.36, 1.08)), (1.1, 0.05, 0.7), "laptop")
lsc = box(LAP + Vector((0, 0.33, 1.08)), (1.0, 0.01, 0.6), "lscreen")
bpy.ops.object.light_add(type="POINT", location=LAP + Vector((0, -0.6, 1.2))); ll = bpy.context.active_object
ll.data.energy = 80; ll.data.color = hexc("#9d85ff")
LAPSC = LAP + Vector((0, 0.3, 1.08))

# ---------------- 신호 경로 ----------------
def arc(a, b, h, n=24):
    return [a.lerp(b, i / n) + Vector((0, 0, h * math.sin(math.pi * i / n))) for i in range(n + 1)]


def path_len(p): return sum((p[i + 1] - p[i]).length for i in range(len(p) - 1))


def at(p, u):
    u = min(max(u, 0), 1); L = path_len(p) * u
    for i in range(len(p) - 1):
        s = (p[i + 1] - p[i]).length
        if L <= s: return p[i].lerp(p[i + 1], L / s if s else 0)
        L -= s
    return p[-1]


CALCK = CALC + Vector((0, 0, 0.2))
P1 = [LENS, CALCK]                                    # 촬영 → 계산기 명령
P2 = [CALCK, PHONE + Vector((0, 0, 0.1))]             # 계산기 → 휴대전화
P3 = arc(PHONE + Vector((0, 0, 0.1)), LAPSC, 6.0)     # 휴대전화 → 자택 노트북
P4 = arc(LAPSC, PHONE + Vector((0, 0, 0.1)), 4.5)     # 노트북(AI 풀이) → 휴대전화
P5 = [PHONE + Vector((0, 0, 0.1)), MON + Vector((0, -0.05, 0.05))]   # → 초소형 모니터
for p in (P3, P4):                                    # 옅은 길 표시
    for i in range(0, len(p) - 1, 2):
        rod(p[i], p[i + 1], 0.02, "line")


def make_packets(n, m):
    out = []
    for _ in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.09)
        o = bpy.context.active_object; o.data.materials.append(M[m]); out.append(o)
    return out


PK_OUT = make_packets(6, "packet")
PK_IN = make_packets(6, "packet2")

# ---------------- 배경 ----------------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 40, -0.7))
f_ = bpy.context.active_object; f_.scale = (300, 220, 1); f_.data.materials.append(M["ground"])
for k in range(9):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    hh = bpy.context.active_object
    hh.location = (random.uniform(-60, 70), random.uniform(60, 95), -2)
    hh.scale = (random.uniform(14, 26), random.uniform(6, 10), random.uniform(5, 11))
    hh.data.materials.append(M["hill"] if k % 2 else M["hill2"])
for _ in range(50):
    x = random.uniform(-20, 40); y = random.uniform(12, 45)
    if (abs(x - HOME.x) < 6 and abs(y - HOME.y) < 6) or (abs(x) < 9 and y < 16):
        continue
    s_ = random.uniform(0.7, 1.6)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.45 * s_, depth=1.9 * s_, location=(x, y, 0.2 * s_))
    bpy.context.active_object.data.materials.append(M["tree"])

# ---------------- 하늘 & 조명(본보기와 같은 해 질 녘) ----------------
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB"); bg = nt.nodes.new("ShaderNodeBackground"); out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], ramp.inputs[0])
nt.links.new(ramp.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
cr = ramp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = (*hexc("#f2a65a"), 1)
e = cr.elements.new(0.12); e.color = (*hexc("#c76b8a"), 1)
e = cr.elements.new(0.3); e.color = (*hexc("#4a3f7a"), 1)
cr.elements[-1].position = 0.7; cr.elements[-1].color = (*hexc("#141a3a"), 1)
bg.inputs[1].default_value = 0.7
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(60), 0, math.radians(-35)))
sun = bpy.context.active_object; sun.data.energy = 3.0; sun.data.color = hexc("#ffb27a")
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(160)))
fill = bpy.context.active_object; fill.data.energy = 0.9; fill.data.color = hexc("#8aa0ff")
bpy.ops.object.light_add(type="AREA", location=(0, -5, 4), rotation=(math.radians(50), 0, 0))
key = bpy.context.active_object; key.data.energy = 260; key.data.size = 8; key.data.color = hexc("#ffd9b8")

# ---------------- 카메라 ----------------
bpy.ops.object.empty_add(location=(0, 0, 0)); tgt = bpy.context.active_object
bpy.ops.object.camera_add(); cam = bpy.context.active_object
cam.data.lens = 32; scene.camera = cam
trk = cam.constraints.new("TRACK_TO"); trk.target = tgt; trk.track_axis = "TRACK_NEGATIVE_Z"; trk.up_axis = "UP_Y"


def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u


# (시각, 카메라 위치, 바라보는 곳)
KEYS = [
    (0.0, Vector((-1.6, -3.6, 2.6)), Vector((0.3, 0.6, 0.0))),     # 책상 가까이: 수정테이프·시험지
    (1.8, Vector((-0.6, -3.9, 2.9)), Vector((0.9, 0.0, 0.0))),     # 계산기 쪽으로
    (3.0, Vector((-1.0, -6.5, 4.2)), Vector((1.6, -0.6, -0.2))),   # 휴대전화까지 보이게
    (4.6, Vector((-4.5, -7.5, 7.0)), Vector((5.0, 7.0, 0.3))),     # 높이 빠져 자택까지 경로 전체
    (5.6, Vector((-4.0, -7.0, 6.6)), Vector((5.0, 7.0, 0.3))),
    (7.0, Vector((-0.4, -3.4, 1.5)), Vector((0.55, -1.35, 0.2))),  # 초소형 모니터로 들어감
]


def campose(t):
    for (t0, c0, g0), (t1, c1, g1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            u = ease((t - t0) / (t1 - t0)); return c0.lerp(c1, u), g0.lerp(g1, u)
    return KEYS[-1][1], KEYS[-1][2]


# 단계 시각(초)
T_SHOT, T_KEY, T_PH, T_HOME, T_AI, T_BACK, T_MON = 0.4, 1.6, 2.6, 3.2, 4.6, 5.1, 6.2


def setup(fr):
    t = fr / FPS
    flash = 0.5 + 0.5 * math.sin(t * 14)
    on = T_SHOT <= t <= T_KEY + 0.4
    bsdf(M["rec"]).inputs["Emission Strength"].default_value = 3 + 6 * flash
    for b in beam:
        b.hide_render = not on
    bsdf(M["beam"]).inputs["Emission Strength"].default_value = 2 + 3 * flash
    # 계산기 키가 차례로 눌림(노랑으로 켜졌다 꺼짐)
    for i, k in enumerate(keys):
        bs = bsdf(k.data.materials[0])
        lit = False
        if i in KEYSEQ:
            tk = T_KEY + 0.13 * KEYSEQ.index(i)
            lit = tk <= t <= tk + 0.18
        bs.inputs["Base Color"].default_value = (*hexc("#ffd84d" if lit else "#596070"), 1)
        bs.inputs["Emission Color"].default_value = (*hexc("#ffd84d"), 1)
        bs.inputs["Emission Strength"].default_value = 5.0 if lit else 0.0
        k.location.z = CALC.z + 0.085 - (0.025 if lit else 0)
    # 보내는 신호(파랑): 촬영 → 계산기 → 휴대전화 → 자택
    for j, o in enumerate(PK_OUT):
        d = j * 0.07
        if t < T_SHOT + 0.5 + d: u, p = 0, None
        elif t < T_PH + d: u, p = (t - T_SHOT - 0.5 - d) / (T_PH - T_SHOT - 0.5), P1 + P2[1:]
        elif t < T_AI + d: u, p = (t - T_PH - d) / (T_AI - T_PH), P3
        else: u, p = 1, None
        o.hide_render = p is None
        if p: o.location = at(p, u)
    # 노트북 AI가 푸는 동안 화면이 깜박임
    busy = T_HOME + 0.6 <= t <= T_BACK + 0.4
    bsdf(M["lscreen"]).inputs["Emission Strength"].default_value = 4 + (6 * (0.5 + 0.5 * math.sin(t * 22)) if busy else 0)
    # 돌아오는 답(초록): 노트북 → 휴대전화 → 초소형 모니터
    for j, o in enumerate(PK_IN):
        d = j * 0.07
        if t < T_BACK + d: u, p = 0, None
        elif t < T_MON + d: u, p = (t - T_BACK - d) / (T_MON - T_BACK), P4 + P5[1:]
        else: u, p = 1, None
        o.hide_render = p is None
        if p: o.location = at(p, u)
    # 초소형 모니터: 답이 오면 초록 글줄이 차례로 켜짐
    for k, o in enumerate(mlines):
        o.hide_render = t < T_MON - 0.1 + k * 0.12
    bsdf(M["mscreen"]).inputs["Emission Strength"].default_value = 0.3 + (1.5 if t >= T_MON - 0.1 else 0)
    c, g = campose(t); cam.location = c; tgt.location = g
    scene.frame_set(fr)


r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 780, args.scale
r.fps = FPS; r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"

if args.labels:   # 이름표 위치 계산(1080x780 기준 화면 좌표)
    marks = {"tape": TAPE, "calc": CALC, "phone": PHONE, "laptop": LAPSC, "mon": MON, "paper": PAPER}
    outj = {}
    for fr in range(args.start, args.end, 15):
        setup(fr); bpy.context.view_layer.update()
        outj[fr] = {k: [round(v.x * 1080), round((1 - v.y) * 780)] for k, p in marks.items()
                    for v in [world_to_camera_view(scene, cam, p)]}
    json.dump(outj, open(args.labels, "w"), indent=0); print("labels", args.labels); sys.exit(0)

if args.engine == "CYCLES":
    r.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True; scene.cycles.max_bounces = 4; r.use_persistent_data = True
else:
    r.engine = args.engine
os.makedirs(args.out, exist_ok=True)
for fr in range(args.start, args.end, args.step):
    setup(fr)
    r.filepath = os.path.join(args.out, f"f{fr:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("done", fr, flush=True)
