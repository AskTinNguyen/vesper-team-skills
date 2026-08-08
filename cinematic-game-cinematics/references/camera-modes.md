# Real-Time Camera Modes (Haigh-Hutchinson)

Source: Mark Haigh-Hutchinson, *Real-Time Cameras* (epub). Interaction design and engineering design are the two halves of a camera system; the engineer must satisfy what the designer specifies for the player's experience.

## Camera types

- **First person / point of view (POV):** The view is from the protagonist's eyes and the camera sits near the player character. It is the closest to "you are there" and the basis of the first-person shooter genre.
- **Third person / detached:** The camera is positioned relative to the player character; the look-at position is often distinct from the target object. It must manage navigation, occlusion, and the spatial relationship between avatar and camera so control feels stable.
- **Cinematic:** The view is outside player control. It can use the same technology, but the presented view is fixed by the designer; used for cut-scenes and cineractives. It should repeat consistently unless game state intentionally changes it.

## Behavior and control

- Look-at: define the desired camera orientation by a position relative to a target; keep a locked look-at offset or interpolate when the target changes.
- Free-look: the player reorients the camera during gameplay; constrain pitch (and sometimes yaw) so the view stays sensible.
- Tracking and slaving: the camera moves consistently relative to another object, such as the player character.
- Reactive vs predictive cameras: compensate for player actions and anticipate where the action is going.

## Transitions

- First-to-third and third-to-first require position and orientation plans; do not snap trust-breaking jumps.
- Full-screen to split-screen and back need defined viewport transitions, for example iris transitions.
- Cinematic versus interactive handoff must be legible to the player so control loss and return are never confusing.

## Occlusion, navigation, and motion

- Occlusion: determine when the environment blocks the ideal camera position, predict it, and resolve it (nudge, raise, or window the view) so the camera never passes through walls.
- Navigation: move the camera through the environment without violating gameplay framing.
- Motion and collision: keep motion continuous and smooth, and resolve camera-object collisions predictably.
- Performance: treat the camera as a significant ongoing game object; watch the frame cost of third-person navigation and collision and keep interactive camera budgets in check.
