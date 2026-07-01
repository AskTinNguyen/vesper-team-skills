# Repo Map: Electron Bun Tests

Use this map to quickly locate canonical command and configuration sources.

## Command Sources

- Root command scripts: `package.json`
  - `typecheck:all` runs core + shared + electron `tsc --noEmit`
- Electron workspace scripts: `apps/electron/package.json`
  - `typecheck`
  - `build`/`dev` entries useful for reproduction context
- Shared workspace scripts: `packages/shared/package.json`
  - `test`

## Test Discovery and Compiler Config

- Electron Bun test root: `apps/electron/bunfig.toml`
  - `[test] root = "./src"`
- Electron TypeScript config: `apps/electron/tsconfig.json`
- Shared TypeScript config: `packages/shared/tsconfig.json`
- Root base TypeScript config: `tsconfig.json`

## Main-Process Test Areas

- Primary brittle mock surfaces:
  - `apps/electron/src/main/__tests__/personas.test.ts`
  - `apps/electron/src/main/__tests__/sessions.unexpected-exit.test.ts`
  - `apps/electron/src/main/__tests__/platform-bindings.test.ts`
- Commonly mocked shared module:
  - `apps/electron/src/main/workspace-path-resolver.ts`
- Commonly mocked runtime module:
  - `electron` (for `app`, `ipcMain`, `BrowserWindow`, `nativeImage`)

## Known Stabilization Doc

- Troubleshooting write-up:
  - `docs/solutions/workflow-issues/bun-test-discovery-and-mock-export-race-vesper-electron-20260223.md`

## Existing Overlapping Skill

- Broader Electron testing strategy:
  - `skills/vesper-electron-testing/SKILL.md`
