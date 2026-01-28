# Edit with AI - Implementation Examples

This document contains real-world implementation examples from the Vesper codebase.

## Example 1: Schedule Editing

### EditContext Configuration

```typescript
// Edit existing scheduled task with AI
'edit-schedule': (location) => ({
  context: {
    label: 'Edit Schedule',
    filePath: location, // JSON string with schedule data
    context:
      'The user wants to modify an existing scheduled task. ' +
      'The current schedule details are provided below. Parse their natural language request to understand what they want to change. ' +
      'Common requests: "change the time to 3pm", "make it run hourly", "update the prompt to...", "disable it", "rename it to...". ' +
      'Use the schedule_update tool with the scheduleId and only the fields being changed. ' +
      'Always confirm the changes with the user before applying. ' +
      'If the request is ambiguous, ask clarifying questions.',
  },
  example: 'Change it to run at 3pm',
  overridePlaceholder: 'How would you like to change this schedule?',
}),
```

### Data Types

```typescript
// Input data for schedule updates
export interface ScheduleUpdateData {
  scheduleId: string;          // Required: ID of schedule to update
  name?: string;               // Optional: New name
  prompt?: string;             // Optional: New prompt text
  scheduleType?: 'recurring' | 'once';
  frequency?: 'hourly' | 'daily' | 'weekdays' | 'weekly' | 'monthly' | 'custom';
  hour?: number;               // 0-23
  minute?: number;             // 0-59
  dayOfWeek?: number;          // 0-6 (Sun=0)
  dayOfMonth?: number;         // 1-31
  customCron?: string;         // Raw cron for custom
  scheduledFor?: string;       // ISO timestamp for one-time
  enabled?: boolean;           // Enable/disable
}

// Result from schedule update
export interface ScheduleUpdateResult {
  success: boolean;
  scheduleId?: string;
  scheduleName?: string;
  nextRun?: string;
  cronExpression?: string;
  humanReadable?: string;
  error?: string;
}
```

### Tool Implementation

```typescript
export function createScheduleUpdateTool(sessionId: string) {
  return tool(
    'schedule_update',
    `Update an existing scheduled task.

**Use this tool to modify any aspect of a schedule:**
- Change the name or prompt
- Update the timing (frequency, hour, minute, day)
- Enable or disable the schedule
- Convert between recurring and one-time

**Required:**
- scheduleId: The ID of the schedule to update (provided in context)

**Optional fields to update:**
- name: New name for the schedule
- prompt: New prompt to run
- scheduleType: Change to "recurring" or "once"
- frequency: hourly|daily|weekdays|weekly|monthly|custom
- hour: 0-23
- minute: 0-59
- dayOfWeek: 0-6 (0=Sunday)
- dayOfMonth: 1-31
- customCron: Raw cron expression
- scheduledFor: ISO timestamp for one-time
- enabled: true/false

**Examples:**
- Change time: { scheduleId: "xxx", hour: 15, minute: 30 }
- Change prompt: { scheduleId: "xxx", prompt: "New task description" }
- Disable: { scheduleId: "xxx", enabled: false }
- Change to weekly: { scheduleId: "xxx", frequency: "weekly", dayOfWeek: 1 }

