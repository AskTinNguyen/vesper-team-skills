---
name: jeff-plan
description: Generate comprehensive technical plan using Jeff's methodology
argument-hint: "<feature description>"
---

# /jeff-plan — Planning Phase

Generate a comprehensive technical plan for a feature using Jeffrey Emanuel's methodology.

## Usage
```
/jeff-plan <feature description>
```

## What This Does

1. **Expand the idea** into a detailed technical specification
2. **Structure** with architecture, modules, data models, APIs
3. **Iterate** through 4-5 refinement rounds
4. **Output** a plan document ready for bead generation

## Process

### Step 1: Read Jeff's Methodology
```
Read: ~/.openclaw/workspace/agents/jeff-agent/knowledge/WORKFLOW_DETAILS.md
Focus on: "Phase 2: Planning"
```

### Step 2: Generate Initial Plan

Use this prompt template:
```
I want to build: $ARGUMENTS

Create a comprehensive technical plan including:
1. Executive summary (what we're building, why)
2. Architecture overview with mermaid diagrams
3. Module-by-module breakdown with responsibilities
4. Data models and API contracts
5. Testing strategy
6. Performance considerations
7. Risks and mitigations
8. Non-goals (explicit exclusions)
9. Open questions to resolve

Be thorough — this plan will be converted into atomic tasks for AI agents.
Target: 5,000-15,000 words depending on scope.
```

### Step 3: Iterate (4-5 rounds)

After initial plan, run these critique prompts:
- "What edge cases are missing?"
- "How does this handle [specific scenario]?"
- "Add explicit acceptance criteria for each module"
- "What would a senior engineer question?"
- "Final polish — ensure every module has clear inputs/outputs/deps"

### Step 4: Save Plan

Save to: `plans/PLAN_[FEATURE_NAME].md`

Format:
```markdown
# PLAN: [Feature Name]
Generated: [Date]
Status: Draft | Ready for Beads

[Plan content...]

## Next Steps
Run `/jeff-beads plans/PLAN_[FEATURE_NAME].md` to generate tasks.
```

## Output

Announce when complete:
```
✅ Plan generated: plans/PLAN_[feature].md
- Sections: [count]
- Estimated beads: [rough count]
- Ready for: /jeff-beads
```

## Reference
- Full methodology: `~/.openclaw/workspace/agents/jeff-agent/AGENTS.md`
- Workflow details: `~/.openclaw/workspace/agents/jeff-agent/knowledge/WORKFLOW_DETAILS.md`
