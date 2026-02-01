---
name: setup-statusline-advanced
description: This skill should be used when setting up an advanced Claude Code statusline that displays real-time session metrics including directory, git branch, worktree info, task list environment, file operation counts, and a visual directory heatmap. It applies when users want enhanced visibility into their coding session activity, tracking which areas of the codebase are being touched, or when onboarding team members who need a comprehensive statusline configuration.
---

# Setup Advanced Statusline

## Overview

Configure an advanced statusline for Claude Code that provides rich contextual information about the current session, including real-time tracking of file operations and a visual heatmap of codebase activity.

This skill sets up a comprehensive statusline that displays:
- **Directory context**: Current directory name and git branch
- **Worktree awareness**: Detection and display of git worktree usage
- **Task list environment**: Shows the active TASKLIST_ENV variable
- **Operation metrics**: Real-time counts of file reads, writes, and edits
- **Directory heatmap**: Visual representation of the top 3 most-touched directories

## When to Use

Use this skill when:
- Setting up Claude Code for the first time and wanting comprehensive session visibility
- Onboarding team members who need consistent statusline configuration
- Working on large codebases where tracking activity areas is valuable
- Using git worktrees and needing clear indication of which worktree is active
- Managing multiple task list environments and needing to know which one is active
- Wanting to understand session activity patterns without checking git status repeatedly

## Setup Process

### Step 1: Create Session Tracking Infrastructure

Create the directory for storing session tracking data:

```bash
mkdir -p ~/.claude/session-tracking
```

### Step 2: Install the Tracking Script

Copy the tracking script from `scripts/track-operations.sh` to the session tracking directory:

```bash
cp scripts/track-operations.sh ~/.claude/session-tracking/track-operations.sh
chmod +x ~/.claude/session-tracking/track-operations.sh
```

The tracking script:
- Monitors Read, Write, Edit, NotebookEdit, Grep, and Glob tool usage
- Stores session data in `~/.claude/session-tracking/session-{session_id}.json`
- Tracks operation counts and directory activity
- Runs asynchronously to avoid impacting performance

### Step 3: Configure PostToolUse Hook

Add the tracking hook to `~/.claude/settings.json` in the `hooks.PostToolUse` array:

```json
{
  "matcher": "Read|Write|Edit|NotebookEdit|Grep|Glob",
  "hooks": [
    {
      "type": "command",
      "command": "~/.claude/session-tracking/track-operations.sh",
      "async": true
    }
  ]
}
```

If there are existing PostToolUse hooks, add this as a new array element alongside them. If the PostToolUse section doesn't exist, create it within the hooks object.

### Step 4: Configure the StatusLine

