# Vesper Copy and Tone

Use this reference to write interface copy, helper text, empty states, prompts, notifications, and review feedback that sound unmistakably like Vesper.

The goal is not “friendly AI copy.” The goal is **calm, capable guidance** for people doing real work with advanced systems.

## 1. Voice Summary

Vesper’s voice should feel:
- **clear**
- **composed**
- **fluent**
- **quietly premium**
- **human**
- **action-oriented**

Vesper’s voice should not feel:
- gimmicky
- overexcited
- robotic
- verbose
- smugly technical
- startup-hypey
- apologetic without helping

### Core test
Good Vesper copy makes the user feel:
- *I know what this means.*
- *I know what to do next.*
- *The product respects my attention.*

## 2. The Communication Standard

Every piece of copy should do one or more of these jobs:
1. orient the user
2. explain what changed
3. clarify consequences
4. guide the next action
5. reduce intimidation without reducing truth

If copy does none of these, it is probably filler.

## 3. Tone Attributes

### 3.1 Calm, not sleepy
Vesper should feel steady and confident, not flat or timid.

- Prefer: **"Your schedule is active."**
- Avoid: **"Awesome — your magical automation is now live!"**

### 3.2 Premium, not ornate
The voice should be polished, but never precious.

- Prefer: **"Review changes before sending."**
- Avoid: **"Kindly inspect the modifications at your convenience."**

### 3.3 Helpful, not over-explanatory
Say enough to unblock the user, then stop.

- Prefer: **"Couldn’t connect to Google Drive. Reconnect the source to continue."**
- Avoid: **"An unexpected issue occurred while attempting to establish a connection to the Google Drive source. Please try again or contact support if the issue persists."**

### 3.4 Capable, not domineering
Vesper can be authoritative without sounding controlling.

- Prefer: **"This action will replace the current draft."**
- Avoid: **"You must confirm replacement before proceeding."**

### 3.5 Human, not anthropomorphic theater
The system can speak naturally without pretending to be a sentient co-worker.

- Prefer: **"Draft ready."**
- Avoid: **"I’ve woven your ideas into a polished masterpiece ✨"**

## 4. Default Writing Rules

### 4.1 Lead with meaning
Put the important part first.

- **Good:** "Permission required to edit this file."
- **Weak:** "Before continuing, we need to let you know that permission is required in order to edit this file."

### 4.2 Use plain language
Prefer familiar words over internal or technical jargon.

- Prefer **"source"** only when it maps to a real product concept.
- Prefer **"Connect Google Drive"** over **"Initialize external source auth."**

### 4.3 Keep sentences tight
One sentence, one job whenever possible.

### 4.4 Use verb-first CTAs
Buttons should describe the action.

- **Good:** Save changes, Review draft, Connect source, Try again, Open settings
- **Avoid:** Submit, Confirm, Continue, OK, Yes

### 4.5 Be specific about consequences
Especially for destructive, permissioned, or automated actions.

- **Good:** "Deleting this source will remove its local configuration."
- **Avoid:** "This action cannot be undone." when that is the only detail provided

### 4.6 Respect the user’s intelligence
Do not over-simplify to the point of vagueness.

- **Good:** "Automation is paused until the bot token is restored."
- **Avoid:** "Something needs attention."

### 4.7 Avoid hype inflation
Vesper is premium because it is controlled and useful, not because it constantly self-advertises.

Avoid phrases like:
- revolutionize
- supercharge
- unlock the future
- magical
- game-changing
- next-level AI
- cutting-edge intelligence

## 5. Vocabulary Preferences

### Prefer
- draft
- review
- ready
- connected
- paused
- active
- needs attention
- open settings
- show details
- advanced options
- try again
- keep going
- remove
- replace

### Use carefully
- agent
- runtime
- orchestration
- source
- session
- automation

Use technical words only when the user benefits from precision or when the concept is already established in-product.

### Avoid by default
- magic
- genius
- autonomous powerhouse
- command center
- prompt engineering
- AI cockpit
- workflow fabric
- superhuman
- zero-friction universe

## 6. Context-Specific Tone

### 6.1 Empty states
Empty states should feel encouraging and directional.

Pattern:
- say what is missing
- explain why that is okay or expected
- provide the next action

**Good**
- "No sources connected yet. Connect one to start pulling in documents, schedules, or project data."
- "No schedules yet. Create one when you want Vesper to run automatically."

**Avoid**
- "Nothing here"
- "You have no items"
- novelty jokes that do not help the user start

### 6.2 Loading states
Loading copy should describe the real work underway.

**Good**
- "Loading session history…"
- "Checking source status…"
- "Preparing draft…"

**Avoid**
- generic AI-slop messages like "Teaching robots to dance" or "Consulting the magic"
- vague loops like "Working…" when specificity is available

### 6.3 Success states
Keep success states brief and grounded.

