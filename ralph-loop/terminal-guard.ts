#!/usr/bin/env bun

import {
  completionNote,
  computeCounts,
  ensureGuard,
  loadJson,
  nowIso,
  type RalphState,
  writeJson,
  writeText,
} from './lib/state-tools'

function parseOptions(args: string[]): Record<string, string | undefined> {
  const options: Record<string, string | undefined> = {}
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (!arg.startsWith('--')) continue
    const key = arg.slice(2)
    const next = args[index + 1]
    if (next && !next.startsWith('--')) {
      options[key] = next
      index += 1
    } else {
      options[key] = 'true'
    }
  }
  return options
}

function requireOption(options: Record<string, string | undefined>, key: string): string {
  const value = options[key]
  if (!value) {
    throw new Error(`Missing required option --${key}`)
  }
  return value
}

async function main() {
  const options = parseOptions(process.argv.slice(2))
  const statePath = requireOption(options, 'state')
  const notePath = requireOption(options, 'completion-note')
  const requiredHits = Number(options['required-consecutive-hits'] ?? 2)

  const state = loadJson<RalphState>(statePath)
  const counts = computeCounts(state)
  const guard = ensureGuard(state)
  const isTerminalNow = counts.pending === 0 && counts.in_progress === 0

  if (isTerminalNow) {
    guard.consecutive_terminal_hits += 1
    guard.last_terminal_at = nowIso()
    if (!guard.first_terminal_at) {
      guard.first_terminal_at = guard.last_terminal_at
    }
  } else {
    guard.consecutive_terminal_hits = 0
    guard.first_terminal_at = null
    guard.last_terminal_at = null
  }

  const disableNow = isTerminalNow && guard.consecutive_terminal_hits >= requiredHits
  let noteWrittenNow = false

  if (disableNow && !guard.completion_note_written) {
    writeText(notePath, completionNote(state, counts))
    guard.completion_note_written = true
    guard.completion_note_path = notePath
    noteWrittenNow = true
  }

  state.updated_at = nowIso()
  writeJson(statePath, state)

  console.log(JSON.stringify({
    ok: true,
    is_terminal_now: isTerminalNow,
    disable_now: disableNow,
    terminal_hits: guard.consecutive_terminal_hits,
    required_hits: requiredHits,
    completion_note_written_now: noteWrittenNow,
    completion_note_written: guard.completion_note_written,
    completion_note_path: guard.completion_note_path,
    counts,
  }))
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})