**IMPORTANT:**
- Always confirm changes with the user before updating
- Only include fields that are being changed
- The scheduleId is provided in the edit context`,
    {
      scheduleId: z.string().describe('ID of the schedule to update'),
      name: z.string().min(1).max(100).optional().describe('New name for the schedule'),
      prompt: z.string().min(1).optional().describe('New prompt to run'),
      scheduleType: z.enum(['recurring', 'once']).optional(),
      frequency: z.enum(['hourly', 'daily', 'weekdays', 'weekly', 'monthly', 'custom']).optional(),
      hour: z.number().min(0).max(23).optional(),
      minute: z.number().min(0).max(59).optional(),
      dayOfWeek: z.number().min(0).max(6).optional(),
      dayOfMonth: z.number().min(1).max(31).optional(),
      customCron: z.string().optional(),
      scheduledFor: z.string().optional(),
      enabled: z.boolean().optional(),
    },
    async (args) => {
      const callbacks = sessionScopedToolCallbackRegistry.get(sessionId);

      if (!callbacks?.onScheduleUpdate) {
        return {
          content: [{ type: 'text' as const, text: 'Schedule update not available in this context.' }],
          isError: true,
        };
      }

      try {
        const result = await callbacks.onScheduleUpdate(args);

        if (result.success) {
          const changes: string[] = [];
          if (args.name) changes.push(`Name: ${args.name}`);
          if (args.prompt) changes.push(`Prompt: ${args.prompt.substring(0, 50)}${args.prompt.length > 50 ? '...' : ''}`);
          if (args.frequency) changes.push(`Frequency: ${args.frequency}`);
          if (args.hour !== undefined || args.minute !== undefined) {
            changes.push(`Time: ${args.hour ?? '*'}:${String(args.minute ?? 0).padStart(2, '0')}`);
          }
          if (args.enabled !== undefined) changes.push(`Enabled: ${args.enabled}`);

          return {
            content: [{
              type: 'text' as const,
              text: `✓ Schedule "${result.scheduleName}" updated successfully!\n\n` +
                    (changes.length > 0 ? `Changes:\n${changes.map(c => `  • ${c}`).join('\n')}\n\n` : '') +
                    `Schedule: ${result.humanReadable || result.cronExpression}\n` +
                    `Next run: ${result.nextRun}`
            }],
            isError: false,
          };
        } else {
          return {
            content: [{ type: 'text' as const, text: `Failed to update schedule: ${result.error}` }],
            isError: true,
          };
        }
      } catch (error) {
        return {
          content: [{
            type: 'text' as const,
            text: `Error updating schedule: ${error instanceof Error ? error.message : 'Unknown error'}`
          }],
          isError: true,
        };
      }
    }
  );
}
```

### Main Process Handler

```typescript
// In sessions.ts - wire up when session is created
managed.agent.onScheduleUpdate = async (data: ScheduleUpdateData): Promise<ScheduleUpdateResult> => {
  sessionLog.info(`Schedule update request for session ${managed.id}:`, data.scheduleId);

  try {
    const scheduler = getScheduler(managed.workspace.id, managed.workspace.rootPath);

    // Build partial update from provided fields
    const updates: Partial<{
      name: string;
      prompt: string;
      cron: string | null;
      scheduledFor: number | null;
      enabled: boolean;
    }> = {};

    if (data.name !== undefined) updates.name = data.name;
    if (data.prompt !== undefined) updates.prompt = data.prompt;
    if (data.enabled !== undefined) updates.enabled = data.enabled;

    // Handle timing changes
    if (data.scheduleType === 'once' && data.scheduledFor) {
      updates.cron = null;
      updates.scheduledFor = new Date(data.scheduledFor).getTime();
    } else if (data.frequency || data.hour !== undefined || data.minute !== undefined) {
      // Generate new cron from parameters
      updates.cron = generateCronFromParams({
        ...data,
        scheduleType: 'recurring',
      });
      updates.scheduledFor = null;
    }

    const updated = await scheduler.update(data.scheduleId, updates);

    if (!updated) {
      return { success: false, error: 'Schedule not found' };
    }

    // Broadcast update for UI reactivity
    broadcast({
      type: 'schedule-updated',
      scheduleId: updated.id,
    }, managed.workspace.id);

    return {
      success: true,
      scheduleId: updated.id,
      scheduleName: updated.name,
      nextRun: updated.nextRun ? new Date(updated.nextRun).toLocaleString() : undefined,
      cronExpression: updated.cron || undefined,
      humanReadable: updated.cron ? cronToHumanReadable(updated.cron) : 'One-time schedule',
    };
  } catch (error) {
    sessionLog.error(`Failed to update schedule:`, error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};
```

### UI Component

```tsx
// In ScheduleDetailPanel.tsx
const editConfig = useMemo(() => {
  const context = JSON.stringify({
    scheduleId: schedule.id,
    name: schedule.name,
    prompt: schedule.prompt,
    cron: schedule.cron,
    enabled: schedule.enabled,
    nextRun: schedule.nextRun,
  });
  return getEditConfig('edit-schedule', context);
}, [schedule]);

return (
  <EditPopover
    trigger={
      <Button size="sm" variant="outline" className="gap-2">
        <Sparkles className="w-3 h-3" />
        Edit with AI
      </Button>
    }
    context={editConfig.context}
    example={editConfig.example}
    overridePlaceholder={editConfig.overridePlaceholder}
    workspaceId={workspaceId}
  />
);
```

