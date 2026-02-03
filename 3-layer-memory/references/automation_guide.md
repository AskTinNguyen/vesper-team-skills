# Optional Automation for 3-Layer Memory

## Philosophy

> **Manual until it hurts.** Start simple, add automation only when needed.

The 3-layer memory system is designed to work well without any automation. Use these options only when manual maintenance becomes painful.

## When to Consider Automation

| Situation | Recommendation |
|-----------|----------------|
| Creating 5+ entities per day | Use `manage_entity.py` script |
| Extracting facts from long conversations | Use `extract_facts.py` |
| Entity summaries always feel stale | Set up weekly synthesis |
| Too many daily notes to organize | Simplify format first |

## Option 1: Fact Extraction Script

```bash
# Add a fact manually
python3 ~/.claude/skills/3-layer-memory/scripts/extract_facts.py \
  --add -e maria.person.md --fact "Business partner on AI project"

# Supersede an old fact
python3 ~/.claude/skills/3-layer-memory/scripts/extract_facts.py \
  --add -e maria.person.md --fact "New status" --supersede "Old status"
```

## Option 2: Weekly Synthesis Script

```bash
# Dry run (see what would change)
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py --dry-run

# Apply changes
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py
```

## Option 3: Cron Automation (Advanced)

If you want automatic weekly synthesis:

```bash
# Add to crontab (runs every Sunday at 9 AM)
0 9 * * 0 python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py
```

## Migration from Complex Systems

If you have existing automation:

1. **Assess need**: Do you actually need automation? Try manual for a week.
2. **Simplify scripts**: Remove complex JSON handling
3. **Update entity format**: Convert to single-file markdown
4. **Test thoroughly**: Ensure automation still works with new format

## Monitoring

### Check Entity Count

```bash
ls -1 ~/life/entities/ | wc -l
```

### View Recent Facts

```bash
# Search for current facts
grep -r "\[current\]" ~/life/entities/
```

### Check Synthesis Status

```bash
# View synthesis logs (if using automation)
tail -50 ~/.memory_synthesis.log
```

## Troubleshooting

### Too Much Maintenance

- Reduce automation
- Simplify entity format
- Use simpler daily notes

### Facts Getting Disorganized

- Review and clean up manually
- Use consistent `[current]`/`[was]` prefixes
- Rewrite summaries when stale

### Automation Breaking

- Remember: automation is optional
- Fall back to manual editing
- Fix automation only if the pain returns
