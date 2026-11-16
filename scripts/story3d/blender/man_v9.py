# 이 남자 v3: 기본 도형을 합친 뒤 복셀 리메시+스무딩으로 점토처럼 한 덩어리로 녹임(크기 제어가 정확함)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from mathutils import Euler, Matrix
from PIL import ImageFilter
OUT = sys.argv[-1]

def _sel(objs, active):
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    for ob in objs: ob.select_set(True)
    bpy.context.view_layer.objects.active = active
def prim(p):
    k = p[0]
    if k == 'e':  # 타원체: 중심, 반지름(x,y,z), 회전
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24, location=p[1]); o = bpy.context.active_object; o.scale = p[2]
        if len(p) > 3: o.rotation_euler = p[3]
    elif k == 'c':  # 캡슐: 시작점, 끝점, 반지름
        a, b, r = Vector(p[1]), Vector(p[2]), p[3]; d = b - a
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=32, location=(a + b) / 2); o = bpy.context.active_object
        o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); objs = [o]
        for q in (a, b): bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=32, ring_count=16, location=q); objs.append(bpy.context.active_object)
        _sel(objs, o); bpy.ops.object.join(); o = bpy.context.active_object
    elif k == 't':  # 도넛: 중심, 큰반지름, 작은반지름, 회전
        bpy.ops.mesh.primitive_torus_add(major_radius=p[2], minor_radius=p[3], location=p[1], rotation=p[4] if len(p) > 4 else (0, 0, 0)); o = bpy.context.active_object
    elif k == 'b':  # 상자: 중심, 크기
        bpy.ops.mesh.primitive_cube_add(size=1, location=p[1]); o = bpy.context.active_object; o.scale = p[2]
    _sel([o], o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); return o
def blob(name, parts, mat, vox=0.012, sub=(), smooth=6):
    objs = [prim(p) for p in parts]; base = objs[0]
    _sel(objs, base); bpy.ops.object.join(); base = bpy.context.active_object; base.name = name
    base.data.remesh_voxel_size = vox; bpy.ops.object.voxel_remesh()
    for s in sub:
        c = prim(s)
        if s[0] == 'c': c.data.remesh_voxel_size = vox * 0.5; _sel([c], c); bpy.ops.object.voxel_remesh()
        m = base.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = c; m.solver = 'EXACT'
        _sel([base], base); bpy.ops.object.modifier_apply(modifier='cut'); bpy.data.objects.remove(c)
    if sub: bpy.ops.object.voxel_remesh()
    if smooth: s = base.modifiers.new('sm', 'SMOOTH'); s.factor = 0.8; s.iterations = smooth
    bpy.ops.object.shade_smooth(); base.data.materials.clear(); base.data.materials.append(mat); return base
def surf(obj, x, z, eps=0.004):
    dg = bpy.context.evaluated_depsgraph_get(); ev = obj.evaluated_get(dg)
    hit, loc, n, i = ev.ray_cast(Vector((x, -3, z)), Vector((0, 1, 0)))
    return (loc.x, loc.y - eps, loc.z) if hit else (x, -0.3, z)
def oriented(o, d):
    o.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler(); return o

# ── 배경·재질
world((0.75, 0.56, 0.36), 0.6)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, size=40); bg = bpy.context.active_object
for v in bg.data.vertices:
    if v.co.y > 3.5: d = v.co.y - 3.5; v.co.z = d * d * 0.3 if d < 3 else (2.7 + (d - 3) * 1.8)
bpy.ops.object.shade_smooth(); bg.data.materials.append(M('bg', (0.6, 0.44, 0.27), 0.95, emit=(0.6, 0.44, 0.27), ei=0.08))
SKIN = M('skin', (0.91, 0.64, 0.5), 0.5, sss=0.1, sss_r=(1.0, 0.35, 0.22))
NOSE = M('nose', (0.95, 0.5, 0.36), 0.4, sss=0.12)
TEAL = M('teal', (0.02, 0.13, 0.2), 0.82, sheen=0.25, bump=0.05, bump_scale=260)
TEAL_D = M('tealD', (0.016, 0.105, 0.16), 0.8, sheen=0.2, bump=0.15, bump_scale=120)
NAVY = M('navy', (0.005, 0.008, 0.045), 0.65, sheen=0.1, bump=0.04, bump_scale=300)
WHITE = M('white', (0.85, 0.85, 0.84), 0.5, sss=0.05)
HAIR = M('hair', (0.008, 0.008, 0.01), 0.55)
INK = M('ink', (0.01, 0.008, 0.007), 0.35)
EYEW = M('eyew', (0.92, 0.92, 0.9), 0.2, coat=0.6)
LIP = M('lip', (0.6, 0.12, 0.1), 0.4)
GREY = M('grey', (0.3, 0.32, 0.35), 0.35, metal=0.5)
STR = M('str', (0.18, 0.2, 0.23), 0.7)
everything = []

