"""Blender-only, low-detail workflow fixtures for SP-02, MV-06 and CB-05."""
import argparse
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vfx_contract import from_study, require, validate, write_new


def interpolation(owner):
    action = owner.animation_data.action if owner.animation_data else None
    if not action:
        return
    # Slot-aware API in current Blender; older Action.fcurves remains supported.
    curves = list(getattr(action, "fcurves", []))
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                curves.extend(bag.fcurves)
    for curve in curves:
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"


def material(name, color, strength=1, surface=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    if surface:
        node = nodes.new("ShaderNodeBsdfPrincipled")
        node.inputs["Base Color"].default_value = (*color, 1)
        node.inputs["Roughness"].default_value = .7
        mat.node_tree.links.new(node.outputs[0], out.inputs[0])
    else:
        node = nodes.new("ShaderNodeEmission")
        node.inputs["Color"].default_value = (*color, 1)
        node.inputs["Strength"].default_value = strength
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        mat.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
        mat.node_tree.links.new(node.outputs[0], mix.inputs[2])
        mat.node_tree.links.new(mix.outputs[0], out.inputs[0])
        for frame, alpha in [(1,0),(5,.08),(16,.5),(30,.8),(40,1),(52,.6),(70,.25),(85,0),(90,0)]:
            mix.inputs[0].default_value = alpha
            mix.inputs[0].keyframe_insert("default_value", frame=frame)
        interpolation(mat.node_tree)
    return mat


def curve(name, points, radius, mat, scene, closed=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spline = data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point, co in zip(spline.points, points):
        point.co = (*co,1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def sphere(name, location, scale, mat, scene):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def tag(obj, effect, layer, start=5, end=86):
    obj["vfx_layer"] = layer
    obj["vfx_feature_id"] = f"{effect}-{layer}"
    for frame, hidden in [(1,True),(start,False),(end,True),(90,True)]:
        obj.hide_render = hidden
        obj.keyframe_insert("hide_render",frame=frame)


def scale_keys(obj, keys):
    base = obj.scale.copy()
    for frame, value in keys:
        obj.scale = base * value
        obj.keyframe_insert("scale",frame=frame)
    interpolation(obj)


def camera(name, location, target, scene):
    obj = bpy.data.objects.new(name,bpy.data.cameras.new(name))
    obj.location = location
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.data.type = "ORTHO"
    obj.data.ortho_scale = 5.2
    scene.collection.objects.link(obj)
    return obj


def configure(scene, world, variant, scenario):
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.seed = 230519
    scene.render.resolution_x = 640
    scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.frame_start, scene.frame_end = 1,90
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.use_compositing = False
    scene["vfx_variant"] = variant
    scene["vfx_scenario"] = scenario
    scene["vfx_seed"] = 230519
    scene["vfx_variant_signature"] = variant
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8


def build(catalog, effect, output):
    require(effect in ("SP-02","MV-06","CB-05"), "Fixture builder supports SP-02, MV-06, CB-05 only; author other recipes explicitly")
    out = Path(output).resolve()
    require(not out.exists(), "Output exists; use a new versioned project directory")
    out.mkdir(parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Standard"
    rng = random.Random(230519)
    world = bpy.data.worlds.new("NeutralWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.065,.075,.09,1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .5
    configure(scene,world,"Standard","normal")
    ground_mat = material("ProxyGround",(.105,.125,.15),surface=True)
    body_mat = material("ProxyBody",(.18,.23,.28),surface=True)
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.name="GroundProxy"
    bpy.context.object.data.materials.append(ground_mat)
    body_x = -1.55 if effect=="SP-02" else 0
    sphere("ActorProxyBody",(body_x,0,.68),(.23,.19,.53),body_mat,scene)
    sphere("ActorProxyHead",(body_x,0,1.36),(.18,.17,.2),body_mat,scene)
    main=camera("GameplayCamera",(3,-6,3.4),(0,0,1),scene)
    camera("ObliqueCamera",(-4,-3,2.7),(0,0,1),scene)
    light=bpy.data.objects.new("KeyLight",bpy.data.lights.new("KeyLight","AREA"))
    light.location=(0,-3,5)
    light.data.energy=600
    light.data.shape="DISK"
    light.data.size=5
    scene.collection.objects.link(light)
    scene.camera=main
    mats={"L1":material("PrimaryGold",(1,.49,.12),2),"L2":material("FlowGold",(1,.7,.25),1.6),"L3":material("Grains",(.68,.32,.085),1),"L4":material("Accent",(1,.85,.5),3)}
    vfx=[]
    primary=[]
    center_z=1.15 if effect != "MV-06" else 1.0
    # Coherent portal rim, charge ring or shield shell sections.
    for ring in range(3 if effect=="CB-05" else 1):
        points=[]
        for i in range(96):
            a=2*math.pi*i/96
            if effect=="MV-06":
                co=(math.cos(a),math.sin(a),0)
            else:
                co=(.86*math.cos(a),.1*math.sin(a),1.04*math.sin(a))
                if effect=="CB-05":
                    rot=ring*math.pi/3
                    co=(co[0]*math.cos(rot),co[0]*math.sin(rot),co[2])
            points.append(co)
        obj=curve(f"{effect}.L1.rim{ring}",points,.023,mats["L1"],scene,True)
        obj.location.z=center_z
        tag(obj,effect,"L1",end=55 if effect=="MV-06" else 48 if effect=="CB-05" else 52)
        keys=[(1,0),(5,1.45),(16,1.15),(30,.7),(40,.36),(52,.1),(55,0)] if effect=="MV-06" else [(1,0),(5,.1),(16,1),(40,1),(48,1),(52,0)]
        scale_keys(obj,keys)
        primary.append(obj)
        vfx.append(obj)
    for strand in range(5):
        pts=[]
        for i in range(48):
            t=i/47
            a=strand*2*math.pi/5+t*3.0
            r=.23+.63*t
            if effect=="MV-06":
                pts.append((r*math.cos(a),r*math.sin(a),.28*(t-.5)))
            else:
                pts.append((r*math.cos(a),.08*math.sin(a*2),r*math.sin(a)))
        obj=curve(f"{effect}.L2.strand{strand}",pts,.009,mats["L2"],scene)
        obj.location.z=center_z
        tag(obj,effect,"L2",end=60 if effect=="MV-06" else 48 if effect=="CB-05" else 52)
        for frame, rot in [(1,0),(16,.4),(40,1.8),(70,3)]:
            obj.rotation_euler[2 if effect=="MV-06" else 1]=rot
            obj.keyframe_insert("rotation_euler",frame=frame)
        scale_keys(obj,[(1,0),(5,.3),(16,1),(40,.55 if effect=="MV-06" else 1),(60,.2),(80,0)])
        vfx.append(obj)
    if effect=="SP-02":
        # Accepted-use wave is separate from the ready-loop rim and survives its removal.
        points=[(.9*math.cos(i*math.tau/96),0,.9*math.sin(i*math.tau/96)) for i in range(96)]
        pulse=curve(f"{effect}.L2.use-pulse",points,.014,mats['L2'],scene,True)
        pulse.location.z=center_z
        tag(pulse,effect,'L2',start=40,end=58)
        scale_keys(pulse,[(40,1),(48,1.55),(56,1.9),(58,0)])
        vfx.append(pulse)
    if effect in ('SP-02','CB-05'):
        # Dissolve the protected/ready silhouette instead of leaving a smaller intact cage.
        for layer in ('L1','L2'):
            if layer=='L2' and effect=='SP-02':
                continue
            mix=next(n for n in mats[layer].node_tree.nodes if n.type=='MIX_SHADER')
            for frame,alpha in [(40,1),(44,.45),(48,0)]:
                mix.inputs[0].default_value=alpha
                mix.inputs[0].keyframe_insert('default_value',frame=frame)
    for index in range(24):
        a=rng.uniform(0,math.tau)
        r=rng.uniform(.55,1.1)
        base=Vector((r*math.cos(a),rng.uniform(-.2,.2),center_z+r*math.sin(a)))
        if effect=="MV-06":
            base=Vector((r*math.cos(a),r*math.sin(a),center_z+rng.uniform(-.4,.4)))
        obj=sphere(f"{effect}.L3.grain{index}",base,(.024,.024,.045),mats["L3"],scene)
        tag(obj,effect,"L3",start=18,end=83)
        settle=Vector((1.45*math.cos(a),1.45*math.sin(a),.065)) if effect=='SP-02' else Vector((base.x*1.35,base.y*1.35,max(.05,base.z-.45)))
        final=Vector((settle.x,settle.y,.06)) if effect=='SP-02' else Vector((base.x*1.4,base.y*1.4,.06))
        positions = [(18,base*.8),(40,base),(60,settle),(82,final)]
        if effect == 'MV-06':
            focus = Vector((0,0,center_z))
            positions = [(18,base),(24,focus+(base-focus)*.85),(40,focus+(base-focus)*.3),(60,focus+(base-focus)*.08),(82,focus)]
        for frame, pos in positions:
            obj.location=pos
            obj.keyframe_insert("location",frame=frame)
        scale_keys(obj,[(18,.1),(30,.8),(40,1),(70,.55),(82,.02),(83,0)])
        obj["vfx_lite_keep"]= index%4==0
        vfx.append(obj)
    if effect=='CB-05':
        for index in range(8):
            a=index*math.tau/8
            shard=curve(f'{effect}.L3.shard{index}',[(-.04,0,-.08),(.025,0,.09)],.012,mats['L3'],scene)
            origin=Vector((.86*math.cos(a),0,center_z+1.04*math.sin(a)))
            tag(shard,effect,'L3',start=40,end=78)
            for frame,pos in [(40,origin),(48,Vector((origin.x*1.35,-.2,origin.z+.08))),(60,Vector((origin.x*1.8,-.4,max(.08,origin.z-.45)))),(77,Vector((origin.x*2,-.5,.07)))]:
                shard.location=pos
                shard.keyframe_insert('location',frame=frame)
            scale_keys(shard,[(40,1),(60,.65),(77,.02),(78,0)])
            vfx.append(shard)
    for axis in range(2):
        pts=[(-.16,0,0),(.16,0,0)] if axis==0 else [(0,0,-.09),(0,0,.09)]
        obj=curve(f"{effect}.L4.glint{axis}",pts,.009,mats["L4"],scene)
        obj.location=(.0,-.08,center_z)
        if effect=='MV-06':
            obj.location=(.2,-.38,center_z+.05)
        tag(obj,effect,"L4",start=36,end=47)
        scale_keys(obj,[(36,.1),(40,1),(46,.05),(47,0)])
        vfx.append(obj)
    environment=[o for o in scene.objects if not o.get("vfx_layer")]
    variants={"Lite":lambda o:o['vfx_layer']=='L1' or (o['vfx_layer']=='L2' and effect=='SP-02') or (o['vfx_layer']=='L3' and o.get('vfx_lite_keep')),"NoAccents":lambda o:o['vfx_layer']!='L4'}
    for layer in ("L1","L2","L3","L4"):
        variants["Isolate"+layer]=lambda o,l=layer:o['vfx_layer']==l
    for name,predicate in variants.items():
        other=bpy.data.scenes.new(name)
        configure(other,world,name,"normal")
        for o in environment+[o for o in vfx if predicate(o)]:
            other.collection.objects.link(o)
        other.camera=main
    scene.frame_set(24)
    cancel=bpy.data.scenes.new("Cancel")
    configure(cancel,world,"Standard","cancel")
    for o in environment:
        cancel.collection.objects.link(o)
    for o in vfx:
        was_active = not o.hide_render
        clone=o.copy()
        clone.name="Cancel."+o.name
        clone.animation_data_clear()
        clone.matrix_world=o.matrix_world.copy()
        cancel.collection.objects.link(clone)
        for frame,hidden in [(1,True),(5,not was_active),(28,not was_active),(35,True),(90,True)]:
            clone.hide_render=hidden
            clone.keyframe_insert("hide_render",frame=frame)
    cancel.camera=main
    scene.frame_set(1)
    c=from_study(catalog,effect,out/'contract.json')
    c.update(mode="prototype",fidelity="workflow-fixture",coverage_confirmed=True,coverage_note="Low-detail workflow fixture. Covers the primary rim/ring, curved flow, sparse coarse grains, removable glint and termination. Source-specific shader textures, true portal traversal, shield-surface fracture, animated skeletal bodies and production art fidelity are explicitly outside this fixture.")
    p={"fps":30,"frame_start":1,"frame_end":90,"seed":230519,"timing_basis":"proposed","scale_basis":"Assumed meter-scale effect beside a roughly 1.6 m actor proxy; not measured from source","builder_id":"fixture-builder-v1","checkpoint":"effect_v01.blend","events":[{"name":n,"frame":f,"basis":"proposed"} for n,f in [("before",1),("gather",24),("event",40),("residue",60),("clear",90),("cancel",28),("cancel-clear",35)]],"samples":[],"required_roles":[],"expected_clear_samples":["before","clear","cancel-clear"],"required_feature_samples":{}}
    samples=[("before","Standard",1,"before","Standard","normal","before"),("gather","Standard",24,"gather","Standard","normal","gather"),("event","Standard",40,"event","Standard","normal","event"),("post-event","Standard",48,"post-event","Standard","normal",None),("residue","Standard",60,"residue","Standard","normal","residue"),("clear","Standard",90,"clear","Standard","normal","clear"),("oblique","Standard",40,"oblique","Standard","normal",None),("lite","Lite",40,"lite","Lite","normal",None),("no-accents","NoAccents",40,"no-accents","NoAccents","normal",None),("cancel-active","Cancel",24,"cancel-active","Standard","cancel",None),("cancel-clear","Cancel",35,"cancel-clear","Standard","cancel","cancel-clear")]
    for layer in ("L1","L2","L3","L4"):
        samples.append(("isolate-"+layer.lower(),"Isolate"+layer,40,"isolate-"+layer.lower(),"Isolate"+layer,"normal",None))
    for sid,sname,frame,role,variant,scenario,anchor in samples:
        s={"id":sid,"scene":sname,"camera":"ObliqueCamera" if role=="oblique" else "GameplayCamera","frame":frame,"role":role,"variant":variant,"scenario":scenario}
        if anchor:
            s['anchor']=anchor
        p['samples'].append(s)
    p['required_roles']=[s['role'] for s in p['samples']]
    for f in c['features']:
        f['targets']=[o.name for o in vfx if o['vfx_layer']==f['layer']]
        f['phase']='Prototype event at frame 40; clear at frame 90. Source timing unmeasured.'
        p['required_feature_samples'][f['id']]=['event','isolate-'+f['layer'].lower()]
    c['prototype']=p
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'effect_v01.blend'))
    validate(c,out/'contract.json','prototype')
    write_new(out/'contract.json',c)
    print(f"VFX_FIXTURE_READY: {effect}; {out}; proposed timing, not AAA reconstruction")


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',required=True)
    ap.add_argument('--effect',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    build(args.catalog,args.effect,args.out)
