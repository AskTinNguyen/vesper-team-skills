---
name: architectural-review
description: Review architectural drawings, floor plans, and interior design proposals. Use when analyzing building layouts, room proportions, spatial flow, feng shui considerations, or providing design feedback. Triggers on "review floor plan", "check layout", "analyze design", "feng shui review", or when working with architectural PDFs/images.
---

# Architectural Review Skill

Review residential floor plans, interior design proposals, and architectural drawings with a focus on livability, spatial efficiency, and design principles.

## When to Use

- Reviewing floor plans or layout drawings
- Analyzing room proportions and sizes
- Checking spatial flow and circulation
- Evaluating feng shui considerations
- Comparing design iterations
- Providing feedback to architects/designers

## Review Framework

### 1. Initial Assessment

When given a floor plan or design document:

```markdown
## Design Overview

**Project:** [Name/Location]
**Type:** [Villa/Apartment/House]
**Total Area:** [sqm/sqft]
**Floors:** [Number]
**Bedrooms/Bathrooms:** [X bed / Y bath]

**First Impressions:**
- [Key observations]
- [Notable features]
- [Potential concerns]
```

### 2. Spatial Analysis

Evaluate each space against standard guidelines:

| Room Type | Recommended Min Size | Ideal Proportion |
|-----------|---------------------|------------------|
| Master Bedroom | 14-20 sqm | 1:1.2 to 1:1.5 |
| Secondary Bedroom | 10-14 sqm | 1:1 to 1:1.3 |
| Living Room | 20-35 sqm | 1:1.5 to 1:2 |
| Kitchen | 10-18 sqm | Varies by layout |
| Dining Room | 12-20 sqm | 1:1 to 1:1.5 |
| Bathroom (Full) | 5-9 sqm | 1:1.2 to 1:1.8 |
| Bathroom (Half) | 2-4 sqm | 1:1 to 1:1.5 |

### 3. Circulation & Flow

Check for:
- **Primary circulation:** Clear paths between main areas
- **Service circulation:** Kitchen to dining, utility access
- **Privacy gradient:** Public → Semi-private → Private zones
- **Natural light access:** Windows, skylights, light wells
- **Cross-ventilation:** Opposing openings for airflow

### 4. Feng Shui Considerations

Key principles to evaluate:

**Entry (Ming Tang):**
- [ ] Clear, welcoming entrance
- [ ] No direct line to back door (chi escaping)
- [ ] Adequate foyer space

**Living Areas:**
- [ ] Command position for main seating
- [ ] Balanced furniture arrangement
- [ ] Natural light optimization

**Bedrooms:**
- [ ] Bed in command position (see door, not directly in line)
- [ ] Solid wall behind headboard
- [ ] No beams over bed
- [ ] Mirror placement (not facing bed)

**Kitchen:**
- [ ] Stove not directly facing sink (fire vs water)
- [ ] Cook can see entrance
- [ ] Adequate ventilation

**Bathrooms:**
- [ ] Not directly visible from entry
- [ ] Doors kept closed
- [ ] Not above main entrance

### 5. Practical Considerations

**Storage:**
- Closet space per bedroom
- Kitchen storage adequacy
- Utility/linen storage
- Outdoor storage (if applicable)

**Utilities:**
- Plumbing stack efficiency
- Electrical panel access
- HVAC considerations
- Water heater location

**Future-proofing:**
- Accessibility considerations
- Expansion possibilities
- Technology infrastructure

## Output Format

### Design Review Report

```markdown
# Architectural Review: [Project Name]

**Reviewer:** Tin Sidekick
**Date:** [Date]
**Document:** [File reference]

---

## Executive Summary

[2-3 sentence overview of the design quality and key recommendations]

---

## Strengths ✅

1. **[Strength 1]:** [Description]
2. **[Strength 2]:** [Description]
3. **[Strength 3]:** [Description]

---

## Areas for Improvement ⚠️

### Priority 1: [Issue]
- **Location:** [Where in the plan]
- **Concern:** [What's the problem]
- **Recommendation:** [Suggested fix]

### Priority 2: [Issue]
- **Location:** [Where in the plan]
- **Concern:** [What's the problem]
- **Recommendation:** [Suggested fix]

---

## Room-by-Room Analysis

### [Room Name]
- **Size:** [X sqm] — [Adequate/Small/Generous]
- **Proportion:** [Ratio] — [Good/Could improve]
- **Natural Light:** [Assessment]
- **Flow:** [How it connects to other spaces]
- **Notes:** [Specific observations]

---

## Feng Shui Assessment

| Area | Status | Notes |
|------|--------|-------|
| Entry | ✅/⚠️/❌ | [Notes] |
| Living | ✅/⚠️/❌ | [Notes] |
| Master Bed | ✅/⚠️/❌ | [Notes] |
| Kitchen | ✅/⚠️/❌ | [Notes] |

---

## Questions for Designer

1. [Question about specific design choice]
2. [Clarification needed]
3. [Alternative consideration]

---

## Recommended Next Steps

1. [ ] [Action item 1]
2. [ ] [Action item 2]
3. [ ] [Action item 3]
```

## Working with Design Files

### PDF Floor Plans
```bash
# Extract images from PDF for analysis
pdftoppm -png design.pdf output

# Or use pdfimages
pdfimages -png design.pdf output
```

### Creating Annotated Feedback
Use **excalidraw** skill to create visual markup:
- Red: Issues/concerns
- Yellow: Suggestions
- Green: Approved elements
- Blue: Questions

### Tracking Iterations

Create a design log in the project folder:
```markdown
# Design Iteration Log

## V1 - [Date]
- Initial proposal received
- [Key feedback points]

## V2 - [Date]
- Changes made: [list]
- Remaining issues: [list]
```

## References

- `references/room-sizes.md` - Detailed room size guidelines
- `references/feng-shui-guide.md` - Comprehensive feng shui principles
- `references/checklist.md` - Quick review checklist

## Tips

1. **Always start with understanding the client's priorities** - Feng shui vs pure functionality vs aesthetics
2. **Consider the local context** - Climate, culture, building codes
3. **Think about daily routines** - Morning flow, evening relaxation, hosting guests
4. **Don't forget outdoor spaces** - Balconies, gardens, terraces are part of the living experience
