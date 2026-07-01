---
name: flowy-ui-mockup
description: Create UI mockups for iPhone and iPad apps inline in the conversation. Use when designing iOS screens, prototyping interfaces, or documenting visual specifications.
---

# Flowy UI Mockup Skill

Create iPhone and iPad UI mockups in Flowy format - a JSON-based mockup format that renders as interactive, pixel-perfect iOS interfaces in Vesper. This skill enables Claude to design and communicate UI concepts through visual mockups.

## When to Use This Skill

Use this skill when:
- Designing iOS app screens and interfaces
- Planning user interface layouts
- Showing all states of a feature (loading, error, success)
- Documenting screen transitions and user flows
- Prototyping navigation patterns
- Creating visual specifications for developers

Triggers include:
- "create an iOS mockup for..."
- "design an iPhone screen for..."
- "show me a UI mockup of..."
- "create screens for..."
- "prototype the interface for..."

## Output Format

All mockups are written as JSON files to the `.flowy/` directory in the workspace:

```
{workspacePath}/.flowy/{mockup-name}.json
```

The JSON follows the Flowy mockup schema exactly. Users can then view and edit these mockups visually in Vesper.

## JSON Schema

### Document Structure

```typescript
{
  "version": "1.0",
  "name": string,              // Human-readable mockup name
  "description": string,       // Optional description
  "type": "mockup",
  "content": {
    "type": "mockup",
    "screens": MockupScreen[],
    "connections": MockupConnection[]
  },
  "viewport": {
    "zoom": number,           // Default: 0.6 (fits multiple screens)
    "pan": { "x": number, "y": number }
  },
  "createdAt": string,        // ISO 8601 timestamp
  "updatedAt": string         // ISO 8601 timestamp
}
```

### Screen Schema

```typescript
{
  "id": string,                // Unique ID (use screen-{name})
  "title": string,             // Screen name for reference
  "device": "iphone" | "ipad",
  "position": { "x": number, "y": number },  // Left-to-right: 50, 500, 950, etc.
  "components": MockupComponent[],
  "backgroundColor": string,   // Hex color, default: "#ffffff"
  "statusBarStyle": "light" | "dark"  // Default: "dark"
}
```

### Component Schema

```typescript
{
  "id": string,                // Unique ID within screen
  "type": MockupComponentType,
  "position": { "x": number, "y": number },  // Relative to screen
  "size": { "width": number, "height": number },
  "props": ComponentProps      // Type-specific properties
}
```

### Connection Schema

```typescript
{
  "id": string,                // Unique ID (use conn-{n})
  "from": {
    "screenId": string,
    "componentId": string      // Optional - which component triggers
  },
  "to": {
    "screenId": string,
    "componentId": string      // Optional - which component to focus
  },
  "label": string,             // Action label (e.g., "Tap", "Submit")
  "type": "arrow" | "dashed" | "line",
  "style": {}                  // Optional edge styling
}
```

## Device Dimensions

### iPhone (Standard)
- Width: 393px
- Height: 852px
- Safe area top: 59px (status bar + notch)
- Safe area bottom: 34px (home indicator)

### iPad
- Width: 820px
- Height: 1180px
- Safe area top: 24px (status bar)
- Safe area bottom: 20px

## Component Types & Props

### NavBar
```typescript
{
  "type": "navbar",
  "title": string,
  "showBack": boolean,       // Show back button
  "rightAction": string      // Right button label
}
```
Position: `{ x: 0, y: 0 }`, Size: `{ width: 393, height: 44 }`

### Button
```typescript
{
  "type": "button",
  "label": string,
  "variant": "primary" | "secondary" | "destructive" | "ghost",
  "disabled": boolean,
  "icon": string            // Optional icon name
}
```
Size: `{ width: 345, height: 50 }` for full-width

### Card
```typescript
{
  "type": "card",
  "title": string,
  "subtitle": string,
  "content": string,
  "icon": string,
  "variant": "default" | "highlighted" | "error" | "success"
}
```

### Text
```typescript
{
  "type": "text",
  "content": string,
  "variant": "title" | "headline" | "body" | "caption" | "label",
  "align": "left" | "center" | "right",
  "color": string
}
```

### TextField
```typescript
{
  "type": "textfield",
  "placeholder": string,
  "value": string,
  "label": string,
  "variant": "default" | "error" | "success"
}
```
Size: `{ width: 345, height: 44 }`

