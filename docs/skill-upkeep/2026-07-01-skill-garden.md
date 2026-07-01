# Skill Upkeep Report - 2026-07-01

Objective: invoke `auto-upkeep-review-skills` against `vesper-team-skills`, inspect every skill manifest in the repo, and reduce the discoverable skill surface to at most 100 useful skills by archiving non-essential or bundled material.

## Method

- Loaded `auto-upkeep-review-skills` from `~/.codex/skills/auto-upkeep-review-skills/SKILL.md`.
- The referenced quality-bar skills `writing-great-skills`, `hermes-skill-lifecycle-management`, and `hermes-skill-curation` were not present locally, so this pass used the closest available local standards: `skill-creator`, `workflow-improve-skill`, and `hermes-skill-library-management`.
- Parsed every discoverable `SKILL.md` before changes, including nested and backup copies. On macOS, lowercase `commands/skill.md` resolves under case-insensitive `SKILL.md` scans, so it was included in the reviewed set.
- Applied reversible archive actions only: moved non-essential packages under `archive/skills/2026-07-01-skill-garden/` or renamed in-place support/backup manifests to `SKILL.archived.md`.

## Counts

| Measure | Before | After |
|---|---:|---:|
| Discoverable skill manifests | 183 | 100 |
| Top-level discoverable manifests | 163 | 99 |
| Nested discoverable manifests | 10 | 1 |
| Backup discoverable manifests | 10 | 0 |
| New manifests archived in this pass | 0 | 83 |
| Active skill cap | n/a | 100 |

## Verification

```bash
find /Users/tinnguyen/vesper-team-skills -name SKILL.md -type f | wc -l  # 100
python3 - <<'PY'  # 100 records, including case-insensitive macOS path behavior
from pathlib import Path
print(len(list(Path("/Users/tinnguyen/vesper-team-skills").rglob("SKILL.md"))))
PY
find /Users/tinnguyen/vesper-team-skills -path '*/SKILL.md' -type f | rg '/(archive|backups)/|commands/(skill|SKILL)\\.md|gstack/browse/SKILL.md|openclaw-plugin/skills/slash-commands/SKILL.md'  # no output
test ! -f /Users/tinnguyen/vesper-team-skills/commands/skill.md
```

## Active Skills Kept

