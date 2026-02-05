# Jeffrey Emanuel's Tool Ecosystem

*Complete catalog of the 22+ tools in the Agent Flywheel*

---

## Core Orchestration Tools

### NTM (Named Tmux Manager)
**Repo:** github.com/Dicklesworthstone/ntm | ⭐ 129
**Purpose:** Fast CLI for creating, switching, and organizing named tmux sessions

```bash
ntm new backend-agent    # Create named session
ntm list                 # List all sessions
ntm switch frontend      # Switch to session
```

### WezTerm Automata
**Repo:** github.com/Dicklesworthstone/wezterm_automata | ⭐ 16
**Purpose:** Terminal hypervisor for AI agent swarms. Deterministic automation, pattern detection, and workflow management.

### MCP Agent Mail
**Repo:** github.com/Dicklesworthstone/mcp_agent_mail | ⭐ 1,629
**Purpose:** "Gmail for your coding agents" — async coordination via MCP tools

Features:
- Memorable agent identities (e.g., "GreenCastle")
- Inbox/outbox with searchable message history
- Advisory file reservations (leases) to avoid conflicts
- Git-backed for human-auditable artifacts
- SQLite for indexing and queries

```bash
# One-line install
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/scripts/install.sh?$(date +%s)" | bash -s -- --yes

# Start server
am  # alias created during install
```

### MCP Agent Mail Rust
**Repo:** github.com/Dicklesworthstone/mcp_agent_mail_rust | ⭐ 3
**Purpose:** High-performance Rust port of Agent Mail

---

## Task Management Tools

### Beads Viewer (bv)
**Repo:** github.com/Dicklesworthstone/beads_viewer | ⭐ 1,194
**Purpose:** TUI for Steve Yegge's beads task system with graph analytics

Robot flags for AI agents:
```bash
bv --robot-triage        # Full triage with recommendations
bv --robot-next          # Single top pick
bv --robot-plan          # Parallel execution tracks
bv --robot-insights      # PageRank, betweenness, cycles
bv --robot-priority      # Priority recommendations with reasoning
bv --robot-diff --diff-since "1 hour ago"  # What changed
```

### Beads Rust (br/bd)
**Repo:** github.com/Dicklesworthstone/beads_rust | ⭐ 472
**Purpose:** Fast Rust port of Steve Yegge's beads CLI

```bash
bd list                  # List all beads
bd ready                 # Show tasks ready to work on
bd done TASK-ID          # Mark task complete
bd add "Title" --deps X  # Add new bead with dependencies
```

---

## Code Quality & Safety Tools

### Ultimate Bug Scanner (UBS)
**Repo:** github.com/Dicklesworthstone/ultimate_bug_scanner | ⭐ 147
**Purpose:** Industrial-grade static analysis for all popular programming languages. Catches 1000+ bug patterns.

### Destructive Command Guard (DCG)
**Repo:** github.com/Dicklesworthstone/destructive_command_guard | ⭐ 336
**Purpose:** Claude Code hook that blocks destructive git and filesystem commands

Blocks:
- `git checkout -- <files>` (discards uncommitted changes)
- `git reset --hard`
- `git clean -f`
- `git push --force`
- `rm -rf` (non-temp paths)

### SLB (Safety/Limits/Boundaries)
**Purpose:** Safety guardrails for agent operations

### ACIP (Advanced Cognitive Inoculation Prompt)
**Repo:** github.com/Dicklesworthstone/acip | ⭐ 213
**Purpose:** Framework to protect LLMs against prompt injection attacks

Key features:
- Instruction hierarchy (system > developer > user)
- Two-pass response discipline
- Graduated response posture
- Audit mode for monitoring

---

## Search & Memory Tools

### CASS (Coding Agent Session Search)
**Repo:** github.com/Dicklesworthstone/coding_agent_session_search | ⭐ 439
**Purpose:** Search through coding agent session history

### CASS Memory System
**Repo:** github.com/Dicklesworthstone/cass_memory_system | ⭐ 208
**Purpose:** Persistent memory for coding agents

### XF (X/Twitter Fast Search)
**Repo:** github.com/Dicklesworthstone/xf | ⭐ 65
**Purpose:** Ultra-fast CLI for searching Twitter/X data archives. Sub-millisecond queries via Tantivy + SQLite.

---

## Authentication & Account Management

