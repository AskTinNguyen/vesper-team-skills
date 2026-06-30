---
name: agentic-html-video-workflows
description: "Set up, verify, and operate agent-native HTML-to-video repositories/tools: local studio, CLI, templates, Playwright/Chromium render path, and MP4 smoke tests."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, html-video, agents, playwright, ffmpeg, pnpm, studio, rendering]
---

# Agentic HTML→Video Workflows

Use this skill when the user asks to install, set up, troubleshoot, or smoke-test an agent-native HTML-to-video project/tool (for example an HTML/CSS/JS + template gallery + local studio + MP4 export workflow). The goal is not just dependency installation: always verify the actual render path end-to-end when possible.

## Core workflow

1. **Identify the real source repo.**
   - If the request comes from a social post, open/extract the post and comments if needed, then confirm the repository URL from GitHub search or the post's linked repo.
   - Prefer the upstream repo over mirrored snippets.

2. **Clone or update.**
   - Clone into a stable user workspace path.
   - If the directory already exists, inspect remotes before pulling or rebuilding.

3. **Read the repo quick start.**
   - Check `README.md`, package manager metadata (`packageManager`, lockfile), and any agent guidance files.
   - Do not assume `npm`, `pnpm`, or `yarn`; use what the repo declares.

4. **Install dependencies and build.**
   - For pnpm monorepos, run:
     ```bash
     pnpm install
     pnpm -r build
     ```
   - If the package manager itself is missing, install/activate it using the repo-compatible path; capture the fix, not the failure.

5. **Install browser/render prerequisites.**
   - HTML-video render stacks often need both:
     - `ffmpeg` for MP4 encoding/concat/muxing.
     - Playwright/Chromium or system Chrome for headless capture.
   - In pnpm workspaces, Playwright may be a dependency of a filtered package, not the root. Prefer the owning workspace package:
     ```bash
     pnpm --filter <package-that-depends-on-playwright> exec playwright install chromium
     ```

6. **Run built-in diagnostics.**
   - Use project CLI diagnostics if present (`doctor`, `smoke`, `search-templates`, etc.).
   - Treat static doctor warnings as advisory if an actual render smoke test proves the underlying path works (for example, a doctor that only searches system Chrome paths may still warn even when Playwright-managed Chromium is installed and usable).

7. **Do a real render smoke test.**
   - Create or load a minimal project/template.
   - Set the required variables from template inspection.
   - Export an MP4 and verify the command exits successfully and writes an output file.
   - Prefer a very short clip to keep verification fast.

8. **Start and verify the local studio.**
   - Start the studio as a tracked background process, not shell-level `&`/`nohup`.
   - Verify with an HTTP request to a lightweight API endpoint (`/api/templates`, `/api/projects`, `/health`, etc.) instead of only trusting the startup log.

## Windows / git-bash notes

- Use POSIX shell syntax in git-bash, but forward-slash Windows paths are usually safest in command arguments (`C:/Users/...`).
- If `corepack enable pnpm` fails because it wants to write under `C:\Program Files\nodejs`, use a user-level/global npm install instead:
  ```bash
  npm install -g pnpm
  pnpm -v
  ```
- Some Node CLIs that internally use Playwright/prompt-like code can fail in non-TTY background mode with `stdin is not a tty`. Retry the exact same command in a PTY foreground session for render/export verification.

## Verification checklist

Before reporting success, include:

- Repository path.
- Install/build commands that succeeded.
- Diagnostic summary.
- Render smoke-test result and output MP4 path if generated.
- Studio URL and background process/session id if left running.
- Any remaining warnings, clearly distinguished from actual functional failures.

## References

- `references/html-video-windows-setup.md` — session-derived setup and verification recipe for the nexu-io/html-video repo on Windows/git-bash, including Playwright workspace install and PTY render retry.
