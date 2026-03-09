#!/usr/bin/env bash
set -euo pipefail

TASKS_ROOT="$HOME/.claude/tasks"
CURRENT_LIST_FILE="$TASKS_ROOT/.current-list-id"
ARCHIVE_ROOT="$HOME/.claude/tasks-archive"

usage() {
  cat <<'EOF'
Usage: tasklist_env.sh <command> [args]

Commands:
  status              Show current task list environment
  list                List all available environments with task counts
  switch <env-name>   Switch to a different environment
  tasks [env-name]    Show tasks in current (or specified) environment
EOF
}

get_current_env() {
  if [[ -f "$CURRENT_LIST_FILE" ]]; then
    cat "$CURRENT_LIST_FILE"
  else
    echo ""
  fi
}

count_tasks() {
  local dir="$1"
  local status_filter="${2:-}"
  local count=0

  for f in "$dir"/*.json; do
    [[ -f "$f" ]] || continue
    if [[ -z "$status_filter" ]]; then
      count=$((count + 1))
    else
      if grep -q "\"status\": *\"$status_filter\"" "$f" 2>/dev/null; then
        count=$((count + 1))
      fi
    fi
  done
  echo "$count"
}

cmd_status() {
  local file_env
  file_env=$(get_current_env)
  local shell_env="${CLAUDE_TASK_LIST:-}"

  echo "=== Task List Environment Status ==="
  echo ""

  if [[ -n "$file_env" ]]; then
    echo "File (.current-list-id): $file_env"
  else
    echo "File (.current-list-id): (not set)"
  fi

  if [[ -n "$shell_env" ]]; then
    echo "Env (CLAUDE_TASK_LIST):  $shell_env"
  else
    echo "Env (CLAUDE_TASK_LIST):  (not set)"
  fi

  # Check for discrepancy
  if [[ -n "$file_env" && -n "$shell_env" && "$file_env" != "$shell_env" ]]; then
    echo ""
    echo "WARNING: Discrepancy detected!"
    echo "  File says '$file_env' but env var says '$shell_env'"
    echo "  Run 'tasklist_env.sh switch <name>' to align them."
  fi

  # Show task summary for active env
  local active_env="${file_env:-$shell_env}"
  if [[ -n "$active_env" ]]; then
    local env_dir="$TASKS_ROOT/$active_env"
    if [[ -d "$env_dir" ]]; then
      echo ""
      echo "--- Tasks in '$active_env' ---"
      local total pending in_progress completed
      total=$(count_tasks "$env_dir")
      pending=$(count_tasks "$env_dir" "pending")
      in_progress=$(count_tasks "$env_dir" "in_progress")
      completed=$(count_tasks "$env_dir" "completed")
      echo "  Total: $total | Pending: $pending | In Progress: $in_progress | Completed: $completed"
    else
      echo ""
      echo "WARNING: Environment directory '$env_dir' does not exist."
    fi
  else
    echo ""
    echo "No active environment set."
  fi
}

cmd_list() {
  echo "=== Available Task List Environments ==="
  echo ""

  local current_env
  current_env=$(get_current_env)

  local has_envs=false
  for dir in "$TASKS_ROOT"/*/; do
    [[ -d "$dir" ]] || continue
    has_envs=true
    local name
    name=$(basename "$dir")
    local total pending in_progress completed
    total=$(count_tasks "$dir")
    pending=$(count_tasks "$dir" "pending")
    in_progress=$(count_tasks "$dir" "in_progress")
    completed=$(count_tasks "$dir" "completed")

    local marker="  "
    if [[ "$name" == "$current_env" ]]; then
      marker="* "
    fi

    printf "%s%-40s  tasks: %3d (P:%d IP:%d C:%d)\n" "$marker" "$name" "$total" "$pending" "$in_progress" "$completed"
  done

  if [[ "$has_envs" == false ]]; then
    echo "(no environments found)"
  fi

  # Show archived environments
  if [[ -d "$ARCHIVE_ROOT" ]]; then
    local has_archive=false
    for dir in "$ARCHIVE_ROOT"/*/; do
      [[ -d "$dir" ]] || continue
      if [[ "$has_archive" == false ]]; then
        echo ""
        echo "--- Archived ---"
        has_archive=true
      fi
      local name
      name=$(basename "$dir")
      local total
      total=$(count_tasks "$dir")
      printf "  %-40s  tasks: %3d (archived)\n" "$name" "$total"
    done
  fi
}

cmd_switch() {
  local target="${1:-}"
  if [[ -z "$target" ]]; then
    echo "Error: Please specify an environment name."
    echo "Usage: tasklist_env.sh switch <env-name>"
    exit 1
  fi

  local target_dir="$TASKS_ROOT/$target"
  if [[ ! -d "$target_dir" ]]; then
    echo "Error: Environment '$target' does not exist at $target_dir"
    echo "Available environments:"
    for dir in "$TASKS_ROOT"/*/; do
      [[ -d "$dir" ]] || continue
      echo "  $(basename "$dir")"
    done
    exit 1
  fi

  echo "$target" > "$CURRENT_LIST_FILE"
  echo "Switched to environment: $target"

  # Show summary
  local total pending in_progress completed
  total=$(count_tasks "$target_dir")
  pending=$(count_tasks "$target_dir" "pending")
  in_progress=$(count_tasks "$target_dir" "in_progress")
  completed=$(count_tasks "$target_dir" "completed")
  echo "  Tasks: $total (Pending: $pending | In Progress: $in_progress | Completed: $completed)"

  if [[ -n "${CLAUDE_TASK_LIST:-}" && "$CLAUDE_TASK_LIST" != "$target" ]]; then
    echo ""
    echo "Note: CLAUDE_TASK_LIST env var is still set to '$CLAUDE_TASK_LIST'."
    echo "  export CLAUDE_TASK_LIST='$target'"
  fi
}

