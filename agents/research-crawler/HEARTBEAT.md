# HEARTBEAT.md — ResearchCrawler

## No Regular Heartbeat

ResearchCrawler runs on-demand via spawning, not heartbeat polling.

**Active hours:** 11 PM – 6 AM (overnight crawls)
**Triggered by:** Cron job or Coordinator spawn

---

## When Spawned

1. Read agent-notes from previous sessions
2. Check `Areas/RESEARCH-QUEUE.md` for topics
3. Execute research protocol
4. Write outputs to tin-knowledgebase
5. Commit agent-notes
6. Post summary to CodeSquad

---

## If Nothing in Queue

Reply: `RESEARCH_IDLE — No topics in queue. Add to Areas/RESEARCH-QUEUE.md`
