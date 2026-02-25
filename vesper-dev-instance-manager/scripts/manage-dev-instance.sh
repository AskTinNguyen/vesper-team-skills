#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  manage-dev-instance.sh --instance-number <N> [options]

Required:
  --instance-number <N>        Numeric instance number (ex: 2)

Options:
  --action <name>              build-and-launch | launch | build | stop | status
                               Default: build-and-launch
  --worktree <path>            Target worktree path. Default: current directory
  --profile-label <label>      Override auto slug (a-z0-9-)
  --skip-build                 Skip build during build-and-launch
  --help                       Show this help

Examples:
  manage-dev-instance.sh --instance-number 2 --action build-and-launch
  manage-dev-instance.sh --instance-number 2 --action status
  manage-dev-instance.sh --instance-number 2 --action stop
EOF
}

ACTION="build-and-launch"
WORKTREE="$(pwd)"
INSTANCE_NUMBER=""
PROFILE_LABEL=""
SKIP_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --instance-number)
      INSTANCE_NUMBER="${2:-}"
      shift 2
      ;;
    --action)
      ACTION="${2:-}"
      shift 2
      ;;
    --worktree)
      WORKTREE="${2:-}"
      shift 2
      ;;
    --profile-label)
      PROFILE_LABEL="${2:-}"
      shift 2
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$INSTANCE_NUMBER" ]]; then
  echo "--instance-number is required" >&2
  usage
  exit 1
fi

if ! [[ "$INSTANCE_NUMBER" =~ ^[0-9]+$ ]]; then
  echo "--instance-number must be numeric" >&2
  exit 1
fi

if [[ ! -d "$WORKTREE" ]]; then
  echo "Worktree path not found: $WORKTREE" >&2
  exit 1
fi

WORKTREE="$(cd "$WORKTREE" && pwd)"

if [[ ! -f "$WORKTREE/package.json" ]]; then
  echo "Not a repo root (package.json missing): $WORKTREE" >&2
  exit 1
fi

if [[ -z "$PROFILE_LABEL" ]]; then
  WORKTREE_BASENAME="$(basename "$WORKTREE")"
  PROFILE_LABEL="$(echo "$WORKTREE_BASENAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed -E 's/^-+//; s/-+$//')"
  if [[ -z "$PROFILE_LABEL" ]]; then
    PROFILE_LABEL="worktree"
  fi
fi

INSTANCE_ID="dev${INSTANCE_NUMBER}-${PROFILE_LABEL}"
CONFIG_DIR="${HOME}/.vesper-dev/${INSTANCE_ID}"
WORKSPACES_DIR="${CONFIG_DIR}/workspaces"
APP_NAME="Vesper Dev #${INSTANCE_NUMBER} (${PROFILE_LABEL})"
DEEPLINK_SCHEME="vesper-dev-${INSTANCE_NUMBER}-${PROFILE_LABEL}"
PID_FILE="/tmp/vesper-dev-${INSTANCE_NUMBER}-${PROFILE_LABEL}.pid"
LOG_FILE="/tmp/vesper-dev-${INSTANCE_NUMBER}-${PROFILE_LABEL}.log"

export VESPER_DEV_MODE=1
export VESPER_INSTANCE_NUMBER="$INSTANCE_NUMBER"
export VESPER_INSTANCE_ID="$INSTANCE_ID"
export VESPER_CONFIG_DIR="$CONFIG_DIR"
export VESPER_WORKSPACES_DIR="$WORKSPACES_DIR"
export VESPER_APP_NAME="$APP_NAME"
export VESPER_DEEPLINK_SCHEME="$DEEPLINK_SCHEME"

mkdir -p "$WORKSPACES_DIR"