### List
```typescript
{
  "type": "list",
  "variant": "plain" | "inset" | "grouped",
  "items": [
    {
      "id": string,
      "title": string,
      "subtitle": string,
      "icon": string,
      "accessory": "chevron" | "switch" | "checkmark" | "none",
      "selected": boolean
    }
  ]
}
```

### Progress
```typescript
{
  "type": "progress",
  "value": number,           // 0-100
  "max": number,            // Default: 100
  "showLabel": boolean,
  "variant": "bar" | "circle"
}
```

### TabBar
```typescript
{
  "type": "tabbar",
  "tabs": [
    {
      "id": string,
      "label": string,
      "icon": string,
      "active": boolean
    }
  ]
}
```
Position: Bottom of screen, Size: `{ width: 393, height: 49 }`

### Icon
```typescript
{
  "type": "icon",
  "name": string,
  "size": "small" | "medium" | "large",
  "color": string
}
```

### Image
```typescript
{
  "type": "image",
  "placeholder": "landscape" | "portrait" | "square" | "avatar",
  "aspectRatio": number      // Default: 16/9 for landscape
}
```

### Badge
```typescript
{
  "type": "badge",
  "label": string,
  "variant": "default" | "success" | "warning" | "error" | "info"
}
```

### Toggle
```typescript
{
  "type": "toggle",
  "checked": boolean,
  "label": string
}
```

### Slider
```typescript
{
  "type": "slider",
  "value": number,
  "min": number,
  "max": number,
  "label": string
}
```

### Divider
```typescript
{
  "type": "divider",
  "variant": "full" | "inset"
}
```

## Layout Guidelines

### Spacing
- Screen horizontal spacing: 450px (50, 500, 950, 1400...)
- Standard margin: 24px
- Component padding: 16px
- Between components: 20px

### iPhone Component Positioning
- NavBar: `{ x: 0, y: 0 }`
- Content starts at: `y: 60` (after navbar)
- Bottom button: `y: 750` (102px from bottom)
- TabBar: `{ x: 0, y: 803 }` (at bottom)

### Common Widths (iPhone)
- Full width content: 345px (24px margins)
- Full width navbar: 393px (edge to edge)
- Centered content: Start at x: 24

### Component Heights
- NavBar: 44px
- Button (default): 50px
- TextField: 44px
- TabBar: 49px
- List item: 44px
- Card (compact): 100px
- Card (normal): 160px

## Example: Quiz Mockup

