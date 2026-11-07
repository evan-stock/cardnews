# 블렌더(Cycles) 비교 테스트: python scene.py man|brain out.png
import sys, os, math, bpy, bmesh, addon_utils
from mathutils import Vector, noise
sys.path.insert(0, os.path.dirname(__file__))
from faces import face, draw
from PIL import Image, ImageDraw, ImageFont

WHICH, OUT = sys.argv[-2], sys.argv[-1]
HERE = os.path.dirname(os.path.abspath(__file__)); TMP = os.path.join(HERE, 'tmp'); os.makedirs(TMP, exist_ok=True)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
addon_utils.enable('cycles', default_set=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 720, 1280
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.cycles.max_bounces = 6
sc.view_settings.exposure = -0.9

def M(name, base, rough=0.5, sss=0.0, sss_r=(1, 0.4, 0.3), metal=0.0, coat=0.0, emit=None, ei=0.0, sheen=0.0, alpha_img=None, img=None, bump=0.0, bump_scale=30.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = sss_r; b.inputs['Coat Weight'].default_value = coat
    b.inputs['Sheen Weight'].default_value = sheen
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = ei
    if img or alpha_img:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(img or alpha_img); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha_img: nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
        if emit == 'img': pass
    if bump > 0:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bump_scale; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def emissive_img(name, path, strength=2.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(t.outputs['Color'], e.inputs['Color']); nt.links.new(e.outputs['Emission'], o.inputs['Surface']); return m
def obj_from(mesh_fn, name, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, subsurf=0, parent=None, **kw):
    mesh_fn(**kw); o = bpy.context.active_object; o.name = name; o.location = loc; o.rotation_euler = rot; o.scale = scale
    if smooth: bpy.ops.object.shade_smooth()
    if subsurf: s = o.modifiers.new('sub', 'SUBSURF'); s.levels = subsurf; s.render_levels = subsurf
    if mat: o.data.materials.append(mat)
    if parent: o.parent = parent
    return o
def sphere(name, r, mat, loc=(0, 0, 0), scale=(1, 1, 1), parent=None, seg=64, rings=32, rot=(0, 0, 0)):
    return obj_from(bpy.ops.mesh.primitive_uv_sphere_add, name, mat, loc, rot, scale, parent=parent, radius=r, segments=seg, ring_count=rings)
def cyl(name, r, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, verts=48, smooth=True):
    return obj_from(bpy.ops.mesh.primitive_cylinder_add, name, mat, loc, rot, parent=parent, radius=r, depth=h, vertices=verts, smooth=smooth)
def box(name, size, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, bevel=0.01):
    o = obj_from(bpy.ops.mesh.primitive_cube_add, name, mat, loc, rot, (size[0] / 2, size[1] / 2, size[2] / 2), smooth=False, parent=parent, size=2)
    if bevel: b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 3
    return o
def tube(name, pts, r, mat, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, c in zip(sp.bezier_points, pts): p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o); o.data.materials.append(mat)
    if parent: o.parent = parent
    return o
def face_decal(name, target, r, png, parent, cone=0.95, span=0.95):
    """머리 앞(-Y)쪽 구면 조각에 얼굴 그림을 평면 투영으로 붙이고, 머리 표면에 수축포장."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 1.02, segments=96, ring_count=64); o = bpy.context.active_object; o.name = name
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [v for v in bm.verts if (-v.co.y) < r * 1.02 * math.cos(cone)]; bmesh.ops.delete(bm, geom=kill, context='VERTS')
    uv = bm.loops.layers.uv.new(); s = r * span
    for f in bm.faces:
        for l in f.loops: l[uv].uv = (0.5 + l.vert.co.x / (2 * s), 0.5 + l.vert.co.z / (2 * s))
    bm.to_mesh(o.data); bm.free(); bpy.ops.object.shade_smooth()
    o.data.materials.append(M(name + 'M', (1, 1, 1), 0.55, alpha_img=png))
    sw = o.modifiers.new('wrap', 'SHRINKWRAP'); sw.target = target; sw.wrap_method = 'NEAREST_SURFACEPOINT'; sw.offset = 0.004
    o.parent = parent; return o

def add_face(mat, png, s, zoff=0.0):
    """머리 재질에 얼굴 그림을 정면(-Y) 평면 투영으로 합성(오브젝트 좌표). 데칼 메시 없이."""
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links
    base_link = [l for l in nt.links if l.to_socket == b.inputs['Base Color']]
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    u = nt.nodes.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; u.inputs[1].default_value = 1 / (2 * s); u.inputs[2].default_value = 0.5; L.new(sep.outputs['X'], u.inputs[0])
    v = nt.nodes.new('ShaderNodeMath'); v.operation = 'MULTIPLY_ADD'; v.inputs[1].default_value = 1 / (2 * s); v.inputs[2].default_value = 0.5 - zoff / (2 * s); L.new(sep.outputs['Z'], v.inputs[0])
    cmb = nt.nodes.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0], cmb.inputs['X']); L.new(v.outputs[0], cmb.inputs['Y'])
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(png); img.extension = 'CLIP'; L.new(cmb.outputs[0], img.inputs['Vector'])
    front = nt.nodes.new('ShaderNodeMath'); front.operation = 'LESS_THAN'; front.inputs[1].default_value = 0.0; L.new(sep.outputs['Y'], front.inputs[0])
    a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; L.new(img.outputs['Alpha'], a.inputs[0]); L.new(front.outputs[0], a.inputs[1])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; L.new(a.outputs[0], mix.inputs['Factor'])
    if base_link: L.new(base_link[0].from_socket, mix.inputs['A'])
    else: mix.inputs['A'].default_value = b.inputs['Base Color'].default_value[:]
    L.new(img.outputs['Color'], mix.inputs['B']); L.new(mix.outputs['Result'], b.inputs['Base Color'])
    # 그림 부분은 덜 반짝이게
    rgh = nt.nodes.new('ShaderNodeMix'); rgh.data_type = 'FLOAT'; L.new(a.outputs[0], rgh.inputs['Factor']); rgh.inputs['A'].default_value = b.inputs['Roughness'].default_value; rgh.inputs['B'].default_value = 0.6; L.new(rgh.outputs['Result'], b.inputs['Roughness'])
def mitten(name, mat, loc, parent, rot=(0, 0, 0), s=1.0):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc; e.rotation_euler = rot; e.parent = parent; e.scale = (s, s, s)
    sphere(name + 'p', 0.12, mat, (0, 0, 0), (1, 0.8, 1.15), parent=e); sphere(name + 't', 0.055, mat, (0.09, -0.03, 0.03), (0.9, 0.9, 1.3), parent=e); return e
def text_png(path, w, h, bg, lines, fs, fg=(255, 255, 255)):
    im = Image.new('RGB', (w, h), bg); g = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, fs)
    tot = len(lines) * fs * 1.2
    for i, (t, c) in enumerate(lines):
        tw = g.textlength(t, font=f); g.text(((w - tw) / 2, (h - tot) / 2 + i * fs * 1.2), t, font=f, fill=c)
    im.save(path); return path
def area(name, loc, rot, energy, color, size):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = color; L.size = size; o = bpy.data.objects.new(name, L); o.location = loc; o.rotation_euler = rot; bpy.context.collection.objects.link(o); return o
def point(name, loc, energy, color, r=0.1):
    L = bpy.data.lights.new(name, 'POINT'); L.energy = energy; L.color = color; L.shadow_soft_size = r; o = bpy.data.objects.new(name, L); o.location = loc; bpy.context.collection.objects.link(o); return o
def look_at(o, target):
    d = Vector(target) - o.location; o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
def camera(loc, target, lens=50):
    c = bpy.data.cameras.new('cam'); c.lens = lens; o = bpy.data.objects.new('cam', c); bpy.context.collection.objects.link(o); o.location = loc; look_at(o, target); sc.camera = o; return o
def world(col, s=0.4):
    w = bpy.data.worlds.new('w'); w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (*col, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = s; sc.world = w

if WHICH == 'man':
    world((0.06, 0.07, 0.12), 0.25)
    skin = M('skin', (0.93, 0.76, 0.64), 0.48, sss=0.18, sss_r=(1.0, 0.35, 0.2))
    hood = M('hood', (0.03, 0.42, 0.37), 0.85, sheen=0.6, bump=0.15, bump_scale=180)
    hairM = M('hair', (0.025, 0.018, 0.015), 0.38, coat=0.25, bump=0.25, bump_scale=60)
    pot_m = M('pot', (1.0, 0.72, 0.28), 0.28, metal=1.0, bump=0.35, bump_scale=14)  # 양은냄비(찌그러진 느낌)
    soup_m = M('soup', (0.62, 0.12, 0.03), 0.08, sss=0.3, sss_r=(1, 0.3, 0.1), coat=0.6)
    nood_m = M('nood', (0.98, 0.78, 0.38), 0.35, sss=0.2)
    onion = M('onion', (0.25, 0.65, 0.18), 0.4)
    # 바닥·벽·창문·소품
    box('floor', (8, 8, 0.1), M('wood', (0.45, 0.27, 0.15), 0.45, bump=0.08, bump_scale=6), (0, 0, -0.05))
    box('wall', (8, 0.1, 5), M('wallp', (0.82, 0.76, 0.66), 0.9), (0, 2.2, 2.4))
    night = Image.new('RGB', (1024, 768), (10, 14, 48)); g = ImageDraw.Draw(night)
    for i in range(14):
        bx, bh = i * 76, 260 + (i * 97) % 300; g.rectangle([bx, 768 - bh, bx + 66, 768], fill=(16, 20, 50))
        for yy in range(768 - bh + 16, 760, 30):
            for xx in range(bx + 8, bx + 60, 18):
                if (xx * 7 + yy * 3) % 5 < 2: g.rectangle([xx, yy, xx + 8, yy + 13], fill=(255, 205, 110))
    g.ellipse([820, 70, 900, 150], fill=(255, 246, 210)); night.save(os.path.join(TMP, 'night.png'))
    win = obj_from(bpy.ops.mesh.primitive_plane_add, 'win', emissive_img('nightM', os.path.join(TMP, 'night.png'), 1.4), (0.9, 2.14, 2.2), (math.pi / 2, 0, 0), (1.3, 1, 0.95), smooth=False, size=2)
    for x, z, w_, h_ in [(0.9, 3.2, 2.7, 0.08), (0.9, 1.25, 2.7, 0.08), (-0.4, 2.2, 0.08, 2.0), (2.2, 2.2, 0.08, 2.0), (0.9, 2.2, 0.06, 2.0)]: box('fr', (w_, 0.08, h_), M('frm', (0.95, 0.94, 0.9), 0.4), (x, 2.1, z))
    shelf = box('shelf', (1.4, 0.3, 0.05), M('sh', (0.75, 0.62, 0.45), 0.5), (-1.4, 2.0, 2.0))
    cols = [(0.75, 0.15, 0.12), (0.15, 0.45, 0.85), (0.95, 0.75, 0.15), (0.2, 0.6, 0.3), (0.5, 0.25, 0.6)]
    for i in range(9): box('bk', (0.1, 0.22, 0.32 + (i % 3) * 0.05), M('bk%d' % i, cols[i % 5], 0.6), (-1.95 + i * 0.13, 2.0, 2.2 + (i % 3) * 0.025))
    lampS = cyl('lamp', 0.18, 0.25, M('lampm', (1, 0.85, 0.6), 0.6, emit=(1, 0.7, 0.35), ei=8), (-1.9, 1.6, 1.3))
    point('lampL', (-1.9, 1.5, 1.3), 120, (1, 0.7, 0.4), 0.2)
    box('table', (1.6, 1.0, 0.07), M('tab', (0.85, 0.68, 0.45), 0.4), (0, -0.35, 0.62))
    # 이 남자 (앞 = -Y)
    root = bpy.data.objects.new('man', None); bpy.context.collection.objects.link(root); root.location = (0, 0.55, 0)
    torso = sphere('torso', 0.5, hood, (0, 0, 0.95), (1.0, 0.82, 1.05), parent=root); torso.modifiers.new('s', 'SUBSURF').levels = 1
    box('zip', (0.025, 0.02, 0.6), M('zipm', (0.75, 0.78, 0.8), 0.25, metal=0.8), (0, -0.405, 0.95), parent=root, bevel=0.004)
    tube('lan', [(-0.18, -0.25, 1.42), (-0.1, -0.42, 1.12), (0, -0.46, 1.0), (0.1, -0.42, 1.12), (0.18, -0.25, 1.42)], 0.012, M('lanm', (0.1, 0.3, 0.9), 0.4), parent=root)
    text_png(os.path.join(TMP, 'card.png'), 300, 380, (255, 255, 255), [('주식회사 보통', (40, 100, 220)), ('', (0, 0, 0)), ('박보통', (42, 29, 23))], 46)
    card = obj_from(bpy.ops.mesh.primitive_plane_add, 'card', M('cardm', (1, 1, 1), 0.4, img=os.path.join(TMP, 'card.png')), (0, -0.47, 0.82), (math.pi / 2 - 0.15, 0, 0), (0.085, 1, 0.105), smooth=False, size=2); card.parent = root
    head = bpy.data.objects.new('headP', None); bpy.context.collection.objects.link(head); head.parent = root; head.location = (0, 0, 1.78)
    head.rotation_euler = (math.radians(-28), 0, math.radians(8))  # 고개를 뒤로 젖혀 들이켬
    skinH = M('skinH', (0.93, 0.76, 0.64), 0.48, sss=0.18, sss_r=(1.0, 0.35, 0.2))
    hd = sphere('head', 0.6, skinH, (0, 0, 0), parent=head, seg=96, rings=64)
    for sx in (-1, 1): sphere('ear', 0.12, skin, (sx * 0.59, 0, -0.02), (0.55, 0.8, 1.0), parent=head)
    # 머리카락: 앞은 높고 뒤는 낮게 잘라 낸 껍질
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.625, segments=96, ring_count=64); hair = bpy.context.active_object; hair.name = 'hair'
    bm = bmesh.new(); bm.from_mesh(hair.data)
    kill = [v for v in bm.verts if v.co.z / 0.625 < 0.12 + 0.3 * (-v.co.y / 0.625) - 0.05 * math.sin(v.co.x * 25)]
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(hair.data); bm.free(); bpy.ops.object.shade_smooth()
    so = hair.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.05; ss = hair.modifiers.new('ss', 'SUBSURF'); ss.levels = 2
    hair.data.materials.append(hairM); hair.parent = head; hair.rotation_euler = (math.radians(-6), 0, 0)
    fr = sphere('fringe', 0.2, hairM, (-0.18, -0.43, 0.38), (1.6, 0.6, 0.55), parent=head, rot=(0.4, 0, 0.35))
    draw(face('slurp'), os.path.join(TMP, 'face_man.png'), skin=(237, 196, 170))
    add_face(skinH, os.path.join(TMP, 'face_man.png'), 0.6 * 0.95)
    # 입 위치(얼굴 그림의 입 높이 0.66 → 머리 좌표) 에 냄비 가장자리를 붙인다
    span = 0.6 * 0.95; mz = span * (1 - 2 * 0.66) ; my = -math.sqrt(0.6 ** 2 - mz ** 2)
    pot = bpy.data.objects.new('potP', None); bpy.context.collection.objects.link(pot); pot.parent = head
    pot.location = (0.0, my - 0.27, mz - 0.1); pot.rotation_euler = (math.radians(-55), 0, 0); pot.scale = (0.8, 0.8, 0.8)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.2, vertices=64); body = bpy.context.active_object; body.name = 'potBody'
    bm = bmesh.new(); bm.from_mesh(body.data); top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bm.to_mesh(body.data); bm.free()
    body.modifiers.new('so', 'SOLIDIFY').thickness = 0.012; bv = body.modifiers.new('bv', 'BEVEL'); bv.width = 0.006; bv.segments = 3
    body.data.materials.append(pot_m); body.parent = pot; bpy.ops.object.shade_smooth()
    rim = obj_from(bpy.ops.mesh.primitive_torus_add, 'rim', pot_m, (0, 0, 0.1), parent=pot, major_radius=0.32, minor_radius=0.012)
    for sx in (-1, 1): obj_from(bpy.ops.mesh.primitive_torus_add, 'hdl', pot_m, (sx * 0.36, 0, 0.06), (math.pi / 2, 0, 0), (1, 1, 0.6), parent=pot, major_radius=0.06, minor_radius=0.014)
    soup = cyl('soup', 0.305, 0.02, soup_m, (0, 0.03, 0.05), (math.radians(30), 0, 0), parent=pot)  # 기울어도 수면은 수평에 가깝게
    for i in range(7):
        a = i * 0.9; tube('nd%d' % i, [(math.cos(a) * 0.1, math.sin(a) * 0.1, 0.05), (math.cos(a) * 0.2, math.sin(a) * 0.15 - 0.1, 0.1), (math.cos(a + 0.4) * 0.27, -0.28, 0.13 + 0.03 * math.sin(i))], 0.012, nood_m, parent=pot)
    for i in range(6): obj_from(bpy.ops.mesh.primitive_torus_add, 'on', onion, (math.cos(i * 1.1) * 0.18, math.sin(i * 1.1) * 0.15, 0.07), (1.2, 0.3 * i, 0), parent=pot, major_radius=0.025, minor_radius=0.008)
    # 팔·손: 냄비 손잡이를 쥠
    for sx in (-1, 1):
        sh = Vector((sx * 0.42, -0.05, 1.25)); hand_world_local = Vector((sx * 0.38, -0.55, 1.48))
        tube('arm', [tuple(sh), tuple(sh + Vector((sx * 0.12, -0.25, 0.0))), tuple(hand_world_local)], 0.1, hood, parent=root)
        mitten('mit', skin, tuple(hand_world_local), root, rot=(0.6, 0, -sx * 0.4), s=1.05)
    # 조명: 따뜻한 키, 차가운 필, 따뜻한 림 + 램프
    k = area('key', (2.2, -2.6, 3.4), (0, 0, 0), 380, (1.0, 0.82, 0.62), 2.2); look_at(k, (0, 0.5, 1.6))
    f = area('fill', (-2.8, -2.0, 1.6), (0, 0, 0), 110, (0.62, 0.74, 1.0), 3.0); look_at(f, (0, 0.5, 1.4))
    r = area('rim', (-1.2, 2.0, 3.2), (0, 0, 0), 450, (1.0, 0.7, 0.4), 1.5); look_at(r, (0, 0.5, 1.8))
    camera((-2.5, -2.0, 1.55), (0.0, 0.35, 1.75), lens=55)

if WHICH == 'brain':
    world((0.04, 0.05, 0.1), 0.5)
    pink = M('brain', (0.86, 0.36, 0.44), 0.36, sss=0.35, sss_r=(1.0, 0.25, 0.25), coat=0.45, bump=0.12, bump_scale=40)
    # 주름 깊은 곳을 어둡게(포인티니스)
    nt = pink.node_tree; b = nt.nodes['Principled BSDF']; geo = nt.nodes.new('ShaderNodeNewGeometry'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[0].color = (0.45, 0.16, 0.22, 1); ramp.color_ramp.elements[1].position = 0.56; ramp.color_ramp.elements[1].color = (0.86, 0.36, 0.44, 1)
    nt.links.new(geo.outputs['Pointiness'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    dark = M('dark', (0.025, 0.028, 0.035), 0.3, coat=0.5); metal = M('metal', (0.7, 0.72, 0.75), 0.25, metal=1.0)
    # 관제실 배경
    box('floor', (10, 10, 0.1), M('fl', (0.06, 0.08, 0.14), 0.35, coat=0.3), (0, 0, -0.05))
    box('wall', (10, 0.1, 6), M('wl', (0.09, 0.12, 0.2), 0.8), (0, 2.6, 3))
    for i in range(-4, 5): box('rib', (0.06, 0.12, 6), M('rb', (0.16, 0.2, 0.32), 0.5), (i * 1.1, 2.5, 3))
    text_png(os.path.join(TMP, 'mon1.png'), 800, 460, (10, 14, 28), [('혈중 나트륨', (160, 180, 220)), ('짜다!', (255, 70, 60))], 120)
    text_png(os.path.join(TMP, 'mon2.png'), 800, 460, (10, 14, 28), [('① 물 마셔!', (90, 180, 255)), ('② 콩팥: 물 잠가!', (255, 140, 60))], 90)
    for x, img in [(-1.3, 'mon1.png'), (1.3, 'mon2.png')]:
        box('bez', (1.75, 0.08, 1.05), dark, (x, 2.45, 2.4)); obj_from(bpy.ops.mesh.primitive_plane_add, 'scr', emissive_img('scr' + img, os.path.join(TMP, img), 2.5), (x, 2.4, 2.4), (math.pi / 2, 0, 0), (0.8, 1, 0.46), smooth=False, size=2)
    box('console', (3.6, 1.0, 0.8), M('cs', (0.22, 0.27, 0.4), 0.35, coat=0.4), (0, 1.45, 0.4)); box('ctop', (3.7, 1.1, 0.06), dark, (0, 1.45, 0.83))
    btn = [(1, 0.25, 0.2), (1, 0.8, 0.2), (0.3, 0.9, 0.45), (0.3, 0.65, 1)]
    for i in range(14): cyl('b', 0.06, 0.05, M('bt%d' % i, btn[i % 4], 0.25, emit=btn[i % 4], ei=4), (-1.5 + (i % 7) * 0.24, 1.2 + (i // 7) * 0.2, 0.88))
    beacon = cyl('beacon', 0.16, 0.26, M('bc', (1, 0.1, 0.08), 0.2, emit=(1, 0.08, 0.05), ei=25), (0, 2.4, 4.3))
    point('alarm', (0, 1.8, 3.6), 900, (1, 0.12, 0.08), 0.3)
    # 뇌 몸통(주름 = 능선 노이즈) : 앞(-Y) 얼굴 자리는 매끈하게
    root = bpy.data.objects.new('brainR', None); bpy.context.collection.objects.link(root); root.location = (0, 0.2, 0)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.62, subdivisions=6); br = bpy.context.active_object; br.name = 'brain'
    for v in br.data.vertices:
        n = v.co.normalized(); q = n * 2.4
        w = Vector((noise.noise(q * 0.8 + Vector((11, 3, 7))), noise.noise(q * 0.8 + Vector((2, 9, 4))), noise.noise(q * 0.8 + Vector((5, 1, 13))))) * 0.6
        n1 = noise.noise(q * 1.7 + w); n2 = noise.noise(q * 3.3 + w * 1.5 + Vector((3, 3, 3)))
        d = 0.02 - 0.075 * math.exp(-(n1 / 0.07) ** 2) - 0.035 * math.exp(-(n2 / 0.06) ** 2)  # 구불구불한 고랑(노이즈 0선)
        d -= 0.11 * math.exp(-(n.x / 0.05) ** 2) * max(0.0, n.z + 0.25)
        facing = max(0.0, (-n.y - 0.55) / 0.3); d *= (1 - min(1.0, facing) * 0.85)
        v.co = n * 0.62 * (1 + d)
    bpy.ops.object.shade_smooth(); br.scale = (1.12, 0.95, 0.9); br.location = (0, 0, 1.0); br.parent = root
    br.data.materials.append(pink); s = br.modifiers.new('s', 'SUBSURF'); s.levels = 1; s.render_levels = 1
    headP = bpy.data.objects.new('hp', None); bpy.context.collection.objects.link(headP); headP.parent = root; headP.location = (0, 0, 1.0); headP.scale = (1.12, 0.95, 0.9)
    draw(face('determined'), os.path.join(TMP, 'face_brain.png'), skin=(230, 132, 145), eye_y=0.47, mouth_y=0.7)
    add_face(pink, os.path.join(TMP, 'face_brain.png'), 0.62 * 0.9)
    # 헤드셋
    band = obj_from(bpy.ops.mesh.primitive_torus_add, 'band', dark, (0, 0.05, 1.0), (math.pi / 2, 0, 0), (1.18, 1.0, 1.0), parent=root, major_radius=0.62, minor_radius=0.035)
    bm = bmesh.new(); bm.from_mesh(band.data); bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.02], context='VERTS'); bm.to_mesh(band.data); bm.free()
    for sx in (-1, 1): cyl('cup', 0.13, 0.1, dark, (sx * 0.72, 0, 0.98), (0, math.pi / 2, 0), parent=root); cyl('cupr', 0.135, 0.02, metal, (sx * 0.77, 0, 0.98), (0, math.pi / 2, 0), parent=root)
    tube('boom', [(-0.76, -0.05, 0.92), (-0.66, -0.4, 0.7), (-0.3, -0.62, 0.62)], 0.018, dark, parent=root)
    sphere('mic', 0.055, M('micm', (0.85, 0.1, 0.08), 0.3, emit=(1, 0.1, 0.05), ei=2), (-0.27, -0.64, 0.62), parent=root)
    # 작은 팔다리
    limbM = M('limb', (0.86, 0.36, 0.44), 0.4, sss=0.3, sss_r=(1.0, 0.25, 0.25), coat=0.3)
    for sx in (-1, 1):
        tube('leg', [(sx * 0.2, 0, 0.5), (sx * 0.22, -0.02, 0.25), (sx * 0.22, -0.02, 0.06)], 0.08, limbM, parent=root)
        sphere('shoe', 0.12, dark, (sx * 0.22, -0.08, 0.05), (0.8, 1.3, 0.55), parent=root)
    tube('armL', [(0.62, 0, 0.9), (0.85, -0.1, 0.7), (0.9, -0.25, 0.55)], 0.07, limbM, parent=root); mitten('mL', limbM, (0.92, -0.3, 0.5), root, rot=(0.4, 0, 0.6))
    tube('armR', [(-0.62, 0, 0.95), (-0.95, -0.25, 1.15), (-1.0, -0.55, 1.35)], 0.07, limbM, parent=root); mitten('mR', limbM, (-1.0, -0.62, 1.4), root, rot=(-0.6, 0, -0.3))
    k = area('key', (2.0, -2.8, 3.0), (0, 0, 0), 650, (1.0, 0.85, 0.7), 2.0); look_at(k, (0, 0.2, 1.0))
    f = area('fill', (-2.6, -2.2, 1.4), (0, 0, 0), 180, (0.55, 0.7, 1.0), 2.5); look_at(f, (0, 0.2, 1.0))
    r = area('rim', (1.6, 2.0, 2.6), (0, 0, 0), 600, (0.5, 0.75, 1.0), 1.5); look_at(r, (0, 0.2, 1.1))
    camera((0.9, -3.4, 1.25), (0.0, 0.2, 1.0), lens=48)

sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('done', OUT)
