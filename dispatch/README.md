# Dispatch Skill

Coordinate complex features using Claude Code's Task system and parallel subagent execution.

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- [Bun](https://bun.sh) runtime

## Installation

### Option 1: From tarball

```bash
# Extract
tar -xzf dispatch-skill.tar.gz

# Install
cd dispatch
./install.sh
```

### Option 2: Manual

```bash
# Copy to skills directory
mkdir -p ~/.claude/skills
cp -r dispatch ~/.claude/skills/
```

## Usage

The skill is automatically available in Claude Code as `/dispatch`.

### Install the `cc` Command (Recommended)

The easiest way to use dispatch is to install the `cc` wrapper:

```bash
~/.claude/skills/dispatch/scripts/install-cc.sh
```

Now use `cc` instead of `claude` - task coordination is automatic:

```bash
cc                      # Resume last session
cc my-feature           # Use specific task list
cc --new big-refactor   # Force new task list
cc --list               # Show all task lists
```

### Quick Example

```bash
# Start Claude with coordination (automatic with cc!)
cc feature-auth

# Then ask Claude Code to coordinate a complex feature
/dispatch Help me implement user authentication with OAuth, session management, and protected routes
```

### Alternative: Without Installing `cc`

If you prefer not to install the wrapper:

```bash
SKILL=~/.claude/skills/dispatch

# Use start-session.sh
$SKILL/scripts/start-session.sh my-feature

# Or set env var directly
CLAUDE_CODE_TASK_LIST_ID=my-feature claude
```

### Checking Coordination Status

```bash
# Inside Claude, check if coordination is enabled
bun run ~/.claude/skills/dispatch/scripts/init-session.ts --check
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
├── install.sh            # Installer script
├── references/           # Reference documentation
│   ├── dependency-patterns.md
│   ├── example-oauth.md
│   ├── failure-recovery.md
│   ├── task-tools-api.md
│   └── task-architecture.md  # How task system works
└── scripts/              # Utility scripts
    ├── cc                    # Claude wrapper (install to PATH)
    ├── install-cc.sh         # Install cc to /usr/local/bin
    ├── start-session.sh      # Start Claude with coordination
    ├── init-session.ts       # Generate startup command / check status
    ├── migrate-session.ts    # Recovery: migrate current session
    ├── sync-tasks.ts         # Recovery: merge multiple lists
    ├── spawn-agent.ts        # Generate Task() calls
    ├── task-dashboard.ts     # Visual task status
    ├── validate-dependency-graph.ts
    ├── detect-file-conflicts.ts
    ├── detect-stale-tasks.ts
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