---

## Example 2: Adding Sources (Create Flow)

Unlike edit flows, create flows start from scratch without existing data.

### EditContext Configuration

```typescript
'add-source': (location) => ({
  context: {
    label: 'Add Source',
    filePath: `${location}/sources/`, // Workspace sources directory
    context:
      'The user wants to add a new source to their workspace. ' +
      'Sources can be MCP servers (HTTP/SSE or stdio), REST APIs, or local filesystems. ' +
      'Ask clarifying questions if needed: What service? MCP or API? Auth type? ' +
      'Create the source folder and config.json in the workspace sources directory. ' +
      'Follow the patterns in ~/.vesper/docs/sources.md. ' +
      'After creating the source, call source_test with the source slug to verify the configuration.',
  },
  example: 'Connect to my Craft space',
  overridePlaceholder: 'What would you like to connect?',
}),
```

**Key differences from edit flows:**
- `overridePlaceholder` uses action-oriented language ("What would you like to connect?")
- Context instructs agent to ask clarifying questions first
- References documentation files for schema patterns
- Uses validation tool after creation

---

## Example 3: Workspace Permissions

### EditContext Configuration

```typescript
'workspace-permissions': (location) => ({
  context: {
    label: 'Permission Settings',
    filePath: `${location}/permissions.json`,
    context:
      'The user is on the Settings Screen and pressed the edit button on Workspace Permission settings. ' +
      'Their intent is likely to update the setting immediately unless otherwise specified. ' +
      'The permissions.json file configures Explore mode rules. It can contain: allowedBashPatterns, ' +
      'allowedMcpPatterns, allowedApiEndpoints, blockedTools, and allowedWritePaths. ' +
      'After editing, call config_validate with target "permissions" to verify the changes. ' +
      'Confirm clearly when done.',
  },
  example: "Allow running 'make build' in Explore mode",
}),
```

**Key differences:**
- Uses file path instead of JSON state (agent edits the actual file)
- References validation tool for post-edit verification
- No session-scoped tool needed - uses standard file editing tools

---

## Example 4: Session Templates

### EditContext Configuration

```typescript
'add-template': (location) => ({
  context: {
    label: 'Add Template',
    filePath: `${location}/templates/`,
    context:
      'The user wants to create a new session template for quickly starting chats with preset configurations. ' +
      'Templates are stored as JSON files in the templates folder with a UUID filename. ' +
      'Template fields: name (required), description, scope ("workspace"), workspaceId, ' +
      'permissionMode ("safe"/"ask"/"allow-all"), model (e.g., "claude-sonnet-4-20250514"), ' +
      'thinkingLevel (0-5), initialPrompt (text pre-filled in input), gatherContext (instructions for Claude), ' +
      'skillIds (array of skill slugs), workingDirectory. ' +
      'Ask clarifying questions: What is this template for? What permission mode? ' +
      'Should it pre-fill a prompt or have Claude gather context? Any specific skills to attach? ' +
      'Create the template JSON file with a generated UUID as the filename. ' +
      'After creating, confirm the template is ready to use.',
  },
  example: 'Code review template in safe mode',
  overridePlaceholder: 'What kind of workflow do you want to save?',
}),
```

**Key patterns:**
- Detailed schema documentation in context
- Specific clarifying questions to ask
- File-based creation (no session-scoped tool)

---

## Summary: When to Use Each Pattern

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Session-scoped tool** | Operations requiring main process services | Schedule CRUD, source activation |
| **File editing** | Direct config file modifications | Permissions, templates, skill YAML |
| **Hybrid** | Create file + validate/test | Source creation, skill creation |

**Decision tree:**
1. Does the operation need main process services (scheduler, MCP client, etc.)? → Session-scoped tool
2. Is it pure config editing? → File editing with validation tool
3. Does it need both file creation and service interaction? → Hybrid approach
