---
name: flowy-flowchart
description: Create a flowchart diagram inline in the conversation. Use when designing navigation flows, state machines, process diagrams, or decision trees that users can edit visually.
---

# Flowy Flowchart Skill

Create flowcharts, state machines, and process diagrams in Flowy format - a JSON-based visual diagram format that users can edit visually in Vesper. This skill enables Claude to generate diagrams that serve as visual feedback during development.

## When to Use This Skill

Use this skill when:
- Designing navigation flows for apps
- Documenting user journeys or workflows
- Creating state machines for features
- Mapping out decision trees or conditional logic
- Visualizing process flows or system architecture
- Planning feature implementations with visual diagrams

Triggers include:
- "create a flowchart for..."
- "diagram the navigation flow..."
- "show me a state machine for..."
- "visualize the process..."
- "map out the user journey..."

## Output Format

All flowcharts are written as JSON files to the `.flowy/` directory in the workspace:

```
{workspacePath}/.flowy/{diagram-name}.json
```

The JSON follows the Flowy schema exactly. Users can then open and visually edit these diagrams in Vesper.

## JSON Schema

### Document Structure

```typescript
{
  "version": "1.0",
  "name": string,              // Human-readable diagram name
  "description": string,       // Optional description
  "type": "flowchart",
  "content": {
    "type": "flowchart",
    "nodes": FlowyNode[],
    "edges": FlowyEdge[]
  },
  "viewport": {
    "zoom": number,           // Default: 1
    "pan": { "x": number, "y": number }  // Default: { x: 0, y: 0 }
  },
  "createdAt": string,        // ISO 8601 timestamp
  "updatedAt": string         // ISO 8601 timestamp
}
```

### Node Schema

```typescript
{
  "id": string,                // Unique ID (use kebab-case)
  "type": "rect" | "circle" | "diamond",
  "label": string,             // Text displayed in node
  "position": { "x": number, "y": number },
  "size": { "width": number, "height": number },
  "style": {                   // Optional styling
    "fill": string,            // Hex color (e.g., "#d0ebff")
    "stroke": string,          // Border color (e.g., "#1c7ed6")
    "strokeWidth": number,     // Default: 2
    "cornerRadius": number,    // Default: 0 for rect, ignored for circle
    "shadow": boolean,         // Default: false
    "opacity": number,         // 0-1, default: 1
    "font": {
      "family": string,        // Default: system font
      "size": number,          // Default: 14
      "weight": "normal" | "bold" | "light",
      "color": string          // Default: "#000000"
    }
  },
  "icon": {                    // Optional icon
    "name": string,            // Icon name (e.g., "book-open", "play", "help-circle")
    "size": number,            // Default: 16
    "color": string,           // Default: matches stroke
    "position": "top-left" | "top-right" | "center" | "bottom-left" | "bottom-right"
  },
  "data": {}                   // Optional custom data
}
```

### Edge Schema

```typescript
{
  "id": string,                // Unique ID (e.g., "e1", "e2")
  "from": string,              // Source node ID
  "to": string,                // Target node ID
  "type": "arrow" | "dashed" | "line" | "orthogonal" | "curved",
  "label": string,             // Optional edge label
  "style": {                   // Optional styling
    "stroke": string,          // Line color
    "strokeWidth": number,     // Default: 2
    "strokeDasharray": string, // E.g., "5,5" for dashed
    "opacity": number,         // 0-1
    "markerStart": "arrow" | "circle" | "diamond" | "none",
    "markerEnd": "arrow" | "circle" | "diamond" | "none"
  },
  "controlPoints": [           // Optional for curved edges
    { "x": number, "y": number }
  ],
  "data": {}                   // Optional custom data
}
```

## Node Types

- **rect**: Use for screens, states, processes, actions
- **circle**: Use for start/end points, events, states
- **diamond**: Use for decision points, conditional branches

## Edge Types

- **arrow**: Default, shows direction (solid line with arrow)
- **dashed**: Optional/alternate paths, "back" navigation
- **line**: No direction indicator
- **orthogonal**: 90-degree angle routing
- **curved**: Smooth bezier curves

## Color Palette

Use semantic colors to group related nodes:

