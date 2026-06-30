# Unreal build validation via Codex CLI

Use when the user asks Codex CLI to run or validate an Unreal/S2 build, especially when Hermes cannot directly run a native Windows build command or the user wants Codex to act as the validation runner.

## Pattern

1. Run Codex from the repo root with a narrow validation prompt and `pty=true`.
2. Ask Codex to discover/read the repo build instructions first (`AGENTS.md`, build scripts, target files) instead of guessing paths.
3. Prefer the canonical UBT target from repo docs. For S2 this has been:
   - target: `S2Editor Win64 Development`
   - project: `E:\S2_\S2.uproject`
   - UBT shape: `"<ENGINE>\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" S2Editor Win64 Development "-Project=E:\S2_\S2.uproject" -NoLog -WaitMutex -FromMsBuild`
4. If Codex sandbox blocks normal Unreal writes (`UnauthorizedAccessException` under UnrealBuildTool logs, engine `Intermediate`, or project `Intermediate`), rerun with `--yolo` **only for the build validation prompt**, and explicitly say: do not edit files or commit.
5. Verify success from UBT output (`Result: Succeeded`, exit code 0), not only from Codex's summary.
6. Codex `exec` may linger after reporting UBT success. If the underlying build has completed and the summary is captured, it is safe to kill the lingering Codex process.
7. If the build fails, capture the first relevant UHT/compiler error, fix it yourself or with a focused agent, then rerun the same build.

## Common Unreal/S2 gotchas observed

### UHT reflected-parameter shadowing

UHT can reject reflected function parameters that shadow inherited `AActor` members, even when C++ would otherwise compile. In UFUNCTION-facing APIs on actors/volumes, avoid parameter names such as:

- `Owner` (can shadow `AActor::Owner`)
- `Role` (can shadow `AActor::Role`)

Prefer explicit names:

- `ReservationOwner`
- `ReservationRole`
- `RequestingActor`
- `OwningActor`

### Automation command batching

For S2 automation validation, run one `Automation RunTests ...; Quit` command per editor-cmd process. Do **not** chain multiple `Automation RunTests` commands in one `-ExecCmds` string with semicolons; observed behavior was that Unreal queued the first suite and treated the second `Automation RunTests ...` as an unknown automation command. If multiple suites are required, run separate commands and verify each log contains:

- `Found N automation tests based on '<Suite>'`
- `**** TEST COMPLETE. EXIT CODE: 0 ****`

### Python commandlet asset workflows

Unreal Python commandlets are reliable for read-only asset registry probes, duplicating/saving core assets, CDO property edits, and creating a dedicated blank validation map. Use them to generate JSON evidence under `Saved/Logs/`.

Important invocation detail: for S2's UnrealEditor-Cmd, `-ExecutePythonScript=<path>` may appear in the command line but not actually run the script in some commandlet/editor-cmd contexts. Prefer:

```text
UnrealEditor-Cmd.exe E:/S2_/S2.uproject -run=pythonscript -script="E:/S2_/path/to/script.py" -unattended -NullRHI -NoSound -NoSplash -stdout -FullStdOutLogOutput -log
```

After every Python run, verify the expected `Saved/Logs/<evidence>.json` exists before trusting the process exit code.

Be cautious with map mutation/loading in commandlet/editor-cmd mode: duplicating a map and then loading/replacing actors can trip Unreal world-memory-leak fatals (`Old level package ... not cleaned up by garbage collection while loading new map`). Safer map setup pattern: start a fresh process, create a new blank map (`EditorLoadingAndSavingUtils.new_blank_map(False)`), spawn only tagged validation actors, save it, and exit. Capture the safe fallback: create/validate core assets first, then run map/PIE smoke separately.

### Live Coding build blocker

S2/Unreal UBT builds fail while a live editor session has Live Coding active:

```text
Unable to build while Live Coding is active. Exit the editor and game, or press Ctrl+Alt+F11
```

Before declaring a code build failure, check for `UnrealEditor.exe` / `LiveCodingConsole.exe`. Treat this as an environment gate, not a source failure, then rerun the same UBT command after the gate is cleared.

If the user has explicitly authorized autonomous editor/window management on the Windows host, clear the gate yourself instead of stopping for manual closure. Prefer process-name termination over MSYS pseudo-PIDs:

```bash
MSYS_NO_PATHCONV=1 taskkill.exe /IM UnrealEditor.exe /T /F || true
MSYS_NO_PATHCONV=1 taskkill.exe /IM LiveCodingConsole.exe /T /F || true
sleep 5
tasklist.exe | grep -Ei 'UnrealEditor|LiveCoding|S2Editor' || true
```

Pitfalls:
- `ps -W` PID values can be MSYS pseudo-PIDs; `taskkill /PID <ps -W pid>` may say the process is not found.
- In git-bash/MSYS, pass `MSYS_NO_PATHCONV=1` or `/IM` and `/PID` may be path-converted into invalid paths such as `C:/Program Files/Git/IM`.
- After a forced close, wait and verify with both `tasklist.exe` and/or `ps -W` before rerunning UBT.

When the user has explicitly authorized autonomous editor/window management on the Windows host, clear the blocker yourself instead of stopping for the user. In git-bash/MSYS, native Windows flags such as `/PID` are path-converted unless guarded, and `ps -W` can show both MSYS and native PIDs. Prefer terminating by image name with path conversion disabled, then verify after a short delay:

```bash
ps -W | grep -E 'UnrealEditor|LiveCoding|S2Editor' | grep -v grep || true
MSYS_NO_PATHCONV=1 taskkill.exe /IM UnrealEditor.exe /T /F || true
MSYS_NO_PATHCONV=1 taskkill.exe /IM LiveCodingConsole.exe /T /F || true
sleep 10
tasklist.exe | grep -Ei 'UnrealEditor|LiveCoding|S2Editor' || true
ps -W | grep -E 'UnrealEditor|LiveCoding|S2Editor' | grep -v grep || true
```

If `taskkill.exe /PID ...` reports an invalid option like `C:/Program Files/Git/PID`, that is MSYS path conversion, not a Windows taskkill problem; rerun with `MSYS_NO_PATHCONV=1` or use `/IM` as above.

## Example Codex validation prompt

```text
Run the Unreal build for this repo without modifying source files. Read AGENTS.md for the canonical build command. Use UBT to build S2Editor Win64 Development for E:\S2_\S2.uproject. Use -NoLog -WaitMutex -FromMsBuild if needed. Return the exact command, pass/fail result, and first relevant compiler/build errors if it fails. Do not edit files or commit.
```

Use `--yolo` only when sandboxed Codex cannot write Unreal build intermediates/logs and the user has authorized Codex to run the build.
