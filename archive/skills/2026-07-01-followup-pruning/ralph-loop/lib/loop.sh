#!/bin/bash
# loop.sh: Core loop logic for ralph-loop
# Contains: validation, story selection, agent execution, and build orchestration

# Configuration
AGENT_TIMEOUT="${AGENT_TIMEOUT:-600}"  # 10 minutes default

# Validate PRD file exists and is readable
validate_prd() {
  local prd="$1"

  if [[ ! -f "$prd" ]]; then
    echo "Error: PRD file not found: $prd" >&2
    echo "Run 'ralph init' and create your PRD first." >&2
    return 1
  fi

  if [[ ! -r "$prd" ]]; then
    echo "Error: PRD file not readable: $prd" >&2
    return 1
  fi

  return 0
}

# Select next unchecked story from PRD
# Returns: "ID|TITLE|LINE_NUM" or empty if none found
select_story() {
  local prd="$1"

  # Use command substitution to avoid subshell variable loss
  local match=$(grep -n "^### \[ \] US-" "$prd" | head -1)
  [[ -z "$match" ]] && return 1

  local line="${match%%:*}"
  local rest="${match#*:}"
  local id=$(echo "$rest" | grep -o 'US-[0-9]\+')
  local title=$(echo "$rest" | sed 's/^### \[ \] US-[0-9]*: //')

  echo "$id|$title|$line"
}

# Extract story block from PRD (from story header to next ### or EOF)
extract_block() {
  local prd="$1" line_num="$2"

  # Get content from story line to next ### header or EOF
  sed -n "${line_num},\$p" "$prd" | awk '
    NR == 1 { print; next }
    /^### / { exit }
    { print }
  '
}

# Render prompt template with variables
render_prompt() {
  local id="$1" title="$2" prd="$3"
  local template="$SCRIPT_DIR/prompts/build.md"
  local block_file="/tmp/ralph-block-$$.md"

  # Extract block to temp file to avoid awk newline issues
  extract_block "$prd" "$(select_story "$prd" | cut -d'|' -f3)" > "$block_file"

  # Replace simple placeholders with sed
  sed -e "s|{{STORY_ID}}|$id|g" \
      -e "s|{{STORY_TITLE}}|$title|g" \
      -e "s|{{PRD_PATH}}|$prd|g" \
      "$template" | while IFS= read -r line; do
    if [[ "$line" == *"{{STORY_BLOCK}}"* ]]; then
      cat "$block_file"
    else
      echo "$line"
    fi
  done

  rm -f "$block_file"
}

# Mark story as complete in PRD
mark_complete() {
  local prd="$1" id="$2"

  # Use .bak suffix for macOS/Linux compatibility, then remove backup
  sed -i.bak "s/^### \[ \] $id:/### [x] $id:/" "$prd"
  rm -f "${prd}.bak"
}

# Run Claude agent with timeout
run_agent() {
  local prompt_file="$1"

  # Timeout with graceful shutdown (SIGTERM, then SIGKILL after 30s)
  if command -v timeout &>/dev/null; then
    timeout --signal=TERM --kill-after=30 "$AGENT_TIMEOUT" \
      claude -p --dangerously-skip-permissions ${MODEL:+--model "$MODEL"} < "$prompt_file"
  else
    # macOS fallback (no timeout command by default)
    claude -p --dangerously-skip-permissions ${MODEL:+--model "$MODEL"} < "$prompt_file"
  fi

  local exit_code=$?
  if [[ $exit_code -eq 124 ]]; then
    echo "Error: Agent timed out after ${AGENT_TIMEOUT}s" >&2
  fi
  return $exit_code
}

# Verify agent created a commit
verify_commit() {
  local story_id="$1"
  local head_before="$2"
  local head_after=$(git rev-parse HEAD 2>/dev/null || echo "")

  if [[ -z "$head_after" ]]; then
    echo "Warning: Not a git repository, skipping commit verification" >&2
    return 0
  fi

  if [[ "$head_before" == "$head_after" ]]; then
    # No commit created - check for uncommitted changes
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
      echo "Warning: Agent didn't commit. Creating fallback commit..." >&2
      git add -A
      git commit -m "feat($story_id): auto-commit by ralph-loop"
      return 0
    else
      echo "Error: No changes made for $story_id" >&2
      return 1
    fi
  fi

  return 0
}

# Print build summary
print_summary() {
  local completed="$1" total="$2" start_time="$3"
  local duration=$(( $(date +%s) - start_time ))
  local minutes=$((duration / 60)) seconds=$((duration % 60))

  echo ""
  echo "═══════════════════════════════════════════════"
  if [[ $completed -gt 0 ]]; then
    echo "✓ Build Complete"
  else
    echo "⚠ Build Failed"
  fi
  echo "  Stories: $completed/$total"
  echo "  Duration: ${minutes}m ${seconds}s"
  echo "═══════════════════════════════════════════════"
}

# Main build function
run_build() {
  local iterations="${1:-5}"
  local prd_path="${RALPH_DIR}/prd.md"

  # Parse --prd=N flag
  for arg in "$@"; do
    case "$arg" in
      --prd=*) prd_path="${RALPH_DIR}/PRD-${arg#--prd=}/prd.md" ;;
      [0-9]*) iterations="$arg" ;;
    esac
  done

  # Validate PRD exists
  validate_prd "$prd_path" || exit 1

  local completed=0
  local start_time=$(date +%s)

  echo "Starting build: $iterations iterations"
  echo "PRD: $prd_path"
  echo ""

  for i in $(seq 1 "$iterations"); do
    echo "=== Iteration $i/$iterations ==="

    # Select next story
    local story_info=$(select_story "$prd_path")
    if [[ -z "$story_info" ]]; then
      echo "All stories complete!"
      break
    fi

    IFS='|' read -r id title line_num <<< "$story_info"
    echo "Working on: $id - $title"

    # Capture git state before agent
    local head_before=$(git rev-parse HEAD 2>/dev/null || echo "none")

    # Render and run agent
    local prompt_file="/tmp/ralph-prompt-$$.md"
    render_prompt "$id" "$title" "$prd_path" > "$prompt_file"

    if run_agent "$prompt_file"; then
      # Verify commit was created
      if verify_commit "$id" "$head_before"; then
        mark_complete "$prd_path" "$id"
        completed=$((completed + 1))
        echo "✓ Completed: $id"
      else
        echo "✗ Failed: $id (no changes)"
      fi
    else
      echo "✗ Failed: $id (agent error)"
    fi

    rm -f "$prompt_file"
    echo ""
  done

  print_summary "$completed" "$iterations" "$start_time"
}

# Planning function
run_plan() {
  local prd_path="${RALPH_DIR}/prd.md"

  # Parse --prd=N flag
  for arg in "$@"; do
    case "$arg" in
      --prd=*) prd_path="${RALPH_DIR}/PRD-${arg#--prd=}/prd.md" ;;
    esac
  done

  validate_prd "$prd_path" || exit 1

  local template="$SCRIPT_DIR/prompts/plan.md"

  # Render plan prompt (use while loop to handle multi-line content)
  sed -e "s|{{PRD_PATH}}|$prd_path|g" "$template" | while IFS= read -r line; do
    if [[ "$line" == *"{{PRD_CONTENT}}"* ]]; then
      cat "$prd_path"
    else
      echo "$line"
    fi
  done | claude -p --dangerously-skip-permissions ${MODEL:+--model "$MODEL"}
}