| Purpose | Fill | Stroke |
|---------|------|--------|
| Primary/Start | `#d0ebff` | `#1c7ed6` |
| Neutral | `#e9ecef` | `#495057` |
| Success/Action | `#d3f9d8` | `#2f9e44` |
| Warning/Question | `#fff3bf` | `#f08c00` |
| Result/End | `#d0bfff` | `#7950f2` |
| Error/Problem | `#ffe0e0` | `#c92a2a` |

## Common Icons

- Navigation: `arrow-right`, `arrow-left`, `home`, `menu`
- Actions: `play`, `pause`, `check`, `x`, `edit`, `trash`
- States: `circle`, `square`, `star`, `flag`
- UI: `book-open`, `user`, `settings`, `bell`, `search`
- Questions: `help-circle`, `alert-circle`, `info`
- Results: `trophy`, `thumbs-up`, `thumbs-down`

## Positioning Guidelines

### Left-to-Right Layout (Recommended for User Flows)
- Start at x: 80, y: 200
- Horizontal spacing: 200px between nodes
- Vertical spacing: 150px between rows
- Node width: 120px, height: 70px

### Top-to-Bottom Layout (Recommended for Process Flows)
- Start at x: 200, y: 80
- Vertical spacing: 150px between nodes
- Horizontal spacing: 200px between columns
- Node width: 120px, height: 70px

### Grid System
Position nodes on a grid for clean alignment:
- Grid size: 20px
- Snap positions to multiples of 20
- Example: { x: 80, y: 200 }, { x: 280, y: 200 }

## Example: Navigation Flow

```json
{
  "version": "1.0",
  "name": "Quiz Navigation Flow",
  "description": "Navigation structure for the quiz feature",
  "type": "flowchart",
  "content": {
    "type": "flowchart",
    "nodes": [
      {
        "id": "learn-tab",
        "type": "rect",
        "label": "Learn Tab",
        "position": { "x": 80, "y": 200 },
        "size": { "width": 120, "height": 70 },
        "style": { "fill": "#d0ebff", "stroke": "#1c7ed6", "cornerRadius": 10 },
        "icon": { "name": "book-open", "size": 18, "color": "#1c7ed6" }
      },
      {
        "id": "quiz-card",
        "type": "rect",
        "label": "Quiz Card",
        "position": { "x": 280, "y": 200 },
        "size": { "width": 120, "height": 70 },
        "style": { "fill": "#e9ecef", "stroke": "#495057", "cornerRadius": 10 }
      },
      {
        "id": "quiz-intro",
        "type": "rect",
        "label": "Quiz Intro",
        "position": { "x": 480, "y": 200 },
        "size": { "width": 120, "height": 70 },
        "style": { "fill": "#d3f9d8", "stroke": "#2f9e44", "cornerRadius": 10 },
        "icon": { "name": "play", "size": 18, "color": "#2f9e44" }
      },
      {
        "id": "quiz-question",
        "type": "rect",
        "label": "Question Screen",
        "position": { "x": 680, "y": 200 },
        "size": { "width": 120, "height": 70 },
        "style": { "fill": "#fff3bf", "stroke": "#f08c00", "cornerRadius": 10 },
        "icon": { "name": "help-circle", "size": 18, "color": "#f08c00" }
      },
      {
        "id": "quiz-results",
        "type": "rect",
        "label": "Results Screen",
        "position": { "x": 880, "y": 200 },
        "size": { "width": 120, "height": 70 },
        "style": { "fill": "#d0bfff", "stroke": "#7950f2", "cornerRadius": 10 },
        "icon": { "name": "trophy", "size": 18, "color": "#7950f2" }
      }
    ],
    "edges": [
      { "id": "e1", "from": "learn-tab", "to": "quiz-card", "type": "arrow", "label": "displays" },
      { "id": "e2", "from": "quiz-card", "to": "quiz-intro", "type": "arrow", "label": "tap" },
      { "id": "e3", "from": "quiz-intro", "to": "quiz-question", "type": "arrow", "label": "Start" },
      { "id": "e4", "from": "quiz-question", "to": "quiz-results", "type": "arrow", "label": "Complete" },
      { "id": "e5", "from": "quiz-results", "to": "quiz-intro", "type": "dashed", "label": "Play Again" },
      { "id": "e6", "from": "quiz-results", "to": "learn-tab", "type": "dashed", "label": "Done" }
    ]
  },
  "viewport": { "zoom": 1, "pan": { "x": 0, "y": 0 } },
  "createdAt": "2026-01-25T00:00:00.000Z",
  "updatedAt": "2026-01-25T00:00:00.000Z"
}
```

