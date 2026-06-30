# Gateway media delivery

Former standalone skill `gateway-media-delivery`, preserved as a reference under the skill-library management umbrella during consolidation.

Use these notes when skill-library work intersects with Hermes gateway media/file delivery or when generated skill artifacts must be sent as native attachments.

## Trigger

Users report that Hermes gateway agents cannot send images/files/audio as native attachments, `MEDIA:<path>` renders literally, or Telegram/Slack delivery skips local files.

## Core workflow

1. Inspect the active gateway profile/config before assuming the adapter is broken.
   - Slack needs `SLACK_BOT_TOKEN`; Socket Mode gateway also needs `SLACK_APP_TOKEN`; a send target requires `SLACK_HOME_CHANNEL` or an explicit `slack:<channel_id>` target.
   - Telegram needs `TELEGRAM_BOT_TOKEN` and a configured home channel or explicit chat id.
2. Separate configuration blockers from media-path bugs.
3. Exercise the real gateway send path when possible: create a tiny local artifact, send via `send_message` with `MEDIA:<absolute_path>`, and verify the returned platform result/message id.
4. Never imply an image/file was delivered unless a real local file exists and the outgoing message includes `MEDIA:<absolute_path>` (or `send_message` was called with that exact attachment marker). Do not use placeholder markdown such as `![image](attachment)` or say “here is the attachment” without attaching the file.
5. For Telegram image smoke tests, prefer `.png`, `.jpg`, or `.webp` artifacts over `.svg`; SVG may be accepted as a document or handled inconsistently by clients, while raster formats exercise native photo delivery more directly.
6. On Windows, treat path syntax crossing as the likely fault line: agents may emit `/c/Users/Admin/...`, while native Python adapters need `C:/Users/Admin/...` or `C:\\Users\\Admin\\...`.

## Preferred implementation shape

If source changes are needed, avoid Telegram/Slack one-off branches. Put the invariant in a canonical helper module owned by gateway media delivery:

- `normalize_local_media_path(path)`
- `local_path_to_file_url(path)`
- `file_url_to_local_path(url)`
- shared `MEDIA:<path>` and bare local-file extraction regexes

Call helpers from base platform media extraction, base image batching, post-stream delivery, Slack upload boundaries, and Telegram send boundaries.

## Regression tests

- MSYS path normalization: `/c/Users/Admin/out.png` -> `C:/Users/Admin/out.png`
- native Windows path normalization: `C:\\Users\\Admin\\out.png` -> `C:/Users/Admin/out.png`
- `MEDIA:` extraction accepts MSYS and native Windows paths
- bare local-file extraction accepts MSYS and native Windows paths
- `local_path_to_file_url` / `file_url_to_local_path` round trip paths with spaces
- Slack multi-image upload receives normalized local paths
- Telegram multi-image upload opens normalized local paths before the Bot API

## Pitfalls

- Do not commit runtime artifacts such as `.artifacts/` test images.
- Do not include unrelated local changes in the PR.
- Do not record credential absence as a durable tool failure; it is setup state.
- `git diff --no-index` returns exit code 1 when files differ; that is normal.
- On Windows, use `uv run --with ...` for focused tests if default Python lacks pytest or optional gateway dependencies.
