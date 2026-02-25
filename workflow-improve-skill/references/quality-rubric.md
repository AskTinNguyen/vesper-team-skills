# Quality Rubric: Skill Scoring

7 criteria, 100 points total. Each criterion has 4 scoring levels. Grade scale: A (90-100), B (70-89), C (50-69), D (30-49), F (0-29).

## Agent-to-Criterion Mapping

| Criterion | Weight | Primary Agent | Supporting Agent |
|-----------|--------|--------------|-----------------|
| Structure & Conformance | 15 pts | Structure Auditor | Progressive Disclosure |
| Description Quality | 10 pts | Structure Auditor | Ecosystem Consistency |
| Content Accuracy & Freshness | 20 pts | Freshness Verifier | Gap Analyst |
| Actionability | 20 pts | Content Quality | Gap Analyst |
| Progressive Disclosure | 15 pts | Progressive Disclosure | Structure Auditor |
| Examples & Patterns | 10 pts | Content Quality | Gap Analyst |
| Conciseness | 10 pts | Content Quality | Progressive Disclosure |

---

## 1. Structure & Conformance (15 points)

Evaluates YAML frontmatter, file organization, required sections, and XML/markdown structure.

**15 points — Excellent:**
- Valid frontmatter with name (matches directory), description (what + when + triggers), appropriate alwaysAllow
- SKILL.md under 500 lines
- All referenced files exist on disk, no orphaned files
- Required sections present: objective/essential_principles, success_criteria, process/routing
- XML tags properly closed (if used), consistent formatting

**11 points — Good:**
- Frontmatter valid but description missing trigger phrases or "when to use"
- SKILL.md under 500 lines but could be tighter
- One or two referenced files missing or one orphaned file
- Most required sections present

**7 points — Fair:**
- Frontmatter incomplete (missing fields or mismatched name)
- SKILL.md over 500 lines
- Multiple broken references or orphaned files
- Missing key sections (no success_criteria or no process)

**3 points — Poor:**
- Frontmatter missing or invalid
- No file organization (everything in one file)
- Fundamental structural issues

---

## 2. Description Quality (10 points)

Evaluates the frontmatter `description:` field and how discoverable the skill is.

**10 points — Excellent:**
- States WHAT the skill does in one clause
- States WHEN to use it in another clause
- Includes 3+ trigger phrases for discovery
- Third person voice ("Use when..." not "I will...")
- Under 200 characters, dense with meaning

**7 points — Good:**
- States what and when, but trigger phrases are generic
- Slightly verbose or missing one element

**4 points — Fair:**
- States what OR when, not both
- No trigger phrases
- First person or imperative voice

**1 point — Poor:**
- Vague or misleading description
- Doesn't help with discovery at all

---

## 3. Content Accuracy & Freshness (20 points)

Evaluates whether external claims (APIs, CLI flags, framework patterns, URLs) are still accurate.

**20 points — Excellent:**
- All external claims verified as current
- No deprecated patterns or APIs
- Version-specific content matches latest stable version
- All URLs and links resolve
- No outdated recommendations

**15 points — Good:**
- Most claims current, one or two minor outdated references
- No deprecated patterns in critical paths
- URLs mostly resolve

**10 points — Fair:**
- Several outdated references
- One or more deprecated patterns in use
- Some broken URLs or incorrect version info

**5 points — Poor:**
- Major API/CLI changes not reflected
- Deprecated patterns throughout
- Following the skill would produce errors

**0 points — Failing:**
- Skill is fundamentally based on outdated/removed APIs
- Following it would fail completely

---

## 4. Actionability (20 points)

Evaluates whether instructions are concrete, executable, and verifiable.

**20 points — Excellent:**
- Every step has a concrete, executable action
- Commands can be copy-pasted directly
- File paths are real (not `/path/to/` placeholders)
- Each step has a verifiable outcome ("you should see...", "the file now contains...")
- Success criteria are testable (not "user is satisfied")
- Error handling: what to do when things go wrong