## Example: State Machine

```json
{
  "version": "1.0",
  "name": "Login State Machine",
  "type": "flowchart",
  "content": {
    "type": "flowchart",
    "nodes": [
      {
        "id": "idle",
        "type": "circle",
        "label": "Idle",
        "position": { "x": 100, "y": 200 },
        "size": { "width": 80, "height": 80 },
        "style": { "fill": "#e9ecef", "stroke": "#495057" }
      },
      {
        "id": "loading",
        "type": "rect",
        "label": "Loading",
        "position": { "x": 300, "y": 200 },
        "size": { "width": 100, "height": 60 },
        "style": { "fill": "#fff3bf", "stroke": "#f08c00" }
      },
      {
        "id": "check-auth",
        "type": "diamond",
        "label": "Valid?",
        "position": { "x": 520, "y": 180 },
        "size": { "width": 100, "height": 100 },
        "style": { "fill": "#fff3bf", "stroke": "#f08c00" }
      },
      {
        "id": "success",
        "type": "circle",
        "label": "Success",
        "position": { "x": 720, "y": 100 },
        "size": { "width": 80, "height": 80 },
        "style": { "fill": "#d3f9d8", "stroke": "#2f9e44" }
      },
      {
        "id": "error",
        "type": "circle",
        "label": "Error",
        "position": { "x": 720, "y": 300 },
        "size": { "width": 80, "height": 80 },
        "style": { "fill": "#ffe0e0", "stroke": "#c92a2a" }
      }
    ],
    "edges": [
      { "id": "e1", "from": "idle", "to": "loading", "type": "arrow", "label": "submit" },
      { "id": "e2", "from": "loading", "to": "check-auth", "type": "arrow" },
      { "id": "e3", "from": "check-auth", "to": "success", "type": "arrow", "label": "yes" },
      { "id": "e4", "from": "check-auth", "to": "error", "type": "arrow", "label": "no" },
      { "id": "e5", "from": "error", "to": "idle", "type": "dashed", "label": "retry" }
    ]
  }
}
```

## Best Practices

1. **Use Meaningful IDs**: Use kebab-case IDs that describe the node (e.g., `quiz-intro`, `login-screen`)

2. **Position for Readability**:
   - Use left-to-right for user flows
   - Use top-to-bottom for process flows
   - Maintain consistent spacing between nodes (200px horizontal, 150px vertical)

3. **Label Edges**: Add labels to edges to clarify the action or condition (e.g., "tap", "submit", "yes", "no")

4. **Use Colors Semantically**: Group related nodes with similar colors, use the color palette for consistency

5. **Choose Appropriate Node Types**:
   - Rectangles for screens and processes
   - Circles for start/end states
   - Diamonds for decision points

6. **Add Icons for Context**: Include relevant icons to make nodes more recognizable at a glance

7. **Use Dashed Edges**: For optional paths, "back" navigation, or retry flows

8. **Keep It Simple**: Don't overcomplicate diagrams - break complex flows into multiple smaller diagrams

9. **Consistent Sizing**: Use standard node sizes for uniformity:
   - Rectangles: 120x70
   - Circles: 80x80
   - Diamonds: 100x100

10. **Set Viewport**: Include viewport settings for optimal initial display (zoom: 1, pan: {x: 0, y: 0})

## Implementation Notes

- Always create the `.flowy/` directory in the workspace if it doesn't exist
- Use ISO 8601 format for timestamps (e.g., `new Date().toISOString()`)
- Validate all node and edge IDs are unique
- Ensure all edge `from` and `to` references point to existing node IDs
- Use corner radius (10) for modern, friendly appearance on rectangles
- Position nodes on 20px grid for clean alignment
