---
name: ralph-loop
description: Trigger and manage Ralph Loop autonomous coding workflows in Vesper. Create PRDs with checkbox-formatted user stories for automated multi-task execution.
allowed-tools:
  - Read # Read PRD files and validate format
  - Write # Create and update PRD files
  - Bash # File operations
  - Grep # Search for existing PRDs
  - Glob # Find PRD files
triggers:
  - ralph loop
  - start loop
  - autonomous loop
  - run prd
  - vesper loop
  - create prd
  - write prd
---

# Ralph Loop Skill

**Purpose:** Create, validate, and prepare PRDs (Product Requirements Documents) for Ralph Loop autonomous coding workflows in Vesper.

## Overview

Ralph Loop is an autonomous coding system that processes a PRD with checkbox-formatted user stories, working through each story automatically until completion. This skill helps you create properly formatted PRDs and understand how to use Ralph Loop effectively.

### What Ralph Loop Does

- **Autonomy**: Processes multiple stories without constant user intervention
- **Structured Progress**: Tracks completion via checkbox-based PRDs
- **Resilience**: Continues working even when individual stories fail
- **Accountability**: Auto-commits changes with proper attribution
- **Control**: Pause, resume, or cancel at any time

---

## When to Use This Skill

Use this skill when you want to:

1. **Create a new PRD** for autonomous execution
2. **Validate an existing PRD** to ensure it's properly formatted
3. **Start a Ralph Loop** with your PRD in Vesper
4. **Understand the PRD format** and best practices

### Triggers

- "create a prd for..." - Create a new PRD file
- "validate my prd" - Check PRD format
- "start ralph loop" - Prepare and validate PRD for loop execution
- "run this as a loop" - Convert tasks to PRD format

---

## PRD Format

### Required Structure

```markdown
# Feature Name

## Overview
Brief description of the feature.

## User Stories

### [ ] US-001: Story title here
Detailed description of what needs to be implemented.
- Acceptance criteria 1
- Acceptance criteria 2

### [ ] US-002: Another story title
Description of the second story.

### [x] US-003: Already completed story
This story is marked as done.
```

### Story Header Pattern

Each story MUST follow this exact format:

```
### [ ] ID: Title
```

Where:
- `###` - Heading level 3 (required)
- `[ ]` - Unchecked checkbox with single space inside
- `[x]` or `[X]` - Checked checkbox (already completed)
- `ID` - Unique identifier like `US-001`, `STORY-001`, or just `001`
- `:` - Colon separator (required)
- `Title` - Short descriptive title

### Valid Examples

```markdown
### [ ] US-001: Add login form
### [ ] 001: Create user model
### [ ] FEAT-042: Implement dark mode
### [x] BUG-123: Fix null pointer (completed)
```

### Invalid Examples (will NOT be detected)

```markdown
## [ ] US-001: Wrong heading level (use ###)
### [] US-001: Missing space in checkbox
### [ ] US001: Missing hyphen or number format
### [ ] Add login form: Missing ID before title
- [ ] US-001: Using list format instead of heading
```

---

## Creating a PRD

### Step 1: Define the Feature

Start with a clear feature name and overview:

```markdown
# User Authentication

## Overview
Implement secure user authentication with email/password login, session management, and logout functionality.
```

### Step 2: Break Down into Stories

Convert your feature into small, focused stories:

**Good stories are:**
- **Small**: Completable in 5-10 minutes of agent work
- **Focused**: One clear objective per story
- **Independent**: Can be completed without other pending stories
- **Testable**: Have clear acceptance criteria

**Example breakdown:**

```markdown
## User Stories

### [ ] US-001: Create login form component
Create a LoginForm React component with:
- Email input with validation
- Password input
- Submit button
- Error message display

### [ ] US-002: Add form styling
Style the login form:
- Match existing design system
- Responsive layout
- Loading state for submit button

### [ ] US-003: Implement authentication API call
Connect form to backend:
- POST to /api/auth/login
- Handle success (store token)
- Handle errors (display message)

### [ ] US-004: Add logout functionality
Implement logout:
- Clear stored token
- Redirect to login page
- Add logout button to header
```

### Step 3: Save the PRD

Save your PRD as a markdown file in your project:

```bash
# Recommended locations
./prd.md
./docs/prds/feature-name.md
./plans/feature-name-prd.md
```

---

## Validating a PRD

Before running a Ralph Loop, validate your PRD:

### Validation Checklist

1. **Story headers use `###`** (not `##` or `####`)
2. **Checkboxes have single space**: `[ ]` not `[]` or `[  ]`
3. **IDs contain numbers**: `US-001` not `US-ABC`
4. **Colon after ID**: `US-001:` not `US-001 -`
5. **Unique IDs**: No duplicate story IDs
6. **At least one pending story**: `[ ]` not all `[x]`

### Validation Command

Use this skill to validate:

```
Validate this PRD:
[paste your PRD content]
```

Or point to a file:

```
Validate the PRD at ./docs/my-feature.prd.md
```

