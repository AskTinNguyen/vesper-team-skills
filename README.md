# Vesper Team Skills

Shared skills for distribution via Vesper's Team Skills feature.

## Available Skills

| Skill | Description |
|-------|-------------|
| [dispatch](./dispatch/) | Multi-agent task coordination with parallel execution |

## Usage

### For Team Admins

1. Clone this repo
2. Add/update skills (each skill = directory with `SKILL.md`)
3. Commit and push

### For Team Members

1. Open Vesper Settings → Workspace → Team Skills
2. Enter repo URL: `atherslabs/vesper-team-skills`
3. Enter GitHub PAT (with `repo` scope for private repos)
4. Click "Save & Sync"

Skills will appear in your skills list with a "Team" badge.

### Post-Sync Setup

Some skills require additional setup after syncing:

**Dispatch skill:**
```bash
~/.vesper/team-skills/dispatch/setup.sh
```

## Adding New Skills

1. Create a directory: `my-skill/`
2. Add `SKILL.md` with YAML frontmatter:

```markdown
---
name: My Skill
description: What the skill does
icon: 🔧
---

# Instructions here...
```

3. Commit and push
4. Team members click "Sync" to get the new skill

## Skill Structure

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + instructions
├── setup.sh          # Optional: Post-sync setup script
├── icon.png          # Optional: Custom icon
└── ...               # Any additional files
```
