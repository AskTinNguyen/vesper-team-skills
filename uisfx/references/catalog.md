# UI SFX pack and cue catalog

Source: https://uisfx.com/uisfx-catalog.json and https://uisfx.com/docs/agent-guide.md. The npm package was verified as `uisfx@0.4.0` on 2026-08-14.

## Packs

- `minimal`: dry, precise, almost invisible; productivity, SaaS, system UI
- `soft`: rounded, warm, reassuring; mobile, wellness, friendly SaaS
- `glass`: bright, crystalline, premium; media, finance, luxury products
- `arcade`: chunky pixels and cheerful voltage; games, streaks, gamified learning
- `mechanical`: switches, relays, firm detents; devtools, hardware, industrial UI
- `organic`: wood, water, breath, and small stones; education, kids, calm games
- `dreamy`: airy blooms, soft light, and slow sparkle; creative tools, wellness, ambient apps
- `scifi`: clean holographic pings with restrained digital shimmer; AI tools, spatial UI, futuristic games
- `rubber`: tactile elastic taps with a quick friendly rebound; kids, playful mobile, casual games
- `cinematic`: deep impacts, polished tails, and quiet scale; premium media, games, dramatic moments
- `studio`: tactile editing precision with warm cinematic restraint; film, audio, AI creative tools
- `zen`: pure tones, dry wood, and brief washi detail; mindfulness, reading, writing, calm productivity

Every pack implements the same 78 semantic cues. Use the exact hyphenated names below.

## Input

`hover`, `press`, `release`, `double-click`, `focus`, `long-press`

## Selection

`select`, `deselect`, `toggle-on`, `toggle-off`, `check`, `uncheck`

## Navigation

`open`, `close`, `back`, `forward`, `expand`, `collapse`

## Editing

`delete`, `cancel`, `undo`, `redo`, `copy`, `paste`

## Movement

`drag-start`, `drop`, `snap`, `swipe`, `reorder`, `invalid-drop`

## Communication

`send`, `receive`, `notification`, `mention`, `typing`, `reaction`

## Feedback

`success`, `error`, `warning`, `info`, `blocked`, `retry`

## Progress

`start`, `stop`, `progress-step`, `complete`, `queued`, `checkpoint`

## Loops

`loading`, `processing`, `recording`, `connecting`, `scanning`, `streaming`

## Media

`play`, `pause`, `seek`, `volume-change`, `skip-next`, `skip-previous`

## System

`connect`, `disconnect`, `lock`, `unlock`, `wake`, `sleep`

## Reward

`reward`, `level-up`, `achievement`, `streak`, `badge`, `bonus`

## Commerce

`add-to-cart`, `remove-from-cart`, `checkout`, `purchase`, `coupon`, `refund`

## API at a glance

- `createUISFX(options)` creates a player with a pack, volume, enabled state, preferences, voice limit, cooldown, and optional audio context.
- `player.unlock()` resumes Web Audio from trusted intent.
- `player.play(cue, options)` returns a stoppable `PlayingSFX` handle or `null`.
- `player.preload(cues?, options?)` renders selected cues cooperatively and supports cancellation.
- `player.setPack(pack)`, `player.getPack()`, `player.setVolume(value)`, `player.getVolume()`, `player.setEnabled(value)`, and `player.isEnabled()` manage state.
- `player.stopAll()` stops active audio; `player.destroy()` disposes the app-level player.
- `bindUISFX(root?, options?)` provides simple declarative DOM bindings.
- `CUES`, `PACKS`, `CATEGORIES`, `cueNames`, `packNames`, `getCue`, `getPack`, and `getPlaybackMode` expose typed catalogs and metadata.
