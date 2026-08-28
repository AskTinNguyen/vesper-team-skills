---
skill: qa-testcase
invoke: /qa-testcase
alias: /tc
description: Generate QA test cases from feature docs with categories (Functionality, UI, UX, Performance, Integration)
type: qa-testing
category: testing
scope: docs/GameDesign/, docs/features/, docs/pm/
---

# QA Test Case Generation Skill

**Role:** Senior QA Engineer
**Input:** Feature name, PRD/TechDoc, or GDD document path
**Output:** Structured test cases in markdown table format (Excel-compatible)
**Categories:** Functionality, UI, UX, Performance, Integration

## Objective

Generate comprehensive QA test cases by analyzing:
1. **Design documents** in `docs/GameDesign/` and `docs/features/`
2. **Codebase** to understand implementation details
3. **Existing patterns** from similar features

Output follows QA team's standard Excel format with hierarchical categories.

---

## Usage

### Basic Usage

```
/qa-testcase <feature-name>

Examples:
/qa-testcase Friend System
/qa-testcase Party System
/qa-testcase Charged Attack
/qa-testcase Vehicle System
```

### With Document Reference

```
/qa-testcase <feature-name> --doc <path>

Examples:
/qa-testcase Vehicle --doc docs/GameDesign/GDD_Vehicle.md
/qa-testcase Combat --doc docs/features/charged-attack.md
```

### Options

```
--doc <path>          Reference specific design document
--category <cat>      Generate only specific category (Functionality|UI|UX|Performance|Integration)
--output <path>       Output markdown file path (default: docs/qa/TC_{feature}.md)
--dry-run             Preview test cases without writing file
--xlsx                Also generate Excel file (requires pandas)
```

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INPUT ANALYSIS                                               │
├─────────────────────────────────────────────────────────────────┤
│ • Identify feature from user input                              │
│ • Search docs/GameDesign/ for related GDD/PRD                   │
│ • Search docs/features/ for TechDocs                            │
│ • Search codebase for implementation (Source/, Plugins/)        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ 2. DOCUMENT EXTRACTION                                          │
├─────────────────────────────────────────────────────────────────┤
│ • Extract user stories / requirements                           │
│ • Extract acceptance criteria                                   │
│ • Extract UI elements and flows                                 │
│ • Extract edge cases and error states                           │
│ • Extract performance requirements                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ 3. CODEBASE ANALYSIS                                            │
├─────────────────────────────────────────────────────────────────┤
│ • Find relevant classes/components                              │
│ • Identify API endpoints and data flows                         │
│ • Extract validation rules and constraints                      │
│ • Identify integration points with other systems                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ 4. TEST CASE GENERATION                                         │
├─────────────────────────────────────────────────────────────────┤
│ Generate test cases for each category:                          │
│                                                                 │
│ ┌─────────────────┬───────────────────────────────────────────┐ │
│ │ Category        │ Focus Areas                               │ │
│ ├─────────────────┼───────────────────────────────────────────┤ │
│ │ Functionality   │ Core features, business logic, data       │ │
│ │ UI              │ Visual elements, layouts, states          │ │
│ │ UX              │ User flows, feedback, accessibility       │ │
│ │ Performance     │ Load times, responsiveness, limits        │ │
│ │ Integration     │ Cross-system, API, multiplayer            │ │
│ └─────────────────┴───────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ 5. OUTPUT GENERATION                                            │
├─────────────────────────────────────────────────────────────────┤
│ • Generate markdown table in Excel-compatible format            │
│ • Include Summary sheet with category counts                    │
│ • Output to docs/qa/TC_{feature}.md                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Test Case Categories

### 1. Functionality
Core feature behavior and business logic:
- Feature activation/deactivation
- Data operations (CRUD)
- Business rules validation
- State management
- Error handling
- Edge cases and boundaries

### 2. UI (User Interface)
Visual elements and display:
- Element presence and visibility
- Layout correctness
- Visual states (active, disabled, hover)
- Text and labels
- Icons and images
- Animation states
- Responsive design (PC)

### 3. UX (User Experience)
User interaction and flow:
- Navigation paths
- Feedback messages (success, error, loading)
- Input validation feedback
- Confirmation dialogs
- Accessibility
- Intuitive behavior
- Help/guidance

### 4. Performance
Speed, responsiveness, and limits:
- Load times
- Response times
- Capacity limits (max items, cap)
- Memory usage
- Network conditions
- Concurrent operations

### 5. Integration
Cross-system and external:
- API communication
- Multiplayer synchronization
- Steam platform integration
- External service integration
- Data persistence
- Session management

---

## Output Format

### Markdown Table (Excel-Compatible)

