# 블렌더(Cycles) 비교 테스트: python scene.py man|brain out.png
import sys, os, math, bpy, bmesh, addon_utils
from mathutils import Vector, noise
sys.path.insert(0, os.path.dirname(__file__))
from faces import face, draw
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import sys as _s; TMP = os.path.join(HERE, 'tmp'); os.makedirs(TMP, exist_ok=True)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
addon_utils.enable('cycles', default_set=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('SPP', 64)); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = int(os.environ.get('RW', 540)), int(os.environ.get('RH', 960))
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

