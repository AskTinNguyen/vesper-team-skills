# Example Success Scorecard

## Feature
- Name: Trusted Peer Agents
- Owner: Product Lead
- Time horizon: 2 quarters

## North-Star Outcome
- Metric: Weekly trusted-peer workflows completed per active workspace
- Definition: Count of peer coordination workflows that reach a terminal state each week
- Why this is the right top-line signal: It measures repeated real use, not one-time setup

## Leading Indicators (0-3 months)

| Metric | Baseline Plan | Target | Owner | Cadence |
|-------|----------------|--------|-------|---------|
| Beta workspaces with 1+ trusted peer | Track from beta enrollment start | 30% of beta workspaces | PM | Weekly |
| Peer requests approved within 24h | Start with beta cohort baseline | 70% | Ops | Weekly |

## Lagging Indicators (3-12 months)

| Metric | Baseline Plan | Target | Owner | Cadence |
|-------|----------------|--------|-------|---------|
| Manual follow-up messages replaced | Survey + usage sample | 25% reduction | PM | Monthly |
| Coordination workflow retention after 8 weeks | First cohort baseline | 40% | Product Ops | Monthly |

## Guardrail Metrics

| Guardrail | Why it matters | Threshold | Owner | Action if breached |
|----------|----------------|-----------|-------|--------------------|
| Trust or Safety | Users must feel in control | >2% negative trust incidents | PM | Pause rollout and tighten approvals |
| Quality or Reliability | Failed routing breaks confidence | >5% failed deliveries | Eng | Stop expansion and fix reliability |
| Cost or Efficiency | Coordination cannot become too expensive | >20% over cost model | Finance | Reduce automation scope |

## Why This Is Strong
- Focuses on repeated real behavior.
- Includes clear guardrails, not just growth metrics.
- Creates explicit stop conditions before broad rollout.
