# TOOLS.md — Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- API endpoints and credentials references
- Slack channel IDs
- Common command shortcuts
- Device names and locations
- Environment-specific notes

## Examples

```markdown
### Slack Channels
- #general → C01234ABCDE
- #dev → C05678FGHIJ

### Common Commands
- Deploy: `./scripts/deploy.sh prod`
- Test: `npm run test:watch`

### SSH Hosts
- prod-server → 10.0.0.1, user: deploy
```

## Why Separate from Skills?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Agent Tools Plugin

If using the agent-tools plugin from vesper-team-skills:

### Slash Commands
```
/workflows:plan <feature>     # Create project plan
/workflows:work               # Execute work plan
/workflows:review             # Multi-agent code review
/changelog [daily|weekly]     # Generate changelog
```

### Task Management
```
task_list()                   # List all tasks
task_create("Description")    # Create task
task_update(id, status="done") # Update task
```

---

Add whatever helps you do your job. This is your cheat sheet.