| # | Skill root | Name | Lines |
|---:|---|---|---:|
| 1 | `1password-agent` | `1password-agent` | 171 |
| 2 | `3-layer-memory` | `3-layer-memory` | 288 |
| 3 | `agent-browser` | `agent-browser` | 223 |
| 4 | `agent-changelog` | `agent-changelog` | 155 |
| 5 | `agent-native-architecture` | `agent-native-architecture` | 188 |
| 6 | `agent-policy-engine` | `agent-policy-engine` | 254 |
| 7 | `agent-supervisor` | `agent-supervisor` | 253 |
| 8 | `api-and-interface-design` | `api-and-interface-design` | 294 |
| 9 | `auto-upkeep-review-skills` | `auto-upkeep-review-skills` | 131 |
| 10 | `babysit-pr` | `babysit-pr` | 185 |
| 11 | `browser-testing-with-devtools` | `browser-testing-with-devtools` | 317 |
| 12 | `build-electron-features` | `build-electron-features` | 358 |
| 13 | `ci-cd-and-automation` | `ci-cd-and-automation` | 390 |
| 14 | `claude-code-hooks` | `claude-code-hooks` | 466 |
| 15 | `claude-md-improver` | `claude-md-improver` | 179 |
| 16 | `code-mode-porting` | `code-mode-porting` | 110 |
| 17 | `code-review-and-quality` | `code-review-and-quality` | 347 |
| 18 | `codex` | `codex` | 195 |
| 19 | `context-engineering` | `context-engineering` | 289 |
| 20 | `create-agent-skills` | `create-agent-skills` | 299 |
| 21 | `debugging-and-error-recovery` | `debugging-and-error-recovery` | 300 |
| 22 | `deprecation-and-migration` | `deprecation-and-migration` | 206 |
| 23 | `dispatch` | `dispatch` | 196 |
| 24 | `documentation-and-adrs` | `documentation-and-adrs` | 278 |
| 25 | `doubt-driven-development` | `doubt-driven-development` | 243 |
| 26 | `edit-with-ai-pattern` | `edit-with-ai-pattern` | 313 |
| 27 | `electron-bun-test-reviewer` | `electron-bun-test-reviewer` | 127 |
| 28 | `electron-cdp-testing` | `electron-cdp-testing` | 68 |
| 29 | `electron-performance-hardening` | `electron-performance-hardening` | 66 |
| 30 | `electron-ui-inspector` | `electron-ui-inspector` | 93 |
| 31 | `extreme-software-optimization` | `extreme-software-optimization` | 160 |
| 32 | `feature-specification` | `feature-specification` | 702 |
| 33 | `ffmpeg` | `ffmpeg` | 258 |
| 34 | `frontend-design` | `frontend-design` | 147 |
| 35 | `frontend-ui-engineering` | `frontend-ui-engineering` | 328 |
| 36 | `gemini-imagegen` | `gemini-imagegen` | 237 |
| 37 | `gestalt-frontend-design` | `gestalt-frontend-design` | 163 |
| 38 | `git-workflow-and-versioning` | `git-workflow-and-versioning` | 300 |
| 39 | `git-worktree` | `git-worktree` | 302 |
| 40 | `github-credential-hardening` | `github-credential-hardening` | 102 |
| 41 | `github-intel` | `github-intel` | 308 |
| 42 | `github-sync` | `github-sync` | 168 |
| 43 | `goal-instruction-docs` | `goal-instruction-docs` | 293 |
| 44 | `gstack` | `gstack` | 254 |
| 45 | `heartbeat-implementer` | `heartbeat-implementer` | 470 |
| 46 | `hermes-skill-library-management` | `hermes-skill-library-management` | 148 |
| 47 | `idea-refine` | `idea-refine` | 178 |
| 48 | `incremental-implementation` | `incremental-implementation` | 245 |
| 49 | `interview-me` | `interview-me` | 225 |
| 50 | `last30days` | `last30days` | 391 |
| 51 | `last7days` | `last7days` | 243 |
| 52 | `llm-wiki-maintainer` | `llm-wiki-maintainer` | 231 |
| 53 | `mcp-builder` | `mcp-builder` | 328 |
| 54 | `messaging-integration` | `messaging-integration` | 684 |
| 55 | `meta-agent-harness-optimizer` | `meta-agent-harness-optimizer` | 139 |
| 56 | `model-shaped-harness` | `model-shaped-harness` | 206 |
| 57 | `observability-and-instrumentation` | `observability-and-instrumentation` | 203 |
| 58 | `performance-optimization` | `performance-optimization` | 350 |
| 59 | `planning-and-task-breakdown` | `planning-and-task-breakdown` | 223 |
| 60 | `playwright-recording` | `playwright-recording` | 469 |
| 61 | `rails-best-practices-core` | `rails-best-practices-core` | 100 |
| 62 | `ralph-loop` | `ralph-loop` | 721 |
| 63 | `ralph-loop/skills/commit` | `commit` | 160 |
| 64 | `rclone` | `rclone` | 150 |
| 65 | `reducing-entropy` | `reducing-entropy` | 66 |
| 66 | `remotion` | `remotion` | 213 |
| 67 | `repeatedly-apply-skill` | `repeatedly-apply-skill` | 130 |
| 68 | `repo-deep-dive` | `repo-deep-dive` | 110 |
| 69 | `repo-hygiene` | `repo-hygiene` | 102 |
| 70 | `security-and-hardening` | `security-and-hardening` | 461 |
| 71 | `ship-notes` | `ship-notes` | 419 |
| 72 | `shipping-and-launch` | `shipping-and-launch` | 309 |
| 73 | `skill-creator` | `skill-creator` | 209 |
| 74 | `skill-enricher` | `skill-enricher` | 168 |
| 75 | `social30days` | `social30days` | 237 |
| 76 | `source-driven-development` | `source-driven-development` | 194 |
| 77 | `spec-driven-development` | `spec-driven-development` | 200 |
| 78 | `tdd-failing-tests-loop` | `tdd-failing-tests-loop` | 183 |
| 79 | `teach-impeccable` | `teach-impeccable` | 71 |
| 80 | `test-driven-development` | `test-driven-development` | 383 |
| 81 | `thermo-nuclear-code-quality-review` | `thermo-nuclear-code-quality-review` | 226 |
| 82 | `ui-inspector-ai-handoff` | `ui-inspector-ai-handoff` | 124 |
| 83 | `upgrading-vesper-schedules` | `upgrading-vesper-schedules` | 150 |
| 84 | `using-agent-skills` | `using-agent-skills` | 189 |
| 85 | `verify-and-ship` | `verify-and-ship` | 216 |
| 86 | `vesper-desloppify` | `vesper-desloppify` | 38 |
| 87 | `vesper-dev-instance-manager` | `vesper-dev-instance-manager` | 176 |
| 88 | `vesper-electron-testing` | `vesper-electron-testing` | 94 |
| 89 | `vesper-monolith-refactor` | `vesper-monolith-refactor` | 154 |
| 90 | `vesper-release-distribution` | `vesper-release-distribution` | 256 |
| 91 | `vesper-style` | `vesper-style` | 209 |
| 92 | `vesper-ui-visual-polish` | `vesper-ui-visual-polish` | 146 |
| 93 | `webapp-testing` | `webapp-testing` | 162 |
| 94 | `workflow-compound` | `workflow-compound` | 185 |
| 95 | `workflow-improve-skill` | `workflow-improve-skill` | 152 |
| 96 | `workflow-research` | `workflow-research` | 216 |
| 97 | `workflow-review` | `workflow-review` | 140 |
| 98 | `workflow-work` | `workflow-work` | 135 |
| 99 | `working-backwards` | `working-backwards` | 103 |
| 100 | `working-with-github-cli` | `working-with-github-cli` | 150 |