# ── 머리
HC = Vector((0, 0, 2.45)); HR = 0.51
head = sphere('head', HR, SKIN, tuple(HC), (1.1, 0.98, 0.97), seg=96, rings=48)
blush = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0)); g = ImageDraw.Draw(blush)
for cx in (0.27, 0.73): g.ellipse([cx * 1024 - 100, 0.67 * 1024 - 62, cx * 1024 + 100, 0.67 * 1024 + 62], fill=(255, 95, 90, 200))
blush.filter(ImageFilter.GaussianBlur(38)).save(os.path.join(TMP, 'blush.png')); add_face(SKIN, os.path.join(TMP, 'blush.png'), HR)
def sp(az, el, r=HR):
    return HC + Vector((1.1 * math.sin(az) * math.cos(el), -0.98 * math.cos(az) * math.cos(el), 0.97 * math.sin(el))) * r
def dirv(az, el): return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
for sx in (-1, 1):
    oriented(sphere('ear', 0.15, SKIN, tuple(sp(sx * 1.5, -0.04, HR + 0.0)), (0.75, 1.05, 0.5)), dirv(sx * 1.5, 0))
    az, el = sx * 0.33, 0.0
    oriented(sphere('eyeW', 0.112, EYEW, tuple(sp(az, el, HR - 0.014)), (0.9, 0.95, 0.42)), dirv(az, el))
    oriented(sphere('pupil', 0.046, INK, tuple(sp(az + 0.085, el - 0.005, HR + 0.022)), (0.9, 1.05, 0.35)), dirv(az + 0.085, el))
    sphere('hl', 0.012, M('hl', (1, 1, 1), 0.1, emit=(1, 1, 1), ei=4), tuple(sp(az + 0.11, el + 0.035, HR + 0.04)))
    if 0: tube('lid', [tuple(sp(sx * a, e, HR + 0.03)) for a, e in ((0.22, 0.155), (0.34, 0.205), (0.46, 0.15))], 0.007, INK)
    tube('brow', [tuple(sp(sx * a, e, HR + 0.012)) for a, e in ((0.21, 0.225), (0.33, 0.24), (0.45, 0.225))], 0.03, INK)
sphere('nose', 0.062, NOSE, tuple(sp(0.03, -0.13, HR + 0.012)), (1.0, 0.9, 0.85))
tube('mouth', [tuple(sp(a, e, HR + 0.004)) for a, e in ((-0.06, -0.3), (0.03, -0.33), (0.12, -0.295))], 0.013, LIP)
# 머리카락: 모자 같은 덩어리에서 얼굴 쪽을 파내고, 앞머리 덩어리 추가
hair = blob('hair', [('e', (0, 0.04, 2.53), (0.61, 0.55, 0.51)),
                     ('e', tuple(sp(0.36, 0.47, HR + 0.0)), (0.1, 0.07, 0.08), (0.4, 0, 0.4)), ('e', tuple(sp(0.12, 0.58, HR + 0.0)), (0.22, 0.08, 0.09), (0.55, 0, 0.15))], HAIR, vox=0.01,
            sub=[('e', (0, -0.43, 2.2), (0.5, 0.5, 0.52)), ('e', (0, 0.1, 2.05), (0.65, 0.65, 0.36))], smooth=8)

# ── 후드티 몸통
body = blob('hoodie', [('e', (0, 0, 1.46), (0.46, 0.3, 0.56)), ('e', (0, 0.0, 1.78), (0.42, 0.28, 0.24)),
                       ('t', (0, 0.07, 1.95), 0.31, 0.15, (-0.5, 0, 0)), ('e', (0, 0.22, 2.02), (0.36, 0.2, 0.22))], TEAL, smooth=14, sub=[('e', (0, -0.36, 2.04), (0.11, 0.16, 0.2), (0.3, 0, 0))])
