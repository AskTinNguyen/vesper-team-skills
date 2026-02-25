# Gestalt Frontend Design Reference

Detailed code patterns, rationale, and best practices organized by use case. Each section demonstrates the Gestalt thinking behind specific layout decisions with concrete React + Tailwind CSS + shadcn/ui implementations.

---

## Table of Contents

1. [Forms and Input Layouts](#1-forms-and-input-layouts)
2. [Dashboards and Data Displays](#2-dashboards-and-data-displays)
3. [Navigation and Wayfinding](#3-navigation-and-wayfinding)
4. [Modals, Dialogs, and Overlays](#4-modals-dialogs-and-overlays)
5. [Chat and Conversational Interfaces](#5-chat-and-conversational-interfaces)
6. [Agent Dashboards and Multi-Agent UIs](#6-agent-dashboards-and-multi-agent-uis)
7. [Code and Developer Tool Interfaces](#7-code-and-developer-tool-interfaces)
8. [Settings and Configuration Pages](#8-settings-and-configuration-pages)
9. [Cards, Lists, and Grid Layouts](#9-cards-lists-and-grid-layouts)
10. [Dark Mode and Theming](#10-dark-mode-and-theming)
11. [Responsive Adaptations](#11-responsive-adaptations)
12. [Motion and Animation](#12-motion-and-animation)

---

## 1. Forms and Input Layouts

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Proximity** | 3-tier spacing hierarchy (label/field/section) | The brain groups items by spatial distance. Tight label-to-input spacing (4-8px) signals ownership; wider field-to-field spacing (12-16px) signals siblings; section gaps (24-32px) signal category boundaries. |
| **Similarity** | Consistent input styling, uniform label treatment | All text inputs sharing the same height, border-radius, and padding are perceived as "the same kind of thing." Mixed styling forces the user to evaluate each field individually, increasing cognitive load. |
| **Common Region** | Card container around the form; background sections | Enclosing the form in a Card creates a bounded workspace. Sub-sections with subtle backgrounds (e.g., "Shipping" vs "Billing") create nested regions without border clutter. |
| **Continuity** | Single-column layout, top-to-bottom flow | The eye scans downward through a predictable path. Multi-column forms break this continuity and force lateral scanning, which research shows increases completion time. |

### Good Pattern: Proximity-Grouped Form

```tsx
<Card>
  <CardHeader>
    <CardTitle>Create Account</CardTitle>
    <CardDescription>Enter your information to get started.</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="space-y-8">                           {/* Section separation: 32px */}

      {/* Personal Information Section */}
      <section className="space-y-4">                     {/* Field-to-field: 16px */}
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Personal Information
        </h3>
        <div className="grid grid-cols-2 gap-4">          {/* Similarity: equal-width = equal importance */}
          <div className="space-y-2">                     {/* Label-to-input: 8px */}
            <Label htmlFor="firstName">First Name</Label>
            <Input id="firstName" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="lastName">Last Name</Label>
            <Input id="lastName" />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" />
          <p className="text-xs text-muted-foreground">
            Used for account recovery only.
          </p>
        </div>
      </section>

      <Separator />                                       {/* Explicit group boundary */}

      {/* Security Section */}
      <section className="space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Security
        </h3>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirm">Confirm Password</Label>
          <Input id="confirm" type="password" />
        </div>
      </section>
    </div>
  </CardContent>
  <CardFooter className="flex justify-end gap-3">
    <Button variant="outline">Cancel</Button>
    <Button>Create Account</Button>
  </CardFooter>
</Card>
```

**Why this works:**
- Three distinct spacing tiers (8px, 16px, 32px) create an unambiguous hierarchy
- The `Separator` reinforces the section boundary beyond proximity alone
- Grid layout for first/last name uses **symmetry** to signal equal importance
- Helper text sits at 8px below the input, inside the label-input proximity group
- Actions are right-aligned with consistent button styling (**similarity**)

### Bad Pattern: Flat Spacing

```tsx
{/* ANTI-PATTERN: uniform spacing destroys grouping */}
<div className="space-y-4">
  <Input placeholder="First Name" />
  <Input placeholder="Last Name" />
  <Input placeholder="Email" />
  <Input placeholder="Password" />
  <Input placeholder="Confirm Password" />
  <Button>Submit</Button>
</div>
```

**Why this fails:**
- All fields are equidistant (16px), so the brain cannot form logical groups
- No labels -- user must read placeholder text, which disappears on focus
- No section differentiation between personal info and security
- No container boundary -- the form floats without a visual anchor
- Submit button has the same spacing as fields, not perceived as a distinct action zone

---

## 2. Dashboards and Data Displays

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Common Region** | Cards per widget/metric | Each Card boundary signals "this data is one unit." Without cards, adjacent numbers blur into a wall of data. NNGroup research confirms common region "overpowers most other elements, including proximity." |
| **Similarity** | Equal-sized cards for equal-weight data | Cards of the same size signal the same importance. A larger card signals a primary metric; smaller cards signal secondary detail. |
| **Proximity** | Tighter spacing within cards, wider between | 16px padding inside cards with 24px gaps between them creates the proximity differential that defines card boundaries. |
| **Figure-Ground** | Elevated primary metrics over secondary data | Shadow, color contrast, or size prominence on the primary KPI creates a figure that draws the eye first. |

### Good Pattern: KPI Dashboard

```tsx
<div className="space-y-8">
  {/* Primary KPI Row */}
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    {metrics.map((metric) => (
      <Card key={metric.id}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {metric.label}
          </CardTitle>
          <metric.icon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metric.value}</div>
          <p className="text-xs text-muted-foreground mt-1">
            <span className={cn(
              metric.trend > 0 ? "text-green-600" : "text-red-600"
            )}>
              {metric.trend > 0 ? "+" : ""}{metric.trend}%
            </span>
            {" "}from last period
          </p>
        </CardContent>
      </Card>
    ))}
  </div>

  {/* Chart Section -- larger common region for primary visualization */}
  <Card>
    <CardHeader>
      <CardTitle>Revenue Over Time</CardTitle>
      <CardDescription>Last 12 months</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="h-[300px]">
        {/* Chart component here */}
      </div>
    </CardContent>
  </Card>

  {/* Secondary Data -- smaller cards, different density tier */}
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    {secondaryMetrics.map((item) => (
      <Card key={item.id} className="p-4">
        <p className="text-xs text-muted-foreground">{item.label}</p>
        <p className="text-lg font-semibold mt-1">{item.value}</p>
      </Card>
    ))}
  </div>
</div>
```

**Why this works:**
- Three visual tiers: primary KPIs (3-col, detailed cards), chart (full-width, tall), secondary metrics (4-col, compact). **Figure-ground** hierarchy is explicit.
- All primary KPI cards share identical structure (**similarity**). Users can scan the row as one perceptual group.
- `gap-6` between primary cards vs `gap-4` between secondary cards signals different density tiers.
- `space-y-8` between sections creates clear section breaks (**proximity**).
- Trend colors (green/red) use **similarity** for instant pattern recognition: green = positive, red = negative.

---

## 3. Navigation and Wayfinding

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Similarity** | All nav items share baseline styling | Shared font weight, size, and color signals "these are all navigation targets." Users build a mental model: "things that look like this are clickable links." |
| **Figure-Ground** | Active item distinguished from inactive | The active item must be the figure within the nav group. Stronger contrast, background fill, or underline promotes it above its siblings. |
| **Continuity** | Items aligned along a horizontal or vertical axis | The eye follows the continuous line of nav items. Breaking alignment (e.g., one item offset) disrupts the perceived group. |
| **Common Region** | Nav bar with distinct background | A background or border on the nav container creates a common region that groups all nav items and separates them from page content. |

### Good Pattern: Segmented Navigation

```tsx
<nav className="flex items-center gap-1 rounded-lg bg-muted p-1">
  {navItems.map((item) => (
    <button
      key={item.id}
      className={cn(
        "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
        item.active
          ? "bg-background text-foreground shadow-sm"     // Figure: elevated
          : "text-muted-foreground hover:text-foreground"  // Ground: receded
      )}
    >
      {item.label}
    </button>
  ))}
</nav>
```

**Gestalt rationale:**
- `bg-muted p-1 rounded-lg` creates a **common region** container
- All items share `px-3 py-1.5 text-sm font-medium rounded-md` (**similarity**)
- Active item gets `bg-background shadow-sm` -- promoted to **figure** within the group
- `gap-1` maintains tight **proximity** so all items read as one unit
- Horizontal `flex` creates **continuity** along the x-axis

### Good Pattern: Breadcrumb Trail

```tsx
<nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
  {segments.map((segment, i) => (
    <Fragment key={segment.path}>
      {i > 0 && (
        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50" />
      )}
      {i < segments.length - 1 ? (
        <a
          href={segment.path}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          {segment.label}
        </a>
      ) : (
        <span className="text-foreground font-medium">{segment.label}</span>
      )}
    </Fragment>
  ))}
</nav>
```

**Gestalt rationale:**
- Chevrons create **continuity** -- the eye follows the path left to right
- All intermediate items share muted styling (**similarity** as a group)
- Final item breaks similarity with `font-medium` + `text-foreground` (**figure-ground**: current location is the figure)
- `gap-2` is tight enough for items to read as a connected path

---

## 4. Modals, Dialogs, and Overlays

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Figure-Ground** | Dialog elevated over dimmed background | The most direct application of figure-ground in all of UI. The overlay creates an unambiguous "ground" and the dialog is the sole "figure." This is why modals must always have an overlay -- without it, figure-ground is weakened. |
| **Proximity** | Tight content grouping within the dialog | A dialog is a small, focused workspace. Internal spacing should be tighter than page-level spacing to keep content cohesive. |
| **Closure** | Clear action buttons to "complete" the interaction | The dialog is an incomplete state -- the user arrived because something needs resolution. Action buttons represent closure: completing the mental loop. |
| **Common Region** | The dialog itself is a bounded region | Shadow, border-radius, and solid background create a strong container boundary. |

### Good Pattern: Destructive Confirmation Dialog

```tsx
<Dialog>
  <DialogContent className="sm:max-w-[425px]">
    <DialogHeader>
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
          <AlertTriangle className="h-5 w-5 text-red-600" />
        </div>
        <div className="space-y-1">                      {/* Proximity: icon + text grouped */}
          <DialogTitle>Delete Project</DialogTitle>
          <DialogDescription>
            This will permanently delete <span className="font-medium text-foreground">
            "My Project"</span> and all associated data.
          </DialogDescription>
        </div>
      </div>
    </DialogHeader>
    <DialogFooter className="gap-2 sm:gap-0">
      <Button variant="outline">Cancel</Button>
      <Button variant="destructive">Delete Project</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Gestalt rationale:**
- `DialogOverlay` (provided by shadcn) dims the page to pure **ground**
- Dialog has `shadow-lg`, `rounded-lg`, solid `bg-background` -- unmistakable **figure**
- Red icon in red circle uses **similarity** (red = danger) and **common region** (circle bounds the icon)
- Project name in `font-medium text-foreground` uses **figure-ground** within the text: the specific subject stands out from the description
- Two-button footer uses **similarity** (both are buttons) with **dissimilarity** for intent (outline = safe, destructive = danger)

### Good Pattern: Sheet (Side Panel)

```tsx
<Sheet>
  <SheetContent className="w-[400px] sm:w-[540px]">
    <SheetHeader>
      <SheetTitle>Agent Details</SheetTitle>
      <SheetDescription>View and manage agent configuration.</SheetDescription>
    </SheetHeader>
    <div className="space-y-6 py-4">                     {/* Sections separated by 24px */}
      <section className="space-y-3">                    {/* Items in section: 12px */}
        <h4 className="text-sm font-medium">Status</h4>
        {/* status content */}
      </section>
      <Separator />
      <section className="space-y-3">
        <h4 className="text-sm font-medium">Configuration</h4>
        {/* config content */}
      </section>
    </div>
  </SheetContent>
</Sheet>
```

**Gestalt rationale:**
- Sheet slides in from the edge, creating **figure-ground** (sheet is figure, dimmed page is ground)
- Unlike a centered dialog, the sheet maintains spatial connection to the page via its anchored edge (**continuity** with the page layout)
- Internal content uses **proximity** tiers: 12px within sections, 24px between sections

---

## 5. Chat and Conversational Interfaces

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Proximity** | Turn gaps > intra-message gaps > intra-block gaps | Three spacing tiers separate conversation turns, blocks within a response, and elements within a block. This creates the essential rhythm of conversational UI. |
| **Common Region** | Tool call results in bordered containers | Tool outputs (web search results, code execution, file reads) enclosed in distinct containers signal "this is retrieved data, not generated prose." NNGroup confirms common region overpowers proximity for grouping. |
| **Continuity** | Vertical thread flow, streaming text | The conversation reads top-to-bottom as a continuous temporal flow. Streaming tokens maintain animated continuity during generation. |
| **Closure** | Streaming cursor, collapsible reasoning, "Show more" | During generation, the blinking cursor signals incomplete content. Collapsed thinking sections leverage closure -- users perceive the reasoning as "complete at this level." |
| **Figure-Ground** | Message bubbles over canvas; code blocks within messages | Each layer of nesting creates a figure-ground relationship: page < chat flow < message bubble < embedded block (code/tool/decision). |

### Good Pattern: AI Chat Message with Tool Output

```tsx
<div className="space-y-6">                              {/* Turn gap: 24px */}

  {/* User message */}
  <div className="flex justify-end">
    <div className="max-w-[80%] rounded-2xl bg-primary text-primary-foreground px-4 py-3">
      <p className="text-sm">Find the latest revenue numbers and create a chart.</p>
    </div>
  </div>

  {/* Assistant response */}
  <div className="space-y-3">                            {/* Intra-message gap: 12px */}

    {/* Tool call container -- Common Region */}
    <div className="rounded-lg border border-border bg-muted/50 p-3 space-y-2">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Search className="h-3.5 w-3.5" />
        <span className="font-medium">Searching database...</span>
      </div>
      <div className="text-sm">
        Found 4 quarterly revenue records for 2025.
      </div>
    </div>

    {/* Text response */}
    <div className="space-y-2">                          {/* Intra-block gap: 8px */}
      <p className="text-sm">
        Here are the revenue numbers for 2025. Q4 showed the strongest growth
        at 23% quarter-over-quarter.
      </p>
    </div>

    {/* Code block -- nested figure-ground */}
    <div className="rounded-lg bg-gray-950 text-gray-50 p-4 text-sm font-mono overflow-x-auto">
      <pre>{`const data = [
  { quarter: "Q1", revenue: 42500 },
  { quarter: "Q2", revenue: 48200 },
  { quarter: "Q3", revenue: 51800 },
  { quarter: "Q4", revenue: 63700 },
];`}</pre>
    </div>
  </div>
</div>
```

**Why this works:**
- 24px between turns, 12px between blocks in a response, 8px within a block -- three tiers of **proximity**
- Tool call container (`border bg-muted/50 rounded-lg`) is a **common region** with its own internal proximity
- Code block (`bg-gray-950 text-gray-50`) creates **figure-ground** reversal: dark surface against light page
- User message right-aligned, assistant left-aligned -- spatial **dissimilarity** signals different authors
- Tool icon + label use **proximity** (tight `gap-2`) to read as one unit

### Good Pattern: Inline Decision Card

```tsx
<div className="rounded-xl border-2 border-amber-200 bg-amber-50/50 p-4 space-y-3
                shadow-sm">
  <div className="flex items-start gap-3">
    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100
                    mt-0.5">
      <ShieldAlert className="h-4 w-4 text-amber-700" />
    </div>
    <div className="space-y-1 flex-1">
      <p className="text-sm font-medium">File write permission requested</p>
      <p className="text-xs text-muted-foreground">
        The agent wants to create <code className="bg-muted px-1 rounded">
        src/utils/parser.ts</code>
      </p>
    </div>
  </div>
  <div className="flex justify-end gap-2">
    <Button size="sm" variant="outline">Deny</Button>
    <Button size="sm" className="bg-amber-600 hover:bg-amber-700 text-white">
      Allow
    </Button>
  </div>
</div>
```

**Gestalt rationale:**
- Amber border + background creates a **common region** that is visually distinct from regular messages
- `border-2` and `shadow-sm` elevate the card above conversation (**figure-ground**: this demands attention)
- Icon color, border color, and button color all share the amber hue (**similarity**: this is one cohesive "permission" unit)
- Context text and action buttons are in the same container (**proximity**: reducing cognitive load of correlating what needs approval with how to approve)
- Code element (`<code>`) uses background highlight for **figure-ground** within text

---

## 6. Agent Dashboards and Multi-Agent UIs

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Similarity** | Color-coded status across all views | A green "running" badge on Agent A and Agent B creates an implicit group even across spatial distance. Users scan for "all the green ones" using preattentive processing. |
| **Common Fate** | Synchronized animations for coordinated updates | When multiple agents complete simultaneously, animating their status changes together signals a coordinated event. Desynchronized animations break this and create visual chaos. |
| **Proximity** | Tight within agent cards, loose between cards | Agent name, status badge, task description, and metrics tightly grouped within a card. Wider gaps between cards establish card boundaries without needing heavy borders. |
| **Figure-Ground** | Active/errored agents prominent; idle agents receded | The agent needing attention should be the visual figure. Idle agents can recede with muted contrast. |
| **Spatial Stability** | Agents maintain fixed positions | If agent cards rearrange with every update, users lose their spatial mental model. Keep positions stable; signal changes through color/badge updates, not position shifts. |

### Good Pattern: Multi-Agent Status Grid

```tsx
<div className="space-y-6">
  <div className="flex items-center justify-between">
    <h2 className="text-lg font-semibold">Active Agents</h2>
    <Badge variant="outline" className="text-xs">
      {agents.filter(a => a.status === "running").length} running
    </Badge>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {agents.map((agent) => (
      <Card
        key={agent.id}
        className={cn(
          "transition-colors",
          agent.status === "error" && "border-red-300 bg-red-50/50",
          agent.status === "running" && "border-green-200",
          agent.status === "idle" && "opacity-60",          // Ground treatment
        )}
      >
        <CardContent className="p-4 space-y-3">
          {/* Agent identity -- tight proximity */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={cn(
                "h-2 w-2 rounded-full",
                agent.status === "running" && "bg-green-500 animate-pulse",
                agent.status === "error" && "bg-red-500",
                agent.status === "idle" && "bg-gray-400",
                agent.status === "completed" && "bg-blue-500",
              )} />
              <span className="text-sm font-medium">{agent.name}</span>
            </div>
            <Badge variant="secondary" className="text-xs">
              {agent.role}
            </Badge>
          </div>

          {/* Current task */}
          <p className="text-xs text-muted-foreground line-clamp-2">
            {agent.currentTask}
          </p>

          {/* Metrics -- similarity through consistent layout */}
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>{agent.tokensUsed} tokens</span>
            <span>{agent.duration}</span>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
</div>
```

**Gestalt rationale:**
- Status dot color is consistent across the entire app (**similarity**: green=running everywhere)
- `animate-pulse` on running dots creates **common fate** -- all running agents pulse together
- Error agents get `border-red-300 bg-red-50/50` (**figure-ground**: errors demand attention)
- Idle agents get `opacity-60` (receded **ground** treatment)
- All cards share identical internal structure (**similarity**: users learn the layout once)
- `gap-4` between cards vs `space-y-3` (12px) inside cards creates **proximity** differential

### Good Pattern: Task Kanban with Agent Attribution

```tsx
<div className="grid grid-cols-4 gap-4">
  {["queued", "running", "blocked", "completed"].map((column) => (
    <div
      key={column}
      className={cn(
        "rounded-lg p-3 space-y-3 min-h-[200px]",
        column === "blocked" ? "bg-amber-50" : "bg-muted/50"  // Figure-ground: blocked column highlighted
      )}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium capitalize">{column}</h3>
        <span className="text-xs text-muted-foreground">
          {tasks.filter(t => t.status === column).length}
        </span>
      </div>
      <div className="space-y-2">                        {/* Tight between task cards */}
        {tasks
          .filter(t => t.status === column)
          .map((task) => (
            <Card key={task.id} className="p-3 space-y-2">
              <p className="text-sm font-medium line-clamp-1">{task.title}</p>
              <div className="flex items-center gap-2">
                <Avatar className="h-5 w-5">
                  <AvatarFallback className="text-[10px]">
                    {task.agent[0]}
                  </AvatarFallback>
                </Avatar>
                <span className="text-xs text-muted-foreground">{task.agent}</span>
              </div>
            </Card>
          ))}
      </div>
    </div>
  ))}
</div>
```

**Gestalt rationale:**
- Each column is a **common region** (`bg-muted/50 rounded-lg p-3`)
- Blocked column has a distinct background (`bg-amber-50`) -- **figure-ground** escalation
- Task cards within a column use `space-y-2` (tight **proximity**); columns separated by `gap-4`
- Agent avatars within task cards maintain consistent sizing (**similarity**)
- Column headers show count -- **closure** (users can gauge completeness)

---

## 7. Code and Developer Tool Interfaces

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Similarity** | Syntax highlighting groups semantic categories | Keywords, strings, comments, and identifiers each share a color. The brain groups all same-colored tokens across the file, enabling rapid categorical scanning. |
| **Closure** | Code folding collapses functions into signatures | A collapsed function is perceived as a complete entity. The fold indicator (`[+]` or triangle) signals intentional incompleteness, leveraging the brain's tendency to "fill in" the implementation. |
| **Figure-Ground** | Diff views: additions as figure, deletions as ground | Added code (green highlight) is promoted to figure status. Removed code (red/strikethrough) recedes. Unchanged context serves as deep ground with no highlighting. |
| **Continuity** | Inline AI suggestions as ghost text | AI completions appear as grayed-out continuation from the cursor. The user's code and the suggestion form one continuous line, making the suggestion feel like a natural extension. |
| **Proximity** | Terminal command-output grouping | Tight spacing between a command and its output signals they are one unit. Wider gaps between command-output pairs create scannable sections. |

### Good Pattern: Diff View

```tsx
<div className="rounded-lg border overflow-hidden">
  {changes.map((change, i) => (
    <div
      key={i}
      className={cn(
        "flex text-sm font-mono",
        change.type === "add" && "bg-green-50 text-green-900",       // Figure
        change.type === "remove" && "bg-red-50/60 text-red-800/70",  // Receding ground
        change.type === "context" && "text-muted-foreground",         // Deep ground
      )}
    >
      <span className="w-12 text-right pr-3 text-xs text-muted-foreground/60
                        select-none border-r">
        {change.lineNumber}
      </span>
      <span className="w-6 text-center select-none text-xs">
        {change.type === "add" ? "+" : change.type === "remove" ? "-" : " "}
      </span>
      <pre className="flex-1 px-2 py-0.5 whitespace-pre-wrap">
        {change.content}
      </pre>
    </div>
  ))}
</div>
```

**Gestalt rationale:**
- Three-tier **figure-ground**: added (green, full opacity), removed (red, reduced opacity), unchanged (muted)
- Line numbers in faint color serve as **ground** -- present but non-competing
- `+`/`-` symbols use **similarity** with their row color to reinforce the change type
- Monospace font and consistent line height create **continuity** down the diff
- The containing border creates a **common region** for the entire diff

### Good Pattern: Terminal Output Sections

```tsx
<div className="rounded-lg bg-gray-950 text-gray-100 p-4 font-mono text-sm space-y-4">
  {/* Command-output pair -- tight proximity */}
  <div className="space-y-1">
    <div className="flex items-center gap-2 text-green-400">
      <span>$</span>
      <span>bun test --filter auth</span>
    </div>
    <div className="text-gray-400 pl-4 space-y-0.5">
      <p><span className="text-green-400">PASS</span> auth/login.test.ts (12ms)</p>
      <p><span className="text-green-400">PASS</span> auth/session.test.ts (8ms)</p>
      <p><span className="text-red-400">FAIL</span> auth/refresh.test.ts (45ms)</p>
    </div>
  </div>

  {/* Error detail -- grouped under a header */}
  <div className="border-l-2 border-red-500 pl-3 space-y-1">
    <p className="text-red-400 font-medium">auth/refresh.test.ts</p>
    <p className="text-gray-500 text-xs">Expected token to be refreshed within 5s</p>
  </div>
</div>
```

**Gestalt rationale:**
- Command + output grouped with `space-y-1` (tight **proximity**); pairs separated by `space-y-4`
- PASS/FAIL use color **similarity**: green = success, red = failure
- Error detail uses `border-l-2 border-red-500` -- **common region** via left border + **similarity** with the red FAIL text
- `pl-4` indentation on output creates **proximity** nesting under the command

---

## 8. Settings and Configuration Pages

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Proximity** | Section groups with internal tight spacing | Settings are inherently categorical. "Notifications," "Privacy," and "Appearance" are distinct groups that need clear spatial separation. |
| **Common Region** | Card per settings category | Each category in its own Card container creates a bounded workspace. Users can mentally scope their attention to one card at a time. |
| **Similarity** | Consistent toggle/input/select styling | All switches, all inputs, and all selects should be visually identical within their type. Mixed styling forces users to re-evaluate each control. |
| **Continuity** | Vertical flow with section headings | Settings pages are long-form. Consistent section heading styling creates continuity markers that the eye tracks while scrolling. |

### Good Pattern: Sectioned Settings Page

```tsx
<div className="max-w-2xl mx-auto space-y-8">
  <div>
    <h1 className="text-2xl font-bold">Settings</h1>
    <p className="text-muted-foreground mt-1">
      Manage your account preferences.
    </p>
  </div>

  {/* Notifications Section */}
  <Card>
    <CardHeader>
      <CardTitle className="text-base">Notifications</CardTitle>
      <CardDescription>Choose what updates you receive.</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      {notificationSettings.map((setting) => (
        <div
          key={setting.id}
          className="flex items-center justify-between py-2"
        >
          <div className="space-y-0.5">                  {/* Label-description: 2px */}
            <Label className="text-sm font-medium">{setting.label}</Label>
            <p className="text-xs text-muted-foreground">{setting.description}</p>
          </div>
          <Switch checked={setting.enabled} />
        </div>
      ))}
    </CardContent>
  </Card>

  {/* Appearance Section */}
  <Card>
    <CardHeader>
      <CardTitle className="text-base">Appearance</CardTitle>
      <CardDescription>Customize the look and feel.</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex items-center justify-between py-2">
        <div className="space-y-0.5">
          <Label className="text-sm font-medium">Theme</Label>
          <p className="text-xs text-muted-foreground">Select light or dark mode.</p>
        </div>
        <Select defaultValue="system">
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </CardContent>
  </Card>
</div>
```

**Gestalt rationale:**
- Each settings category is a Card (**common region**)
- `space-y-8` (32px) between Cards creates clear section boundaries (**proximity**)
- `space-y-4` (16px) between settings within a Card creates sibling grouping
- `space-y-0.5` (2px) between label and description creates ownership (**proximity**: description belongs to label)
- All switches align to the right; all labels align to the left (**continuity**: vertical alignment guides)
- `max-w-2xl mx-auto` enforces single-column **continuity** and **Pragnanz** (simplest possible flow)

---

## 9. Cards, Lists, and Grid Layouts

### Gestalt Principles at Work

| Principle | Application | Rationale |
|-----------|------------|-----------|
| **Common Region** | Card boundaries group related content | The Card container signals "everything inside is one unit." This is the most literal application of common region in component-based UI. |
| **Symmetry** | Equal-width grid columns for equal-weight items | `grid-cols-3` with `1fr` columns signals three items of equal importance. Asymmetric grids (`2fr 1fr`) signal a primary-secondary relationship. |
| **Similarity** | Consistent card structure across a grid | Every card in a grid should have the same internal layout: image position, title style, metadata format. Users learn the pattern once and scan efficiently. |
| **Proximity** | Tighter internal padding than external gaps | Card padding (16-24px) should feel snug; inter-card gaps (16-24px) should feel spacious enough to separate cards. The critical test: can you tell where one card ends and another begins without borders? |

### Good Pattern: Content Card Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <Card key={item.id} className="overflow-hidden group">
      <div className="aspect-video bg-muted relative">
        <img
          src={item.image}
          alt={item.title}
          className="object-cover w-full h-full"
        />
        <Badge className="absolute top-2 right-2 text-xs">
          {item.category}
        </Badge>
      </div>
      <CardContent className="p-4 space-y-2">           {/* Internal: 8px between elements */}
        <h3 className="font-semibold line-clamp-1">{item.title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {item.description}
        </p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
          <Avatar className="h-5 w-5">
            <AvatarFallback>{item.author[0]}</AvatarFallback>
          </Avatar>
          <span>{item.author}</span>
          <span className="text-muted-foreground/50">|</span>
          <span>{item.date}</span>
        </div>
      </CardContent>
    </Card>
  ))}
</div>
```

**Gestalt rationale:**
- Equal grid columns (**symmetry**: all items carry equal visual weight)
- `gap-6` (24px) between cards > `p-4` (16px) internal padding ratio ensures clear card boundaries (**proximity**)
- Every card follows identical structure: image > title > description > meta (**similarity**: learn once, scan many)
- Category badge uses **common region** (badge container) + **figure-ground** (positioned over image)
- `line-clamp` on title/description ensures **closure** -- truncation with ellipsis signals more content exists
- Author avatar + name at 5px height are tightly proximate -- perceived as one "attribution" unit

### Good Pattern: Interactive List

```tsx
<div className="rounded-lg border divide-y">
  {items.map((item) => (
    <button
      key={item.id}
      className={cn(
        "flex items-center gap-4 w-full px-4 py-3 text-left",
        "hover:bg-muted/50 transition-colors",
        item.selected && "bg-primary/5 border-l-2 border-l-primary"
      )}
    >
      <div className="flex-1 min-w-0 space-y-0.5">
        <p className="text-sm font-medium truncate">{item.title}</p>
        <p className="text-xs text-muted-foreground truncate">{item.subtitle}</p>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
    </button>
  ))}
</div>
```

**Gestalt rationale:**
- `divide-y` creates subtle separators between items without heavy borders
- Selected item uses `border-l-2 border-l-primary bg-primary/5` (**figure-ground**: selected is elevated)
- All items share identical internal layout (**similarity**)
- `space-y-0.5` between title and subtitle creates label-detail **proximity**
- Chevron icons create **continuity** cue (pointing right = navigation continues)

---

## 10. Dark Mode and Theming

### Key Gestalt Considerations

Dark mode inverts figure-ground relationships and requires deliberate adjustments to maintain perceptual grouping.

### Principle: Surface Elevation via Lightness

In light mode, depth is communicated through shadow. In dark mode, shadows are nearly invisible against dark backgrounds. Instead, use progressively lighter surface colors:

```tsx
{/* Light mode: depth via shadow */}
<Card className="bg-white shadow-sm">...</Card>

{/* Dark mode: depth via surface lightness */}
<Card className="bg-white dark:bg-gray-800 shadow-sm dark:shadow-none">...</Card>
```

**Material Design 3 elevation mapping for dark mode:**

| Level | Surface Color | Tailwind Class | Usage |
|-------|--------------|---------------|-------|
| 0 (base) | `#09090b` | `bg-gray-950` | Page background |
| 1 | `#18181b` | `bg-gray-900` | Cards, content areas |
| 2 | `#27272a` | `bg-gray-800` | Elevated cards, popovers |
| 3 | `#3f3f46` | `bg-gray-700` | Dialogs, command palettes |

### Principle: Border Visibility

Borders that work at `border-gray-200` in light mode may vanish against dark backgrounds:

```tsx
<div className="border border-gray-200 dark:border-gray-700 rounded-lg">
  {/* Common region boundary visible in both modes */}
</div>
```

### Principle: Color Similarity Preservation

Color tokens must be semantic, not hard-coded. A status color that passes contrast in light mode may fail in dark mode:

```tsx
{/* BAD: hard-coded colors */}
<Badge className="bg-green-100 text-green-800">Active</Badge>

{/* GOOD: semantic tokens that adapt */}
<Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
  Active
</Badge>
```

**Rationale**: The **similarity** grouping (green = active) must persist across themes. If dark mode renders green-100 as nearly invisible, the grouping breaks.

---

## 11. Responsive Adaptations

### Key Gestalt Considerations

Proximity relationships established on desktop can break on mobile. The core rule: **maintain spacing ratios even as absolute values change.**

### Principle: Proportional Proximity Scaling

```tsx
<div className="space-y-4 md:space-y-6 lg:space-y-8">      {/* Between sections */}
  <section className="space-y-2 md:space-y-3">              {/* Within sections */}
    {/* content */}
  </section>
</div>
```

**Desktop:** 32px between sections, 12px within sections (ratio: 2.7:1)
**Mobile:** 16px between sections, 8px within sections (ratio: 2:1)

The ratio is preserved, so grouping perception is maintained.

### Principle: Grid-to-Stack Continuity

When a multi-column grid collapses to a single column on mobile, the **proximity** cue switches from horizontal adjacency to vertical sequence. Add extra vertical spacing to compensate:

```tsx
<div className="grid grid-cols-1 gap-4 md:grid-cols-3 md:gap-6">
  {/* On mobile, gap-4 is tighter to avoid excessive scrolling */}
  {/* On desktop, gap-6 provides breathing room between columns */}
</div>
```

### Principle: Common Region Simplification

Card shadows that work on desktop can feel heavy on mobile. Reduce or remove:

```tsx
<Card className="shadow-sm md:shadow-md">
  {/* Lighter shadow on mobile, standard on desktop */}
</Card>
```

### Principle: Navigation Continuity

Horizontal navigation wrapping to two lines on mobile breaks **continuity**. Options:

1. Hamburger menu (preserve the group as a single entity)
2. Horizontal scroll with peek (leverage **closure** -- partial visibility of next item)
3. Bottom tab bar (maintain **continuity** along a different axis)

---

## 12. Motion and Animation

### Key Gestalt Considerations

Motion is governed primarily by **Common Fate**: elements that move together, at the same speed, in the same direction, are perceived as a group.

### Principle: Synchronized Group Animation

Elements that belong together must animate together:

```tsx
{/* GOOD: Common Fate -- all items shift in unison */}
<div className="space-y-2">
  {items.map((item, i) => (
    <div
      key={item.id}
      className="transition-all duration-200 ease-out"
      // Same duration + easing for all items = common fate
    >
      {item.content}
    </div>
  ))}
</div>

{/* BAD: desynchronized motion breaks grouping */}
<div>
  {items.map((item, i) => (
    <div
      key={item.id}
      style={{ transitionDuration: `${200 + i * 100}ms` }}
      // Different durations = perceived as independent
    >
      {item.content}
    </div>
  ))}
</div>
```

**Exception**: Staggered entrance animations (30-50ms delay between items) reinforce sequential **continuity** and are acceptable when introducing a list for the first time.

### Principle: Entrance/Exit Asymmetry

Entrances should be slightly slower than exits:

```css
/* Entrance: 250ms ease-out (decelerates into position) */
.entering { transition: all 250ms cubic-bezier(0, 0, 0, 1); }

/* Exit: 200ms ease-in (accelerates out of view) */
.exiting { transition: all 200ms cubic-bezier(0.3, 0, 1, 1); }
```

**Rationale**: Appearing content needs longer to establish its position in the user's spatial model. Disappearing content is already known and can leave quickly.

### Principle: Respect `prefers-reduced-motion`

Motion-based Gestalt cues must degrade gracefully for vestibular sensitivity:

```css
@media (prefers-reduced-motion: reduce) {
  /* Replace motion with instant state changes */
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Alternative: Replace motion with opacity transitions, which are generally safe:

```tsx
<div className={cn(
  "transition-opacity duration-200",
  isVisible ? "opacity-100" : "opacity-0"
  // Opacity transitions are vestibular-safe
)} />
```

### Timing Constants Quick Reference

| Interaction | Duration | Easing |
|-------------|----------|--------|
| Toggle/checkbox | 100ms | `ease-out` |
| Button feedback | 150ms | `ease-out` |
| Tooltip appear | 200ms | `ease-out` |
| Dropdown open | 200ms | `cubic-bezier(0, 0, 0, 1)` |
| Modal enter | 250ms | `cubic-bezier(0, 0, 0, 1)` |
| Modal exit | 200ms | `cubic-bezier(0.3, 0, 1, 1)` |
| Page transition | 300ms | `cubic-bezier(0.2, 0, 0, 1)` |
| Skeleton pulse | 2000ms | `cubic-bezier(0.4, 0, 0.6, 1)` |

---

## Sources

### Academic
- Wertheimer, M. (1923). Laws of Organization in Perceptual Forms.
- Van Geert, E. & Wagemans, J. (2024). Pragnanz in Visual Perception. *Psychonomic Bulletin & Review*, 31, 1484-1508.
- Wagemans, J. et al. (2012). A Century of Gestalt Psychology in Visual Perception. *Psychological Bulletin*, 138(6).
- EEG study on Gestalt Similarity in interface color perception (2024). *International Journal of Industrial Ergonomics*, 98.
- Naik, S. et al. (2025). Exploring Human-AI Collaboration Using Mental Models. *ACM DIS 2025*.

### Design Systems
- Material Design 3: Spacing, Elevation, Motion tokens
- Apple Human Interface Guidelines: Layout, Typography, Vibrancy
- Carbon Design System (IBM): 2x Grid, Spacing scale
- Pinterest Gestalt: Design tokens, ESLint enforcement

### Practitioner
- Nielsen Norman Group: Proximity, Similarity, Common Region, Closure, Figure-Ground articles
- Smashing Magazine: Designing for Agentic AI (2026), Spaces in Web Design with Gestalt
- Interaction Design Foundation: Gestalt Principles (2026 update)
- ShapeofAI.com: Stream of Thought pattern
- Victor Dibia: 4 UX Design Principles for Multi-Agent Systems

### Implementation
- Tailwind CSS v4: Spacing scale, OKLCH colors, gap utilities
- shadcn/ui: Card, Dialog, Accordion, Tabs, Form component patterns
- WCAG 2.2: Contrast ratios, focus order, animation accessibility
