#!/usr/bin/env bun

import {
  beginAttempt,
  getStory,
  loadJson,
  markComplete,
  markFail,
  nextStory,
  type RalphState,
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

function classify(title: string): 'pass' | 'fail_once' | 'fail_twice' | 'perm_fail' {
  const normalized = title.toUpperCase()
  if (normalized.includes('[FAIL_TWICE]')) return 'fail_twice'
  if (normalized.includes('[FAIL_ONCE]')) return 'fail_once'
  if (normalized.includes('[PERM_FAIL]')) return 'perm_fail'
  return 'pass'
}

function shouldPass(profile: ReturnType<typeof classify>, attempts: number): boolean {
  if (profile === 'pass') return true
  if (profile === 'fail_once') return attempts >= 2
  if (profile === 'fail_twice') return attempts >= 3
  return false
}

async function sleep(ms: number) {
  if (ms <= 0) return
  await Bun.sleep(ms)
}

async function main() {
  const options = parseOptions(process.argv.slice(2))
  const statePath = requireOption(options, 'state')
  const maxActions = Number(options['max-actions'] ?? 5)
  const sleepSeconds = Number(options['sleep-seconds'] ?? 0)

  let actions = 0
  const events: Array<Record<string, string | number>> = []

  while (actions < maxActions) {
    const next = nextStory(statePath)
    if (!next) break

    const pre = loadJson<RalphState>(statePath)
    const current = getStory(pre, next.id)
    const currentAttempt = current.attempts + 1
    const profile = classify(next.title)
    const spawnRunId = `mock-${next.id.toLowerCase()}-a${currentAttempt}-${Date.now()}`
    const sessionId = `mock-session-${next.id.toLowerCase()}-${currentAttempt}`

    beginAttempt(statePath, next.id, spawnRunId, sessionId)

    if (shouldPass(profile, currentAttempt)) {
      markComplete(statePath, next.id, `ACCEPTANCE: PASS for ${next.id} (profile=${profile}, attempt=${currentAttempt})`)
      events.push({ story_id: next.id, attempt: currentAttempt, profile, result: 'completed' })
    } else {
      const result = markFail(statePath, next.id, `simulated failure for ${next.id} (profile=${profile}, attempt=${currentAttempt})`)
      events.push({
        story_id: next.id,
        attempt: currentAttempt,
        profile,
        result: result.terminal ? 'failed_terminal' : 'failed_retryable',
      })
    }

    actions += 1
    await sleep(sleepSeconds * 1000)
  }

  const finalState = loadJson<RalphState>(statePath)
  console.log(JSON.stringify({
    ok: true,
    actions,
    events,
    summary: finalState.run_summary,
    cursor: finalState.cursor,
  }))
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
