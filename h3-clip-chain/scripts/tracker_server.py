"""
tracker_server.py - live dashboard for a chain_driver.py run.

Serves a self-contained HTML dashboard and a /api/progress JSON endpoint that
reads the driver's manifest.jsonl + chain.log from --run-dir, polls the ComfyUI
queue for live state, computes per-segment status and ETA, and streams clip
videos / reference frames (with HTTP Range support).
"""
import argparse, json, os, re, time, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

WINDOWS = os.name == "nt"
_submitted_re = re.compile(r"segment (\d+): submitted prompt_id=([0-9a-f-]+)")
_dur_cache = {}

def cli():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", default="h3chain_run")
    ap.add_argument("--output-root", default=r"C:\ComfyUI-H3\output")
    ap.add_argument("--input-root", default=r"C:\ComfyUI-H3\input")
    ap.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    ap.add_argument("--port", type=int, default=8321)
    ap.add_argument("--total", type=int, default=40)
    ap.add_argument("--web", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker.html"))
    return ap.parse_args()

A = cli()
MANIFEST = os.path.join(A.run_dir, "manifest.jsonl")
LOG = os.path.join(A.run_dir, "chain.log")

def json_get(url, timeout=2.5):
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None

def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except Exception:
        return []

def parse_manifest():
    rows = {}
    for line in read_lines(MANIFEST):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            rows[int(r["segment"])] = r
        except Exception:
            continue
    return rows

def parse_submits():
    out = {}
    for line in read_lines(LOG):
        m = _submitted_re.search(line)
        if m:
            seg = int(m.group(1))
            out[seg] = {"prompt_id": m.group(2), "ts": line[:19]}
    return out

def mp4_url(video_path):
    try:
        rel = os.path.relpath(video_path, A.output_root).replace("\\", "/")
        return "/clips/" + urllib.parse.quote(rel)
    except Exception:
        return None

def file_size(p):
    try:
        return os.path.getsize(p)
    except Exception:
        return None

def file_duration(p):
    key = p + "|" + str((os.path.getmtime(p) if os.path.exists(p) else 0))
    if key in _dur_cache:
        return _dur_cache[key]
    d = None
    try:
        import subprocess
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", p], capture_output=True, text=True, timeout=20)
        d = float(out.stdout.strip())
    except Exception:
        d = None
    _dur_cache[key] = d
    return d

def get_queue():
    q = json_get(A.comfy_url + "/queue")
    if isinstance(q, dict):
        running = [str(t[1]) if len(t) > 1 else "" for t in q.get("queue_running", [])]
        pending = [str(t[1]) if len(t) > 1 else "" for t in q.get("queue_pending", [])]
        return running, pending
    return [], []

def build_payload():
    man = parse_manifest()
    subs = parse_submits()
    running_ids, pending_ids = get_queue()
    segments = []
    done = 0
    for seg in range(1, A.total + 1):
        r = man.get(seg, {})
        video = r.get("video")
        pid = r.get("prompt_id") or subs.get(seg, {}).get("prompt_id")
        if video and os.path.exists(video):
            status = "done"
            done += 1
        elif pid in running_ids:
            status = "working"
        elif pid in pending_ids:
            status = "queued"
        elif r.get("status") and r.get("status") != "success":
            status = "error"
        elif subs.get(seg) or r.get("prompt_id"):
            status = "finalizing"
        else:
            status = "pending"
        ref = r.get("ref") or (("chain/ref_%02d.png" % seg) if seg > 1 else None)
        segments.append({
            "seg": seg, "status": status,
            "video": video, "video_url": mp4_url(video) if video else None,
            "video_name": os.path.basename(video) if video else None,
            "size": file_size(video) if video else None,
            "duration": file_duration(video) if video else None,
            "ref": ref, "seed": r.get("seed"), "prompt_id": pid,
            "ts": r.get("ts") or subs.get(seg, {}).get("ts"),
            "status_line": r.get("status"),
        })

    working = None
    last = max(subs.keys()) if subs else None
    if last and not (man.get(last, {}).get("video")):
        wt = subs[last]["ts"]
        pid = subs[last]["prompt_id"]
        state = "working" if pid in running_ids else ("queued" if pid in pending_ids else "finalizing")
        working = {"seg": last, "prompt_id": pid, "started": wt,
                   "elapsed": (time.time() - time.mktime(time.strptime(wt, "%Y-%m-%d %H:%M:%S"))) if wt else None,
                   "state": state,
                   "ref": ("chain/ref_%02d.png" % last) if last > 1 else None}

    avg, eta = None, None
    times = []
    prev = None
    for s in sorted([x for x in segments if x["status"] == "done" and x["ts"]], key=lambda x: x["seg"]):
        if prev is not None:
            d = time.mktime(time.strptime(s["ts"], "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(prev, "%Y-%m-%d %H:%M:%S"))
            times.append(max(30.0, d))
        prev = s["ts"]
    if len(times) >= 2:
        avg = sum(times) / len(times)
        rem = A.total - done
        if rem > 0:
            eta = rem * avg
    last_log = next((l for l in reversed(read_lines(LOG)) if l.strip()), None)
    return {"total": A.total, "done": done, "remaining": A.total - done,
            "eta_seconds": eta, "avg_seconds": avg, "working": working,
            "queue": {"running": running_ids, "pending": pending_ids},
            "segments": segments, "last_log": last_log}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            try:
                with open(A.web, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except Exception:
                self._send(500, b"tracker.html missing", "text/plain")
            return
        if path == "/api/progress":
            self._send(200, json.dumps(build_payload()).encode("utf-8"), "application/json; charset=utf-8")
            return
        if path.startswith("/clips/") or path.startswith("/refs/"):
            name = urllib.parse.unquote(path.split("/", 2)[2])
            root = A.output_root if path.startswith("/clips/") else A.input_root
            full = os.path.normpath(os.path.join(root, name))
            if full != os.path.normpath(root) and not full.startswith(os.path.normpath(root) + os.sep):
                self._send(403, b"forbidden", "text/plain")
                return
            if not os.path.isfile(full):
                self._send(404, b"not found", "text/plain")
                return
            ctype = "video/mp4" if full.lower().endswith(".mp4") else "image/png"
            size = os.path.getsize(full)
            rng = self.headers.get("Range")
            start, end, status = 0, size - 1, 200
            if rng and rng.startswith("bytes="):
                try:
                    spec = rng[6:].split("-", 1)
                    start = int(spec[0]) if spec[0] else 0
                    end = int(spec[1]) if len(spec) > 1 and spec[1] else size - 1
                    end = min(end, size - 1)
                    if start > end or start >= size:
                        self.send_response(416)
                        self.send_header("Content-Range", "bytes */%d" % size)
                        self.end_headers()
                        return
                    status = 206
                except Exception:
                    start, end, status = 0, size - 1, 200
            length = end - start + 1
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            if status == 206:
                self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                with open(full, "rb") as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(1 << 16, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except Exception:
                pass
            return
        self._send(404, b"not found", "text/plain")

def main():
    print("tracker listening on http://127.0.0.1:%d (run-dir=%s)" % (A.port, A.run_dir))
    ThreadingHTTPServer(("127.0.0.1", A.port), Handler).serve_forever()

if __name__ == "__main__":
    main()