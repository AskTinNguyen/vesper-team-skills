---
name: qa-release-guardian
description: "Automated Release QA that combines UI exploratory testing, issue-based regression verification, PR-aware retesting, and structured bug reporting. Use when the user needs to verify a release, run regression tests after deploy, validate PR changes, or perform automated QA on staging/production."
allowed-tools: [Bash, Read, Grep, Glob, Write, agent-browser:*]
---

# QA Release Guardian

Automated Release QA that combines UI exploratory testing, issue-based regression verification, PR-aware retesting, and structured bug reporting. QA teams can run comprehensive tests with a single command.

## Quick Start

```bash
# Basic smoke test on localhost
qa-release-guardian --base_url=http://localhost:3000

# Full regression on staging
qa-release-guardian --base_url=https://staging.app.com --scope=full

# Regression only (skip UI discovery)
qa-release-guardian --base_url=https://app.com --scope=regression_only --since=last_7_days

# With authentication
qa-release-guardian --base_url=https://app.com --auth=cookie --auth_file=auth.json
```

## Configuration

Skill accepts YAML config file or CLI flags:

### Config File (`.qa-guardian.yml`)

```yaml
base_url: https://staging.app.com
auth:
  type: cookie  # cookie | oauth | none
  file: ./auth-state.json

github:
  repo: owner/repo-name
  since: last_7_days  # last_deploy | last_7_days | last_14_days | YYYY-MM-DD

scope:
  mode: full  # smoke | full | regression_only
  max_depth: 3
  exclude_routes:
    - /admin
    - /internal/**
    - /api/**

safety:
  allow_write_actions: false
  skip_danger_keywords:
    - delete
    - remove
    - disable
    - archive
    - purge

reporting:
  output_dir: ./qa-reports
  screenshot_on_error: true
  video_record: false
```

### CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--base_url` | Target URL to test | Required |
| `--config` | Path to YAML config | `.qa-guardian.yml` |
| `--scope` | Test scope: smoke/full/regression_only | `full` |
| `--since` | GitHub lookback: last_deploy/last_7_days/last_14_days/YYYY-MM-DD | `last_7_days` |
| `--auth` | Auth type: cookie/oauth/none | `none` |
| `--auth_file` | Path to auth state file | - |
| `--max_depth` | UI crawl depth | `3` |
| `--output` | Report output directory | `./qa-reports` |
| `--dry_run` | Plan only, don't execute | `false` |

## Execution Phases

### Phase 0 – GitHub Context Intelligence

Fetch closed issues and merged PRs to build regression map:

```bash
# 0.1 Fetch closed issues
gh issue list \
  --repo owner/repo \
  --state closed \
  --limit 50 \
  --search "closed:>2024-01-01" \
  --json number,title,labels,body,closedAt,url

# 0.2 Fetch merged PRs
gh pr list \
  --repo owner/repo \
  --state merged \
  --limit 20 \
  --search "merged:>2024-01-01" \
  --json number,title,body,files,mergedAt,url,headRefName
```

Extracted data structure:
```yaml
regression_map:
  issues:
    - id: 123
      title: "Fix login redirect loop"
      expected_behavior: "User should land on dashboard after login"
      ui_area: "/login, /dashboard"
      severity: high
      linked_prs: [456]
      
  prs:
    - id: 456
      title: "fix(auth): resolve redirect loop"
      files_changed: ["app/login/page.tsx", "lib/auth.ts"]
      affected_routes: ["/login", "/auth/callback"]
      linked_issues: [123]
```

### Phase 1 – UI Discovery (Agent Browser)

Crawl the application to discover all screens and interactions:

```bash
# 1.1 Open base URL
agent-browser open <base_url>

# 1.2 Get interactive snapshot
agent-browser snapshot -i --json

# 1.3 Extract navigation elements
# - Links (<a> tags)
# - Buttons that navigate
# - Menu items
# - Tab controls

# 1.4 Build UI graph (depth-limited)
# Track: route -> elements -> child_routes
```

Discovery output:
```yaml
ui_graph:
  /dashboard:
    elements:
      - type: link
        text: "Profile"
        href: "/profile"
      - type: button
        text: "Add Asset"
        action: "open_modal"
    modals:
      - trigger: "Add Asset"
        content: "asset-form"
  /profile:
    elements:
      - type: form
        fields: ["name", "email"]
      - type: button
        text: "Save"
```

### Phase 2 – Exploratory UI Testing

Test all discovered screens and interactions:

