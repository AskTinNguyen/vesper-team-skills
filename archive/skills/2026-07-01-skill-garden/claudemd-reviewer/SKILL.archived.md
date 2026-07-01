---
name: claudemd-reviewer
description: Review and analyze CLAUDE.md hierarchy in repositories. This skill should be used when reviewing the structure of ancestor and descendant CLAUDE.md files in a codebase, auditing monorepo setups, or optimizing context loading for Claude Code. Triggers on "review CLAUDE.md", "audit CLAUDE.md structure", "analyze CLAUDE hierarchy", or "check CLAUDE.md setup".
---

# CLAUDE.md Hierarchy Reviewer

Analyze and optimize CLAUDE.md file structures in repositories based on the official loading behavior from Claude Code.

## Background: How CLAUDE.md Loading Works

Per Boris Cherny (Claude Code Lead @ Anthropic):

> - **Ancestor CLAUDE.md's** are loaded into context automatically on startup
> - **Descendant CLAUDE.md's** are loaded *lazily* only when Claude reads/writes files in a folder the CLAUDE.md is in. Think of it as a special kind of skill.

### Loading Behavior

| Type | When Loaded | Best For |
|------|-------------|----------|
| **Ancestor** | Always on startup | Global standards, project overview |
| **Descendant** | When accessing files in that folder | Module-specific, package-specific instructions |

## Review Process

### Step 1: Discover CLAUDE.md Files

Scan the repository for all CLAUDE.md (and AGENTS.md) files:

```bash
find . -name "CLAUDE.md" -o -name "AGENTS.md" | sort
```

Map each file to its role:
- **Root level** = Ancestor (always loaded)
- **Subdirectories** = Descendant (lazy loaded)

### Step 2: Analyze Hierarchy Structure

Create a visual map of the hierarchy:

```
/repo/
├── CLAUDE.md                    # 🟢 ANCESTOR - Always loaded
├── packages/
│   ├── frontend/
│   │   └── CLAUDE.md            # 🔵 DESCENDANT - Lazy loaded
│   ├── backend/
│   │   └── CLAUDE.md            # 🔵 DESCENDANT - Lazy loaded
│   └── shared/
│       └── CLAUDE.md            # 🔵 DESCENDANT - Lazy loaded
└── scripts/
    └── CLAUDE.md                # 🔵 DESCENDANT - Lazy loaded
```

### Step 3: Audit Content Distribution

For each CLAUDE.md file, evaluate:

#### Ancestor (Root) Should Contain:
- [ ] Project overview and mission
- [ ] Global coding standards
- [ ] Common commands and scripts
- [ ] Team conventions
- [ ] Technology stack overview
- [ ] Links to documentation

#### Ancestor Should NOT Contain:
- [ ] Package-specific implementation details
- [ ] Module-specific API documentation
- [ ] Framework-specific patterns (unless universal)
- [ ] Environment-specific setup (put in descendants)

#### Descendant Should Contain:
- [ ] Module/package-specific instructions
- [ ] Framework-specific patterns for that area
- [ ] Local testing commands
- [ ] APIs and services used by that module
- [ ] Dependencies specific to that area

#### Descendant Should NOT Contain:
- [ ] Duplicate content from ancestor
- [ ] Global project information
- [ ] Instructions that apply repo-wide

### Step 4: Check for Anti-Patterns

#### ❌ Common Issues

1. **Bloated Root CLAUDE.md**
   - Root file > 5000 words
   - Contains package-specific details
   - Duplicates info in descendants

2. **Missing Descendants**
   - Large packages with no CLAUDE.md
   - Complex modules without specific guidance

3. **Conflicting Instructions**
   - Descendant contradicts ancestor
   - Inconsistent coding standards

4. **Redundant Content**
   - Same instructions in multiple files
   - Copy-pasted sections

5. **Orphaned Descendants**
   - CLAUDE.md in rarely accessed folders
   - Instructions never trigger

### Step 5: Generate Report

Create a structured report:

```markdown
# CLAUDE.md Hierarchy Review Report

## Summary
- Total CLAUDE.md files: X
- Ancestor files: Y
- Descendant files: Z

## Hierarchy Map
[Visual tree structure]

## Findings

### ✅ Good Practices
- [List what's working well]

### ⚠️ Warnings
- [List potential improvements]

### ❌ Issues
- [List problems to fix]

## Recommendations
1. [Specific action item]
2. [Specific action item]
3. [Specific action item]

## Suggested Structure
[Proposed optimal structure if changes needed]
```

### Step 6: Provide Optimization Suggestions

For each issue found, provide:
1. **What to move** - Specific content to relocate
2. **Where to move it** - Target file path
3. **Why** - Benefit of the change

## Best Practice Reference

### Ideal Monorepo Structure

```
/monorepo/
├── CLAUDE.md               # ~1000-2000 words max
│   ├── Project overview
│   ├── Tech stack
│   ├── Coding standards
│   ├── Common commands
│   └── Links to docs
│
├── packages/
│   ├── web/
│   │   └── CLAUDE.md       # React/Next.js specific
│   ├── api/
│   │   └── CLAUDE.md       # Node/Python specific
│   ├── mobile/
│   │   └── CLAUDE.md       # React Native/Flutter specific
│   └── shared/
│       └── CLAUDE.md       # Shared utilities specific
│
├── infra/
│   └── CLAUDE.md           # Terraform/K8s specific
│
└── scripts/
    └── CLAUDE.md           # Build/deploy scripts specific
```

### Word Count Guidelines

| File Type | Recommended | Maximum |
|-----------|-------------|---------|
| Root CLAUDE.md | 500-2000 | 5000 |
| Descendant CLAUDE.md | 200-1000 | 2000 |

## Usage Examples

### Example 1: Review Current Repo
```
Review the CLAUDE.md structure in this repository and provide recommendations
```

### Example 2: Audit Specific Package
```
Analyze the CLAUDE.md hierarchy in the packages/ directory
```

### Example 3: Create Missing Descendants
```
Identify packages that need their own CLAUDE.md and draft them
```

## Output Checklist

When completing a review, ensure:
- [ ] All CLAUDE.md files discovered and mapped
- [ ] Hierarchy visualized
- [ ] Content distribution analyzed
- [ ] Anti-patterns identified
- [ ] Specific recommendations provided
- [ ] Word counts checked
- [ ] Report generated
