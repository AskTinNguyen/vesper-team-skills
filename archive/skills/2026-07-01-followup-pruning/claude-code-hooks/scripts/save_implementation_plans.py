#!/usr/bin/env python3
"""
Save Implementation Plans Hook

PostToolUse hook that automatically saves approved Claude Code implementation plans
to a separate repository for future reference.

Triggers when:
- Write tool creates/updates a plan file (PLAN.md, plan.md, implementation_plan.*)
- Content contains plan indicators (## Tasks, ## Steps, ## Implementation, etc.)

Usage in settings.json:
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/save_implementation_plans.py"
      }]
    }]
  }
}

Configuration:
Set CLAUDE_PLANS_REPO environment variable to your plans repository path.
Default: ~/.claude/saved-plans/

Repository structure:
~/.claude/saved-plans/
├── 2026/
│   └── 01/
│       ├── 2026-01-21-project-name-feature.md
│       └── 2026-01-21-another-project-refactor.md
└── index.md  (auto-generated index)
"""

import json
import sys
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
PLANS_REPO = Path(os.environ.get('CLAUDE_PLANS_REPO', Path.home() / '.claude' / 'saved-plans'))
MIN_PLAN_LENGTH = 200  # Minimum characters to consider as a plan

# Patterns that indicate a file is an implementation plan
PLAN_FILE_PATTERNS = [
    r'plan\.md$',
    r'PLAN\.md$',
    r'implementation[_-]?plan',
    r'project[_-]?plan',
    r'task[_-]?plan',
    r'\.plan\.md$',
]

# Content patterns that indicate implementation plan content
PLAN_CONTENT_PATTERNS = [
    r'^#{1,3}\s*(Implementation\s+)?Plan',
    r'^#{1,3}\s*Tasks?\s*$',
    r'^#{1,3}\s*Steps?\s*$',
    r'^#{1,3}\s*Overview\s*$',
    r'^#{1,3}\s*Objectives?\s*$',
    r'^#{1,3}\s*Requirements?\s*$',
    r'^#{1,3}\s*Phase\s+\d',
    r'^#{1,3}\s*Step\s+\d',
    r'^\s*-\s*\[[\sx]\]',  # Task checkboxes
    r'^#{1,3}\s*Files?\s+to\s+(Modify|Create|Change)',
    r'^#{1,3}\s*Technical\s+Approach',
    r'^#{1,3}\s*Acceptance\s+Criteria',
]

# Minimum number of plan patterns to match
MIN_PATTERN_MATCHES = 3


def is_plan_file(file_path: str) -> bool:
    """Check if filename indicates a plan file."""
    filename = os.path.basename(file_path).lower()
    for pattern in PLAN_FILE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def is_plan_content(content: str) -> tuple[bool, int]:
    """
    Check if content looks like an implementation plan.
    Returns (is_plan, match_count).
    """
    if len(content) < MIN_PLAN_LENGTH:
        return False, 0

    match_count = 0
    for pattern in PLAN_CONTENT_PATTERNS:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            match_count += 1

    return match_count >= MIN_PATTERN_MATCHES, match_count


def extract_plan_title(content: str, file_path: str) -> str:
    """Extract a title from the plan content or filename."""
    # Try to find first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Clean up title
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', '-', title).lower()
        return title[:50]  # Limit length

    # Fall back to filename
    basename = os.path.basename(file_path)
    name = os.path.splitext(basename)[0]
    return name.lower().replace('_', '-')


def get_project_name(cwd: str) -> str:
    """Get project name from working directory."""
    if not cwd:
        return "unknown-project"
    return os.path.basename(cwd).lower().replace(' ', '-')


def ensure_repo_structure():
    """Create the plans repository structure."""
    PLANS_REPO.mkdir(parents=True, exist_ok=True)

    # Create index file if it doesn't exist
    index_file = PLANS_REPO / 'index.md'
    if not index_file.exists():
        with open(index_file, 'w') as f:
            f.write("# Saved Implementation Plans\n\n")
            f.write("Auto-saved plans from Claude Code sessions.\n\n")
            f.write("---\n\n")