Update or add the `statusLine` configuration in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "input=$(cat); dir=$(echo \"$input\" | jq -r '.workspace.current_dir'); model=$(echo \"$input\" | jq -r '.model.display_name'); remaining=$(echo \"$input\" | jq -r '.context_window.remaining_percentage // empty'); sid=$(echo \"$input\" | jq -r '.session_id // empty'); branch=$(cd \"$dir\" 2>/dev/null && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo ''); worktree=''; if [ -n \"$branch\" ] && [ -f \"$dir/.git\" ]; then worktree=$(cd \"$dir\" && git worktree list | grep \"$(pwd)\" | awk '{print $1}' | xargs basename); fi; tasklist=\"${TASKLIST_ENV:-default}\"; session_file=''; if [ -n \"$sid\" ]; then session_file=\"$HOME/.claude/session-tracking/session-${sid}.json\"; fi; ops=''; heatmap=''; if [ -n \"$session_file\" ] && [ -f \"$session_file\" ]; then r=$(jq -r '.read // 0' \"$session_file\"); w=$(jq -r '.write // 0' \"$session_file\"); e=$(jq -r '.edit // 0' \"$session_file\"); ops=\" | $(printf '\\033[34m')R:$r $(printf '\\033[32m')W:$w $(printf '\\033[35m')E:$e$(printf '\\033[0m')\"; dirs=$(jq -r '.dirs | to_entries | sort_by(-.value) | limit(3; .[]) | \"\\(.key):\\(.value)\"' \"$session_file\" 2>/dev/null); if [ -n \"$dirs\" ]; then heatmap=' |'; while IFS=: read -r d c; do intensity='░'; [ \"$c\" -ge 5 ] && intensity='▒'; [ \"$c\" -ge 10 ] && intensity='▓'; [ \"$c\" -ge 15 ] && intensity='█'; heatmap=\"$heatmap $(printf '\\033[90m')$d:$intensity$(printf '\\033[0m')\"; done <<< \"$dirs\"; fi; fi; context_info=''; [ -n \"$remaining\" ] && context_info=\" | Context: ${remaining}%\"; git_info=''; [ -n \"$branch\" ] && git_info=\" ($(printf '\\033[36m')$branch$(printf '\\033[0m'))\"; worktree_info=''; [ -n \"$worktree\" ] && worktree_info=\" [$(printf '\\033[35m')wt:$worktree$(printf '\\033[0m')]\"; tasklist_info=\" | $(printf '\\033[33m')TL:$tasklist$(printf '\\033[0m')\"; printf \"$(printf '\\033[32m')%s$(printf '\\033[0m')%s%s | %s%s%s%s%s\" \"$(basename \"$dir\")\" \"$git_info\" \"$worktree_info\" \"$model\" \"$context_info\" \"$tasklist_info\" \"$ops\" \"$heatmap\""
  }
}
```

### Step 5: Verify Installation

After updating settings.json, start a new Claude Code session to verify the statusline appears correctly. The statusline should show:

**Initial display (no operations yet):**
```
vesper (main) | Claude 3.5 Sonnet | Context: 100% | TL:default
```

**After some file operations:**
```
vesper (feat/search) [wt:feature] | Claude 3.5 Sonnet | Context: 94% | TL:production | R:5 W:3 E:2 | src:▓ tests:▒ docs:░
```

## StatusLine Components Explained

### Colors
- 🟢 **Green**: Directory name
- 🔵 **Cyan**: Git branch
- 🟣 **Magenta**: Worktree info and edit count
- 🟡 **Yellow**: Task list environment
- 🔵 **Blue**: Read count
- 🟢 **Green**: Write count
- ⚫ **Gray**: Directory heatmap

### Operation Counts
- **R:** (Read): Number of files read in this session
- **W:** (Write): Number of files written in this session
- **E:** (Edit): Number of files edited in this session

### Directory Heatmap Intensity
- **░** (Light): 1-4 operations
- **▒** (Medium-Light): 5-9 operations
- **▓** (Medium-Dark): 10-14 operations
- **█** (Intense): 15+ operations

The heatmap shows the top 3 directories by activity level, making it easy to see which areas of the codebase are being actively worked on.

## Task List Environment Variable

To use different task list environments, set the `TASKLIST_ENV` environment variable before starting Claude Code:

```bash
export TASKLIST_ENV=production
claude-code
```

Or set it in your shell profile (.zshrc, .bashrc) for persistence.

## Session Tracking Data

Session data is stored in `~/.claude/session-tracking/session-{session_id}.json` with the following structure:

```json
{
  "read": 5,
  "write": 3,
  "edit": 2,
  "grep": 1,
  "glob": 2,
  "dirs": {
    "src": 12,
    "tests": 7,
    "docs": 3
  }
}
```

Each Claude Code session creates its own file, keyed by the session ID provided by the hook. Sessions automatically start fresh when you open a new session.

## Troubleshooting

**StatusLine not updating:**
- Verify the tracking script is executable: `ls -la ~/.claude/session-tracking/track-operations.sh`
- Check that jq is installed: `which jq`
- Ensure the PostToolUse hook is properly configured in settings.json

**Session file not created:**
- Check directory permissions: `ls -la ~/.claude/session-tracking/`
- Verify the hook is running (check Claude Code logs)

**Heatmap not showing:**
- Perform some file operations (Read, Write, Edit) to populate the session data
- Check that the session file exists and contains directory data

## Customization

To customize the statusline:

1. **Change colors**: Modify the ANSI color codes in the statusLine command
   - `\033[32m` = green, `\033[36m` = cyan, `\033[35m` = magenta, etc.

2. **Adjust heatmap thresholds**: Change the intensity thresholds in the statusLine command
   - Default: 5, 10, 15 for ▒, ▓, █

3. **Add more metrics**: Extend the tracking script to track additional operations
   - Modify `scripts/track-operations.sh` to track other tool usage

4. **Change display format**: Reorder or modify the printf statement in the statusLine command
