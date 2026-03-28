# Gateway Response Contract

Use this when defining the bundled gateway result shape and teaching agents how to retry safely.

## Recommended Response Shape

Keep the exact field names app-specific if needed, but preserve these concepts:

```ts
type GatewayResponse = {
  ok: boolean;
  logs: Array<{ level: 'log' | 'warn' | 'error'; message: string }>;
  result?: unknown;
  error?: {
    code: string;
    message: string;
    toolName?: string;
  };
  completedCalls: Array<{
    callId: string;
    toolName: string;
  }>;
  inFlightCalls: Array<{
    callId: string;
    toolName: string;
  }>;
  timedOut: boolean;
  retryGuidance:
    | 'safe_to_retry'
    | 'inspect_before_retry'
    | 'do_not_blind_retry';
};
```

The exact schema can vary. The invariant is that the agent must be able to tell:

- what finished
- what may still be running
- whether blind retry is safe

## Success Example

```json
{
  "ok": true,
  "logs": [
    { "level": "log", "message": "Loaded task_1042" },
    { "level": "log", "message": "Updated status to in_progress" }
  ],
  "result": {
    "taskId": "task_1042",
    "status": "in_progress"
  },
  "completedCalls": [
    { "callId": "call_1", "toolName": "task_get" },
    { "callId": "call_2", "toolName": "task_update" }
  ],
  "inFlightCalls": [],
  "timedOut": false,
  "retryGuidance": "safe_to_retry"
}
```

## Structured Tool Failure Example

Use this when a real host-side tool fails and the bundled block should stop.

```json
{
  "ok": false,
  "logs": [
    { "level": "log", "message": "Loaded task_1042" }
  ],
  "error": {
    "code": "TASK_CONFLICT",
    "message": "Task was updated by another actor",
    "toolName": "task_update"
  },
  "completedCalls": [
    { "callId": "call_1", "toolName": "task_get" }
  ],
  "inFlightCalls": [],
  "timedOut": false,
  "retryGuidance": "inspect_before_retry"
}
```

## Timeout Or Partial-Mutation Example

Use this when some side effects may already have persisted.

```json
{
  "ok": false,
  "logs": [
    { "level": "log", "message": "Created comment on task_1042" }
  ],
  "error": {
    "code": "GATEWAY_TIMEOUT",
    "message": "Execution timed out after 120000ms"
  },
  "completedCalls": [
    { "callId": "call_1", "toolName": "task_comment_create" }
  ],
  "inFlightCalls": [
    { "callId": "call_2", "toolName": "task_update" }
  ],
  "timedOut": true,
  "retryGuidance": "do_not_blind_retry"
}
```

If your gateway cannot return `completedCalls` and `inFlightCalls`, it is not ready for side-effectful bundled execution.

## Worked Example

Use a neutral proxy noun such as `workspace.*` in portable docs. Replace it with your app's real gateway object.

### 1. Discovery

```ts
await workspace.tool_catalog_list({ query: 'task update', pack: 'core', limit: 5 });
await workspace.tool_catalog_get({ name: 'task_update' });
```

Expected result:

- the list call returns a small preview set
- the get call returns one exact schema with required and optional params

### 2. Bundled Execution

```ts
const task = await workspace.task_get({ taskId: 'task_1042' });

if (task.status !== 'in_progress') {
  await workspace.task_update({
    taskId: 'task_1042',
    status: 'in_progress'
  });
}

await workspace.task_comment_create({
  taskId: 'task_1042',
  body: 'Agent resumed work and updated status.'
});
```

### 3. Expected Agent Guidance

Teach the model:

1. search the common pack first
2. inspect one exact tool schema
3. call concrete methods directly
4. isolate long waits in a dedicated gateway call with an explicit timeout

### 4. Failure Interpretation

If the response says:

- `safe_to_retry`: the block failed before any side effect persisted
- `inspect_before_retry`: inspect the last completed call and refresh state first
- `do_not_blind_retry`: assume some side effect may already have persisted

## Acceptance Check

Before shipping, confirm you can paste these three artifacts into a design review:

1. one success payload
2. one structured tool failure payload
3. one timeout or partial-mutation payload
