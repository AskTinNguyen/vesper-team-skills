#!/usr/bin/env python3
"""
Code Quality Check Hook

PostToolUse hook that checks files after Edit/Write for quality violations.
Reports issues as non-blocking feedback (exit code 2).

Usage in settings.json:
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/code-quality-hook/scripts/code_quality_check.py",
        "timeout": 15
      }]
    }]
  }
}
"""

import json
import os
import re
import sys

# Paths/patterns to skip
SKIP_PATTERNS = [
    "node_modules",
    "vendor",
    "dist/",
    "build/",
    ".min.",
    "__pycache__",
    ".pyc",
]

SKIP_TEST_PATTERNS = [
    "test",
    "spec",
    "_test.go",
    "_spec.rb",
    ".test.",
    ".spec.",
]

MAX_FUNCTION_LINES = 50
MAX_NESTING_DEPTH = 4
MAX_FILE_LINES = 500
MAX_COMMENTED_BLOCK = 10


def should_skip(file_path: str) -> bool:
    """Check if file should be skipped."""
    lower = file_path.lower()
    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return True
    for pattern in SKIP_TEST_PATTERNS:
        if pattern in lower:
            return True
    return False


def check_function_size(lines: list[str]) -> list[str]:
    """Find functions longer than MAX_FUNCTION_LINES."""
    violations = []
    func_pattern = re.compile(
        r"^\s*"
        r"(def |function |async function "
        r"|(?:export\s+)?(?:async\s+)?(?:function\s+)?"
        r"(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(?"
        r"|func "
        r"|(?:public|private|protected)\s+(?:static\s+)?(?:async\s+)?\w+\s*\()"
    )
    func_start = None
    func_name = ""

    for i, line in enumerate(lines):
        if func_pattern.search(line):
            if func_start is not None:
                length = i - func_start
                if length > MAX_FUNCTION_LINES:
                    violations.append(
                        f"  Line {func_start + 1}: function '{func_name}' is {length} lines (max {MAX_FUNCTION_LINES})"
                    )
            func_start = i
            # Extract a rough function name
            match = re.search(r"(?:def|function|func|const|let|var)\s+(\w+)", line)
            func_name = match.group(1) if match else "anonymous"

    # Check last function
    if func_start is not None:
        length = len(lines) - func_start
        if length > MAX_FUNCTION_LINES:
            violations.append(
                f"  Line {func_start + 1}: function '{func_name}' is {length} lines (max {MAX_FUNCTION_LINES})"
            )

    return violations


def check_nesting_depth(lines: list[str]) -> list[str]:
    """Find lines with nesting deeper than MAX_NESTING_DEPTH."""
    violations = []
    reported_regions = set()

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not stripped:
            continue
        # Measure indentation
        leading = len(line) - len(line.lstrip())
        # Heuristic: detect indent unit from leading spaces, or tabs
        if "\t" in line[:leading]:
            depth = line[:leading].count("\t")
        else:
            # Use 4-space indent (most common); falls back gracefully for 2-space
            depth = leading // 4

        if depth > MAX_NESTING_DEPTH:
            # Report once per 10-line region to avoid spam
            region = i // 10
            if region not in reported_regions:
                reported_regions.add(region)
                violations.append(
                    f"  Line {i + 1}: nesting depth {depth} (max {MAX_NESTING_DEPTH})"
                )

    return violations


def check_file_size(lines: list[str]) -> list[str]:
    """Check if file exceeds MAX_FILE_LINES."""
    if len(lines) > MAX_FILE_LINES:
        return [f"  File is {len(lines)} lines (max {MAX_FILE_LINES})"]
    return []


def check_commented_blocks(lines: list[str]) -> list[str]:
    """Find blocks of 10+ consecutive commented-out lines with code syntax."""
    violations = []
    code_keywords = re.compile(
        r"(function|class|if|for|while|return|import|const|let|var|def |;|\{|\}|\(|\))"
    )
    comment_pattern = re.compile(r"^\s*(//|#|--|/\*|\*)")

    run_start = None
    run_length = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if comment_pattern.match(stripped) and code_keywords.search(stripped):
            if run_start is None:
                run_start = i
            run_length += 1
        else:
            if run_length >= MAX_COMMENTED_BLOCK:
                violations.append(
                    f"  Lines {run_start + 1}-{run_start + run_length}: {run_length} lines of commented-out code"
                )
            run_start = None
            run_length = 0

    # Check trailing block
    if run_length >= MAX_COMMENTED_BLOCK:
        violations.append(
            f"  Lines {run_start + 1}-{run_start + run_length}: {run_length} lines of commented-out code"
        )

    return violations


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    if should_skip(file_path):
        sys.exit(0)

    if not os.path.isfile(file_path):
        sys.exit(0)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        sys.exit(0)

    violations = []
    violations.extend(check_function_size(lines))
    violations.extend(check_nesting_depth(lines))
    violations.extend(check_file_size(lines))
    violations.extend(check_commented_blocks(lines))

    if violations:
        print(
            f"Code quality issues in {os.path.basename(file_path)}:",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
