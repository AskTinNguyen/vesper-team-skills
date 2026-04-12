# Vesper Style — Layout Patterns

Use this file to choose the right **page structure, disclosure model, and information hierarchy** for Vesper surfaces.

The goal is not maximum feature visibility. The goal is **orientation + calm control**.

## 1. Orientation-first rule

Every Vesper surface should answer these quickly:
- **Where am I?**
- **What am I looking at?**
- **What changed or what is happening?**
- **What should I do next?**

If the layout makes the user inspect too many controls before they can answer those questions, it is too dense.

## 2. Canonical hierarchy model

Default to three visual levels:

| Level | What belongs here | Design posture |
|---|---|---|
| **Primary** | main title, main content, key action, live state | largest emphasis, clearest placement |
| **Secondary** | tabs, support controls, descriptions, related actions | quieter grouping, still easy to scan |
| **Tertiary** | metadata, timestamps, helper text, maintenance actions | demoted but readable |

Common failure mode: multiple competing “primary” regions.

## 3. Three-pane working model

This is one of Vesper’s strongest default patterns.

### Structure
1. **Navigation / context rail**
2. **Collection / index panel**
3. **Detail / working surface**

### Use it when
- the user needs to stay oriented while moving between many items
- there is a strong overview → selection → detail flow
- the workflow benefits from visible context without modal hopping

### Good examples of what each pane does
- rail: workspace, mode, area, section identity
- index: sessions, artifacts, entities, tasks, documents
- detail: reading, editing, configuring, reviewing, acting

### Design notes
- keep the rail visually quieter than the active work surface
- avoid giving all three panes equal visual weight
- the detail pane should usually feel the most readable and spacious

## 4. Document-centric work surface

Vesper often works best when the main area feels like a **readable document or workbench**, not a dashboard.

### Use this when
- the user is reading, composing, reviewing, or editing
- the content has narrative flow or multi-step reasoning
- the surface needs calm vertical rhythm more than dense widget density

### Rules
- control reading width
- group content into named sections
- keep actions nearby but visually subordinate to the content
- favor top-to-bottom flow over fragmented card farms

## 5. List-detail management layout

A common Vesper pattern for settings, sources, personas, plugins, and administrative surfaces.

### Structure
- **Left column:** categories, entities, or filters
- **Right column:** current detail, configuration, explanation, and actions

### Rules
- list labels should be easy to scan at a glance
- dangerous or maintenance actions should be separated from ordinary editing
- forms should be broken into calm sections with short helper text
- the right side should feel like a working document, not a control wall

## 6. Header pattern

Headers in Vesper are usually **compact, centered, and quiet**.

### Header should do
- identify the current surface clearly
- optionally show one small badge or state marker
- hold a limited set of actions on the right

### Header should not do
- become a crowded toolbar
- compete with the content area for attention
- carry every possible filter, toggle, and status item at once

A good Vesper header orients first and advertises tools second.

## 7. Primary-action pattern

Each surface should have **one obvious next step**.

### Good posture
- one clearly strongest action
- secondary actions grouped into quieter controls
- advanced or rare actions behind menus, expandable panels, or secondary regions

### Bad posture
- four equal-weight buttons in the header
- multiple semantic button colors competing for urgency
- important actions visually buried among utility actions

## 8. Progressive disclosure

Vesper exposes power gradually.

### Show by default
- current state
- current selection
- primary action
- the minimum context needed to act confidently

### Hide until needed
- advanced filters
- maintenance actions
- verbose configuration detail
- edge-case controls
- debugging or power-user tooling

### Good disclosure mechanisms
- inline expand/collapse
- tabs
- quiet “Advanced” sections
- overflow menus
- companion/detail rails

## 9. Companion rail pattern

When context is useful but not primary, use a **quiet companion rail**.

### Good for
- metadata
- status summaries
- related actions
- supporting context or guidance
- secondary previews

### Rules
- companion content must stay subordinate to the main work surface
- avoid turning the rail into a second dashboard
- keep copy concise and scannable

## 10. Empty-state pattern

A Vesper empty state should feel like an invitation, not a dead end.

It should:
- explain what this area is for
- show one strong next action
- reduce ambiguity
- keep tone calm and encouraging

Avoid:
- over-illustrated empties
- long paragraphs
- multiple equal-weight CTA buttons

## 11. Status and trust pattern

Because Vesper is agent-native, status communication matters.

### Good status design
- surface what matters now
- use text + structure + color together
- show progress or system state without flooding the screen
- keep automation understandable and inspectable

### Avoid
- status noise everywhere
- tiny unreadable badges doing too much work
- making the user decode semantic color without text support

## 12. Layout anti-patterns

Reject these quickly:
- dense control bars with equal-weight actions
- symmetrical card grids where one region should be primary
- dashboard sprawl for document-like tasks
- too many simultaneous accent treatments
- sidebars, filters, badges, and meta surfaces all shouting at once
- light-mode panels separated only by faint translucency instead of real structure

## 13. Fast layout decision guide

| Situation | Default pattern |
|---|---|
| Many items + selection + deep detail | Three-pane working model |
| Configuration/editing of selected item | List-detail layout |
| Reading, composing, reviewing | Document-centric work surface |
| Main content needs supporting context | Work surface + companion rail |
| User needs a clear first step from zero | Empty state with one strong CTA |

## 14. Final layout check

Before shipping, ask:
1. Is the main action obvious within a few seconds?
2. Does the layout help the user stay oriented?
3. Are advanced controls available without dominating the default view?
4. Is the main reading/editing surface calmer than the surrounding chrome?
5. Would a non-technical founder feel guided rather than overwhelmed?