```markdown
# Test Cases: {Feature Name}

## Summary

| # | Category | Progress | Total TC | Passed | Failed | Pending |
|---|----------|----------|----------|--------|--------|---------|
| 1 | Functionality | Not started | {N} | 0 | 0 | 0 |
| 2 | UI | Not started | {N} | 0 | 0 | 0 |
| 3 | UX | Not started | {N} | 0 | 0 | 0 |
| 4 | Performance | Not started | {N} | 0 | 0 | 0 |
| 5 | Integration | Not started | {N} | 0 | 0 | 0 |
| | **Total** | | **{Total}** | 0 | 0 | 0 |

---

## Functionality Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-1 | Not started | {Feature} | {SubFeature} | {Component} | {What to verify} | {Expected outcome} | P1 |
| TC-2 | Not started | | | {Component2} | {What to verify} | {Expected outcome} | P1 |
...

## UI Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
...

## UX Test Cases
...

## Performance Test Cases
...

## Integration Test Cases
...
```

---

## Column Definitions

| Column | Description | Example |
|--------|-------------|---------|
| **No.** | Test case ID | TC-1, TC-2, ... |
| **Results** | Test execution status | Not started, Passed, Failed, Pending |
| **Large Items** | Major feature area | Friend System, Party, Combat |
| **Medium Items** | Sub-feature or screen | Friend List, Add Friend, Friend Request |
| **Small Items** | Specific component/element | Friend Code, Copy Button, Input Field |
| **Objectives** | What to verify (action) | Verify that the user can copy the friend code |
| **Expected Results** | Expected outcome | The friend code is copied to clipboard |
| **Priority** | Test priority | P0 (Critical), P1 (High), P2 (Medium), P3 (Low) |

---

## Priority Guidelines

| Priority | Description | Examples |
|----------|-------------|----------|
| **P0** | Critical path, blocker if fails | Login, core gameplay loop, payment |
| **P1** | Important features | Friend add/remove, party join, rewards |
| **P2** | Secondary features | UI polish, suggestions, sort/filter |
| **P3** | Nice-to-have | Animations, sound effects, tooltips |

---

## Test Case Writing Rules

### Objectives (Verify...)
- Start with "Verify that..." or "Verify when..."
- Be specific about the action and condition
- One testable item per row

**Good Examples:**
- "Verify that the user can press the Add Friend button"
- "Verify when the friend code is invalid, the Add button is disabled"
- "Verify that the friend list displays max 100 friends"

**Bad Examples:**
- "Test friend feature" (too vague)
- "Check button" (unclear what to check)

### Expected Results
- Describe observable outcome
- Be specific about state changes
- Include visual feedback when applicable

**Good Examples:**
- "The friend request is sent and confirmation toast appears"
- "The Add Friend button changes to disabled state (grey)"
- "Error message 'Invalid code' displayed below input field"

**Bad Examples:**
- "It works" (not specific)
- "Success" (no observable detail)

---

## Hierarchical Structure

Use **Large Items > Medium Items > Small Items** hierarchy:

```
Friend System (Large)
├── Add Friend (Medium)
│   ├── Friend Code (Small)
│   │   ├── TC-1: Display friend code
│   │   ├── TC-2: Copy button functionality
│   │   └── TC-3: Input field validation
│   └── Add Button (Small)
│       ├── TC-4: Button states
│       └── TC-5: Send friend request
├── Friend List (Medium)
│   ├── Display (Small)
│   └── Status (Small)
└── Friend Request (Medium)
    ├── Receive (Small)
    └── Accept/Decline (Small)
```

---

## Example Output

### Feature: Friend System

