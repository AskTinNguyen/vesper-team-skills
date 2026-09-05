"""Run in Blender: capture a declared VFX contract from a saved checkpoint."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vfx_contract import digest, read, require, resolve, validate, verify, write_new


def render_eligible(scene):
    # Viewport hide_set()/hide_viewport do not define render eligibility.
    eligible = set()
    def walk(layer, parent_enabled=True):
        enabled = parent_enabled and not layer.exclude and not layer.collection.hide_render
        if enabled:
            eligible.update(layer.collection.objects)
        for child in layer.children:
            walk(child, enabled)
    walk(scene.view_layers[0].layer_collection)
    return [o for o in eligible if o.get("vfx_layer") and not o.hide_render and max(abs(v) for v in o.matrix_world.to_scale()) > 1e-5]


def compositor_enabled(scene):
    tree = getattr(scene, "compositing_node_group", None)
    if tree is None:
        tree = getattr(scene, "node_tree", None)
    return bool(scene.render.use_compositing and tree and len(tree.nodes))


def capture(contract_path, output):
    contract_path = Path(contract_path).resolve()
    out = Path(output).resolve()
    c = validate(read(contract_path), contract_path, "prototype")
    p = c["prototype"]
    require(Path(bpy.data.filepath).resolve() == resolve(contract_path, p["checkpoint"]), "Open .blend does not match contract checkpoint")
    require(not bpy.data.is_dirty, "Capture requires a freshly reopened clean checkpoint")
    require(not out.exists(), "Evidence output already exists; use a new version")
    grouped = defaultdict(list)
    for sample in p["samples"]:
        scene = bpy.data.scenes.get(sample["scene"])
        require(scene is not None, f"Missing scene: {sample['scene']}")
        camera = scene.objects.get(sample["camera"])
        require(camera is not None and camera.type == "CAMERA", f"Missing camera: {sample['camera']}")
        require(scene.get("vfx_variant") == sample["variant"] and scene.get("vfx_scenario") == sample["scenario"], "Scene variant/scenario tag mismatch")
        require(scene.render.fps / scene.render.fps_base == p["fps"], "Scene FPS differs from contract")
        grouped[sample["scene"]].append(sample)
    for f in c["features"]:
        if f["disposition"] == "implement":
            for name in f["targets"]:
                require(bpy.data.objects.get(name) is not None, f"Feature target does not exist: {name}")
    out.mkdir(parents=True)
    manifest = {"schema_version": 1, "blender_version": bpy.app.version_string, "contract_sha256": digest(contract_path), "checkpoint_sha256": digest(bpy.data.filepath), "reference_hashes": {r["id"]: r["sha256"] for r in c["references"]}, "samples": []}
    for scene_name, samples in grouped.items():
        scene = bpy.data.scenes[scene_name]
        if bpy.context.window:
            bpy.context.window.scene = scene
        scene.frame_set(p["frame_start"])
        previous = p["frame_start"]
        for sample in sorted(samples, key=lambda s: s["frame"]):
            for frame in range(previous + 1, sample["frame"] + 1):
                scene.frame_set(frame)
            scene.frame_set(sample["frame"])
            previous = sample["frame"]
            camera = scene.objects[sample["camera"]]
            scene.camera = camera
            visible = render_eligible(scene)
            filename = f"{sample['id']}.png"
            require(Path(filename).name == filename and '/' not in filename and '\\' not in filename, "Sample ID cannot contain path separators")
            scene.render.image_settings.file_format = "PNG"
            scene.render.filepath = str(out / filename)
            bpy.ops.render.render(write_still=True, scene=scene.name)
            manifest["samples"].append({**sample, "path": filename, "sha256": digest(out / filename), "scene_variant": scene.get("vfx_variant"), "scene_scenario": scene.get("vfx_scenario"), "variant_signature": scene.get("vfx_variant_signature", ""), "seed": scene.cycles.seed if scene.render.engine == "CYCLES" else scene.get("vfx_seed"), "fps": scene.render.fps / scene.render.fps_base, "engine": scene.render.engine, "resolution": [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage], "camera_matrix": [list(row) for row in camera.matrix_world], "camera_lens": camera.data.lens, "camera_type": camera.data.type, "color_management": {"display": scene.display_settings.display_device, "view": scene.view_settings.view_transform, "look": scene.view_settings.look, "exposure": scene.view_settings.exposure, "gamma": scene.view_settings.gamma}, "compositor_enabled": compositor_enabled(scene), "visible_targets": sorted(o.name for o in visible), "visible_layers": sorted({o['vfx_layer'] for o in visible})})
    write_new(out / "manifest.json", manifest)
    verify(c, contract_path, manifest, out / "manifest.json")
    print(f"VFX_CAPTURE_PASS: {len(manifest['samples'])} samples; {out / 'manifest.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    capture(args.contract, args.out)