```json
{
  "version": "1.0",
  "name": "Quiz UI Mockup",
  "description": "iPhone mockups for the quiz feature",
  "type": "mockup",
  "content": {
    "type": "mockup",
    "screens": [
      {
        "id": "screen-intro",
        "title": "Quiz Intro",
        "device": "iphone",
        "position": { "x": 50, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "intro-navbar", "type": "navbar", "position": { "x": 0, "y": 0 }, "size": { "width": 393, "height": 44 }, "props": { "type": "navbar", "title": "Quiz", "showBack": true } },
          { "id": "intro-icon", "type": "icon", "position": { "x": 170, "y": 150 }, "size": { "width": 53, "height": 53 }, "props": { "type": "icon", "name": "brain", "size": "large", "color": "#8b5cf6" } },
          { "id": "intro-title", "type": "text", "position": { "x": 50, "y": 230 }, "size": { "width": 293, "height": 40 }, "props": { "type": "text", "content": "Test Your Knowledge", "variant": "title", "align": "center" } },
          { "id": "intro-btn", "type": "button", "position": { "x": 24, "y": 480 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Start Quiz", "variant": "primary" } }
        ]
      },
      {
        "id": "screen-question",
        "title": "Question",
        "device": "iphone",
        "position": { "x": 500, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "q-navbar", "type": "navbar", "position": { "x": 0, "y": 0 }, "size": { "width": 393, "height": 44 }, "props": { "type": "navbar", "title": "Question 1 of 5" } },
          { "id": "q-progress", "type": "progress", "position": { "x": 24, "y": 60 }, "size": { "width": 345, "height": 8 }, "props": { "type": "progress", "value": 20, "max": 100, "variant": "bar" } },
          { "id": "q-card", "type": "card", "position": { "x": 24, "y": 100 }, "size": { "width": 345, "height": 100 }, "props": { "type": "card", "content": "What keyboard shortcut cycles through permission modes?", "variant": "default" } },
          { "id": "q-list", "type": "list", "position": { "x": 24, "y": 220 }, "size": { "width": 345, "height": 200 }, "props": { "type": "list", "variant": "inset", "items": [ { "id": "a", "title": "Cmd+Tab" }, { "id": "b", "title": "Shift+Tab", "selected": true, "accessory": "checkmark" }, { "id": "c", "title": "Ctrl+P" }, { "id": "d", "title": "Alt+M" } ] } },
          { "id": "q-btn", "type": "button", "position": { "x": 24, "y": 500 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Next", "variant": "primary" } }
        ]
      },
      {
        "id": "screen-results",
        "title": "Results",
        "device": "iphone",
        "position": { "x": 950, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "r-navbar", "type": "navbar", "position": { "x": 0, "y": 0 }, "size": { "width": 393, "height": 44 }, "props": { "type": "navbar", "title": "Results" } },
          { "id": "r-title", "type": "text", "position": { "x": 50, "y": 100 }, "size": { "width": 293, "height": 50 }, "props": { "type": "text", "content": "Great Job!", "variant": "title", "align": "center" } },
          { "id": "r-score", "type": "text", "position": { "x": 50, "y": 160 }, "size": { "width": 293, "height": 80 }, "props": { "type": "text", "content": "4/5", "variant": "headline", "align": "center" } },
          { "id": "r-badge", "type": "badge", "position": { "x": 120, "y": 260 }, "size": { "width": 153, "height": 30 }, "props": { "type": "badge", "label": "New Best Score!", "variant": "success" } },
          { "id": "r-again-btn", "type": "button", "position": { "x": 24, "y": 340 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Play Again", "variant": "primary" } },
          { "id": "r-done-btn", "type": "button", "position": { "x": 24, "y": 410 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Done", "variant": "secondary" } }
        ]
      }
    ],
    "connections": [
      { "id": "conn-1", "from": { "screenId": "screen-intro", "componentId": "intro-btn" }, "to": { "screenId": "screen-question" }, "label": "Start", "type": "arrow" },
      { "id": "conn-2", "from": { "screenId": "screen-question", "componentId": "q-btn" }, "to": { "screenId": "screen-results" }, "label": "Complete", "type": "arrow" },
      { "id": "conn-3", "from": { "screenId": "screen-results", "componentId": "r-again-btn" }, "to": { "screenId": "screen-intro" }, "label": "Restart", "type": "dashed" }
    ]
  },
  "viewport": { "zoom": 0.6, "pan": { "x": 0, "y": 0 } },
  "createdAt": "2026-01-25T00:00:00.000Z",
  "updatedAt": "2026-01-25T00:00:00.000Z"
}
```

## Example: Login Flow

