#!/usr/bin/env bun

import {
  beginAttempt,
  getStory,
  markComplete,
  markFail,
  nextStory,
  syncState,
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
  const [command, ...rest] = process.argv.slice(2)
  if (!command) {
    throw new Error('Usage: <bun> state-manager.ts <sync|begin|complete|fail|next> [options]')
  }

  const options = parseOptions(rest)

  if (command === 'sync') {
    const state = syncState({
      prdPath: requireOption(options, 'prd'),
      statePath: requireOption(options, 'state'),
      worker: requireOption(options, 'worker'),
      workspaceRoot: requireOption(options, 'workspace-root'),
      config: {
        max_retries: Number(options['max-retries'] ?? 3),
        timeout_seconds: Number(options['timeout-seconds'] ?? 1800),
        base_backoff_seconds: Number(options['base-backoff-seconds'] ?? 30),
        max_backoff_seconds: Number(options['max-backoff-seconds'] ?? 300),
      },
    })
    console.log(JSON.stringify({ ok: true, stories: state.stories.length, summary: state.run_summary }))
    return
  }

  if (command === 'begin') {
    const state = beginAttempt(
      requireOption(options, 'state'),
      requireOption(options, 'story-id'),
      requireOption(options, 'spawn-run-id'),
      options['session-id'] ?? null,
    )
    console.log(JSON.stringify({
      ok: true,
      story_id: requireOption(options, 'story-id'),
      attempts: getStory(state, requireOption(options, 'story-id')).attempts,
    }))
    return
  }

  if (command === 'complete') {
    markComplete(
      requireOption(options, 'state'),
      requireOption(options, 'story-id'),
      requireOption(options, 'evidence'),
    )
    console.log(JSON.stringify({ ok: true, story_id: requireOption(options, 'story-id'), status: 'completed' }))
    return
  }

  if (command === 'fail') {
    const result = markFail(
      requireOption(options, 'state'),
      requireOption(options, 'story-id'),
      requireOption(options, 'error'),
    )
    console.log(JSON.stringify({ ok: true, story_id: requireOption(options, 'story-id'), terminal: result.terminal }))
    return
  }

  if (command === 'next') {
    console.log(JSON.stringify({ ok: true, next_story: nextStory(requireOption(options, 'state')) }))
    return
  }

  throw new Error(`Unknown command: ${command}`)
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
