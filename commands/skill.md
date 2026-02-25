---
description: Explicitly invoke a skill by name
argument-hint: "<skill-name> [task description]"
---

# Skill

Explicitly invoke a skill by name, loading its knowledge and context regardless of automatic triggers.

## Usage

```
/skill <skill-name> [optional task description]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `skill-name` | Yes | Name of the skill to invoke (e.g., `remotion`, `elevenlabs`, `frontend-design`) |
| `task description` | No | Optional task to perform with the skill |

## Examples

```
/skill remotion
→ Loads Remotion skill context, ready for video creation tasks

/skill elevenlabs "Generate a voiceover for product demo"
→ Activates ElevenLabs skill with specific task context

/skill frontend-design
→ Loads frontend-design skill, ready to build UI components

/skill ffmpeg "convert input.mp4 to 1080p"
→ Invokes FFmpeg skill with conversion task
```

## Entry Point

On invocation with skill name:

### Step 1: Validate Skill

```
1. Check if skill exists in .claude/skills/{skill-name}/SKILL.md
2. If not found, search for partial matches
3. If multiple matches, list them and ask for clarification
4. If no matches, suggest checking /skills for available skills
```

### Step 2: Load Skill

```
1. Read .claude/skills/{skill-name}/SKILL.md
2. Parse YAML frontmatter (name, description, allowed-tools, etc.)
3. Load the skill's knowledge into context
4. If reference.md exists, note it for on-demand loading
```

### Step 3: Confirm Activation

```
✓ Skill activated: {skill-name}

{description from SKILL.md}

Ready to help. What would you like to do?
[Or use the task description if provided]
```

## Error Handling

### Skill Not Found

```
❌ Skill "{name}" not found.

Did you mean:
  • remotion (video creation)
  • ralph-loop (autonomous workflows)

Available skills: /skills
```

### Ambiguous Match

```
Multiple skills match "{partial-name}":

1. frontend-design - UI/UX design patterns
2. frontend-testing - Frontend testing workflows

Please specify the full skill name.
```

## Comparison with Automatic Triggers

| Mechanism | When to Use | Example |
|-----------|-------------|---------|
| **Natural language** | Casual requests | "Create a video with Remotion" |
| **Explicit `/skill`** | Force skill activation, scripting, or when natural language fails | `/skill remotion` |
| **In workflows** | Chain skills in automation | `/skill plan → /skill work` |

## Use Cases

1. **Override automatic selection** - When Claude picks the wrong skill
2. **Maintain context** - Keep skill loaded across multiple prompts
3. **Scripting** - Use in compound commands like `/lfg`
4. **Discovery** - Try skills you haven't used before
5. **Force reload** - Refresh skill context without restarting Claude

## Technical Notes

- Skills are loaded fresh on each `/skill` invocation
- Previous skill context is replaced, not stacked
- Arguments after skill name are passed as initial context
- Does not modify any files or registry

## See Also

- `/skills` - List all available skills
- `/skill-creator` - Create new skills
- `/heal-skill` - Fix skill formatting issues