sphere('tee', 0.15, WHITE, (0, -0.17, 1.9), (0.7, 0.6, 0.6))
hem = cyl('hem', 0.4, 0.07, TEAL_D, (0, 0, 1.0)); hem.scale = (1, 0.74, 1)
for sx in (-1, 1):
    a, b = Vector((sx * 0.43, 0, 1.84)), Vector((sx * 0.57, -0.02, 1.1))
    blob('arm', [('c', tuple(a), tuple(b), 0.14)], TEAL)
    cuff = cyl('cuff', 0.125, 0.11, TEAL_D, tuple(b + (b - a).normalized() * 0.08)); oriented(cuff, b - a)
    gx = sx * 0.59
    G = lambda p: tuple(Vector((gx, -0.02, 0.95)) + (Vector(p) - Vector((gx, -0.02, 0.95))) * 1.4)
    blob('glove', [('e', G((gx, -0.02, 0.88)), (0.091, 0.119, 0.119)),
                   ('c', G((gx, -0.075, 0.84)), G((gx + sx * 0.005, -0.08, 0.74)), 0.038), ('c', G((gx, -0.028, 0.83)), G((gx + sx * 0.01, -0.03, 0.72)), 0.039),
                   ('c', G((gx, 0.018, 0.83)), G((gx + sx * 0.01, 0.02, 0.73)), 0.038), ('c', G((gx, 0.055, 0.85)), G((gx + sx * 0.005, 0.06, 0.77)), 0.035),
                   ('c', G((gx - sx * 0.03, -0.09, 0.9)), G((gx - sx * 0.05, -0.12, 0.83)), 0.038)], WHITE, vox=0.006, smooth=4)
blob('pants', [('e', (0, 0, 1.0), (0.4, 0.28, 0.14)), ('c', (-0.19, 0, 0.98), (-0.19, -0.01, 0.22), 0.185), ('c', (0.19, 0, 0.98), (0.19, -0.01, 0.22), 0.185)], NAVY, smooth=4)
for sx in (-1, 1):
    blob('shoe', [('e', (sx * 0.19, -0.12, 0.1), (0.16, 0.33, 0.1)), ('e', (sx * 0.19, 0.03, 0.15), (0.15, 0.17, 0.11))], WHITE, vox=0.008)
    s = cyl('sole', 0.16, 0.05, M('sole', (0.7, 0.7, 0.68), 0.6), (sx * 0.19, -0.11, 0.03)); s.scale = (1.05, 2.1, 1)
# ── 지퍼·끈·주머니·사원증 (몸통 표면에 붙임)
tube('zip', [surf(body, 0, z, 0.03 if z < 1.42 else 0.004) for z in (1.9, 1.75, 1.55, 1.44, 1.38, 1.2, 1.05)], 0.009, GREY)
box('pull', (0.035, 0.015, 0.075), GREY, surf(body, 0.0, 1.86, 0.012), bevel=0.006)
bm = bmesh.new()
for z in [1.04 + i * 0.02 for i in range(17)]:
    w = 0.3 - (z - 1.04) * 0.25
    for i in range(13): bm.verts.new((-w + 2 * w * i / 12, -1.0, z))
bm.verts.ensure_lookup_table()
for r_ in range(16):
    for c_ in range(12): a_ = r_ * 13 + c_; bm.faces.new([bm.verts[a_], bm.verts[a_ + 1], bm.verts[a_ + 14], bm.verts[a_ + 13]])
pme = bpy.data.meshes.new('pk'); bm.to_mesh(pme); bm.free(); pko = bpy.data.objects.new('pocketP', pme); bpy.context.collection.objects.link(pko)
sw = pko.modifiers.new('sw', 'SHRINKWRAP'); sw.target = body; sw.wrap_method = 'PROJECT'; sw.use_project_y = True; sw.use_positive_direction = True; sw.offset = 0.004
so_ = pko.modifiers.new('so', 'SOLIDIFY'); so_.thickness = 0.022; so_.offset = 1; bv = pko.modifiers.new('bv', 'BEVEL'); bv.width = 0.008; bv.segments = 3
sb = pko.modifiers.new('sb', 'SUBSURF'); sb.levels = 1; sb.render_levels = 2; pme.materials.append(TEAL); pme.polygons.foreach_set('use_smooth', [True] * len(pme.polygons))
if 0: tube('pocket', [surf(body, x, z, 0.003) for x, z in ((-0.3, 1.06), (-0.27, 1.25), (-0.2, 1.38), (0.2, 1.38), (0.27, 1.25), (0.3, 1.06))], 0.013, M('pk', (0.012, 0.09, 0.11), 0.8))
for sx in (-1, 1):
    p0 = surf(body, sx * 0.09, 1.97, 0.02); tube('string', [p0, surf(body, sx * 0.1, 1.82, 0.025), surf(body, sx * 0.105, 1.68, 0.025)], 0.011, STR)
    cyl('tip', 0.014, 0.05, GREY, surf(body, sx * 0.105, 1.645, 0.025))