```bash
# For each screen in ui_graph:
# 2.1 Navigate to screen
agent-browser open <base_url><screen_path>

# 2.2 Get interactive elements
agent-browser snapshot -i --json

# 2.3 Test each button (safe ones only)
# - Skip if text matches danger_keywords
# - Click and observe
# - Check for console/network errors

# 2.4 Test form inputs
# - Fill with dummy data (safe values)
# - Don't submit if allow_write_actions=false
# - Validate field behavior

# 2.5 Check for issues:
# - Console errors: agent-browser console
# - Network errors: agent-browser network requests
# - UI freezes: timeouts
# - Unexpected redirects: agent-browser get url

# 2.6 Capture evidence on error
agent-browser screenshot --full <output_dir>/errors/<screen>-<timestamp>.png
agent-browser console > <output_dir>/errors/<screen>-console.log
```

### Phase 3 – Issue-Based Regression Testing

Verify closed issues remain fixed:

```bash
# For each issue in regression_map.issues:
# 3.1 Navigate to affected UI area
agent-browser open <base_url><ui_area>

# 3.2 Attempt to reproduce original issue
# Follow reproduce_steps from issue analysis

# 3.3 Assert expected behavior
# Compare actual vs expected_behavior

# 3.4 Document result
# PASS: Issue remains fixed
# FAIL: Regression detected (don't auto-reopen)
```

Regression test example:
```yaml
test_results:
  - issue_id: 123
    title: "Fix login redirect loop"
    status: PASS
    evidence:
      screenshot: "./qa-reports/regression/issue-123-pass.png"
      notes: "Login flow works correctly, redirects to dashboard"
    
  - issue_id: 124
    title: "Asset deletion fails silently"
    status: FAIL
    severity: P1
    evidence:
      screenshot: "./qa-reports/regression/issue-124-fail.png"
      console_errors: ["TypeError: Cannot read property 'id' of undefined"]
      reproduction: "Click delete on asset #12345, no confirmation shown"
```

### Phase 4 – PR-Aware Retesting

Focus on areas affected by recent PRs:

```bash
# For each merged PR:
# 4.1 Identify affected routes from files_changed
# Map files to UI routes:
# - app/(dashboard)/assets/page.tsx -> /assets
# - components/asset-card.tsx -> anywhere AssetCard is used
# - lib/auth.ts -> all authenticated routes

# 4.2 Priority testing for critical flows:
# - Auth routes (if auth files changed)
# - Permission checks (if middleware changed)
# - Payment flows (if payment components changed)
# - State persistence (if storage/cache changed)

# 4.3 Run targeted tests on affected areas
# Re-run Phase 2 tests for affected routes only
```

### Phase 5 – Reporting & Artifacts

Generate comprehensive reports:

#### 1. QA Summary Report (`qa-summary.md`)

```markdown
# QA Release Report

**Date:** 2024-01-15 14:30 UTC  
**Target:** https://staging.app.com  
**Scope:** full  
**Duration:** 12m 34s

## Summary

| Metric | Count |
|--------|-------|
| Screens Tested | 24 |
| Interactions | 156 |
| New Bugs Found | 3 |
| Regression Failures | 1 |
| Issues Verified | 12 |
| PRs Validated | 5 |

## New Bugs

### P1: Login button unresponsive on mobile
- **Screen:** /login
- **Steps:** 1. Open /login on mobile viewport 2. Enter valid credentials 3. Click "Sign In"
- **Expected:** Redirect to dashboard
- **Actual:** Button shows spinner indefinitely
- **Evidence:** [Screenshot](./bugs/new/login-mobile-fail.png)

### P2: Asset form missing validation
...

## Regressions

### Issue #124: Asset deletion fails silently (REGRESSION)
- **Previous Status:** Fixed
- **Current Status:** Broken
- **Severity:** P1
- **Evidence:** [Screenshot](./bugs/regression/issue-124.png)

## Recommendations

- [ ] Fix P1 mobile login issue before release
- [ ] Re-verify issue #124 fix
- [ ] Consider adding e2e test for asset deletion
```

#### 2. Bug Reports (`bugs/new-bugs.md`)

#### 3. Regression Report (`bugs/regressions.md`)

## Safety Guardrails

### Data Protection

The skill enforces these safety rules:

1. **No Destructive Actions** (unless `allow_write_actions: true`)
   - Delete/Remove/Disable buttons are skipped
   - Forms are filled but not submitted
   - Confirmation dialogs are dismissed

2. **Danger Keyword Detection**
   ```yaml
   danger_keywords:
     - delete
     - remove
     - disable
     - archive
     - purge
     - deactivate
     - unsubscribe
     - cancel.*account
   ```

