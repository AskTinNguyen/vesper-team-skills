"""
chain_driver.py - automated MiniMax H3 clip-chaining into a long-form video.

Takes any MiniMax H3 ComfyUI single-clip workflow (I2V first/last-frame or R2V
reference-to-video), renders segment 1 from it, then loops: extract the previous
clip's last frame, feed it as the next segment's subject reference, submit, wait,
repeat. Writes manifest.jsonl + chain.log in a run directory and concatenates the
finished segments.

Resume-safe: rerunning the same command picks up from the last completed segment.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, time
from urllib.request import Request, urlopen

GEN_NODES = {"MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo"}
TEXT_SOURCES = {"PrimitiveStringMultiline", "PrimitiveString", "String", "CLIPTextEncode"}

DEFAULT_BEATS = [
 "The subject advances with sharp, precise footwork, punctuating the beat with a spinning kick held for the camera.",
 "The subject performs a quick acrobatic sequence across the floor, then lands crouched and looks directly into the lens.",
 "A dynamic vault-and-roll move around a prop, ending in a low stance staring calmly at camera.",
 "The subject circles with a prowling gait, throws a snap kick, and freezes mid-pose as the camera tightens.",
 "A feint followed by a burst of fast strikes toward camera, then a slow exhale and relaxed fighter stance.",
 "The subject balances on one leg in a controlled stretch, then kicks up into a light flip and lands facing the lens.",
 "A rhythmic, athletic footwork dance crossing frame, then a hard stop with eyes fixed on camera.",
 "The subject drops into a floor sweep, rolls back up, and finishes turned to camera with arms open.",
]

def log(msg, path):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)

def http_json(root, path, data=None, timeout=30):
    req = Request(root + path, data=(json.dumps(data).encode() if data is not None else None),
                  headers={"Content-Type": "application/json"} if data is not None else {"Accept": "application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.load(r)

def build_api(workflow_path):
    d = json.load(open(workflow_path, encoding="utf-8"))
    nodes = {n["id"]: n for n in d["nodes"]}
    link_map = {l[0]: l for l in d["links"]}
    reach = set()
    stack = [nid for nid, n in nodes.items() if n["type"] == "SaveVideo"]
    while stack:
        nid = stack.pop()
        if nid in reach:
            continue
        reach.add(nid)
        n = nodes.get(nid)
        if n is None:
            continue
        for ui in n.get("inputs", []):
            if ui.get("link") is not None:
                stack.append(link_map[ui["link"]][1])
    api = {}
    for nid in sorted(reach):
        n = nodes[nid]
        cls = n["type"]
        if cls == "MarkdownNote" or (len(cls) == 36 and cls.count("-") == 4):
            continue
        wv = list(n.get("widgets_values", []))
        inputs = {}
        special = {"ComfyMathExpression": ["expression"],
                   "MiniMaxH3ReferenceToVideo": ["ref_image_size"]}.get(cls, [])
        for ui in n.get("inputs", []):
            name = ui["name"]
            t = ui.get("type")
            if ui.get("link") is not None:
                l = link_map[ui["link"]]
                inputs[name] = [str(l[1]), l[2]]
            elif ui.get("widget") is not None and t != "IMAGEUPLOAD":
                if special and name in special:
                    if wv:
                        inputs[name] = wv.pop()
                elif wv:
                    inputs[name] = wv.pop(0)
        if cls == "ComfyMathExpression" and "expression" not in inputs and wv:
            inputs["expression"] = wv.pop(0)
        api[str(nid)] = {"class_type": cls, "inputs": inputs}

    meta = {"gen": None, "save": None, "seed": None, "prompt_node": None,
            "prompt_widget": None, "prompt_direct": None, "ref_node": None}
    for nid in sorted(reach):
        cls = nodes[nid]["type"]
        if cls in GEN_NODES:
            meta["gen"] = str(nid)
        elif cls == "SaveVideo":
            meta["save"] = str(nid)
        elif cls == "RandomNoise":
            meta["seed"] = str(nid)
    if meta["gen"]:
        gn = nodes[int(meta["gen"])]
        img_candidates = []
        for ui in gn.get("inputs", []):
            name, link = ui["name"], ui.get("link")
            if link is None:
                continue
            val = api[meta["gen"]]["inputs"].get(name)
            if name == "prompt":
                if isinstance(val, list):
                    src = val[0]
                    src_node = nodes.get(int(src))
                    if src_node and src_node["type"] in TEXT_SOURCES:
                        for s in src_node.get("inputs", []):
                            if s.get("widget") is not None and s.get("type") == "STRING":
                                meta["prompt_node"], meta["prompt_widget"] = str(src), s["name"]
                                break
                else:
                    meta["prompt_direct"] = name
            if ui["type"] == "IMAGE" and isinstance(val, list):
                src_id = int(val[0])
                if nodes.get(src_id, {}).get("type") == "LoadImage" and not img_candidates:
                    img_candidates.append((name, src_id))
        if img_candidates:
            img_candidates.sort(key=lambda x: x[0] != "first_frame")
            meta["ref_node"] = str(img_candidates[0][1])
    return api, meta

def apply_overrides(api, meta, ref_name, prompt_text, seed, prefix):
    if meta["save"]:
        api[meta["save"]]["inputs"]["filename_prefix"] = prefix
    if meta["seed"]:
        api[meta["seed"]]["inputs"]["noise_seed"] = seed
    if meta["ref_node"] and ref_name:
        api[meta["ref_node"]]["inputs"]["image"] = ref_name
    if meta["prompt_node"] and meta["prompt_widget"]:
        api[meta["prompt_node"]]["inputs"][meta["prompt_widget"]] = prompt_text
    elif meta["prompt_direct"] and meta["gen"]:
        api[meta["gen"]]["inputs"][meta["prompt_direct"]] = prompt_text

def make_prompt(seg, beats):
    beat = beats[(seg - 2) % len(beats)]
    return ("<Picture 1> is the exact subject from the previous shot. Preserve its "
            "identity, outfit, and environment exactly; never change them. Continue this "
            "15-second shot starting from the ending pose of the previous clip with "
            "continuous, physically plausible motion. " + beat + " Keep the same "
            "environment, camera style, lighting, and character. Emphasize natural motion, "
            "stable anatomy, confident body language, and matching ambient audio with "
            "motion-matched sound effects and no dialogue. Style: cinematic, dramatic "
            "lighting, sharp detail, hard cuts between shots, no text, no logos, no "
            "watermarks.")

def extract_last_frame(ffmpeg, video, png):
    if os.path.exists(png):
        os.remove(png)
    subprocess.run([ffmpeg, "-y", "-sseof", "-0.05", "-i", video, "-frames:v", "1", png],
                   check=True, capture_output=True)
    if not os.path.exists(png) or os.path.getsize(png) == 0:
        raise RuntimeError("frame extract produced empty file")

def wait_done(root, pid, max_minutes=40):
    deadline = time.time() + max_minutes * 60
    while time.time() < deadline:
        q = http_json(root, "/queue", timeout=10)
        running = {str(t[1]) for t in q.get("queue_running", [])}
        pending = {str(t[1]) for t in q.get("queue_pending", [])}
        if pid not in running | pending:
            hist = http_json(root, "/history/" + pid, timeout=10)
            if pid in hist:
                return hist[pid].get("status", {}).get("status_str", "unknown"), hist[pid].get("status", {})
        time.sleep(6)
    return "timeout", {}

def read_manifest(path):
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows

def append_manifest(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")

def newest_segment_video(output_root, seg, prefix_basename):
    pat = os.path.join(output_root, "video", prefix_basename + "_%02d_" % seg + "*.mp4")
    m = sorted(glob.glob(pat))
    return max(m, key=os.path.getmtime) if m else None

def concat(ffmpeg, workdir, output_root, prefix_basename, manifest_path):
    rows = sorted(read_manifest(manifest_path), key=lambda r: r["segment"])
    videos = [r["video"] for r in rows if r.get("video") and os.path.exists(r["video"])]
    if len(videos) >= 2:
        lst = os.path.join(workdir, "concat_list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for v in videos:
                f.write("file '" + v.replace("'", "'\\''") + "'\n")
        final = os.path.join(workdir, prefix_basename + "_final.mp4")
        try:
            subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                            "-c", "copy", final], check=True, capture_output=True)
            return final
        except Exception:
            subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", final],
                           check=True, capture_output=True)
            return final
    return None

def main():
    ap = argparse.ArgumentParser(description="Chain MiniMax H3 clips into a long video.")
    ap.add_argument("--workflow", required=True, help="Single-clip ComfyUI workflow JSON (I2V or R2V).")
    ap.add_argument("--prompt", default=None, help="Override the workflow's scene prompt.")
    ap.add_argument("--beats-file", default=None, help="JSON file with a list of script beats to rotate.")
    ap.add_argument("--subject", default=None, help="Base image file for segment 1 (optional).")
    ap.add_argument("--minutes", type=float, default=None)
    ap.add_argument("--total", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=15.0)
    ap.add_argument("--seed", type=int, default=332354276794873)
    ap.add_argument("--run-dir", default="h3chain_run")
    ap.add_argument("--output-root", default=r"C:\ComfyUI-H3\output")
    ap.add_argument("--input-root", default=r"C:\ComfyUI-H3\input")
    ap.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    ap.add_argument("--ffmpeg", default=None, help="Path to ffmpeg (auto-detected if omitted).")
    ap.add_argument("--output-prefix", default="video/h3chain")
    ap.add_argument("--dry-run", action="store_true", help="Build and print the API prompt for segment 1.")
    args = ap.parse_args()

    if not args.dry_run:
        args.ffmpeg = args.ffmpeg or shutil.which("ffmpeg")
        if not args.ffmpeg:
            print("ERROR: ffmpeg not found; pass --ffmpeg")
            sys.exit(1)

    if args.total is None and args.minutes is None:
        args.total = 40
    if args.total is None:
        seg_per_min = 60.0 / args.max_seconds
        args.total = max(2, int(round(args.minutes * seg_per_min)))

    beats = list(DEFAULT_BEATS)
    if args.beats_file:
        beats = json.load(open(args.beats_file, encoding="utf-8"))
    if not beats:
        beats = [""]

    if not args.dry_run:
        os.makedirs(args.run_dir, exist_ok=True)
        os.makedirs(os.path.join(args.input_root, "chain"), exist_ok=True)
    logpath = os.path.join(args.run_dir, "chain.log")
    manpath = os.path.join(args.run_dir, "manifest.jsonl")

    api, meta = build_api(args.workflow)
    if meta["gen"] is None:
        log("ERROR: no MiniMax H3 generation node found in workflow", logpath)
        sys.exit(1)

    base_prompt = args.prompt
    if base_prompt is None:
        if meta["prompt_node"]:
            base_prompt = api[meta["prompt_node"]]["inputs"].get(meta["prompt_widget"], "")
        elif meta["prompt_direct"]:
            base_prompt = api[meta["gen"]]["inputs"][meta["prompt_direct"]]
        else:
            base_prompt = ""

    prefix_basename = args.output_prefix.rsplit("/", 1)[-1]

    if args.dry_run:
        api2, meta2 = build_api(args.workflow)
        apply_overrides(api2, meta2, args.subject, base_prompt, args.seed,
                        args.output_prefix + "_01")
        print("detected:", json.dumps(meta2, default=str))
        print("nodes:", sorted(api2.keys()))
        print("gen inputs:", json.dumps(api2[meta2["gen"]]["inputs"], ensure_ascii=False)[:1200])
        return

    man = read_manifest(manpath)
    by_seg = {r["segment"]: r for r in man}
    if 1 not in by_seg:
        append_manifest(manpath, {"segment": 1, "prompt_id": None, "video": None})
        by_seg = {r["segment"]: r for r in read_manifest(manpath)}

    for seg in range(1, args.total + 1):
        if by_seg.get(seg, {}).get("video") and os.path.exists(by_seg[seg]["video"]):
            continue
        if seg == 1:
            ref = args.subject
            prompt = base_prompt
        else:
            prev = by_seg[seg - 1].get("video")
            if not prev or not os.path.exists(prev):
                log("segment %d: missing previous video; halting" % seg, logpath)
                break
            ref = "chain/ref_%02d.png" % seg
            ref_path = os.path.join(args.input_root, "chain", "ref_%02d.png" % seg)
            try:
                extract_last_frame(args.ffmpeg, prev, ref_path)
            except Exception as e:
                log("segment %d: frame extract failed: %r; halting" % (seg, e), logpath)
                break
            prompt = make_prompt(seg, beats)
        seed = args.seed + seg * 7919
        prefix = args.output_prefix + "_%02d" % seg
        cur_api, _ = build_api(args.workflow)
        apply_overrides(cur_api, meta, ref, prompt, seed, prefix)
        try:
            pid = http_json(args.comfy_url, "/prompt",
                            {"prompt": cur_api, "client_id": "chain-" + prefix_basename})["prompt_id"]
        except Exception as e:
            log("segment %d: submit failed: %r; halting" % (seg, e), logpath)
            break
        log("segment %d: submitted prompt_id=%s starting" % (seg, pid), logpath)
        st, detail = wait_done(args.comfy_url, pid)
        if st != "success":
            log("segment %d: render status=%s; halting" % (seg, st), logpath)
            append_manifest(manpath, {"segment": seg, "prompt_id": pid, "video": None, "status": st})
            break
        video = newest_segment_video(args.output_root, seg, prefix_basename)
        append_manifest(manpath, {"segment": seg, "prompt_id": pid, "video": video,
                                  "status": "success",
                                  "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
        by_seg[seg] = {"segment": seg, "video": video}
        log("segment %d: DONE video=%s" % (seg, video), logpath)

    final = concat(args.ffmpeg, args.run_dir, args.output_root, prefix_basename, manpath)
    if final:
        log("concat OK -> %s (%s bytes)" % (final, os.path.getsize(final)), logpath)
    log("chain run finished", logpath)

if __name__ == "__main__":
    main()