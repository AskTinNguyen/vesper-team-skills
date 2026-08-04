# Unquiet Archive publishing

## Current archive

- Source: `C:\Users\Admin\minimax-video-gallery`
- Public URL: `https://unquiet-archive.asktinnguyen.chatgpt.site`
- Hosting metadata: `.openai\hosting.json`
- Existing project ID: `appgprj_6a70bd8734948191a37ac23a4c6cbdd5`
- Media directory: `public\series`
- Main catalog/UI: `app\page.tsx`
- Continuous playback: `app\series-playlist.tsx`

Treat these as known values to verify, not secrets to repeat to the user.

## Staging

Run `stage-site` only after all intended chapters are accepted and `verify` passes. It copies accepted individual MP4 files, makes/copies posters, and merge-updates `public\series\archive-catalog.json`. Existing catalog entries are preserved. When no catalog exists, the script seeds it from existing numbered media and recoverable chapter tuples in `app\page.tsx`; inspect placeholder entries before treating the catalog as editorially authoritative. It does not rewrite the React page or deploy.

The current site expects chapter video filenames and `chapter-NN-poster.jpg` files in `public\series`. Update `app\page.tsx` so titles, notes, movements, totals, durations, technical facts, and navigation counts agree with the staged catalog. Keep `SeriesPlaylist` for seamless “play all” behavior.

## Size policy

Treat 25,000,000 bytes as the safe per-file ceiling unless the current Sites connector reports another limit. Individual 15-second chapters normally fit. Combined movement and full-series masters often do not.

Prefer:

1. individual chapter files;
2. the existing continuous playlist;
3. optional movement masters only when each fits;
4. a heavily compressed full master only when explicitly requested and visually acceptable.

Do not silently omit an oversized required chapter. Report it and create a compliant web encode or change the hosting plan.

## Validation and deployment

From the site source:

```powershell
npm run lint
npm test
```

Inspect `git status` and preserve unrelated user changes. Confirm the built site references files that actually exist and that every staged MP4 is below the current limit.

Then invoke `sites:sites-hosting`, read its current `SKILL.md`, and follow its connector-driven publish flow. Reuse the existing project ID and publish the exact validated source. Do not create a replacement site when an update is intended.

Publishing modifies a public external system. If the active user request does not include upload, deployment, or publication, stop after local staging and say that the site has not been published.
