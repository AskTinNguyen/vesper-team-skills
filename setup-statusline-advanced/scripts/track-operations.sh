#!/bin/bash
# Track file operations for statusline display

# Read the hook input (contains tool name and parameters)
input=$(cat)

# Extract tool name, file path, session ID, and cwd from hook JSON
tool=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.notebook_path // empty' 2>/dev/null)
session_id=$(echo "$input" | jq -r '.session_id // empty' 2>/dev/null)
cwd=$(echo "$input" | jq -r '.cwd // empty' 2>/dev/null)

# Skip if no valid tool
[[ -z "$tool" ]] && exit 0

# For Grep/Glob we don't require a file path
if [[ "$tool" != "Grep" && "$tool" != "Glob" ]]; then
  [[ -z "$file_path" ]] && exit 0
fi

# Get session file keyed by session_id from hook input
[[ -z "$session_id" ]] && exit 0
session_file="$HOME/.claude/session-tracking/session-${session_id}.json"

# Initialize session file if it doesn't exist
if [ ! -f "$session_file" ]; then
  echo '{"read":0,"write":0,"edit":0,"grep":0,"glob":0,"dirs":{}}' > "$session_file"
fi

# Get the directory of the file (relative to cwd)
dir="root"
if [[ -n "$file_path" ]]; then
  file_dir=$(dirname "$file_path")
  # Make path relative to cwd if it's an absolute path under cwd
  if [[ -n "$cwd" && "$file_dir" == "$cwd"* ]]; then
    rel_dir="${file_dir#"$cwd"}"
    rel_dir="${rel_dir#/}"
    dir=$(echo "$rel_dir" | cut -d/ -f1)
  elif [[ "$file_dir" == /* ]]; then
    # Absolute path outside cwd — use first meaningful component
    dir=$(echo "$file_dir" | cut -d/ -f2)
  else
    # Already relative
    dir=$(echo "$file_dir" | cut -d/ -f1)
  fi
  [[ -z "$dir" || "$dir" == "." ]] && dir="root"
fi

# Update counters
case "$tool" in
  Read)
    jq ".read += 1 | .dirs[\"$dir\"] += 1" "$session_file" > "${session_file}.tmp" && mv "${session_file}.tmp" "$session_file"
    ;;
  Write)
    jq ".write += 1 | .dirs[\"$dir\"] += 1" "$session_file" > "${session_file}.tmp" && mv "${session_file}.tmp" "$session_file"
    ;;
  Edit|NotebookEdit)
    jq ".edit += 1 | .dirs[\"$dir\"] += 1" "$session_file" > "${session_file}.tmp" && mv "${session_file}.tmp" "$session_file"
    ;;
  Grep)
    jq ".grep += 1" "$session_file" > "${session_file}.tmp" && mv "${session_file}.tmp" "$session_file"
    ;;
  Glob)
    jq ".glob += 1" "$session_file" > "${session_file}.tmp" && mv "${session_file}.tmp" "$session_file"
    ;;
esac

exit 0