```markdown
# Test Cases: Friend System

## Summary

| # | Category | Progress | Total TC | Passed | Failed | Pending |
|---|----------|----------|----------|--------|--------|---------|
| 1 | Functionality | Not started | 25 | 0 | 0 | 0 |
| 2 | UI | Not started | 15 | 0 | 0 | 0 |
| 3 | UX | Not started | 10 | 0 | 0 | 0 |
| 4 | Performance | Not started | 5 | 0 | 0 | 0 |
| 5 | Integration | Not started | 8 | 0 | 0 | 0 |
| | **Total** | | **63** | 0 | 0 | 0 |

---

## Functionality Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-1 | Not started | Friend System | Add Friend | Friend Code | Verify that each user has a unique friend code | Display a friend code that matches the user's UID | P1 |
| TC-2 | Not started | | | Copy Button | Verify that pressing the copy button copies the friend code | The friend code is copied to clipboard | P1 |
| TC-3 | Not started | | | Input Field | Verify that the friend code input field accepts valid format | The Add Friend button becomes active | P1 |
| TC-4 | Not started | | | | Verify when invalid format is entered | The Add Friend button remains disabled (grey) | P1 |
| TC-5 | Not started | | | Add Button | Verify that pressing Add Friend sends a friend request | Friend request is sent to target user | P0 |
| TC-6 | Not started | | Friend List | Display | Verify that accepted friends appear in the friend list | Friend is displayed with avatar and name | P1 |
| TC-7 | Not started | | | Status | Verify that online friends show Online status | Display "Online" indicator for in-game friends | P1 |
| TC-8 | Not started | | | | Verify that offline friends show Offline status | Display "Offline" indicator for not-in-game friends | P1 |
| TC-9 | Not started | | Friend Request | Receive | Verify that incoming friend requests are displayed | Friend request appears in Friend Requests section | P1 |
| TC-10 | Not started | | | Accept | Verify that accepting a friend request adds both users as friends | Both users see each other in their friend lists | P0 |

## UI Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-11 | Not started | Friend System | Friend Tab | Layout | Verify that the Friend tab displays correctly | Display Add Friend tab by default when opened | P1 |
| TC-12 | Not started | | | Tabs | Verify that all tabs are visible and selectable | Tabs: Add Friend, Friend List, Friend Request visible | P2 |
| TC-13 | Not started | | Add Friend | Friend Code Display | Verify that friend code is displayed prominently | Friend code shown with copy icon button | P2 |
| TC-14 | Not started | | | Input Field | Verify input field placeholder text | Display "Enter friend code" placeholder | P3 |
| TC-15 | Not started | | | Button States | Verify Add Friend button has correct visual states | Active: colored, Disabled: grey | P2 |

## UX Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-16 | Not started | Friend System | Add Friend | Copy Feedback | Verify that copy action provides feedback | Toast notification "Copied!" appears | P2 |
| TC-17 | Not started | | | Error Feedback | Verify that invalid code shows clear error | Error message displayed below input field | P1 |
| TC-18 | Not started | | | Success Feedback | Verify that successful friend request shows feedback | Success message "Friend request sent!" | P1 |
| TC-19 | Not started | | Friend List | Empty State | Verify that empty friend list shows guidance | Display "Add friends to play together!" message | P2 |
| TC-20 | Not started | | | Navigation | Verify that tapping a friend shows options | Display friend options menu (Invite, Remove, etc.) | P2 |

## Performance Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-21 | Not started | Friend System | Friend List | Load Time | Verify that friend list loads within acceptable time | List loads within 2 seconds | P1 |
| TC-22 | Not started | | | Max Capacity | Verify that friend list handles max capacity (100 friends) | All 100 friends display without performance issues | P1 |
| TC-23 | Not started | | Suggestions | Load Time | Verify that suggestions load within acceptable time | Suggestions load within 3 seconds | P2 |
| TC-24 | Not started | | | Max Display | Verify that suggestions list handles max items (30) | All 30 suggestions display correctly | P2 |
| TC-25 | Not started | | Status Update | Refresh Rate | Verify that status updates are reasonably real-time | Status updates within 5 seconds of change | P2 |

## Integration Test Cases

| No. | Results | Large Items | Medium Items | Small Items | Objectives | Expected Results | Priority |
|-----|---------|-------------|--------------|-------------|------------|------------------|----------|
| TC-26 | Not started | Friend System | Steam | Add Friend | Verify that friend can be added via Steam overlay | Friend request sent through Steam | P1 |
| TC-27 | Not started | | | Status Sync | Verify that Steam friend status syncs correctly | Status shown correctly from Steam | P1 |
| TC-28 | Not started | | Multiplayer | Post-Match | Verify that friend can be added from post-match screen | Friend option available for other players | P1 |
| TC-29 | Not started | | | Party Integration | Verify that friend can be invited to party | Invite option works and party invite received | P0 |
| TC-30 | Not started | | Server | Offline Mode | Verify behavior when server is unreachable | Appropriate error message displayed | P1 |
```

---

## Document Search Locations

When analyzing a feature, search these locations:

| Location | Content Type |
|----------|--------------|
| `docs/GameDesign/` | GDD (Game Design Documents) |
| `docs/features/` | TechDocs (Technical specifications) |
| `docs/pm/sprints/` | Sprint planning and requirements |
| `Source` | Game source code |
| `Plugins/Sipher*/` | Plugin implementations |
| `Source/LyraGame/UI/` | UI implementations |

---

## Critical Reminders

1. **Always read the design document first** - Don't generate test cases without understanding the feature
2. **Cover all categories** - Every feature should have tests in all 5 categories
3. **Use hierarchical structure** - Large > Medium > Small items for organization
4. **Be specific** - Objectives and Expected Results must be testable
5. **Assign priorities** - Critical paths get P0/P1, polish items get P2/P3
6. **Consider platform** - Steam (PC only)
7. **Include negative cases** - Test what happens when things go wrong

---

## Related Documentation

- QA Template: `C:\Users\devop\Downloads\_NU [G1][QA][GL] Friend & Party.xlsx`
- Design Docs: `docs/GameDesign/`
- Sprint Planning: `docs/pm/sprints/`
