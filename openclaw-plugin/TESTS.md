# Agent Tools Plugin — Test Suite

Run these tests after any plugin changes to verify functionality.

## Prerequisites

```bash
# Ensure plugin is installed
openclaw plugins list | grep agent-tools
# Should show: agent-tools | loaded

# Ensure commands are linked
ls ~/.openclaw/commands/ | head -5
# Should show command files
```

---

## Test 1: Plugin Loading

```bash
openclaw plugins list 2>&1 | grep -E "agent-tools.*loaded"
```

**Expected:** Shows `agent-tools | loaded`

---

## Test 2: slash_list

Ask the agent:
```
List available slash commands
```

**Expected:** Agent calls `slash_list()` and returns 44+ commands with descriptions.

---

## Test 3: slash_read (simple)

Ask the agent:
```
/changelog
```

**Expected:** Agent calls `slash_read("changelog")`, reads the file, and follows instructions.

---

## Test 4: slash_read (namespaced)

Ask the agent:
```
/workflows:plan Build a test feature
```

**Expected:** Agent calls `slash_read("workflows:plan")` and follows with "Build a test feature" as $ARGUMENTS.

---

## Test 5: task_create

Ask the agent:
```
Create a test task: "Verify plugin works" with high priority
```

**Expected:** Agent calls `task_create(description="Verify plugin works", priority="high")` and returns task ID.

---

## Test 6: task_list

Ask the agent:
```
What tasks do we have?
```

**Expected:** Agent calls `task_list()` and shows the test task created above.

---

## Test 7: task_update

Ask the agent:
```
Mark that test task as done
```

**Expected:** Agent calls `task_update(id="<id>", status="done")` and confirms update.

---

## Quick Verification Script

```bash
#!/bin/bash
# Run from any directory

echo "=== Test 1: Plugin Loading ==="
openclaw plugins list 2>&1 | grep -E "agent-tools" && echo "✅ PASS" || echo "❌ FAIL"

echo ""
echo "=== Test 2: Commands Directory ==="
[ -d ~/.openclaw/commands ] && [ "$(ls ~/.openclaw/commands/*.md 2>/dev/null | wc -l)" -gt 0 ] && echo "✅ PASS: Commands found" || echo "❌ FAIL: No commands"

echo ""
echo "=== Test 3: Tasks Directory ==="
[ -d ~/.openclaw/tasks ] && echo "✅ PASS: Tasks dir exists" || echo "⚠️ WARN: Tasks dir missing (will be created on first use)"

echo ""
echo "=== Manual Tests Required ==="
echo "Run these in a chat session:"
echo "  1. 'List slash commands' → should show 44+ commands"
echo "  2. '/changelog' → should follow changelog instructions"
echo "  3. 'Create test task' → should create and return ID"
echo "  4. 'List tasks' → should show the task"
echo "  5. 'Mark task done' → should update status"
```

---

## After Updates

```bash
# 1. Pull latest
cd ~/vesper-team-skills && git pull

# 2. Re-install plugin
cp -r openclaw-plugin ~/.openclaw/extensions/agent-tools

# 3. Restart gateway
openclaw gateway restart

# 4. Run tests
bash openclaw-plugin/test.sh
```
