# Improvement Categories

8 categories of improvements, each mapped to affected rubric criteria and typical severity levels. Use this when converting audit findings into prioritized improvement actions in Phase 4.

## Category Overview

| # | Category | Typical Severity | Primary Criteria Affected |
|---|----------|-----------------|--------------------------|
| 1 | Frontmatter Fixes | Important–Critical | Structure, Description |
| 2 | Structural Reorganization | Important–Critical | Structure, Progressive Disclosure |
| 3 | Content Accuracy | Critical–Important | Accuracy & Freshness |
| 4 | Example Enhancement | Important–Minor | Examples & Patterns |
| 5 | Clarity Improvements | Important–Minor | Actionability, Conciseness |
| 6 | Cross-File Consistency | Important–Minor | Structure, Progressive Disclosure |
| 7 | Freshness Updates | Critical–Important | Accuracy & Freshness |
| 8 | Integration Gaps | Important–Minor | Actionability, Examples |

---

## 1. Frontmatter Fixes

Corrections to the YAML frontmatter block in SKILL.md.

**Common fixes:**
- Add missing `name:` or fix name/directory mismatch
- Rewrite `description:` to include what + when + trigger phrases
- Change voice from first person to third person ("Use when...")
- Adjust `alwaysAllow:` to match actual tool usage (not overly permissive)

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| Missing or invalid name | Critical |
| Name/directory mismatch | Critical |
| No description | Critical |
| Description missing "when to use" | Important |
| Missing trigger phrases | Important |
| Wrong voice (first person) | Minor |
| alwaysAllow too broad | Important |

**Effort:** S (most are single-field edits)

---

## 2. Structural Reorganization

Moving content to the right files, splitting monoliths, creating missing directories.

**Common fixes:**
- Split SKILL.md over 500 lines into SKILL.md + references/ + workflows/
- Move domain knowledge from workflows/ to references/
- Move procedures from SKILL.md to workflows/
- Move large code blocks from markdown to scripts/
- Create missing references/ or workflows/ directories
- Add `<required_reading>` tags to workflows that need reference files
- Remove orphaned files not referenced by anything

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| SKILL.md over 500 lines (monolith) | Critical |
| Procedures embedded in SKILL.md (should be workflows/) | Important |
| Domain knowledge in workflows/ (should be references/) | Important |
| Large code blocks in markdown (should be scripts/) | Important |
| Missing directory that should exist | Important |
| Orphaned file not referenced | Minor |
| Content slightly misplaced but findable | Minor |

**Effort:** M–L (requires content moves across files)

---

## 3. Content Accuracy

Fixing factually incorrect claims about external tools, APIs, or frameworks.

**Common fixes:**
- Update deprecated API endpoints or parameters
- Fix CLI flags that changed in newer versions
- Update framework patterns to current best practices
- Correct wrong URLs or broken links
- Update version-specific instructions

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| API endpoint removed or fundamentally changed | Critical |
| CLI flag removed or behavior changed | Critical |
| Deprecated pattern still documented as primary | Important |
| Newer alternative exists but old way still works | Minor |
| Broken URL to external docs | Important |
| Minor version mismatch (still compatible) | Minor |

**Effort:** S–M (per claim, but may be many claims)

---

## 4. Example Enhancement

Adding, fixing, or improving examples.

**Common fixes:**
- Replace foo/bar/baz with realistic data
- Add expected output to existing examples
- Add error handling examples
- Add end-to-end example if missing
- Add edge case examples
- Fix examples that reference deprecated APIs

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| No examples at all | Critical |
| Examples would fail if followed | Critical |
| Examples use only placeholder data | Important |
| Missing error handling examples | Important |
| Missing expected output | Minor |
| Could use more edge case coverage | Minor |

**Effort:** M (writing good examples takes care)

---

## 5. Clarity Improvements

Making instructions more specific, concrete, and verifiable.

**Common fixes:**
- Replace vague instructions with specific steps ("configure appropriately" → "run `./configure --prefix=/usr/local`")
- Replace placeholder paths with real paths
- Add verifiable outcomes to steps ("you should see..." / "the file now contains...")
- Make success criteria testable
- Replace paragraphs with scannable tables/lists
- Remove filler sentences that don't add value
- Fix inconsistent terminology

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| Critical step is vague/unexecutable | Critical |
| Placeholder paths in important instructions | Important |
| Success criteria untestable ("user is satisfied") | Important |
| Verbose section that could be a table | Minor |
| Filler sentence | Minor |
| Inconsistent term usage | Minor |

**Effort:** S–M (per fix)

---

## 6. Cross-File Consistency

Ensuring all files reference each other correctly and content isn't duplicated.

**Common fixes:**
- Fix broken references (SKILL.md mentions a file that doesn't exist)
- Remove duplicate content across files (same info in SKILL.md and references/)
- Align terminology between SKILL.md and workflow files
- Add missing cross-references (workflow doesn't point to its reference file)
- Fix routing table entries that point to wrong files

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| SKILL.md references a file that doesn't exist | Critical |
| Routing table entry points to wrong file | Critical |
| Same content duplicated in 2+ files | Important |
| Workflow missing `<required_reading>` for reference it needs | Important |
| Inconsistent terminology between files | Minor |
| Missing cross-reference (content exists but isn't linked) | Minor |

**Effort:** S–M

---

## 7. Freshness Updates

Updating content based on external changes discovered by the Freshness Verifier.

**Common fixes:**
- Update API endpoints/parameters to current version
- Update CLI commands to current syntax
- Replace deprecated framework patterns with current ones
- Update version numbers and compatibility info
- Refresh URLs that redirected or changed

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| Following the skill would produce errors | Critical |
| Deprecated pattern still used as primary approach | Important |
| Newer approach available but old one still works | Minor |
| Version number slightly outdated | Minor |

**Effort:** S–M (per update)

**Note:** Freshness updates often overlap with Content Accuracy (Category 3). The distinction: Content Accuracy fixes things that were always wrong; Freshness Updates fix things that became wrong over time.

---

## 8. Integration Gaps

Missing content that connects this skill to the broader ecosystem.

**Common fixes:**
- Add "Next Step" section routing to related skills
- Document how this skill chains with other skills
- Add installation/setup section for dependencies
- Add configuration section for required settings
- Add error handling / troubleshooting section
- Add anti-patterns section
- Add testing/verification section

**Severity mapping:**
| Issue | Severity |
|-------|----------|
| Missing setup that would cause skill to fail | Critical |
| No error handling guidance for common failures | Important |
| Missing anti-patterns section | Important |
| No "Next Step" or pipeline routing | Minor |
| Missing testing/verification section | Minor |
| No mention of related skills | Minor |

**Effort:** M–L (new sections require writing)

---

## Severity → Priority Mapping

| Severity | Priority | Action |
|----------|----------|--------|
| Critical | P1 | Must fix — skill is broken or misleading without it |
| Important | P2 | Should fix — meaningfully improves skill quality |
| Minor | P3 | Nice to fix — polish and refinement |

## Ordering Within Severity

Within the same severity level, prioritize by:
1. **Score impact** — fixes that improve more rubric points first
2. **Effort** — lower effort first (S before M before L)
3. **Blast radius** — fixes that affect multiple criteria first

## Improvement Action Template

Each improvement action should specify:

```
### [Action Title]
- **Category**: [1-8 from above]
- **Severity**: Critical / Important / Minor
- **File**: [path to file]
- **Criterion**: [which rubric criterion this improves]
- **Impact**: +N points (estimated)
- **Effort**: S / M / L
- **Before**: [exact current text]
- **After**: [replacement text]
- **Reason**: [why this change improves the skill]
```
