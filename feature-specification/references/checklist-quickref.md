# Feature Specification Quick Reference

One-page cheat sheet for writing feature specifications.

---

## Pre-Writing Checklist

Before writing, confirm you have:

```
□ Feature name and problem statement
□ Target users identified
□ Success criteria defined
□ Stakeholder alignment (PM, Eng, Design)
□ Dependencies identified
□ Affected systems listed
□ Business rules documented (or SME available)
□ Regulatory requirements known
□ Edge cases considered
```

---

## The 5 Sections (At a Glance)

### 1. What Is It
- One-sentence definition
- Plain English explanation
- In scope / Out of scope table
- User personas

### 2. How To Use
- Primary user flow (step-by-step)
- Input/output specification
- Alternative scenarios
- Error scenarios table

### 3. Terms & Regulations
- Business rules table (ID, Rule, When, Result)
- Terms & conditions
- Compliance requirements (GDPR, etc.)
- Security requirements

### 4. Logic Behind
- Algorithm/pseudocode
- Decision matrix
- State machine diagram
- Data transformations
- Integration logic

### 5. Impact On Other Functions
- Dependencies (this depends on)
- Dependents (depends on this)
- Database schema changes
- API changes
- Breaking changes
- Testing impact
- Documentation impact

---

## Quick Template

```markdown
# Feature Spec: [Name]

## 1. What Is It
**Definition:** [One sentence]
**Scope:** [In/Out table]

## 2. How To Use
**Flow:** [Step 1] → [Step 2] → [Result]
**Inputs:** [Field | Type | Validation]
**Errors:** [Scenario | Message | Recovery]

## 3. Terms & Regulations
| Rule | When | Result |
|------|------|--------|
| [Rule] | [Trigger] | [Action] |

**Compliance:** [GDPR/SOC2/etc requirements]

## 4. Logic Behind
```
IF [condition]:
    [action]
```
**State:** [State diagram]
**Calculations:** [Formula]

## 5. Impact
**Depends on:** [System | Critical? | If down]
**Changes:** [DB/API/UI modifications]
**Breaking:** [Change | Migration]
```

---

## Quality Gates

Before completing:

```
□ All 5 sections filled
□ Non-technical stakeholders understand it
□ Engineers can implement without questions
□ Edge cases covered
□ Cross-functional review complete
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Vague requirements | Add specific examples |
| Missing error cases | Add error scenario table |
| Implicit dependencies | List all dependencies explicitly |
| No compliance check | Add regulatory section |
| Unclear logic | Add pseudocode or decision matrix |
| No impact analysis | Document all affected systems |

---

## When to Use This Skill

| Scenario | Use? |
|----------|------|
| New feature development | ✅ Yes |
| Complex bug fix | ✅ Yes |
| API changes | ✅ Yes |
| Refactoring | ✅ Yes |
| Simple UI tweak | ❌ No (overkill) |
| One-line fix | ❌ No (overkill) |