ensure_worktree_node_modules() {
  if [[ -e "$WORKTREE/node_modules" || -L "$WORKTREE/node_modules" ]]; then
    return
  fi

  local common_dir
  common_dir="$(git -C "$WORKTREE" rev-parse --git-common-dir 2>/dev/null || true)"
  local common_root=""
  if [[ -n "$common_dir" ]]; then
    if [[ "$common_dir" = /* ]]; then
      common_root="$(cd "$common_dir/.." 2>/dev/null && pwd || true)"
    else
      common_root="$(cd "$WORKTREE/$common_dir/.." 2>/dev/null && pwd || true)"
    fi
  fi

  if [[ -n "$common_root" && -d "$common_root/node_modules" ]]; then
    ln -s "$common_root/node_modules" "$WORKTREE/node_modules"
    echo "Linked node_modules from common root: $common_root/node_modules"
    return
  fi

  echo "node_modules missing in worktree; running bun install..."
  (cd "$WORKTREE" && bun install)
}

build_app() {
  ensure_worktree_node_modules
  (cd "$WORKTREE" && bun run electron:build)
}

find_running_pids() {
  ps -ax -o pid=,command= \
    | awk -v worktree="$WORKTREE" 'index($0, worktree "/node_modules/.bin/electron apps/electron") { print $1 }'
}

sync_pid_file_from_processes() {
  local pid
  pid="$(find_running_pids | head -n 1)"
  if [[ -n "$pid" ]]; then
    echo "$pid" >"$PID_FILE"
    return 0
  fi
  return 1
}

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  if sync_pid_file_from_processes; then
    return 0
  fi
  return 1
}

stop_instance() {
  local pids=()
  local seen=""
  local pid=""

  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      pids+=("$pid")
      seen=" $pid "
    fi
  fi

  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    if [[ "$seen" != *" $pid "* ]]; then
      pids+=("$pid")
      seen="${seen}${pid} "
    fi
  done < <(find_running_pids)

  if [[ "${#pids[@]}" -eq 0 ]]; then
    rm -f "$PID_FILE"
    echo "No running instance for profile $PROFILE_LABEL"
    return
  fi

  local killed=()
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
    killed+=("$pid")
  done

  sleep 1
  for pid in "${killed[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  done

  rm -f "$PID_FILE"
  echo "Stopped instance PID(s): ${killed[*]}"
}

launch_app() {
  local electron_bin="$WORKTREE/node_modules/.bin/electron"
  if [[ ! -x "$electron_bin" ]]; then
    echo "Electron binary not found: $electron_bin" >&2
    echo "Try: bun install" >&2
    exit 1
  fi

  ensure_worktree_node_modules
  stop_instance
  : >"$LOG_FILE"
  (cd "$WORKTREE" && nohup "$electron_bin" apps/electron >>"$LOG_FILE" 2>&1 & echo $! >"$PID_FILE")
  sleep 1
  if is_running; then
    local pid
    pid="$(cat "$PID_FILE")"
    echo "Launched PID: $pid"
  else
    echo "Launch failed. Check log: $LOG_FILE" >&2
    exit 1
  fi
}

print_status() {
  echo "Instance Number : $INSTANCE_NUMBER"
  echo "Worktree        : $WORKTREE"
  echo "Instance ID     : $INSTANCE_ID"
  echo "Config Dir      : $CONFIG_DIR"
  echo "Workspaces Dir  : $WORKSPACES_DIR"
  echo "App Name        : $APP_NAME"
  echo "Deep Link       : ${DEEPLINK_SCHEME}://"
  echo "PID File        : $PID_FILE"
  echo "Log File        : $LOG_FILE"
  if is_running; then
    local pid
    pid="$(cat "$PID_FILE")"
    echo "Running         : yes (PID $pid)"
  else
    echo "Running         : no"
  fi
}

case "$ACTION" in
  build-and-launch)
    if [[ "$SKIP_BUILD" -eq 0 ]]; then
      build_app
    fi
    launch_app
    print_status
    ;;
  build)
    build_app
    print_status
    ;;
  launch)
    launch_app
    print_status
    ;;
  stop)
    stop_instance
    print_status
    ;;
  status)
    print_status
    ;;
  *)
    echo "Unsupported action: $ACTION" >&2
    usage
    exit 1
    ;;
esac