3. **Safe Test Data**
   - Email: `qa-test-<timestamp>@example.com`
   - Text: `QA Test String <timestamp>`
   - Numbers: Sequential safe values
   - Files: Small dummy files only

4. **Scope Limits**
   - Respects `exclude_routes` pattern
   - Honors `max_depth` crawl limit
   - Stops on auth walls (reports them)

## Usage Examples

### Example 1: Smoke Test Before Deploy

```bash
qa-release-guardian \
  --base_url=https://staging.app.com \
  --scope=smoke \
  --output=./qa-reports/staging-$(date +%Y%m%d-%H%M%S)
```

Tests only critical paths:
- Homepage loads
- Login works
- Main navigation accessible
- No console errors on key screens

### Example 2: Full Regression Test

```bash
qa-release-guardian \
  --base_url=https://app.com \
  --scope=full \
  --since=last_7_days \
  --auth=cookie \
  --auth_file=./prod-auth.json
```

Runs complete test suite:
- All UI discovery (depth 3)
- All closed issues from last 7 days
- All merged PRs from last 7 days
- Full interaction testing

### Example 3: PR Validation

```bash
qa-release-guardian \
  --base_url=https://pr-123.staging.app.com \
  --scope=regression_only \
  --since=2024-01-10
```

Focuses on:
- Issues closed since Jan 10
- PRs merged since Jan 10
- Skips UI discovery (faster)

### Example 4: Dry Run (Planning)

```bash
qa-release-guardian \
  --base_url=https://app.com \
  --dry_run \
  --output=./qa-plan.md
```

Generates test plan without execution:
- Lists screens to test
- Lists issues to verify
- Lists PRs to validate
- Estimated duration

## Output Structure

```
qa-reports/
├── 20240115-143000/           # Timestamped report dir
│   ├── qa-summary.md          # Main report
│   ├── ui-graph.json          # Discovered UI structure
│   ├── regression-map.json    # GitHub issues/PRs
│   ├── test-log.jsonl         # Detailed execution log
│   ├── bugs/
│   │   ├── new-bugs.md        # New issues found
│   │   ├── regressions.md     # Regression failures
│   │   └── p1/               # P1 screenshots
│   │       ├── login-mobile-fail.png
│   │       └── ...
│   ├── evidence/
│   │   ├── screens/          # All screen screenshots
│   │   └── errors/           # Error screenshots
│   └── videos/               # If video_record=true
└── latest -> 20240115-143000  # Symlink to latest
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: QA Guardian
on:
  deployment_status:
    states: [success]

jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run QA Guardian
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude skill qa-release-guardian \
            --base_url=${{ github.event.deployment_status.target_url }} \
            --scope=full \
            --since=last_deploy
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: qa-report
          path: ./qa-reports/latest/
      
      - name: Comment on PR
        if: failure()
        run: |
          gh pr comment ${{ github.event.pull_request.number }} \
            --body-file ./qa-reports/latest/qa-summary.md
```

## Design Principles

1. **Zero Hard-coded Selectors**
   - Uses semantic locators (role, label, text)
   - Falls back to visual position only when necessary
   - Adapts to UI changes automatically

2. **Deterministic Behavior**
   - Same inputs = same test path
   - Reproducible results
   - Consistent reporting format

3. **Fail Loudly, Report Clearly**
   - Every failure has evidence
   - Stack traces captured
   - Screenshots for visual issues

4. **QA-Friendly Output**
   - No code knowledge required
   - Markdown reports readable by anyone
   - Clear severity levels (P1/P2/P3)

## Troubleshooting

### Issue: "Cannot access authenticated routes"

**Solution:** Provide auth state file:
```bash
# 1. Manually login and save state
agent-browser open https://app.com/login
# ... perform login ...
agent-browser state save ./auth.json

# 2. Use in QA Guardian
qa-release-guardian --base_url=https://app.com --auth=cookie --auth_file=./auth.json
```

### Issue: "Too many false positives"

**Solution:** Adjust scope and exclusions:
```yaml
scope:
  mode: smoke  # Less aggressive
  exclude_routes:
    - /experimental/**
    - /beta/**
```

### Issue: "Tests taking too long"

**Solution:** 
- Reduce `max_depth` to 2
- Use `scope: regression_only` to skip discovery
- Use `--since=last_deploy` to test only recent changes

## Requirements

- GitHub CLI (`gh`) authenticated
- Agent Browser available
- Network access to target URL
- Write access to output directory

## See Also

- `agent-browser` - Browser automation primitives
- `report-bug` - Structured bug reporting skill
