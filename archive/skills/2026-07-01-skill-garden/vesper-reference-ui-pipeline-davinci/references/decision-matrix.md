# Decision Matrix

## Which skill comes first?

| Situation | Skill |
|---|---|
| Need to find the best source examples | `shadcn-component-reference-davinci` |
| Already have references but need Vesper translation | `vesper-premium-ui-remix-davinci` |
| Need layout/container/spacing correctness in code | `gestalt-frontend-design` |
| Need component pattern selection help | `ui-design-brain` |
| Need final premium cleanup | `polish` |

## Optional follow-on skills

| Problem appears | Skill |
|---|---|
| Copy feels generic, vague, or product-weak | `clarify` |
| Edge cases, empty states, or resilience are weak | `harden` |
| Motion feels abrupt or lifeless | `animate` |
| Responsive behavior is weak | `adapt` |
| Performance starts to suffer | `optimize` |

## Skip rules
Skip `shadcn-component-reference-davinci` when:
- the reference set is already chosen and strong
- the UI is based on an internal pattern, not external examples

Skip `vesper-premium-ui-remix-davinci` when:
- the design already feels Vesper-native
- the work is mostly bug-fixing or mechanical implementation

Skip `polish` only when:
- the task is explicitly low-fidelity exploration
- the user wants fast scaffolding instead of premium finish

## Anti-Pattern
Do not do this:
1. find references
2. jump straight to code
3. try to fix everything in polish

That usually produces reference-clone UI with late cosmetic cleanup instead of a strong product translation.

Also avoid this:
1. skip reference discovery
2. force the Vesper remix skill onto weak source material
3. blame implementation quality for what was actually a bad reference choice
