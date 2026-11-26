"""Render original conceptual equipment views with Blender Cycles."""
import array
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

OUT = Path('public/assets/renders').resolve()
PRODUCTS = json.loads(Path('src/products.json').read_text())
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12
scene.cycles.use_denoising = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.render.image_settings.file_format = 'PNG'
scene.world.color = (.15, .15, .15)
scene.view_settings.view_transform = 'AgX'

def material(name, rgb, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return m

def aim(obj, destination):
    obj.rotation_euler = (Vector(destination) - obj.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
steel = material('Brushed steel', (.57,.61,.66), .87, .27)
dark = material('Cast and machined metal', (.19,.23,.28), .69, .31)
accent = material('Motor terminal housing', (.29,.10,.038), .45, .36)
black = material('Dark hardware', (.06,.07,.08), .55, .34)
floor = material('Studio floor', (.024,.031,.040), .25, .42)
bpy.ops.mesh.primitive_plane_add(size=200)
ground = bpy.context.object
ground.data.materials.append(floor)

def light(name, position, power, color, size, height):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.color, data.shape, data.size, data.size_y = power, color, 'RECTANGLE', size, height
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0,0,0))

light('Left softbox', (-3,-4,3), 720, (.80,.89,1), 2, 5)
light('Right softbox', (4,-1,2), 490, (1,.91,.82), 1.3, 4)
light('Overhead', (0,0,5), 440, (.83,.9,1), 4, 3)
light('Amber edge', (2,3,2), 640, (1,.34,.10), 2, 3)
light('Rear softbox', (-3,3,2), 620, (.71,.83,1), 2, 4)
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = 'ORTHO'
scene.camera = camera

def equipment(kind):
    raw = array.array('f')
    raw.frombytes(Path('/tmp/unity-geometry', kind).read_bytes())
    verts, norms, faces, colors = [], [], [], []
    for offset in range(0, len(raw), 27):
        i = len(verts)
        for j in (offset, offset+9, offset+18):
            x,y,z,nx,ny,nz = raw[j:j+6]
            verts.append((x,-z,y))
            norms.append((nx,-nz,ny))
        a,b,c = map(Vector, verts[-3:])
        faces.append((i,i+1,i+2) if (b-a).cross(c-a).dot(Vector(norms[i])) >= 0 else (i,i+2,i+1))
        red = raw[offset+6]
        colors.append(2 if red > .8 else 0 if red > .5 else 1 if red > .15 else 3)
    mesh = bpy.data.meshes.new(kind)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(kind, mesh)
    scene.collection.objects.link(obj)
    for mat in (steel,dark,accent,black):
        mesh.materials.append(mat)
    for p, idx in zip(mesh.polygons, colors):
        p.use_smooth = True
        p.material_index = idx
    mesh.normals_split_custom_set_from_vertices(norms)
    ground.location.z = min(v[2] for v in verts) - .012
    return obj

def render(kind, suffix, angle, elevation, size, scale):
    camera.location = (5*math.sin(angle), -5*math.cos(angle), elevation)
    aim(camera, (0,0,0))
    camera.data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(Path('/tmp/unity-render', kind + suffix + '.png'))
    bpy.ops.render.render(write_still=True)

Path('/tmp/unity-render').mkdir(exist_ok=True)
for product in sorted(PRODUCTS, key=lambda p: p['kind'] != 'reactor-limpet'):
    kind = product['kind']
    obj = equipment(kind)
    if kind == 'reactor-limpet':
        render(kind, '-hero', .64, .75, (1500,1300), 3.30)
    render(kind, '', .63, 1.8, (640,540), 3.65)
    render(kind, '-alt', 2.18, 2.5, (640,540), 3.65)
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)