## Archived In This Pass

| # | Original root | Category | Absorbed into / replacement | Archive path |
|---:|---|---|---|---|
| 1 | `adapt` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/adapt/SKILL.archived.md` |
| 2 | `animate` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/animate/SKILL.archived.md` |
| 3 | `architectural-review` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/architectural-review/SKILL.archived.md` |
| 4 | `arrange` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/arrange/SKILL.archived.md` |
| 5 | `audit` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/audit/SKILL.archived.md` |
| 6 | `bolder` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/bolder/SKILL.archived.md` |
| 7 | `clarify` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/clarify/SKILL.archived.md` |
| 8 | `claude-design-auditor` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/claude-design-auditor/SKILL.archived.md` |
| 9 | `colorize` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/colorize/SKILL.archived.md` |
| 10 | `critique` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/critique/SKILL.archived.md` |
| 11 | `delight` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/delight/SKILL.archived.md` |
| 12 | `distill` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/distill/SKILL.archived.md` |
| 13 | `extract` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/extract/SKILL.archived.md` |
| 14 | `harden` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/harden/SKILL.archived.md` |
| 15 | `normalize` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/normalize/SKILL.archived.md` |
| 16 | `onboard` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/onboard/SKILL.archived.md` |
| 17 | `optimize` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/optimize/SKILL.archived.md` |
| 18 | `overdrive` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/overdrive/SKILL.archived.md` |
| 19 | `polish` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/polish/SKILL.archived.md` |
| 20 | `quieter` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/quieter/SKILL.archived.md` |
| 21 | `theme-contrast-remediator` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/theme-contrast-remediator/SKILL.archived.md` |
| 22 | `typeset` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/typeset/SKILL.archived.md` |
| 23 | `flowy-ui-mockup` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/flowy-ui-mockup/SKILL.archived.md` |
| 24 | `shadcn-component-reference-davinci` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/shadcn-component-reference-davinci/SKILL.archived.md` |
| 25 | `ui-design-pipeline-superdesigner` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/ui-design-pipeline-superdesigner/SKILL.archived.md` |
| 26 | `vesper-premium-ui-remix-davinci` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/vesper-premium-ui-remix-davinci/SKILL.archived.md` |
| 27 | `vesper-reference-ui-pipeline-davinci` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/vesper-reference-ui-pipeline-davinci/SKILL.archived.md` |
| 28 | `vesper-option-action-depth` | frontend/design micro-skill: Narrow UI/design modifier covered by active frontend/Vesper umbrellas. | frontend-design, frontend-ui-engineering, gestalt-frontend-design, vesper-style, vesper-ui-visual-polish | `archive/skills/2026-07-01-skill-garden/vesper-option-action-depth/SKILL.archived.md` |
| 29 | `andrew-kane-gem-writer` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/andrew-kane-gem-writer/SKILL.archived.md` |
| 30 | `dhh` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/dhh/SKILL.archived.md` |
| 31 | `dhh-rails-style` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/dhh-rails-style/SKILL.archived.md` |
| 32 | `dspy-ruby` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/dspy-ruby/SKILL.archived.md` |
| 33 | `rails-hotwire-realtime` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-hotwire-realtime/SKILL.archived.md` |
| 34 | `rails-jobs` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-jobs/SKILL.archived.md` |
| 35 | `rails-migrations` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-migrations/SKILL.archived.md` |
| 36 | `rails-security-multitenancy` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-security-multitenancy/SKILL.archived.md` |
| 37 | `rails-testing` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-testing/SKILL.archived.md` |
| 38 | `rails-webhooks` | Ruby/Rails narrow sibling: Specialized Ruby/Rails path kept recoverable but removed from default trigger surface. | rails-best-practices-core | `archive/skills/2026-07-01-skill-garden/rails-webhooks/SKILL.archived.md` |
| 39 | `code-simplification` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/code-simplification/SKILL.archived.md` |
| 40 | `code-simplifier` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/code-simplifier/SKILL.archived.md` |
| 41 | `sentry-code-simplifier` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/sentry-code-simplifier/SKILL.archived.md` |
| 42 | `code-optimization-agent-skills` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/code-optimization-agent-skills/SKILL.archived.md` |
| 43 | `code-quality-hook` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/code-quality-hook/SKILL.archived.md` |
| 44 | `code-review-expert` | code quality duplicate: Overlaps active review, TDD, performance, and maintainability skills. | code-review-and-quality, test-driven-development, performance-optimization, thermo-nuclear-code-quality-review | `archive/skills/2026-07-01-skill-garden/code-review-expert/SKILL.archived.md` |
| 45 | `heartbeat-implementation` | oversized duplicate: 1438-line implementation monolith superseded by the more compact active heartbeat skill. | heartbeat-implementer | `archive/skills/2026-07-01-skill-garden/heartbeat-implementation/SKILL.archived.md` |
| 46 | `gstack/browse` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `gstack/browse/SKILL.archived.md` |
| 47 | `gstack/plan-ceo-review` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `archive/skills/2026-07-01-skill-garden/gstack/plan-ceo-review/SKILL.archived.md` |
| 48 | `gstack/plan-eng-review` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `archive/skills/2026-07-01-skill-garden/gstack/plan-eng-review/SKILL.archived.md` |
| 49 | `gstack/retro` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `archive/skills/2026-07-01-skill-garden/gstack/retro/SKILL.archived.md` |
| 50 | `gstack/review` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `archive/skills/2026-07-01-skill-garden/gstack/review/SKILL.archived.md` |
| 51 | `gstack/ship` | nested gstack subskill: Nested subskill duplicate; active gstack umbrella remains. | gstack | `archive/skills/2026-07-01-skill-garden/gstack/ship/SKILL.archived.md` |
| 52 | `prd-writing/enterprise` | nested PRD variant: PRD variants are covered by active spec and product-planning skills. | feature-specification, working-backwards | `archive/skills/2026-07-01-skill-garden/prd-writing/enterprise/SKILL.archived.md` |
| 53 | `prd-writing/individual` | nested PRD variant: PRD variants are covered by active spec and product-planning skills. | feature-specification, working-backwards | `archive/skills/2026-07-01-skill-garden/prd-writing/individual/SKILL.archived.md` |
| 54 | `openclaw-plugin/skills/slash-commands` | nested plugin command skill: OpenClaw command helper is too narrow for default repo skill surface. | openclaw plugin docs | `openclaw-plugin/skills/slash-commands/SKILL.archived.md` |
| 55 | `commands/skill.md` | command file case-insensitive collision: Lowercase command file matched SKILL.md on macOS and inflated the active skill count. | commands/skills.md or built-in skill invocation | `archive/skills/2026-07-01-skill-garden/commands/skill-command.archived.md` |
| 56 | `agentic-html-video-workflows` | media workflow overlap: Narrow media path covered by the retained media primitives. | ffmpeg, playwright-recording, remotion | `archive/skills/2026-07-01-skill-garden/agentic-html-video-workflows/SKILL.archived.md` |
| 57 | `apple-notes` | niche utility: Useful only in specialized personal environments; archived out of the shared default surface. | manual restore when needed | `archive/skills/2026-07-01-skill-garden/apple-notes/SKILL.archived.md` |
| 58 | `claudemd-reviewer` | duplicate docs reviewer: Covered by the retained CLAUDE.md improver. | claude-md-improver | `archive/skills/2026-07-01-skill-garden/claudemd-reviewer/SKILL.archived.md` |
| 59 | `compound-docs` | workflow overlap: Knowledge capture is covered by workflow-compound and llm-wiki-maintainer. | workflow-compound, llm-wiki-maintainer | `archive/skills/2026-07-01-skill-garden/compound-docs/SKILL.archived.md` |
| 60 | `every-style-editor` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/every-style-editor/SKILL.archived.md` |
| 61 | `flowy-flowchart` | diagram niche: Narrow diagram output format; default surface keeps broader planning/spec skills. | planning-and-task-breakdown, feature-specification | `archive/skills/2026-07-01-skill-garden/flowy-flowchart/SKILL.archived.md` |
| 62 | `game-level-building-python` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/game-level-building-python/SKILL.archived.md` |
| 63 | `ian-xiaohei-illustrations` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/ian-xiaohei-illustrations/SKILL.archived.md` |
| 64 | `launchpad-remotion` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/launchpad-remotion/SKILL.archived.md` |
| 65 | `news30days` | research overlap: The active research set keeps last30days and social30days; news-only variant archived. | last30days, social30days | `archive/skills/2026-07-01-skill-garden/news30days/SKILL.archived.md` |
| 66 | `repo-deep-dive-interactive` | duplicate repo analysis mode: Interactive variant overlaps retained repo-deep-dive. | repo-deep-dive | `archive/skills/2026-07-01-skill-garden/repo-deep-dive-interactive/SKILL.archived.md` |
| 67 | `scheduled-codebase-review` | review/QA overlap: Covered by active review, testing, shipping, and webapp testing skills. | code-review-and-quality, verify-and-ship, webapp-testing | `archive/skills/2026-07-01-skill-garden/scheduled-codebase-review/SKILL.archived.md` |
| 68 | `skill-qa-release-guardian` | review/QA overlap: Covered by active review, testing, shipping, and webapp testing skills. | code-review-and-quality, verify-and-ship, webapp-testing | `archive/skills/2026-07-01-skill-garden/skill-qa-release-guardian/SKILL.archived.md` |
| 69 | `sales-materials-creator` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/sales-materials-creator/SKILL.archived.md` |
| 70 | `graphics-reverse-engineering-research` | specialized creative/project skill: High-context creative/project-specific workflow; recoverable but not essential default skill. | domain skill can be restored when needed | `archive/skills/2026-07-01-skill-garden/graphics-reverse-engineering-research/SKILL.archived.md` |
| 71 | `qmd-search` | specialized implementation spike: Niche implementation helper not essential to the shared top-100 surface. | source-driven-development, mcp-builder, repo-deep-dive | `archive/skills/2026-07-01-skill-garden/qmd-search/SKILL.archived.md` |
| 72 | `pi-autoresearch-bootstrap` | specialized implementation spike: Niche implementation helper not essential to the shared top-100 surface. | source-driven-development, mcp-builder, repo-deep-dive | `archive/skills/2026-07-01-skill-garden/pi-autoresearch-bootstrap/SKILL.archived.md` |
| 73 | `setup-statusline-advanced` | niche utility: Useful only in specialized personal environments; archived out of the shared default surface. | manual restore when needed | `archive/skills/2026-07-01-skill-garden/setup-statusline-advanced/SKILL.archived.md` |
| 74 | `backups/hermes-top10-skills-20260630-200956/agentic-html-video-workflows` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/agentic-html-video-workflows/SKILL.archived.md` |
| 75 | `backups/hermes-top10-skills-20260630-200956/code-optimization-agent-skills` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/code-optimization-agent-skills/SKILL.archived.md` |
| 76 | `backups/hermes-top10-skills-20260630-200956/codex` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/codex/SKILL.archived.md` |
| 77 | `backups/hermes-top10-skills-20260630-200956/extreme-software-optimization` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/extreme-software-optimization/SKILL.archived.md` |
| 78 | `backups/hermes-top10-skills-20260630-200956/goal-instruction-docs` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/goal-instruction-docs/SKILL.archived.md` |
| 79 | `backups/hermes-top10-skills-20260630-200956/graphics-reverse-engineering-research` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/graphics-reverse-engineering-research/SKILL.archived.md` |
| 80 | `backups/hermes-top10-skills-20260630-200956/hermes-skill-library-management` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/hermes-skill-library-management/SKILL.archived.md` |
| 81 | `backups/hermes-top10-skills-20260630-200956/ian-xiaohei-illustrations` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/ian-xiaohei-illustrations/SKILL.archived.md` |
| 82 | `backups/hermes-top10-skills-20260630-200956/repeatedly-apply-skill` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/repeatedly-apply-skill/SKILL.archived.md` |
| 83 | `backups/hermes-top10-skills-20260630-200956/thermo-nuclear-code-quality-review` | backup snapshot: Already a backup copy; renamed manifest to prevent accidental active loading. | current top-level equivalent or archive manifest | `backups/hermes-top10-skills-20260630-200956/thermo-nuclear-code-quality-review/SKILL.archived.md` |

## Notes

- No archived skill was deleted; restoration is a rename/move back to `SKILL.md`.
- The retained set intentionally favors broad workhorse skills, Vesper/Electron operations, agent-platform maintenance, source-driven implementation, testing, GitHub/release workflow, and a small media/research surface.
- Remaining over-500-line active skills are `feature-specification`, `messaging-integration`, and `ralph-loop`; they are retained because they are broad anchors rather than narrow duplicates, but they are good future candidates for progressive-disclosure splitting.