### CAAM (Coding Agent Account Manager)
**Repo:** github.com/Dicklesworthstone/coding_agent_account_manager | ⭐ 43
**Purpose:** Instant auth switching for AI coding tool subscriptions (Claude Max, GPT Pro, Gemini)

Why needed: When hitting rate limits, quickly swap to another account without losing momentum.

---

## Development Utilities

### RU (Repo Sync)
**Purpose:** Repository synchronization utilities

### Your Source to Prompt
**Repo:** github.com/Dicklesworthstone/your-source-to-prompt.html | ⭐ 731
**Purpose:** Turn code projects into LLM prompts, locally

### Markdown Web Browser
**Repo:** github.com/Dicklesworthstone/markdown_web_browser | ⭐ 117
**Purpose:** Web browser for LLMs that turns every page into rich markdown

### Process Triage
**Repo:** github.com/Dicklesworthstone/process_triage | ⭐ 13
**Purpose:** Interactive zombie/abandoned process killer

### Remote Compilation Helper
**Repo:** github.com/Dicklesworthstone/remote_compilation_helper | ⭐ 20
**Purpose:** Transparent compilation offloading for AI coding agents

---

## Claude Code Specific Tools

### Post Compact Reminder
**Repo:** github.com/Dicklesworthstone/post_compact_reminder | ⭐ 14
**Purpose:** SessionStart hook that reminds Claude to re-read AGENTS.md after context compaction

### Meta Skill
**Repo:** github.com/Dicklesworthstone/meta_skill | ⭐ 104
**Purpose:** CLI for managing Claude Code skills: indexing, building, bundling, and sharing

### Claude Code Agent Farm
**Repo:** github.com/Dicklesworthstone/claude_code_agent_farm | ⭐ 640
**Purpose:** Infrastructure for running multiple Claude Code agents

---

## TUI & Rendering

### FrankenTUI
**Repo:** github.com/Dicklesworthstone/frankentui | ⭐ 67
**Purpose:** High-performance terminal UI kernel for agent harnesses

Key innovations:
- Inline-first (preserves scrollback)
- Bayesian algorithms for diff strategy selection
- BOCPD for resize detection
- "Alien artifact" quality engineering

### Charmed Rust
**Repo:** github.com/Dicklesworthstone/charmed_rust | ⭐ 8
**Purpose:** Rust port of Go's Charm libraries (bubbletea, lipgloss)

### OpenTUI Rust
**Repo:** github.com/Dicklesworthstone/opentui_rust | ⭐ 9
**Purpose:** Terminal UI library with alpha blending, scissoring, double-buffered rendering

---

## Misc & Experimental

### LLM Aided OCR
**Repo:** github.com/Dicklesworthstone/llm_aided_ocr | ⭐ 2,900
**Purpose:** Enhance Tesseract OCR output using LLM corrections

### Fast Vector Similarity
**Repo:** github.com/Dicklesworthstone/fast_vector_similarity | ⭐ 424
**Purpose:** Efficient computation of various similarity measures between vectors (Rust)

### Automated Plan Reviser Pro
**Repo:** github.com/Dicklesworthstone/automated_plan_reviser_pro | ⭐ 37
**Purpose:** Iteratively refine plans with AI

### Pi Agent Rust
**Repo:** github.com/Dicklesworthstone/pi_agent_rust | ⭐ 15
**Purpose:** Rust port of Mario Zechner's Pi Agent

### Flywheel Connectors
**Repo:** github.com/Dicklesworthstone/flywheel_connectors | ⭐ 26
**Purpose:** Secure, modular connectors for AI agent integration with external services

---

## Websites & Resources

### Agent Flywheel Setup (ACFS)
**Repo:** github.com/Dicklesworthstone/agentic_coding_flywheel_setup | ⭐ 987
**Website:** agent-flywheel.com
**Purpose:** Complete system for bootstrapping agentic coding environments

One-liner install:
```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/agentic_coding_flywheel_setup/main/install.sh?$(date +%s)" | bash -s -- --yes --mode vibe
```

### Jeffrey's Prompts
**Repo:** github.com/Dicklesworthstone/jeffreysprompts.com | ⭐ 60
**Purpose:** Curated collection of battle-tested prompts for agentic coding

### Misc Coding Agent Tips
**Repo:** github.com/Dicklesworthstone/misc_coding_agent_tips_and_scripts | ⭐ 190
**Purpose:** Practical guides for AI coding agents, terminal customization, and tooling
