# Task Tools API Reference

This document details the Claude Code Task tools used for coordination.

## TaskCreate

Creates a new task in the current task list.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Brief title in imperative form (e.g., "Implement login endpoint") |
| `description` | string | Yes | Detailed requirements, context, and acceptance criteria |
| `activeForm` | string | Recommended | Present continuous form shown while in progress (e.g., "Implementing login endpoint") |
| `metadata` | object | No | Arbitrary key-value pairs for custom data |

### Example

```
TaskCreate(
  subject: "Implement user authentication endpoint",
  description: "Create POST /api/auth/login endpoint that:\n- Validates email and password\n- Returns JWT token on success\n- Returns 401 on invalid credentials\n- Rate limits to 5 attempts per minute per IP\n\nAcceptance criteria:\n- [ ] Endpoint responds to POST requests\n- [ ] Returns 200 with { token: string } on success\n- [ ] Returns 401 with { error: string } on failure\n- [ ] Rate limiting implemented and tested",
  activeForm: "Implementing user authentication endpoint"
)
```

### Notes

- Tasks are created with status `pending`
- Task IDs are auto-generated
- Use imperative form for `subject`, present continuous for `activeForm`

---

## TaskUpdate

Updates an existing task's properties.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | string | Yes | The ID of the task to update |
| `status` | string | No | New status: `pending`, `in_progress`, or `completed` |
| `subject` | string | No | New subject line |
| `description` | string | No | New description |
| `activeForm` | string | No | New active form text |
| `owner` | string | No | Agent/session identifier claiming the task |
| `addBlockedBy` | string[] | No | Task IDs that block this task |
| `addBlocks` | string[] | No | Task IDs that this task blocks |
| `metadata` | object | No | Metadata keys to merge (set key to null to delete) |

### Examples

**Set task in progress with owner:**
```
TaskUpdate(
  taskId: "1",
  status: "in_progress",
  owner: "agent-sonnet-001"
)
```

**Add dependency:**
```
TaskUpdate(
  taskId: "3",
  addBlockedBy: ["1", "2"]
)
```

**Mark completed:**
```
TaskUpdate(
  taskId: "1",
  status: "completed"
)
```

### Status Workflow

```
pending → in_progress → completed
```

- Set `in_progress` when starting work (with owner)
- Set `completed` only when fully done
- Never skip states or go backward

---

## TaskList

Retrieves summary of all tasks in the current list.

### Parameters

None.

### Returns

Array of task summaries:

| Field | Description |
|-------|-------------|
| `id` | Task identifier |
| `subject` | Brief description |
| `status` | Current status |
| `owner` | Agent ID if claimed |
| `blockedBy` | List of blocking task IDs |

### Example Usage

```
TaskList()
```

### Output

```
Tasks:
1. [completed] Design API schema
2. [in_progress] Implement user model (owner: sonnet-001)
3. [pending] Build auth endpoints (blocked by: 2)
4. [pending] Write tests (blocked by: 3)
```

### Identifying Ready Tasks

A task is ready to spawn when:
- `status` is `pending`
- `blockedBy` is empty OR all blockedBy tasks are `completed`
- No `owner` assigned

---

## TaskGet

Retrieves full details of a specific task.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | string | Yes | The ID of the task to retrieve |

### Returns

Full task object including:
- `id`, `subject`, `description`
- `status`, `owner`
- `blockedBy`, `blocks`
- `metadata`
- `activeForm`

### Example

```
TaskGet(taskId: "3")
```

### Use Cases

- Get full description before spawning agent
- Check task dependencies
- Verify task state before updating

---

## Task (Subagent Spawning)

Spawns a subagent to work on a task. This is the core Task tool for agent orchestration.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subagent_type` | string | Yes | Agent type (usually "general-purpose") |
| `prompt` | string | Yes | Instructions for the subagent |
| `description` | string | Yes | Short description shown in UI (3-5 words) |
| `model` | string | No | Model selection: "opus", "sonnet", "haiku" |
| `run_in_background` | boolean | No | Run without blocking |
| `allowed_tools` | string[] | No | Tools to grant the agent |

### Example

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "Complete task 3: Build auth endpoints.\n\nRequirements:\n[paste task description]\n\nWhen done, mark task complete with TaskUpdate(taskId: \"3\", status: \"completed\")",
  description: "Building auth endpoints"
)
```

### Model Selection Guide

| Complexity | Model | Token Cost | Use Cases |
|------------|-------|------------|-----------|
| High | opus | $$$ | Architecture, complex refactors, multi-file logic |
| Medium | sonnet | $$ | Standard features, tests, integrations |
| Low | haiku | $ | Docs, config, simple fixes |

### Best Practices

1. **Include task context** in prompt - subagent has no prior context
2. **Specify completion action** - tell agent to call TaskUpdate when done
3. **Set owner first** - use TaskUpdate to claim task before spawning
4. **Match model to complexity** - don't use Opus for simple tasks

### Parallel Spawning

To spawn multiple agents in parallel, include multiple Task calls in a single message:

```
[Message with 3 Task tool calls]

Task(prompt: "Complete task 2...", model: "sonnet", ...)
Task(prompt: "Complete task 3...", model: "sonnet", ...)
Task(prompt: "Complete task 4...", model: "haiku", ...)
```

All three agents spawn concurrently.
