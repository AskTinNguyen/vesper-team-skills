# Jeffrey Emanuel's Workflow — Detailed Breakdown

*The exact process from idea to shipped code*

---

## Phase 1: Ideation (15 minutes)

**Goal:** Capture the raw idea before it evaporates

Write a "scrappy email-style blurb" containing:
- The problem you're solving
- Desired UX/experience
- Any must-have stack picks
- Rough scope

**Example blurb:**
```
Subject: Build a terminal UI framework

Problem: Most TUI libraries flicker, corrupt scrollback, and can't handle
streaming logs + stable UI chrome simultaneously. Agent harnesses need both.

Desired UX:
- Inline mode that preserves scrollback
- No flicker during rapid updates
- Works in tmux/screen
- Simple API for agent devs

Stack: Rust (performance critical), crossterm backend, Elm architecture

Scope: ~50k lines, 5 days, full test coverage
```

---

## Phase 2: Planning (1-4 hours)

**Goal:** Transform blurb into a granular, executable plan

### Step 1: Initial Plan Generation

Feed blurb to GPT-5 Pro (or Claude Opus):
```
I want to build [DESCRIPTION FROM BLURB].

Please create a comprehensive technical plan that includes:
1. Executive summary
2. Architecture overview with diagrams (mermaid)
3. Module-by-module breakdown with responsibilities
4. Data models and API contracts
5. Testing strategy
6. Performance budgets
7. Potential risks and mitigations
8. Non-goals (what we're explicitly NOT building)
9. Open questions to resolve

Be thorough. This plan will be converted into atomic tasks for AI agents.
The plan should be 5,000-30,000 words depending on scope.
```

### Step 2: Iterate on the Plan

**Do 4-5 revision rounds:**

Round 1: "This is good. Now add more detail to the [X] section. What are the edge cases?"

Round 2: "The architecture looks right. But how do we handle [specific scenario]?"

Round 3: "Add explicit acceptance criteria for each module."

Round 4: "What's missing? What would a senior engineer ask about?"

Round 5: "Final polish. Make sure every module has clear inputs, outputs, and dependencies."

**Jeffrey's rule:** "Iterate on the plan while it's still cheap to change."

### Step 3: Save the Plan

Save as: `PLAN_TO_CREATE_[PROJECT]__OPUS.md`

The plan becomes:
- Source of truth for the project
- Input for bead generation
- Reference for agents during execution

---

## Phase 3: Bead Generation (30-60 minutes)

**Goal:** Convert plan into atomic, dependency-aware tasks

### Prompt for Bead Generation

```
Here is a technical plan for [PROJECT]:

[PASTE FULL PLAN]

Convert this into atomic tasks ("beads") with the following structure:

For each task, provide:
- id: Unique identifier (MODULE-XXX format)
- type: "epic" | "task" | "bug" | "chore"
- status: "open"
- priority: "critical" | "high" | "medium" | "low"
- title: Clear, action-oriented title
- desc: Detailed description of what to do
- deps: Array of task IDs this depends on (empty if none)
- labels: Array of categories (e.g., ["core", "rendering", "tests"])
- acceptance: Array of criteria that define "done"

Rules:
1. Each task should be completable in 30min-2hrs
2. If a task is bigger, split it
3. Be explicit about dependencies
4. Include test tasks for each module
5. Include documentation tasks

Output as JSONL (one JSON object per line).
```

### Example Output

```jsonl
{"id":"CORE-001","type":"task","status":"open","priority":"critical","title":"Set up Cargo workspace structure","desc":"Create the multi-crate workspace with ftui-core, ftui-render, ftui-runtime, etc.","deps":[],"labels":["setup","core"],"acceptance":["Workspace compiles","All crates have basic lib.rs","CI runs successfully"]}
{"id":"CORE-002","type":"task","status":"open","priority":"high","title":"Implement Cell struct","desc":"Create the Cell type representing a single terminal cell with grapheme, fg, bg, and attributes","deps":["CORE-001"],"labels":["core","rendering"],"acceptance":["Cell struct defined","16-byte size for cache alignment","Unit tests pass"]}
{"id":"CORE-003","type":"task","status":"open","priority":"high","title":"Implement Buffer struct","desc":"Create 2D grid of Cells with efficient indexing and dirty tracking","deps":["CORE-002"],"labels":["core","rendering"],"acceptance":["Buffer creation works","Cell access is O(1)","Dirty region tracking works"]}
```

### Decomposition Guidelines

**Good bead:**
- "Implement JWT token generation with HS256"
- "Add unit tests for user authentication"
- "Create database migration for users table"

