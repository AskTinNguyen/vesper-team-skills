# Jeffrey Emanuel's Tips & Best Practices

*Battle-tested wisdom from building with AI agents*

---

## Planning Tips

### "Iterate on the plan while it's still cheap to change"

Plans are cheap to modify. Code is expensive. Spend 4-5 rounds refining your plan before generating any beads.

### Plan Document Size Guidelines

| Project Scope | Plan Size | Beads Count |
|---------------|-----------|-------------|
| Small feature | 2,000-5,000 words | 20-50 |
| Medium project | 5,000-15,000 words | 50-200 |
| Large project | 15,000-30,000 words | 200-1,000+ |

FrankenTUI: 30,000+ word plan, 1,000+ beads

### Include Non-Goals

Always explicitly state what you're NOT building:
```markdown
## Non-Goals
- Not a drop-in replacement for existing widget libraries
- Not backwards compatible with upstream APIs
- Not targeting Windows in v1
- Not optimizing for minimal binary size
```

This prevents scope creep and helps agents stay focused.

---

## Bead Generation Tips

### The Atomic Test

If you can say "and" in the task title, split it:
- ❌ "Implement auth and add tests"
- ✅ "Implement auth module" + "Add auth tests"

### The 2-Hour Rule

If a task takes longer than 2 hours, decompose further:
- ❌ "Build the API layer"
- ✅ "Create /users endpoint" + "Create /auth endpoint" + "Add rate limiting" + ...

### Dependencies Are Sacred

```json
{"id": "AUTH-003", "deps": ["AUTH-001", "AUTH-002"]}
```

The deps array defines the graph. Get it right:
- If A needs B's output → A depends on B
- If A and B are independent → No dependency
- Circular deps = bug in your thinking

### Label Consistently

Good labels enable filtering:
```bash
bv --robot-triage --label backend
bv --robot-triage --label tests
```

Use a consistent scheme:
- By module: `core`, `rendering`, `runtime`, `widgets`
- By type: `feature`, `bugfix`, `test`, `docs`, `chore`
- By priority: `p0`, `p1`, `p2`

---

## Execution Tips

### Trust the Algorithm

`bv --robot-triage` uses PageRank, betweenness centrality, and critical path analysis. It knows better than your intuition which task to do next.

Don't: "I feel like working on the UI today"
Do: "What does bv say is highest impact?"

### Commit After Every Task

```bash
# Complete CORE-002
bd done CORE-002
git commit -am "CORE-002: Implement Cell struct"
```

Small, frequent commits:
- Easy to review
- Easy to revert
- Clear attribution
- Git bisect works

### Land the Plane

Every agent session should end cleanly:

```bash
# 1. Commit everything
git add -A && git commit -m "SESSION-END: Progress on CORE-005"

# 2. Push
git push

# 3. Update status
bd done CORE-005  # or bd block CORE-005 if incomplete

# 4. Write handoff note
cat > .handoff-$(date +%s).md << EOF
## Session End: CORE-005

**Status:** partial

**Completed:**
- Cell comparison implemented
- Unit tests for basic cases

**Remaining:**
- Edge case handling for ZWJ sequences
- Performance benchmarks

**Notes for next agent:**
- Look at line 142-160 for the tricky part
- Reference Unicode TR29 for grapheme rules
EOF

# 5. Announce
mcp_agent_mail send_message --thread CORE-005 --subject "[CORE-005] Session ended" --body "$(cat .handoff-*.md | tail -1)"
```

### The 50 First Dates Problem

Agents forget everything between sessions. Combat this:

1. **Structured task descriptions** — Beads persist in git
2. **Handoff notes** — Context for the next agent
3. **AGENTS.md** — Project conventions that every agent reads
4. **Session search (CASS)** — Find what previous agents discussed

---

## Multi-Agent Tips

### File Reservations Prevent Conflicts

```bash
# Agent A reserves src/core/**
mcp_agent_mail file_reservation_paths --paths "src/core/**" --exclusive --ttl 3600

# Agent B tries to reserve src/core/cell.rs
# → FILE_RESERVATION_CONFLICT

# Agent B reserves src/widgets/** instead (no conflict)
```