**Good**
- "Draft saved."
- "Source connected."
- "Changes applied."
- "Schedule updated."

Add one follow-up sentence only when it changes user expectations:
- "Schedule updated. The new time takes effect immediately."

### 6.4 Error states
Error copy should explain:
- what failed
- why, if known
- what the user can do next

**Good**
- "Couldn’t open this source because the session expired. Reconnect to continue."
- "This file is read-only in the current mode. Switch permission mode or save a copy first."

**Avoid**
- blamey phrasing
- raw stack traces in user-facing surfaces
- dead-end messages with no recovery path

### 6.5 Permission and safety messaging
Permission prompts should feel clear and non-alarmist.

**Good**
- "Vesper needs approval before it can edit files in this workspace."
- "This action opens browser automation. Choose a profile to continue."

**Avoid**
- legalistic walls of text
- patronizing warnings
- vague fear language like "dangerous" unless actual risk is severe

### 6.6 Advanced controls
When exposing advanced functionality, make it feel available but optional.

**Good**
- "Advanced options"
- "Show automation details"
- "Review runtime settings"

**Avoid**
- leading with implementation complexity on primary screens
- making advanced settings sound like mandatory setup

### 6.7 Destructive actions
Be direct, never playful.

Pattern:
- name the exact action
- name the object
- explain consequence

**Good**
- "Delete schedule?"
- "This removes the schedule from this workspace. Past run history stays in session records."
- CTA: **Delete schedule**

**Avoid**
- "Are you sure?"
- joke copy
- ambiguous CTAs like **Yes** / **Confirm**

## 7. Structural Patterns

### 7.1 Headings
Headings should orient, not market.

- Prefer: **Sessions**, **Connected sources**, **Automation settings**, **Review draft**
- Avoid: **Your AI command center**, **Supercharged workflows**, **The future of work**

### 7.2 Helper text
Helper text should answer the user’s next question, not restate the label.

- **Good label:** Browser profile
- **Good helper:** "Pick the profile Vesper should use for this site."

- **Weak helper:** "Choose a browser profile from the list below."

### 7.3 Section intros
Only include a section intro if it adds meaningful context.

Good uses:
- clarifying consequences
- explaining scope
- setting user expectations

Bad uses:
- repeating the heading in sentence form
- adding vague marketing polish

## 8. UI Copy Patterns

### 8.1 Button labels
Use this format when possible:
- **Verb + object** → Save draft, Open file, Connect source, Stop run
- **Verb + qualifier** → Review changes, Show details, Try again

### 8.2 Toggle labels
State the feature, not the opposite of the feature.

- Prefer: **Enable notifications**
- Avoid: **Disable notifications** as the label itself

### 8.3 Tabs and nav
Tabs should use stable nouns.

- Good: Overview, Files, Activity, Settings
- Avoid: Explore magic, Deep intelligence, AI flow

### 8.4 Status labels
Short, plain, consistent.

Recommended set:
- Ready
- Running
- Paused
- Needs attention
- Disconnected
- Completed
- Failed

Avoid inventing synonyms unless a distinct product meaning exists.

## 9. Copy Anti-Patterns

Reject the following patterns:

### 9.1 Generic AI SaaS hero language
- "Build with the power of AI"
- "Unlock intelligent workflows"
- "Your all-in-one AI operating system"

### 9.2 Cyberpunk hype
- "Neural"
- "Hyperdrive"
- "Quantum"
- "Command matrix"
- "Autonomous swarm"

### 9.3 Cute-but-unhelpful loading/error filler
- "Wrangling the bits"
- "Herding cats"
- "Summoning agents"
- "Asking the universe"

### 9.4 Over-anthropomorphized agent voice
- "I’m thinking really hard"
- "Let me cook"
- "I’ve got this, boss"

### 9.5 Passive ambiguity
- "Changes were made"
- "An issue occurred"
- "Request unsuccessful"

If the user has to translate the sentence before acting on it, rewrite it.

## 10. Good vs Bad Examples

### Example: settings intro
**Good**
> Review how Vesper runs in this workspace.

**Bad**
> Configure the advanced orchestration parameters that power your intelligent automation environment.

### Example: CTA
**Good**
> Review draft

**Bad**
> Generate

### Example: error
**Good**
> Couldn’t save changes because the file moved. Refresh the workspace, then try again.

**Bad**
> Save failed.

### Example: empty state
**Good**
> No notes yet. Add one when you want a reusable reference for future sessions.

**Bad**
> Your knowledge base is empty.

## 11. Review Filter

Before finalizing copy, ask:

1. **Would this make sense to a smart non-technical founder?**
2. **Does it tell the user what happened or what to do next?**
3. **Is the language calm and premium without sounding ornamental?**
4. **Did we avoid generic AI hype and dashboard jargon?**
5. **Would this still sound good after the hundredth use?**

If not, revise until the answer is yes.