**Bad bead (too big):**
- "Build the authentication system" → Split into 10+ beads
- "Implement the API" → Split by endpoint
- "Add tests" → Split by module

**Dependency rules:**
- If A uses output of B → A depends on B
- If A and B can run in parallel → No dependency
- Circular deps are bugs in your decomposition

---

## Phase 4: Execution

**Goal:** Work through the task graph systematically

### The Core Loop

```bash
# 1. Get the top task
bv --robot-triage | jq '.triage.quick_ref.top_picks[0]'

# 2. Hand to agent (or work yourself)
# "Implement CORE-002: Cell struct. See acceptance criteria."

# 3. Complete the task
# ... agent works ...

# 4. Mark done
bd done CORE-002

# 5. Commit
git commit -am "CORE-002: Implement Cell struct"

# 6. Check what's unblocked
bv --robot-triage | jq '.triage.quick_ref'

# 7. Repeat
```

### Multi-Agent Execution

When running multiple agents:

```bash
# Terminal 1: Agent A
bv --robot-triage | jq '.triage.recommendations[0]'
# Works on CORE-002

# Terminal 2: Agent B
bv --robot-triage | jq '.triage.recommendations[1]'
# Works on STYLE-001 (no conflict with CORE-002)

# Terminal 3: Agent C
bv --robot-plan  # Shows parallel tracks
# Picks from a different track
```

**Conflict prevention:**
- `bv --robot-plan` shows independent tracks
- Agent Mail file reservations prevent overlapping edits
- Each agent works on different parts of the codebase

### Session Management

**Starting a session:**
```bash
# Register identity
mcp_agent_mail register_agent --name "BlueKnight" --project /path/to/repo

# Reserve files
mcp_agent_mail file_reservation_paths --paths "src/core/**" --ttl 3600 --exclusive

# Announce start
mcp_agent_mail send_message --thread "CORE-002" --subject "[CORE-002] Starting Cell implementation"
```

**Ending a session ("Landing the plane"):**
```bash
# Commit all changes
git add -A && git commit -m "CORE-002: Implement Cell struct"

# Push
git push

# Update task status
bd done CORE-002

# Release reservations
mcp_agent_mail release_file_reservations --paths "src/core/**"

# Announce completion
mcp_agent_mail send_message --thread "CORE-002" --subject "[CORE-002] Complete" --body "Implemented Cell struct with 16-byte alignment. Tests passing."
```

---

## Phase 5: Review & Iteration

### Continuous Review

After each batch of completed beads:
- Run tests: `cargo test`
- Run lints: `cargo clippy`
- Check coverage
- Review diffs

### Adding Discovered Work

When agents discover new tasks during execution:
```bash
bd add "Handle edge case in Cell comparison" --deps CORE-002 --priority medium --labels core,bugfix
```

The new bead enters the graph and will surface when its dependencies are met.

### Handling Blockers

When a task is blocked:
```bash
bd block CORE-005 --reason "Waiting for design decision on color handling"
```

Agent Mail notification:
```bash
mcp_agent_mail send_message --thread "CORE-005" --subject "[CORE-005] BLOCKED" --body "Need human decision on: should we support 24-bit color on all terminals or feature-detect?" --importance high
```

---

## Productivity Multipliers

### Account Swapping

When hitting rate limits:
```bash
caam switch claude-account-2
```

Continue working without waiting for rate limit reset.

### Parallel Worktrees

Each agent can work in its own git worktree:
```bash
git worktree add ../project-agent-1 main
git worktree add ../project-agent-2 main
```

Agents work independently, merge when done.

### The "Machine Tending" Phase

After planning and bead generation (Phases 1-3), execution becomes mechanical:

1. Check `bv --robot-triage`
2. Assign task to available agent
3. Monitor for blockers
4. Swap accounts when rate limited
5. Merge completed work
6. Repeat

Jeffrey: "After this point, it's mostly machine tending and account swapping: totally mechanical and formulaic."

---

## Time Estimates

| Phase | Time | Human Effort |
|-------|------|--------------|
| Ideation | 15 min | High |
| Planning | 1-4 hours | High |
| Bead Generation | 30-60 min | Medium |
| Execution | Hours to days | Low (monitoring) |
| Review | Continuous | Medium |

**Jeffrey's FrankenTUI:**
- Planning: ~4 hours (30,000 word doc)
- Bead Generation: ~1 hour (1,000+ beads)
- Execution: ~5 days (multiple agents)
- Result: 50,000+ lines of sophisticated Rust
