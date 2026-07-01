# nexu-io/html-video setup notes on Windows/git-bash

Session-derived recipe for installing and verifying `https://github.com/nexu-io/html-video` on a Windows host where the terminal tool runs through git-bash/MSYS.

## Discovery

The X post described an open-source project named `html-video`. GitHub search for `html-video` surfaced the target repo:

- `nexu-io/html-video` — "Programmatic video for coding agents — turn HTML, CSS & data into real MP4s..."

## Install/build recipe

```bash
cd C:/Users/Admin
if [ ! -d html-video ]; then
  git clone https://github.com/nexu-io/html-video.git
fi
cd C:/Users/Admin/html-video

# If pnpm is missing and corepack cannot write to Program Files on Windows:
npm install -g pnpm

pnpm install
pnpm -r build
```

## Playwright browser install

The repo's root may not expose a root-level `playwright` binary because Playwright is a dependency of the adapter workspace package. Use the package filter:

```bash
cd C:/Users/Admin/html-video
pnpm --filter @html-video/adapter-hyperframes exec playwright install chromium
```

A static `doctor` command may still warn that Chrome/Chromium is not detected if it only checks standard system Chrome locations. If a real render works, Playwright-managed Chromium is sufficient for the render path.

## CLI verification

```bash
cd C:/Users/Admin/html-video
node packages/cli/dist/bin.js doctor
node packages/cli/dist/bin.js search-templates --intent "product promo" --top 3
```

Minimal render smoke test used in session:

```bash
cd C:/Users/Admin/html-video
node packages/cli/dist/bin.js project-create \
  --name test-install \
  --intent 'short product promo for html-video' \
  --aspect 16:9

node packages/cli/dist/bin.js project-set-template <project_id> --template vfx-text-cursor
node packages/cli/dist/bin.js project-set-var <project_id> --key text --value 'HTML becomes video — on your laptop.'
node packages/cli/dist/bin.js project-set-var <project_id> --key duration_sec --value 3
node packages/cli/dist/bin.js project-set-var <project_id> --key speed_cps --value 20

mkdir -p test-output
node packages/cli/dist/bin.js project-render <project_id> \
  --output test-output/test-install.mp4 \
  --stream-progress
```

On the observed Windows/git-bash host, background/non-TTY render failed with `stdin is not a tty`; rerunning the same `project-render` command in a foreground PTY session succeeded and wrote the MP4.

## Studio verification

Start as a tracked background process:

```bash
cd C:/Users/Admin/html-video
node packages/cli/dist/bin.js studio --port 3071
```

Verify with HTTP endpoints:

```text
http://127.0.0.1:3071/api/templates
http://127.0.0.1:3071/api/projects
```

Report both the studio URL and the process/session id if leaving it running for the user.