LAN = M('lan', (0.04, 0.12, 0.7), 0.45)
tube('lan', [(-0.2, 0.04, 2.0), surf(body, -0.16, 1.86, 0.02), surf(body, -0.03, 1.66, 0.03), surf(body, 0.03, 1.61, 0.035), surf(body, 0.09, 1.66, 0.03), surf(body, 0.16, 1.86, 0.02), (0.2, 0.04, 2.0)], 0.012, LAN)
card_img = Image.new('RGB', (300, 400), (246, 248, 252)); g = ImageDraw.Draw(card_img)
g.rectangle([0, 0, 300, 60], fill=(70, 130, 225)); g.rounded_rectangle([95, 95, 205, 225], 10, fill=(205, 220, 245))
g.ellipse([127, 112, 173, 158], fill=(70, 115, 200)); g.rounded_rectangle([108, 166, 192, 225], 18, fill=(70, 115, 200))
g.rectangle([55, 265, 245, 285], fill=(150, 160, 178)); g.rectangle([85, 305, 215, 320], fill=(185, 192, 205)); card_img.save(os.path.join(TMP, 'card3.png'))
p1, p2 = Vector(surf(body, 0.03, 1.6, 0.035)), Vector(surf(body, 0.03, 1.38, 0.035)); Yv = (p1 - p2).normalized(); Zv = Vector((1, 0, 0)).cross(Yv).normalized(); Xv = Yv.cross(Zv)
bpy.ops.mesh.primitive_plane_add(size=1); card = bpy.context.active_object
card.matrix_world = Matrix.Translation((p1 + p2) / 2 + Zv * 0.01) @ Matrix((Xv, Yv, Zv)).transposed().to_4x4() @ Matrix.Diagonal((0.15, 0.2, 1, 1)); cl = tuple(p1)
card.data.materials.append(M('cardm', (1, 1, 1), 0.3, img=os.path.join(TMP, 'card3.png'))); so = card.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.01
box('clip', (0.03, 0.012, 0.04), GREY, (cl[0], cl[1] - 0.01, cl[2]), bevel=0.004)

# ── 전체를 살짝 돌려 3/4 각도
HT = Matrix.Translation(HC) @ Matrix.Rotation(-0.22, 4, 'Z') @ Matrix.Translation(-HC)
for o in list(bpy.context.scene.objects):
    if o.name.split('.')[0] in ('head', 'ear', 'eyeW', 'pupil', 'hl', 'brow', 'nose', 'mouth', 'hair', 'lid'): o.matrix_world = HT @ o.matrix_world
rig = bpy.data.objects.new('rig', None); bpy.context.collection.objects.link(rig)
for o in list(bpy.context.scene.objects):
    if o not in (bg, rig) and o.parent is None and o.type in ('MESH', 'CURVE'): o.parent = rig
rig.rotation_euler.z = 0.3
# ── 조명·카메라
k = area('key', (-3.5, -4.0, 4.5), (0, 0, 0), 700, (1.0, 0.9, 0.8), 6.0); look_at(k, (0, 0, 1.6))
f = area('fill', (3.5, -3.2, 2.0), (0, 0, 0), 260, (0.85, 0.9, 1.0), 4.0); look_at(f, (0, 0, 1.5))
r = area('rim', (2.0, 2.2, 3.4), (0, 0, 0), 450, (1.0, 0.85, 0.65), 2.0); look_at(r, (0, 0, 2.0))
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = float(os.environ.get('EXP', -0.75))
camera((-0.25, -7.6, 1.75), (0, 0, 1.5), lens=70)
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('done', OUT)