```json
{
  "version": "1.0",
  "name": "Login Flow Mockup",
  "type": "mockup",
  "content": {
    "type": "mockup",
    "screens": [
      {
        "id": "screen-login",
        "title": "Login",
        "device": "iphone",
        "position": { "x": 50, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "login-title", "type": "text", "position": { "x": 24, "y": 100 }, "size": { "width": 345, "height": 40 }, "props": { "type": "text", "content": "Welcome Back", "variant": "title" } },
          { "id": "login-subtitle", "type": "text", "position": { "x": 24, "y": 150 }, "size": { "width": 345, "height": 20 }, "props": { "type": "text", "content": "Sign in to continue", "variant": "body", "color": "#666666" } },
          { "id": "email-field", "type": "textfield", "position": { "x": 24, "y": 220 }, "size": { "width": 345, "height": 44 }, "props": { "type": "textfield", "placeholder": "Email", "label": "Email" } },
          { "id": "password-field", "type": "textfield", "position": { "x": 24, "y": 284 }, "size": { "width": 345, "height": 44 }, "props": { "type": "textfield", "placeholder": "Password", "label": "Password" } },
          { "id": "login-btn", "type": "button", "position": { "x": 24, "y": 368 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Sign In", "variant": "primary" } }
        ]
      },
      {
        "id": "screen-loading",
        "title": "Loading",
        "device": "iphone",
        "position": { "x": 500, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "loading-progress", "type": "progress", "position": { "x": 146, "y": 400 }, "size": { "width": 100, "height": 100 }, "props": { "type": "progress", "value": 50, "variant": "circle" } },
          { "id": "loading-text", "type": "text", "position": { "x": 100, "y": 520 }, "size": { "width": 193, "height": 20 }, "props": { "type": "text", "content": "Signing in...", "variant": "body", "align": "center", "color": "#666666" } }
        ]
      },
      {
        "id": "screen-error",
        "title": "Error",
        "device": "iphone",
        "position": { "x": 950, "y": 50 },
        "backgroundColor": "#ffffff",
        "statusBarStyle": "dark",
        "components": [
          { "id": "error-icon", "type": "icon", "position": { "x": 170, "y": 300 }, "size": { "width": 53, "height": 53 }, "props": { "type": "icon", "name": "alert-circle", "size": "large", "color": "#c92a2a" } },
          { "id": "error-title", "type": "text", "position": { "x": 50, "y": 380 }, "size": { "width": 293, "height": 40 }, "props": { "type": "text", "content": "Login Failed", "variant": "title", "align": "center" } },
          { "id": "error-message", "type": "text", "position": { "x": 50, "y": 430 }, "size": { "width": 293, "height": 40 }, "props": { "type": "text", "content": "Invalid email or password", "variant": "body", "align": "center", "color": "#666666" } },
          { "id": "retry-btn", "type": "button", "position": { "x": 24, "y": 510 }, "size": { "width": 345, "height": 50 }, "props": { "type": "button", "label": "Try Again", "variant": "primary" } }
        ]
      }
    ],
    "connections": [
      { "id": "conn-1", "from": { "screenId": "screen-login", "componentId": "login-btn" }, "to": { "screenId": "screen-loading" }, "label": "Submit", "type": "arrow" },
      { "id": "conn-2", "from": { "screenId": "screen-loading" }, "to": { "screenId": "screen-error" }, "label": "Error", "type": "arrow" },
      { "id": "conn-3", "from": { "screenId": "screen-error", "componentId": "retry-btn" }, "to": { "screenId": "screen-login" }, "label": "Retry", "type": "dashed" }
    ]
  }
}
```

## Best Practices

1. **Show All States**: Always include loading, error, and success states for features

2. **Screen Positioning**: Space screens 450px apart horizontally for readability
   - First screen: x: 50
   - Second screen: x: 500
   - Third screen: x: 950

3. **Use Standard Components**: Leverage built-in iOS components (NavBar, TabBar, List) for authentic feel

4. **Respect Safe Areas**:
   - iPhone top: Start content at y: 60 (after navbar)
   - iPhone bottom: Keep buttons above y: 750

5. **Component IDs**: Use descriptive prefixes (e.g., `intro-btn`, `q-navbar`, `r-title`)

6. **Full-Width Content**: Use 24px margins (345px width on iPhone)

7. **Consistent Spacing**:
   - Between components: 20px
   - Button from bottom: 102px
   - Section spacing: 40px

8. **Use Variants**: Leverage component variants for semantic meaning
   - Buttons: `primary` for main action, `secondary` for alternatives
   - Cards: `error` for problems, `success` for confirmations

9. **Connect Screens**: Always add connections showing navigation flow

10. **Set Zoom**: Use zoom: 0.6 for mockups to fit multiple screens in viewport

11. **Label Connections**: Make navigation actions clear ("Tap", "Submit", "Complete")

12. **Use Icons**: Add icons to enhance visual communication and match iOS patterns

## iOS Patterns

### Navigation
- Always include NavBar at top
- Use "Back" button for hierarchical navigation
- Right actions for "Done", "Save", "Edit"

### Forms
- Group related fields together
- Use appropriate keyboard types
- Show validation states (error/success variants)

### Lists
- Use `inset` variant for grouped settings
- Use `plain` variant for full-width lists
- Include appropriate accessories (chevron, switch, checkmark)

### Buttons
- Primary for main action (one per screen)
- Secondary for alternatives
- Destructive for delete/cancel actions

### Feedback
- Progress bars for multi-step processes
- Loading states for async operations
- Error screens with retry actions
- Success states with clear next steps

## Implementation Notes

- Always create the `.flowy/` directory in the workspace if it doesn't exist
- Use ISO 8601 format for timestamps (e.g., `new Date().toISOString()`)
- Validate all component IDs are unique within each screen
- Ensure all connection screenIds and componentIds exist
- Position screens left-to-right with 450px spacing
- Use 24px margins for iPhone content (393 - 48 = 345px width)
- Include both forward (arrow) and backward (dashed) navigation
