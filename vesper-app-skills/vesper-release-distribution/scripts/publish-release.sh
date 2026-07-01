#!/usr/bin/env bash
set -euo pipefail

REPO="sipherxyz/vesper"
WORKFLOW="desktop.yml"
WATCH=1
ALLOW_DIRTY=0
VERSION=""

usage() {
  cat <<'EOF'
Usage: publish-release.sh --version X.Y.Z [options]

Options:
  --version X.Y.Z       Required semver to write into apps/electron/package.json
  --repo owner/repo     GitHub repo (default: sipherxyz/vesper)
  --workflow FILE       Workflow file name (default: desktop.yml)
  --no-watch            Trigger workflow and exit without waiting
  --allow-dirty         Skip dirty-tree guard (not recommended)
  -h, --help            Show help
EOF
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION="${2:-}"
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --workflow)
      WORKFLOW="${2:-}"
      shift 2
      ;;
    --no-watch)
      WATCH=0
      shift
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  echo "--version is required" >&2
  usage
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be semver X.Y.Z (got: $VERSION)" >&2
  exit 1
fi

require_cmd git
require_cmd gh
require_cmd node
require_cmd bun

if [[ ! -f "apps/electron/package.json" ]]; then
  echo "Run this from repo root (apps/electron/package.json not found)." >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
  echo "Expected to run on main branch, got: $BRANCH" >&2
  exit 1
fi

if [[ "$ALLOW_DIRTY" -ne 1 ]] && [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is dirty. Commit/stash changes first, or use --allow-dirty." >&2
  exit 1
fi

echo "Checking GitHub auth..."
gh auth status -h github.com >/dev/null

echo "Checking for existing tag v$VERSION on origin..."
if git ls-remote --exit-code --tags origin "refs/tags/v$VERSION" >/dev/null 2>&1; then
  echo "Tag v$VERSION already exists on origin. Choose a new version." >&2
  exit 1
fi

echo "Bumping release version markers to $VERSION..."
node -e "
  const fs = require('fs');

  const jsonPaths = ['apps/electron/package.json'];
  if (fs.existsSync('apps/viewer/package.json')) {
    jsonPaths.push('apps/viewer/package.json');
  }

  for (const path of jsonPaths) {
    const data = JSON.parse(fs.readFileSync(path, 'utf8'));
    data.version = process.argv[1];
    fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
  }

  const appVersionPath = 'packages/shared/src/version/app-version.ts';
  const source = fs.readFileSync(appVersionPath, 'utf8');
  const updated = source.replace(
    /export const APP_VERSION = '[^']+';/,
    'export const APP_VERSION = \'' + process.argv[1] + '\';'
  );

  if (source === updated) {
    throw new Error('Could not update APP_VERSION in ' + appVersionPath);
  }

  fs.writeFileSync(appVersionPath, updated);
" "$VERSION"

echo "Refreshing bun.lock..."
bun install

echo "Committing release bump..."
git add apps/electron/package.json packages/shared/src/version/app-version.ts bun.lock
if [[ -f "apps/viewer/package.json" ]]; then
  git add apps/viewer/package.json
fi
git commit -m "chore(release): bump desktop version to $VERSION"

echo "Pushing main..."
git push origin main

echo "Mirroring main -> release..."
git push origin main:release

EXPECTED_SHA="$(git rev-parse HEAD)"
ACTUAL_RELEASE_SHA="$(git ls-remote --heads origin release | awk '{print $1}')"
if [[ -z "$ACTUAL_RELEASE_SHA" ]]; then
  echo "Could not resolve origin/release after push." >&2
  exit 1
fi
if [[ "$ACTUAL_RELEASE_SHA" != "$EXPECTED_SHA" ]]; then
  echo "origin/release ($ACTUAL_RELEASE_SHA) does not match expected release commit ($EXPECTED_SHA)." >&2
  exit 1
fi

echo "Dispatching workflow $WORKFLOW on ref=release..."
gh workflow run "$WORKFLOW" --repo "$REPO" --ref release -f force=true

sleep 2
RUN_ID="$(gh run list \
  --repo "$REPO" \
  --workflow "Desktop build" \
  --branch release \
  --event workflow_dispatch \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')"

if [[ -z "$RUN_ID" || "$RUN_ID" == "null" ]]; then
  echo "Could not find the triggered workflow run." >&2
  exit 1
fi

echo "Workflow run: https://github.com/$REPO/actions/runs/$RUN_ID"

if [[ "$WATCH" -eq 0 ]]; then
  exit 0
fi

gh run watch "$RUN_ID" --repo "$REPO" --interval 20

CONCLUSION="$(gh run view "$RUN_ID" --repo "$REPO" --json conclusion --jq .conclusion)"
if [[ "$CONCLUSION" != "success" ]]; then
  echo "Workflow completed with conclusion=$CONCLUSION" >&2
  exit 1
fi

RELEASE_URL="$(gh release view "v$VERSION" --repo "$REPO" --json url --jq .url)"
echo "Release published: $RELEASE_URL"

LATEST_VERSION="$(gh api "repos/$REPO/contents/electron/latest?ref=gh-pages" --jq '.content' | tr -d '\n' | base64 --decode | node -e "const fs=require('fs');const x=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(x.version)")"
if [[ "$LATEST_VERSION" != "$VERSION" ]]; then
  echo "Warning: gh-pages latest is '$LATEST_VERSION' (expected '$VERSION')." >&2
else
  echo "Update manifest verified: electron/latest = $LATEST_VERSION"
fi
