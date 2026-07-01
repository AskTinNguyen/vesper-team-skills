# Electron Bun Test Failure Patterns

Use this file to map observed failures to likely root causes and minimal fixes.

## Discovery Scope

### Signature
- Bun executes tests under `apps/electron/release/*` or other packaged output
- Failures reference bundled app paths instead of `apps/electron/src/*`

### Likely Cause
- Bun test discovery root is not constrained for the Electron workspace

### Preferred Fix
- Add `apps/electron/bunfig.toml`:
```toml
[test]
root = "./src"
```

## Missing Named Export From Mocked Module

### Signature
- `SyntaxError: Export named 'X' not found in module ...`
- Error appears in multi-file test runs but not always in single-file runs
- Common concrete case:
  - `Export named 'migrateLegacyWorkspaceConfigFields' not found in module ...workspace-path-resolver.ts`

### Likely Cause
- `mock.module()` for a shared dependency exports only a subset of names
- Another module in same run imports a missing symbol

### Preferred Fix
- Expand the mock export surface to include all named exports used by modules loaded in that test run
- Keep no-op implementations explicit and typed where useful

## Electron Runtime Import Errors

### Signature
- `Export named 'ipcMain' not found in module .../node_modules/electron/index.js`
- Main-process tests importing `sessions.ts` fail during module load

### Likely Cause
- Test file mock for `electron` omits runtime keys required by transitive imports

### Preferred Fix
- In the test file that defines the `electron` mock, include at least:
  - `app`
  - `ipcMain`
  - `BrowserWindow`
  - `nativeImage`

## Cross-File Mock Lifecycle Race

### Signature
- One file passes alone; combined file run fails with module/export errors

### Likely Cause
- `mock.restore()` in `afterEach` tears down module mocks before later imports in the same file sequence

### Preferred Fix
- Use `afterAll(() => mock.restore())` for module-scope mocks
- Keep per-test cleanup limited to data/filesystem state, not module registry teardown

## TypeScript Strictness In Test Files

### Signature
- `TS2532 Object is possibly 'undefined'`
- `TS18048 'value' is possibly 'undefined'`

### Likely Cause
- Direct indexed access without guard in strict mode

### Preferred Fix
- Add explicit guard and narrow type:
  - assert element exists before property access
  - use typed filter predicates checking `typeof value === 'number'`
  - avoid broad non-null assertions where easy guards are clearer
