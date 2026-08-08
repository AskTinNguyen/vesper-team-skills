# Cinematic Craft Route Map

Use this table to route a request to the specialist skill that owns the work. Fail forward to the pipeline if the request spans more than one stage.

| Stage | Task | Route to |
| --- | --- | --- |
| Story | Premise, logline, beats, genre, theme, three-act, mythic journey | `$cinematic-story-structure` |
| Character | Want vs need, arc type, ghost, arc beats, impact character | `$cinematic-character-arcs` |
| Visual plan | Scene breakdown, blocking, staging, coverage, shot list | `$cinematic-visual-direction` |
| Camera | Setup, lens, framing, and move per shot | `$cinematic-master-shots` |
| Action | Fight, chase, and confrontation staging; motion and rhythm | `$cinematic-action-motion` |
| Game | Cut-scenes, cineractives, camera modes, transitions, occlusion | `$cinematic-game-cinematics` |

## Full-pipeline order

1. Story structure.
2. Character arcs.
3. Visual direction and coverage.
4. Master shots and camera setups.
5. Action staging and rhythm (for fights, chases, and confrontations).
6. Game cinematics (when the output is a game or real-time sequence).
7. Coherence review: every shot traces to a story beat and character turn, with valid eyelines, screen direction, and editing options.