cmd_tasks() {
  local env_name="${1:-}"
  if [[ -z "$env_name" ]]; then
    env_name=$(get_current_env)
  fi

  if [[ -z "$env_name" ]]; then
    echo "Error: No environment specified and no current environment set."
    echo "Usage: tasklist_env.sh tasks [env-name]"
    exit 1
  fi

  local env_dir="$TASKS_ROOT/$env_name"
  if [[ ! -d "$env_dir" ]]; then
    echo "Error: Environment '$env_name' does not exist."
    exit 1
  fi

  echo "=== Tasks in '$env_name' ==="
  echo ""

  local has_tasks=false
  for f in "$env_dir"/*.json; do
    [[ -f "$f" ]] || continue
    has_tasks=true

    local id subject status blocked_by
    id=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('id','?'))" "$f" 2>/dev/null || echo "?")
    subject=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('subject','(no subject)'))" "$f" 2>/dev/null || echo "(parse error)")
    status=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('status','unknown'))" "$f" 2>/dev/null || echo "unknown")
    blocked_by=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); b=d.get('blockedBy',[]); print(','.join(b) if b else '')" "$f" 2>/dev/null || echo "")

    local status_icon
    case "$status" in
      pending)     status_icon="[ ]" ;;
      in_progress) status_icon="[~]" ;;
      completed)   status_icon="[x]" ;;
      *)           status_icon="[?]" ;;
    esac

    local blocked_str=""
    if [[ -n "$blocked_by" ]]; then
      blocked_str="  (blocked by: $blocked_by)"
    fi

    printf "  %s #%-4s %s%s\n" "$status_icon" "$id" "$subject" "$blocked_str"
  done

  if [[ "$has_tasks" == false ]]; then
    echo "  (no tasks)"
  fi
}

# Main dispatch
command="${1:-}"
shift || true

case "$command" in
  status)  cmd_status ;;
  list)    cmd_list ;;
  switch)  cmd_switch "$@" ;;
  tasks)   cmd_tasks "$@" ;;
  -h|--help|help|"")  usage ;;
  *)
    echo "Unknown command: $command"
    usage
    exit 1
    ;;
esac