---

## Starting a Ralph Loop

### In Vesper (Electron App)

1. **Open your project** in Vesper
2. **Provide the PRD** in the chat by either:
   - Pasting the PRD content directly
   - Referencing the PRD file: "Run Ralph Loop with ./prd.md"
3. **Vesper will**:
   - Parse your PRD
   - Switch to Ralph mode (orange indicator)
   - Begin processing stories

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `maxIterationsPerStory` | 5 | Attempts per story before skipping |
| `timeoutPerStoryMs` | 600000 (10 min) | Max time per story |
| `autoCommit` | true | Auto-commit completed stories |
| `commitMessagePrefix` | "feat" | Prefix for commit messages |

---

## Controlling the Loop

Once running, you can control the loop:

| Action | How | What Happens |
|--------|-----|--------------|
| **Pause** | Click \|\| button | Finishes current operation, then stops |
| **Resume** | Click resume button | Continues with next pending story |
| **Cancel** | Click X button | Stops immediately |

### Progress Indicator

```
Running | Story 3/5 [=======>     ] | US-003 Add auth | 4m 32s | [||] [X]
```

- **Status**: Running, Paused, Completed, Error
- **Story N/M**: Current story / Total stories
- **Progress bar**: Visual completion
- **Story info**: Current story ID and title
- **Elapsed time**: Total loop duration
- **Controls**: Pause and Cancel buttons

---

## Best Practices

### DO

- **Keep stories small** - 5-10 minutes of work each
- **Be specific** - Include exact requirements and acceptance criteria
- **Use unique IDs** - US-001, US-002, etc.
- **Include context** - Describe the "why" not just the "what"
- **Test with few stories first** - Start with 2-3 before running large PRDs

### DON'T

- **Don't make stories too large** - Break big features into multiple stories
- **Don't use vague descriptions** - "Make it better" won't work
- **Don't skip acceptance criteria** - Agent needs to know when it's done
- **Don't create dependencies** - Each story should be completable alone

### Story Size Guide

| Size | Description | Example |
|------|-------------|---------|
| Too Small | Trivial change | "Fix typo in comment" |
| Just Right | Focused task | "Add email validation to login form" |
| Too Large | Multiple tasks | "Build complete authentication system" |

---

## PRD Template

Copy this template to start a new PRD:

```markdown
# [Feature Name]

## Overview

[Brief description of what this feature accomplishes and why it's needed.]

## User Stories

### [ ] US-001: [First story title]

[Description of what needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### [ ] US-002: [Second story title]

[Description of what needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### [ ] US-003: [Third story title]

[Description of what needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

---

## Troubleshooting

### Stories not detected

**Check:** Headers use `###`, checkboxes have space `[ ]`, IDs have numbers

### Story keeps failing

**Try:** Break into smaller stories, add more detail, check dependencies

### Loop too slow

**Try:** Make stories smaller, reduce max iterations

### No commits created

**Check:** You're in a git repo, auto-commit is enabled, changes were made

---

## Example PRDs

### Simple Feature

```markdown
# Dark Mode Toggle

## Overview
Add dark mode support with a toggle in settings.

## User Stories

### [ ] US-001: Add theme context provider
Create ThemeContext with light/dark state and toggle function.

### [ ] US-002: Create theme toggle component
Add toggle switch to settings page that updates theme context.

### [ ] US-003: Apply dark theme styles
Update CSS variables for dark mode colors.
```

### API Integration

```markdown
# Weather Widget Integration

## Overview
Add a weather widget to the dashboard showing current conditions.

## User Stories

### [ ] US-001: Create weather API service
Create service to fetch weather from OpenWeatherMap API.
- Handle API key from environment
- Parse response into WeatherData type

### [ ] US-002: Build WeatherWidget component
Display current temperature, conditions, and icon.
- Loading state while fetching
- Error state for failed requests

### [ ] US-003: Add widget to dashboard
Place WeatherWidget in dashboard grid.
- Responsive sizing
- Refresh every 30 minutes
```

---

## Integration with Vesper

This skill prepares PRDs that work with Vesper's Ralph Loop system. The actual loop execution happens in the Vesper Electron app where:

1. Your PRD is parsed into stories
2. Ralph mode activates (orange indicator)
3. Each story is sent to the agent
4. Progress is tracked with commits
5. You can pause/resume/cancel anytime

---

## Scripts & Files Reference

This section documents all the scripts and files needed to run Ralph Loop via CLI.

### Directory Structure

```
ralph-loop/
├── ralph                    # CLI entry point
├── lib/loop.sh              # Core loop logic
├── prompts/
│   ├── build.md             # Build iteration prompt template
│   └── plan.md              # Planning prompt template
├── skills/commit/SKILL.md   # Commit skill for conventional commits
├── hooks/
│   ├── on-complete.sh       # Stop hook (runs on session end)
│   └── on-start.sh          # UserPromptSubmit hook
├── .ralph/
│   └── prd.md               # Active PRD file (default location)
└── CLAUDE.md                # Agent instructions
```

