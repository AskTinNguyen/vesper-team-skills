# Heartbeat Integration for 3-Layer Memory

## Overview

The three-layer memory system integrates with Claude's heartbeat mechanism to automatically extract facts from conversations.

## Configuration

Add this section to your `HEARTBEAT.md`:

```markdown
## Memory System — Fact Extraction

On each heartbeat:
1. Check for new conversations since `lastExtractedTimestamp`
2. Spawn cheap sub-agent (Haiku or equivalent) to extract durable facts
3. For each extracted fact:
   - Identify matching entity (person/company/project)
   - Create new entity if needed
   - Append fact to entity's `items.json`
4. Update `lastExtractedTimestamp` in `~/.memory_system`

### Extraction Criteria

**Extract these:**
- Relationship changes ("my new boss is James")
- Status changes ("left Acme Corp", "started new job")
- Milestones ("launched the product", "hired 3 people")
- Preferences expressed ("I prefer async communication")
- Project updates ("deadline moved to March")

**Skip these:**
- Casual chat ("how are you?", "thanks!")
- Temporary info ("meet in 10 minutes")
- Code snippets and technical details
- Questions and clarifications

### Cost Optimization

- Use cheapest available model for extraction (~$0.001 per run)
- Extract in batches (last 30 minutes of conversation)
- Only run if new conversation content exists
- Limit extraction to ~20 facts per run
```

## Implementation

### Option 1: Direct Integration

If your Claude setup supports custom heartbeat actions:

```python
# In heartbeat handler
def on_heartbeat():
    config = load_memory_config()
    last_extracted = config.get("lastExtractedTimestamp")
    
    # Check for new conversation content
    new_content = get_conversation_since(last_extracted)
    
    if not new_content:
        return
    
    # Spawn cheap sub-agent for extraction
    facts = extract_facts_with_cheap_model(new_content)
    
    # Save facts to entities
    for fact in facts:
        save_fact_to_entity(fact)
    
    # Update timestamp
    config["lastExtractedTimestamp"] = datetime.now().isoformat()
    save_memory_config(config)
```

### Option 2: Cron-Based (Alternative)

If heartbeat integration isn't available, use cron:

```bash
# Add to crontab (runs every 30 minutes)
*/30 * * * * python3 ~/.claude/skills/3-layer-memory/scripts/extract_facts.py --since $(cat ~/.memory_last_extracted) >> ~/.memory_extraction.log 2>&1
```

## Weekly Synthesis Cron

Add to crontab for automatic weekly synthesis:

```bash
# Run every Sunday at 9 AM
0 9 * * 0 python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py >> ~/.memory_synthesis.log 2>&1
```

Or use the skill manually:

```bash
# Dry run (see what would change)
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py --dry-run

# Full synthesis
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py
```

## Example Heartbeat Flow

```
[Heartbeat triggered]
    ↓
[Check lastExtractedTimestamp]
    ↓
[Get conversation since timestamp]
    ↓
[Any new content?] — No → [Exit]
    ↓ Yes
[Spawn cheap sub-agent]
    ↓
[Extract durable facts]
    ↓
For each fact:
    [Identify entity] → [Create if needed]
        ↓
    [Append to items.json]
    ↓
[Update lastExtractedTimestamp]
    ↓
[Done]
```

## Sub-Agent Prompt for Extraction

Use this prompt when spawning the extraction sub-agent:

```
You are a fact extraction agent. Your job is to identify durable facts from the conversation that should be saved to a knowledge graph.

Conversation:
{{conversation_text}}

Extract facts that are:
1. About people, companies, or projects
2. Likely to be relevant in future conversations
3. Changes to relationships, status, or milestones

For each fact, provide:
- Entity type (person/company/project)
- Entity name (create slug like "john-doe" or "acme-corp")
- Fact text (concise, 1-2 sentences)
- Category (relationship/milestone/status/preference)

Format as JSON:
{
  "facts": [
    {
      "entity_type": "person",
      "entity_name": "maria",
      "fact": "Business partner on AI project",
      "category": "relationship"
    }
  ]
}

Only include facts that are clearly stated in the conversation. Skip casual chat and temporary information.
```

## Monitoring

### Check Extraction Status

```bash
# View system config
cat ~/.memory_system | jq

# Check last extraction time
python3 -c "import json; print(json.load(open('.memory_system')).get('lastExtractedTimestamp', 'Never'))"

# View recent extraction log
tail -50 ~/.memory_extraction.log
```

### Check Synthesis Status

```bash
# View last synthesis time
cat ~/.memory_system | jq '.lastSynthesisTimestamp'

# View synthesis log
tail -50 ~/.memory_synthesis.log

# Count entities by type
ls -1 ~/life/areas/people/ | wc -l
ls -1 ~/life/areas/companies/ | wc -l
ls -1 ~/life/areas/projects/ | wc -l
```

## Troubleshooting

### Extraction Not Running

1. Check `lastExtractedTimestamp` is being updated
2. Verify conversation history is accessible
3. Check extraction logs for errors
4. Ensure sub-agent has proper permissions

### Too Many Facts Being Extracted

- Refine extraction criteria in the sub-agent prompt
- Add length limits to extraction
- Filter by confidence score

### Facts Not Being Saved

- Verify entity folders are writable
- Check `items.json` schema is valid
- Ensure proper JSON formatting

### Summaries Going Stale

- Verify weekly synthesis is scheduled
- Check `lastSynthesisTimestamp` updates
- Review synthesis logs for errors