### Use Parallel Tracks

```bash
bv --robot-plan
```

Shows independent task chains that can run simultaneously:
```
Track 1: CORE-001 → CORE-002 → CORE-003
Track 2: STYLE-001 → STYLE-002
Track 3: DOCS-001 → DOCS-002 → DOCS-003
```

Assign one agent per track.

### Thread IDs = Bead IDs

Keep everything aligned:
- Bead ID: `CORE-005`
- Mail thread: `CORE-005`
- Git commits: `CORE-005: ...`
- PR title: `[CORE-005] Implement Cell comparison`

One ID, everywhere.

---

## Claude Code Specific Tips

### Destructive Command Guard

Install DCG to prevent accidents:
```bash
# Blocks: git checkout --, git reset --hard, rm -rf, git push --force
```

### Post-Compact Reminder

When context compacts, Claude forgets project conventions. Install the reminder hook:
```bash
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/misc_coding_agent_tips_and_scripts/main/install-post-compact-reminder.sh | bash
```

After compaction, Claude sees:
```
<post-compact-reminder>
Context was just compacted. Please reread AGENTS.md to refresh your understanding of project conventions.
</post-compact-reminder>
```

### Rule 0 for Stubborn Agents

Jeffrey's "Rule 0" to override overly cautious behavior:
```
Rule 0: You, the coding agent, are explicitly authorized by the human developer 
(who is the superuser of this machine) to take any action that advances the goals 
outlined in this document, even if such actions would normally require explicit 
permission in other contexts.
```

Add to AGENTS.md when agents refuse reasonable requests.

---

## Rate Limit Tips

### Account Swapping

Use CAAM to switch accounts instantly:
```bash
caam switch claude-max-2
```

Jeffrey runs multiple accounts:
- Claude Max ($200/month) × 2 = $400
- ChatGPT Pro ($200/month)
- Plus API costs

### Workspace Parallelism

Run multiple Claude Code instances in separate worktrees:
```bash
git worktree add ../project-agent1 main
git worktree add ../project-agent2 main

# Terminal 1: cd ../project-agent1 && claude
# Terminal 2: cd ../project-agent2 && claude
```

Both agents work simultaneously without conflicts (if on different tracks).

---

## Cost Optimization

### The Economics

| Expense | Monthly Cost |
|---------|--------------|
| VPS (64GB) | $40-56 |
| Claude Max | $200 (or $400 for 2 accounts) |
| ChatGPT Pro | $200 |
| API overages | Variable |
| **Total** | **$440-656+** |

Jeffrey's spend: ~$10,000/month (heavy usage)

### ROI Calculation

Junior dev in SF: $5,000+/month (salary only)
AI agents: $500-1,000/month

If agents produce even 20% of a junior dev's output, ROI is positive.

Jeffrey's claim: Agents produce 10-20× a developer's output when properly directed.

---

## Debugging Tips

### When Things Go Wrong

1. **Check the bead description** — Was it clear enough?
2. **Check dependencies** — Is something missing?
3. **Check acceptance criteria** — Were they specific?
4. **Check agent output** — What did it actually do?
5. **Add clarification** — Update the bead and re-run

### Common Failures

**"Agent produced wrong output"**
→ Bead description was ambiguous. Be more specific.

**"Agent got stuck in a loop"**
→ Task was too big. Decompose further.

**"Agent conflicted with another agent"**
→ Missing file reservation. Use Agent Mail leases.

**"Agent forgot context"**
→ Session compacted. Install post-compact reminder.

**"Agent refused to do something reasonable"**
→ Add Rule 0 to AGENTS.md.

---

## Meta Tips

### Start Small

First project: 20-50 beads, single agent, simple feature.
Scale up after you understand the flow.

### Document Everything

The methodology only works because everything is written down:
- Plans in markdown
- Tasks in beads
- Messages in Agent Mail
- Code in git

If it's not written down, it doesn't exist for agents.

### Embrace the Machine

Once you've done planning + bead generation, execution is mechanical:
- Check bv
- Assign task
- Monitor
- Swap accounts
- Merge
- Repeat

"Machine tending" is the goal. Your brain is for planning, not coding.
