# Dispatch Skill

Coordinate complex features using Claude Code's Task system and parallel subagent execution.

## Requirements

- [Claude Code](https://claude.ai/code) CLI or [Vesper](https://vesper.atherslabs.com)
- [Bun](https://bun.sh) runtime

## Installation

### Option 1: Team Skills (Recommended for Teams)

If using Vesper with Team Skills:

1. Open Vesper Settings → Workspace → Team Skills
2. Enter repo URL: `AskTinNguyen/vesper-team-skills` (or your team's repo)
3. Enter GitHub PAT (with `repo` scope for private repos)
4. Click "Save & Sync"
5. Run setup:
   ```bash
   ~/.vesper/team-skills/dispatch/setup.sh
   ```

The skill will appear in Vesper's skills list with a "Team" badge.

### Option 2: Manual Installation

```bash
# Copy to Claude Code skills directory
mkdir -p ~/.claude/skills
cp -r dispatch ~/.claude/skills/

# Run setup
~/.claude/skills/dispatch/setup.sh
```

### Option 3: From Tarball

```bash
# Extract
tar -xzf dispatch-skill.tar.gz

# Install
cd dispatch
./install.sh
./setup.sh
```

## Post-Install Setup

The `setup.sh` script installs:
- **`cc` and `ccd` commands** - Claude wrappers with automatic task coordination
- **Auto-archive hook** - Preserves task history when sessions end

```bash
# Run from your install location:
~/.vesper/team-skills/dispatch/setup.sh   # Team Skills
~/.claude/skills/dispatch/setup.sh        # Manual install
```

## Usage

The skill is automatically available as `/dispatch`.

### Using the `cc` Command

After setup, use `cc` instead of `claude` for automatic task coordination:

```bash
cc                      # Resume last session
cc my-feature           # Use specific task list
cc --new big-refactor   # Force new task list
cc --list               # Show all task lists
cc --dangerous          # Skip permission prompts
```

**Shortcut:** `ccd` = `cc --dangerous`

### Quick Example

```bash
# Start Claude with coordination
cc feature-auth

# Then ask Claude Code to coordinate a complex feature
/dispatch Help me implement user authentication with OAuth, session management, and protected routes
```

### Alternative: Without `cc`

```bash
# Set environment variable manually
CLAUDE_CODE_TASK_LIST_ID=my-feature claude
```

### Checking Coordination Status

```bash
# Inside Claude, check if coordination is enabled
bun run ~/.claude/skills/dispatch/scripts/init-session.ts --check

# Or for Team Skills location
bun run ~/.vesper/team-skills/dispatch/scripts/init-session.ts --check
```

### Recovery: Forgot to Set Env Var?

If you created tasks but forgot to set `CLAUDE_CODE_TASK_LIST_ID`:

```bash
# Migrate current session's tasks to a shared list
bun run ~/.claude/skills/dispatch/scripts/migrate-session.ts my-project

# Or merge multiple orphaned lists
bun run ~/.claude/skills/dispatch/scripts/sync-tasks.ts --list
bun run ~/.claude/skills/dispatch/scripts/sync-tasks.ts --target my-project

# Then restart Claude with the shared list
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

## Contents

```
dispatch/
├── SKILL.md              # Main skill instructions
├── README.md             # This file
├── setup.sh              # One-command setup (cc + hook)
├── install.sh            # Legacy installer
├── hooks/
│   ├── auto-archive.sh   # Stop hook for task archival
│   └── install-hook.sh   # Hook installer
├── references/           # Reference documentation
│   ├── dependency-patterns.md
│   ├── example-oauth.md
│   ├── failure-recovery.md
│   ├── task-tools-api.md
│   └── task-architecture.md
└── scripts/
    ├── cc                # Claude wrapper
    ├── ccd               # cc + dangerous mode
    ├── install-cc.sh     # Install cc to PATH
    ├── start-session.sh  # Start with coordination
    ├── init-session.ts
    ├── migrate-session.ts
    ├── sync-tasks.ts
    ├── spawn-agent.ts
    ├── task-dashboard.ts
    ├── validate-dependency-graph.ts
    ├── detect-file-conflicts.ts
    ├── detect-stale-tasks.ts
    ├── archive-tasks.ts
    ├── list-archives.ts
    ├── get-task-list-id.ts
    ├── pre-spawn-validation.ts
    └── lib/
        └── task-list-resolver.ts
```

## Documentation

See `SKILL.md` for full documentation including:
- How task coordination works
- Starting coordinated sessions
- Decision matrix for when to use dispatch
- Workflow steps
- Script reference
- Error recovery patterns
- Troubleshooting guide
- Anti-patterns to avoid

## Distribution

This skill can be distributed via:

| Method | Location | Best For |
|--------|----------|----------|
| Team Skills | `~/.vesper/team-skills/dispatch/` | Teams using Vesper |
| Manual | `~/.claude/skills/dispatch/` | Individual users |
| Tarball | Download and extract | Offline installation |

Both locations work identically - just run `setup.sh` from the install location.
