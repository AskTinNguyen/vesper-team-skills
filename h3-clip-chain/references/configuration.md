# chain_driver.py configuration

## Purpose
Renders one MiniMax H3 clip, then loops: copy the previous clip's last frame into
the model's input folder as the next segment's subject reference, submit the same
workflow with that reference, wait, and repeat until the requested runtime is met.
Tracks every segment in `manifest.jsonl` and logs to `chain.log` inside `--run-dir`.

## CLI options

| Option | Default | Meaning |
| --- | --- | --- |
| `--workflow` | (required) | Single-clip ComfyUI workflow JSON (I2V or R2V). |
| `--prompt` | workflow value | Override the scene prompt text for every segment. |
| `--beats-file` | built-in list | JSON array of short action/script beats; rotated per segment. |
| `--subject` | none | Base image for segment 1 (optional). |
| `--minutes` | none | Target runtime; segments = `minutes * (60 / max_seconds)`. |
| `--total` | 40 | Exact number of segments (takes precedence over `--minutes`). |
| `--max-seconds` | 15.0 | Nominal per-clip length; H3 caps around 15 s. |
| `--seed` | 332354276794873 | Base seed; per-segment seed = `seed + seg * 7919`. |
| `--run-dir` | `h3chain_run` | Where manifest.jsonl / chain.log / final.mp4 live. |
| `--output-root` | `C:\ComfyUI-H3\output` | Root ComfyUI output dir (segments saved under `video/`). |
| `--input-root` | `C:\ComfyUI-H3\input` | Root ComfyUI input dir (chain frames written under `chain/`). |
| `--comfy-url` | `http://127.0.0.1:8188` | ComfyUI HTTP endpoint. |
| `--ffmpeg` | auto | Path to ffmpeg if not on PATH. |
| `--output-prefix` | `video/h3chain` | SaveVideo filename prefix; segment number is appended. |
| `--dry-run` | off | Print the detected graph + API payload for segment 1 and exit. |

## What the driver auto-detects in the workflow
Only nodes reachable from the `SaveVideo` node are considered (this ignores notes
and unused template branches). Then:

- `MiniMaxH3ImageToVideo` / `MiniMaxH3ReferenceToVideo` = the generation node.
- `SaveVideo` = the output node (`filename_prefix` is overridden).
- `RandomNoise` = the seed node.
- Prompt text: either the generation node's `prompt` input directly, or the
  `PrimitiveStringMultiline`/`String` node feeding it (its STRING widget is set).
- Reference image: the `LoadImage` node feeding the generation node's `first_frame`
  or first `ref_images.*`/`ref_videos.*` IMAGE input. This image is swapped for the
  extracted frame on segments 2+.

If you hand-build a workflow for this skill, keep those roles and names; the
generic UI-to-API conversion handles subgraph and flat graphs alike.

## tracker_server.py

| Option | Default | Meaning |
| --- | --- | --- |
| `--run-dir` | `h3chain_run` | Must match the driver's run dir. |
| `--output-root` / `--input-root` | ComfyUI roots | Where clips / frames are served from. |
| `--comfy-url` | `http://127.0.0.1:8188` | For live queue state. |
| `--port` | 8321 | Listen port (127.0.0.1 only). |
| `--total` | 40 | Expected segment count. |
| `--web` | `tracker.html` (next to server) | Dashboard HTML to serve. |

Open `http://127.0.0.1:<port>` in a browser. The page polls `/api/progress` every 3 s.

## Resume & failure
Seldom re-run with the same `--run-dir`; completed segments are skipped from the
manifest, so a crashed run resumes where it stopped. A failed render logs the
status and halts the loop rather than burning GPU time.