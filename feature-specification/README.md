# Feature Specification Skill

Write comprehensive feature specifications that give product and engineering teams complete understanding before development.

## What This Skill Does

This skill helps you write feature specifications that answer **five critical questions**:

| Question | Section | Purpose |
|----------|---------|---------|
| **What is it?** | Function Definition | Alignment on scope |
| **How to use?** | Usage Guide | UX clarity |
| **Terms & regulations?** | Business Rules & Compliance | Legal/Compliance requirements |
| **Logic behind?** | Algorithms & State Flows | Implementation guide |
| **Impact on others?** | Dependency Analysis | Risk assessment |

## Quick Start

### When to Use

- ✅ Planning a new feature
- ✅ Handoff from product to engineering
- ✅ Refactoring existing features
- ✅ API/feature deprecation
- ✅ Compliance-heavy features
- ✅ Complex business logic

### When NOT to Use

- ❌ Simple UI tweaks (one-line changes)
- ❌ Bug fixes that don't change behavior
- ❌ Configuration-only changes

### Usage

```bash
# In Claude Code, reference the skill:
@/Users/susan/Documents/GitHub/vesper-team-skills/feature-specification/SKILL.md

# Or say:
"Write a feature specification for [feature name]"
"Create a spec for [feature description]"
"Document the logic and impact of [feature]"
```

## Skill Structure

### SKILL.md (Main Skill File)

The complete skill with:
- **Phase 1**: Pre-writing checklist
- **Phase 2**: Full specification template
- **Phase 3**: Quality review checklist
- **Examples**: Payment processing and content moderation

### References

| File | Purpose |
|------|---------|
| `references/checklist-quickref.md` | One-page cheat sheet for quick reference |
| `references/example-complete-spec.md` | Full example: Subscription Pause feature |

## Specification Structure

```markdown
# Feature Specification: [Name]

## 1. What Is It
- Function definition
- Purpose & value
- User personas

## 2. How To Use
- Step-by-step guide
- Input/output specification
- Error scenarios

## 3. Terms & Regulations
- Business rules table
- Terms & conditions
- Regulatory compliance
- Security requirements

## 4. Logic Behind
- Algorithms/pseudocode
- Decision matrices
- State machines
- Business logic rules

## 5. Impact On Other Functions
- Dependencies
- Database changes
- API changes
- Breaking changes
- Testing impact
```

## Example Output

See [`references/example-complete-spec.md`](references/example-complete-spec.md) for a complete, real-world example of a Subscription Pause feature specification.

## Key Features

### Writing Features Checklist

Before writing, verify you have:
- ✅ Feature name and problem statement
- ✅ Target users identified
- ✅ Success criteria defined
- ✅ Stakeholder alignment
- ✅ Dependencies identified
- ✅ Business rules documented
- ✅ Regulatory requirements known

### Comprehensive Description

Each specification includes:
- **What**: Clear function definition
- **How**: Step-by-step usage guide
- **Terms**: Business rules and compliance
- **Logic**: Algorithms and decision flows
- **Impact**: Dependencies and side effects

### Quality Gates

Before completing:
- ✅ All 5 sections filled
- ✅ Non-technical stakeholders understand it
- ✅ Engineers can implement without questions
- ✅ Edge cases covered
- ✅ Cross-functional review complete

## Integration

### With PRD Skills

Use this skill **after** PRD creation to expand into implementation-ready specifications:

```
PRD (Product) → Feature Spec (Engineering) → Implementation
```

### With Start-New-Feature

The output of this skill feeds directly into `/start-new-feature` command as the feature description.

## File Locations

Save specifications to:
```
docs/specs/[feature-name]-spec.md
```

## Benefits

| Stakeholder | Benefit |
|-------------|---------|
| Product Managers | Clear scope, compliance captured |
| Engineers | Complete implementation guide |
| QA | Test scenarios and edge cases |
| Compliance | Regulatory requirements documented |
| Support | Understanding of user flows |

---

*"A complete specification prevents surprises during development."*