def save_plan(content: str, file_path: str, cwd: str):
    """Save plan to the repository."""
    ensure_repo_structure()

    now = datetime.now()
    year_month = now.strftime("%Y/%m")
    date_prefix = now.strftime("%Y-%m-%d")
    time_suffix = now.strftime("%H%M")

    project = get_project_name(cwd)
    title = extract_plan_title(content, file_path)

    # Create year/month directory
    plan_dir = PLANS_REPO / year_month
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = f"{date_prefix}-{project}-{title}.md"
    plan_path = plan_dir / filename

    # Handle duplicates
    counter = 1
    while plan_path.exists():
        filename = f"{date_prefix}-{project}-{title}-{counter}.md"
        plan_path = plan_dir / filename
        counter += 1

    # Add metadata header
    metadata = f"""---
saved_at: {now.isoformat()}
project: {project}
source_file: {file_path}
source_dir: {cwd}
---

"""

    # Write plan with metadata
    with open(plan_path, 'w') as f:
        f.write(metadata)
        f.write(content)

    # Update index
    update_index(plan_path, project, title, now)

    # Auto-commit to git if enabled
    git_auto_commit(plan_path, project, title)

    return plan_path


def update_index(plan_path: Path, project: str, title: str, timestamp: datetime):
    """Add entry to the index file."""
    index_file = PLANS_REPO / 'index.md'

    # Create relative path for link
    rel_path = plan_path.relative_to(PLANS_REPO)

    entry = f"- [{timestamp.strftime('%Y-%m-%d %H:%M')}] **{project}**: [{title}]({rel_path})\n"

    # Read existing content
    with open(index_file, 'r') as f:
        content = f.read()

    # Find insertion point (after the header)
    header_end = content.find('---\n\n')
    if header_end == -1:
        header_end = len(content)
    else:
        header_end += 5  # Skip past "---\n\n"

    # Insert new entry at the top of the list
    new_content = content[:header_end] + entry + content[header_end:]

    with open(index_file, 'w') as f:
        f.write(new_content)


def git_auto_commit(plan_path: Path, project: str, title: str):
    """Auto-commit if the plans repo is a git repository."""
    import subprocess

    # Check if CLAUDE_PLANS_GIT_COMMIT is enabled
    if os.environ.get('CLAUDE_PLANS_GIT_COMMIT', '').lower() not in ('true', '1', 'yes'):
        return

    # Check if it's a git repo
    git_dir = PLANS_REPO / '.git'
    if not git_dir.exists():
        return

    try:
        # Stage the new plan and index
        subprocess.run(
            ['git', 'add', str(plan_path), str(PLANS_REPO / 'index.md')],
            cwd=PLANS_REPO,
            capture_output=True,
            timeout=10
        )

        # Commit
        commit_msg = f"Add plan: {project} - {title}"
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=PLANS_REPO,
            capture_output=True,
            timeout=10
        )

        # Optional: auto-push if CLAUDE_PLANS_GIT_PUSH is set
        if os.environ.get('CLAUDE_PLANS_GIT_PUSH', '').lower() in ('true', '1', 'yes'):
            subprocess.run(
                ['git', 'push'],
                cwd=PLANS_REPO,
                capture_output=True,
                timeout=30
            )
    except Exception:
        pass  # Don't fail the hook on git errors


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        cwd = data.get('cwd', '')

        # Only process Write and Edit tools
        if tool_name not in ['Write', 'Edit']:
            sys.exit(0)

        file_path = tool_input.get('file_path', '')
        if not file_path:
            sys.exit(0)

        # For Write, content is directly available
        # For Edit, we need to read the file
        if tool_name == 'Write':
            content = tool_input.get('content', '')
        else:
            # For Edit, try to read the file
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except:
                sys.exit(0)

        if not content:
            sys.exit(0)

        # Check if this is a plan file by name
        is_plan_by_name = is_plan_file(file_path)

        # Check if content looks like a plan
        is_plan_by_content, match_count = is_plan_content(content)

        # Save if either condition is met
        if is_plan_by_name or is_plan_by_content:
            saved_path = save_plan(content, file_path, cwd)

            # Optionally notify Claude (comment out if too noisy)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"[Plan saved to {saved_path}]"
                }
            }))

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        print(f"Save plan hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
