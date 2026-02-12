# UI Patterns Reference

## Policy Editor Modal

The policy editor is a settings modal with four sections: JSON editor, preset selector, policy
tester, and summary badge.

### Modal State

```typescript
interface PolicyModalState {
  personaId: string
  personaName: string
  rawJson: string              // Editable JSON in textarea
  issues: string[]             // Zod validation errors
  testToolName: string         // Tool name for tester
  testToolInput: string        // JSON tool input for tester
  testResult: string | null    // Test result feedback
  saving: boolean
}
```

### Component Layout

```
+-- Policy Editor: {personaName} ----------------------------+
|                                                             |
|  Preset: [engineer]  [Apply]                                |
|  Normal dev workflow, credentials hidden                    |
|                                                             |
|  +-- JSON Policy ------------------------------------------+|
|  | {                                                       ||
|  |   "preset": "engineer",                                 ||
|  |   "hardDeniedReadPaths": ["**/.env"],                   ||
|  |   "hardDeniedBashBaseCommands": ["sudo"]                ||
|  | }                                                       ||
|  +---------------------------------------------------------+|
|  Warning: hardDeniedReadPaths[2]: invalid glob              |
|                                                             |
|  +-- Test Policy ------------------------------------------+|
|  | Tool: [Bash        ]  Input: [{"command":"sudo"}]       ||
|  | [Test] -> Blocked: Policy denies "sudo"                 ||
|  +---------------------------------------------------------+|
|                                                             |
|  Summary: 7 deny rules (3 read, 1 bash cmd, 1 bash        |
|  pattern, 1 MCP server, 1 API pattern)                     |
|                                                             |
|  [Cancel]                               [Save Policy]      |
+-------------------------------------------------------------+
```

### Key Callbacks

#### Open Modal

```typescript
async function handleEditPolicy(personaId: string) {
  const result = await ipc.getPersonaPolicy(workspaceId, personaId)
  if (result.success) {
    setPolicyModal({
      personaId,
      personaName: persona.name,
      rawJson: result.rawJson || '{}',
      issues: result.issues || [],
      testToolName: 'Bash',
      testToolInput: '{"command": ""}',
      testResult: null,
      saving: false,
    })
  }
}
```

#### Save Policy

```typescript
async function handleSavePolicy() {
  setPolicyModal(prev => ({ ...prev, saving: true }))
  const result = await ipc.savePersonaPolicy(workspaceId, personaId, rawJson)
  if (result.success) {
    closeModal()
  } else {
    setPolicyModal(prev => ({ ...prev, issues: result.issues, saving: false }))
  }
}
```

#### Test Tool Against Policy

```typescript
async function handleTestPolicy() {
  const result = await ipc.testPersonaPolicy(
    workspaceId, personaId, testToolName, JSON.parse(testToolInput)
  )
  setPolicyModal(prev => ({
    ...prev,
    testResult: result.allowed
      ? 'Allowed -- this tool would execute normally'
      : `Blocked -- ${result.message}`,
  }))
}
```

#### Apply Preset

```typescript
function handleApplyPreset(presetName: PolicyPreset) {
  const preset = POLICY_PRESETS[presetName]
  setPolicyModal(prev => ({
    ...prev,
    rawJson: JSON.stringify(preset, null, 2),
    issues: [],  // Presets are always valid
  }))
}
```

### Real-Time Validation

Validate JSON on every textarea change and display errors inline:

```typescript
function handleJsonChange(newJson: string) {
  let issues: string[] = []
  try {
    const parsed = JSON.parse(newJson)
    const result = PolicySchema.safeParse(parsed)
    if (!result.success) {
      issues = result.error.issues.map(i => `${i.path.join('.')}: ${i.message}`)
    }
  } catch (e) {
    issues = [`Invalid JSON: ${e.message}`]
  }
  setPolicyModal(prev => ({ ...prev, rawJson: newJson, issues }))
}
```

### IPC Handlers

Three IPC handlers support the UI:

| Channel | Direction | Payload | Response |
|---------|-----------|---------|----------|
| `persona:policy:get` | renderer to main | `{ workspaceId, personaId }` | `{ success, rawJson, parsed, summary, issues? }` |
| `persona:policy:save` | renderer to main | `{ workspaceId, personaId, rawJson }` | `{ success, summary, issues? }` |
| `persona:policy:test` | renderer to main | `{ workspaceId, personaId, toolName, toolInput }` | `{ success, allowed, message }` |

### Summary Badge

Show a compact summary of active deny rules:

```typescript
function PolicyBadge({ summary }: { summary: PolicySummary }) {
  if (summary.totalDenyRules === 0) return <Badge variant="outline">No restrictions</Badge>

  return (
    <Badge variant="secondary">
      {summary.preset && `${summary.preset} + `}
      {summary.totalDenyRules} deny rule{summary.totalDenyRules !== 1 ? 's' : ''}
    </Badge>
  )
}
```