### CLI Entry Point: `ralph`

Main entry point for all Ralph Loop operations.

**Location:** `./ralph`

**Commands:**

```bash
# Initialize .ralph directory
ralph init

# Create implementation plan from PRD
ralph plan [--prd=N]

# Run N build iterations (default: 5)
ralph build [N] [--prd=N]

# Show help
ralph help
```

**Examples:**

```bash
# Initialize and create PRD
ralph init
# Then create .ralph/prd.md with your stories

# Run 10 build iterations
ralph build 10

# Plan a specific PRD
ralph plan --prd=2  # Uses .ralph/PRD-2/prd.md
```

### Core Loop: `lib/loop.sh`

Contains the core loop logic with these functions:

| Function | Purpose |
|----------|---------|
| `validate_prd` | Validates PRD file exists and is readable |
| `select_story` | Finds next unchecked story (`### [ ] US-XXX:`) |
| `extract_block` | Extracts story content from PRD |
| `render_prompt` | Renders build.md template with story data |
| `mark_complete` | Changes `[ ]` to `[x]` in PRD |
| `run_agent` | Executes Claude with timeout |
| `verify_commit` | Ensures agent created a commit |
| `run_build` | Main build loop orchestration |
| `run_plan` | Planning function |

**Key behavior:**
- Selects stories matching pattern `### [ ] US-XXX:`
- Extracts story block (from header to next `###` or EOF)
- Runs Claude agent with prompt
- Verifies commit was created (auto-commits if agent forgot)
- Marks story complete in PRD

### Build Prompt: `prompts/build.md`

Template rendered for each story iteration.

**Placeholders:**
- `{{STORY_ID}}` - Story identifier (e.g., `US-001`)
- `{{STORY_TITLE}}` - Story title
- `{{STORY_BLOCK}}` - Full story content from PRD
- `{{PRD_PATH}}` - Path to PRD file

**Agent Rules (from template):**
1. Implement ONLY this story
2. No questions - make reasonable assumptions
3. Verify before done - run tests/checks
4. Use `/commit` - create conventional commits
5. One commit per story

### Plan Prompt: `prompts/plan.md`

Template for planning operations.

**Placeholders:**
- `{{PRD_CONTENT}}` - Full PRD file content
- `{{PRD_PATH}}` - Path to PRD file

**Output format:**
- Creates stories in `### [ ] US-XXX: Title` format
- Includes acceptance criteria
- Orders by dependency

### Commit Skill: `skills/commit/SKILL.md`

Conventional commit skill used by agents.

**Commit Types:**
| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code refactoring |
| `test` | Test additions |
| `docs` | Documentation |
| `chore` | Maintenance |
| `perf` | Performance |
| `ci` | CI/CD changes |

**Format:** `type(scope): subject`

**Example:** `feat(US-001): implement user authentication`

### Hooks

**`hooks/on-complete.sh`** - Stop hook
- Runs when Claude Code session ends
- Currently a no-op placeholder

**`hooks/on-start.sh`** - UserPromptSubmit hook
- Runs when user submits a prompt
- Currently a no-op placeholder

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RALPH_ROOT` | `.ralph` | Override .ralph directory location |
| `MODEL` | (none) | Claude model: `haiku`, `sonnet`, `opus` |
| `AGENT_TIMEOUT` | `600` | Agent timeout in seconds |

**Examples:**

```bash
# Use opus model with 15-minute timeout
MODEL=opus AGENT_TIMEOUT=900 ralph build 5

# Use alternate PRD location
RALPH_ROOT=/path/to/prds ralph build
```

### PRD File Format

**Location:** `.ralph/prd.md` (default) or `.ralph/PRD-N/prd.md`

**Story header pattern (REQUIRED):**
```markdown
### [ ] US-001: Story title
```

**Story detection regex:** `^### \[ \] US-[0-9]+:`

**Completion mark:** `### [x] US-001: Story title`

---

## Running Ralph Loop via CLI

### Quick Start

```bash
# 1. Clone or navigate to ralph-loop
cd ralph-loop

# 2. Initialize
./ralph init

# 3. Create PRD
cat > .ralph/prd.md << 'EOF'
# My Feature

## User Stories

### [ ] US-001: First task
Description here.

### [ ] US-002: Second task
Description here.
EOF

# 4. Run the loop
./ralph build 5
```

### Full Workflow

```bash
# Plan first (optional - generates stories from high-level PRD)
./ralph plan

# Run build iterations
./ralph build 10

# Check progress
cat .ralph/prd.md | grep "### \["
```

### Advanced Usage

```bash
# Multiple PRDs
mkdir -p .ralph/PRD-1 .ralph/PRD-2
# Create prd.md in each, then:
./ralph build 5 --prd=1
./ralph build 5 --prd=2

# Custom model and timeout
MODEL=opus AGENT_TIMEOUT=1200 ./ralph build 3
```

For more details, see the full Ralph Loop documentation.
