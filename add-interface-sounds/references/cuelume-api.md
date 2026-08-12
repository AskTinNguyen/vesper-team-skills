# Cuelume integration reference

Cuelume 0.1.2 is an MIT-licensed, ESM-only library that synthesizes UI sounds through the Web Audio API. It has no runtime dependencies or audio files. Source: https://github.com/Danilaa1/cuelume and https://cuelume-site.pages.dev/

## API

```ts
import { bind, play, setEnabled, sounds, type SoundName } from "cuelume";
```

- `bind(root?: ParentNode)`: delegate supported data-attribute interactions under a root; safe to call repeatedly for the same root and supports later DOM changes.
- `play(name?: SoundName)`: synthesize a cue immediately; defaults to `chime` and silently no-ops when playback is unavailable.
- `setEnabled(enabled: boolean)`: enable or disable future playback; the app owns preference persistence.
- `sounds`: all supported cue names.

## Cue map

| Cue | Character | Good uses |
| --- | --- | --- |
| `chime` | soft ascending bell | sparse hover, gentle discovery |
| `sparkle` | quick twinkle | playful reward, favorite added |
| `droplet` | downward glide | dismiss, collapse, favorite removed |
| `bloom` | warm swell | reveal, expand, modal open |
| `whisper` | quiet breath | dense-list feedback |
| `tick` | crisp tick | navigation or menu hover |
| `press` | muted knock | pointer down |
| `release` | springy tick | pointer up |
| `toggle` | click-clack | switches, tabs, filters |
| `success` | warm confirmation | completed save or confirmed action |
| `error` | soft descending refusal | recoverable validation or request error |
| `page` | paper-and-glass flick | pagination, carousel, random next item |
| `loading` | unresolved shimmer | user-initiated work begins |
| `ready` | focus and bloom | requested content finishes loading |

## Declarative binding

```html
<button data-cuelume-press data-cuelume-release>Save</button>
<a data-cuelume-hover="tick">Docs</a>
<button data-cuelume-toggle>Dark mode</button>
```

Empty values use defaults. Set an explicit cue name to override:

```html
<button data-cuelume-press="whisper" data-cuelume-release="sparkle">Favorite</button>
```

Defaults are `chime` for hover, `press` for pointer down, `release` for pointer up, and `toggle` for click. Fine-pointer hover is throttled globally; keyboard and touch activate native click/toggle behavior.

## React pattern

Call `bind()` once in a mounted client component. Own the preference in the app:

```tsx
"use client";

import { useEffect } from "react";
import { bind, setEnabled } from "cuelume";

useEffect(() => {
  const stored = window.localStorage.getItem("interface-sounds");
  setEnabled(stored !== "off");
  bind();
}, []);
```

For meaningful results, play imperatively after state is confirmed:

```ts
await saveFavorite(id);
play("sparkle");
```

## Vanilla pattern

```js
import { bind, play, setEnabled } from "cuelume";

const key = "interface-sounds";
setEnabled(localStorage.getItem(key) !== "off");
bind();

soundButton.addEventListener("click", () => {
  const next = localStorage.getItem(key) === "off";
  setEnabled(next);
  localStorage.setItem(key, next ? "on" : "off");
  if (next) play("toggle");
});
```

Wrap storage access when privacy settings or embedded contexts may block it.