**15 points — Good:**
- Most steps concrete and executable
- Minor placeholder paths or vague steps (1-2 instances)
- Most success criteria testable

**10 points — Fair:**
- Mix of concrete and vague steps
- Several placeholder paths or untestable criteria
- Missing error handling guidance

**5 points — Poor:**
- Mostly vague instructions ("configure appropriately", "handle errors")
- Placeholder paths throughout
- No verifiable outcomes

**0 points — Failing:**
- Instructions are theoretical, not actionable
- Cannot be followed without significant interpretation

---

## 5. Progressive Disclosure (15 points)

Evaluates information architecture: is content in the right place?

**15 points — Excellent:**
- SKILL.md is a compact router: essential principles + intake + routing table
- Domain knowledge in references/ (facts, schemas, rubrics)
- Step-by-step procedures in workflows/
- Executable code in scripts/ (correct shebangs, not embedded in markdown)
- No file over 500 lines
- Clear `<required_reading>` directives in workflows
- No content duplication across files

**11 points — Good:**
- Mostly well-structured, one area where content could be better separated
- SKILL.md slightly over-detailed but still navigable
- Minor duplication (1-2 instances)

**7 points — Fair:**
- SKILL.md tries to contain too much (procedures + knowledge + code)
- references/ or workflows/ missing when they should exist
- Code blocks embedded in markdown instead of scripts/
- Some duplication across files

**3 points — Poor:**
- Monolithic SKILL.md with everything in one file
- No use of references/, workflows/, or scripts/
- Significant duplication or mixed concerns

---

## 6. Examples & Patterns (10 points)

Evaluates the quality and coverage of examples.

**10 points — Excellent:**
- At least one complete end-to-end example
- Examples use realistic data (not foo/bar/baz)
- Examples show common use cases AND edge cases
- Examples include expected output
- Error handling examples present
- Examples match current API version

**7 points — Good:**
- Has examples but missing edge cases or error handling
- Mostly realistic data with occasional foo/bar
- Expected output not always shown

**4 points — Fair:**
- Few examples, mostly placeholder data
- No error handling examples
- Missing expected output

**1 point — Poor:**
- No examples, or examples that would fail if followed

---

## 7. Conciseness (10 points)

Evaluates information density: does every line earn its place?

**10 points — Excellent:**
- No filler paragraphs or obvious statements
- No redundancy across files
- Each sentence adds unique value
- Dense, scannable format (tables, lists over paragraphs)
- No unnecessary verbose explanations of simple concepts

**7 points — Good:**
- Mostly concise, one or two verbose sections
- Minor redundancy (same info in two places)

**4 points — Fair:**
- Several verbose sections or filler paragraphs
- Noticeable redundancy across files
- Paragraph format where tables/lists would be clearer

**1 point — Poor:**
- Mostly filler, restates obvious things
- Significant redundancy throughout

---

## Scoring Process

1. **Collect agent findings** and map each to its primary criterion
2. **Start each criterion at maximum points**, deduct based on findings:
   - Critical finding: -5 to -8 points from the criterion
   - Important finding: -2 to -4 points from the criterion
   - Minor finding: -1 to -2 points from the criterion
3. **Floor each criterion at 0** (no negative scores)
4. **Sum all criteria** for total score
5. **Assign grade** using the scale above
6. **Record per-criterion scores** for the before/after comparison table

## Deduction Guidelines

| Finding Severity | Typical Deduction | Example |
|-----------------|-------------------|---------|
| Critical | -5 to -8 pts | SKILL.md over 500 lines (-6 from Structure), deprecated API in critical path (-7 from Freshness) |
| Important | -2 to -4 pts | Missing trigger phrases (-3 from Description), vague step (-3 from Actionability) |
| Minor | -1 to -2 pts | Foo/bar in one example (-1 from Examples), one verbose section (-1 from Conciseness) |

Multiple findings in the same criterion stack, but the criterion floor is 0.
