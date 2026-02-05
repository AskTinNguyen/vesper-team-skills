#!/bin/bash
# Agent Tools Plugin - Quick Verification Script
# Run: bash test.sh

set -e

echo "🧪 Agent Tools Plugin Tests"
echo "==========================="
echo ""

# Test 1: Plugin Loading
echo "Test 1: Plugin Loading"
if openclaw plugins list 2>&1 | grep -q "agent-tools.*loaded"; then
    echo "  ✅ PASS: Plugin loaded"
else
    echo "  ❌ FAIL: Plugin not loaded"
    echo "  Run: openclaw plugins enable agent-tools && openclaw gateway restart"
    exit 1
fi

# Test 2: Commands Directory
echo ""
echo "Test 2: Commands Directory"
if [ -d ~/.openclaw/commands ] && [ "$(ls ~/.openclaw/commands/*.md 2>/dev/null | wc -l)" -gt 0 ]; then
    CMD_COUNT=$(ls ~/.openclaw/commands/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✅ PASS: $CMD_COUNT commands found"
else
    echo "  ❌ FAIL: No commands found"
    echo "  Run: ln -sf ~/vesper-team-skills/commands ~/.openclaw/commands"
    exit 1
fi

# Test 3: Tasks Directory
echo ""
echo "Test 3: Tasks Directory"
if [ -d ~/.openclaw/tasks ]; then
    echo "  ✅ PASS: Tasks directory exists"
else
    echo "  ⚠️  WARN: Tasks directory missing (will be created on first use)"
fi

# Test 4: Skill File
echo ""
echo "Test 4: Slash Commands Skill"
if [ -f ~/.openclaw/extensions/agent-tools/skills/slash-commands/SKILL.md ]; then
    echo "  ✅ PASS: Skill file exists"
else
    echo "  ❌ FAIL: Skill file missing"
    exit 1
fi

# Summary
echo ""
echo "==========================="
echo "🎉 Automated tests passed!"
echo ""
echo "📋 Manual tests (run in chat):"
echo "  1. 'List slash commands' → expect 44+ commands"
echo "  2. '/changelog' → expect changelog generation"
echo "  3. 'Create a test task' → expect task ID"
echo "  4. 'List tasks' → expect task list"
echo "  5. 'Mark task <id> done' → expect status update"
