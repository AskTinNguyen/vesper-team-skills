#!/usr/bin/env bun

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname } from 'node:path'

export const STORY_RE = /^### \[( |x)\] (US-\d+): (.+)$/

export type StoryStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export interface RalphConfig {
  max_retries: number
  timeout_seconds: number
  base_backoff_seconds: number
  max_backoff_seconds: number
}

export interface RalphStory {
  id: string
  title: string
  prd_heading_line: string
  order: number
  checked?: boolean
  status: StoryStatus
  attempts: number
  last_spawn_run_id: string | null
  last_session_id: string | null
  last_error: string | null
  evidence: string | null
  next_retry_not_before: string | null
}

export interface RalphState {
  version: number
  workspace_root: string
  prd_path: string
  worker_persona: string
  created_at: string
  updated_at: string
  config: RalphConfig
  stories: RalphStory[]
  cursor: {
    current_story_id: string | null
    last_completed_story_id: string | null
  }
  run_summary: {
    completed: number
    failed: number
    skipped: number
  }
  terminal_guard?: {
    consecutive_terminal_hits: number
    completion_note_written: boolean
    completion_note_path: string | null
    first_terminal_at: string | null
    last_terminal_at: string | null
  }
}

export function nowIso(): string {
  return new Date().toISOString()
}

export function parseTs(ts: string): Date {
  return new Date(ts)
}

export function loadJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T
}

export function writeJson(path: string, payload: unknown): void {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`, 'utf8')
}

export function writeText(path: string, content: string): void {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, content, 'utf8')
}

export function parsePrd(prdPath: string): Array<{
  id: string
  title: string
  prd_heading_line: string
  order: number
  checked: boolean
}> {
  const lines = readFileSync(prdPath, 'utf8').split(/\r?\n/)
  const stories: Array<{
    id: string
    title: string
    prd_heading_line: string
    order: number
    checked: boolean
  }> = []
  let order = 0

  for (const line of lines) {
    const match = STORY_RE.exec(line)
    if (!match) continue
    order += 1
    stories.push({
      id: match[2],
      title: match[3],
      prd_heading_line: line,
      order,
      checked: match[1] === 'x',
    })
  }

  return stories
}

export function baseStory(story: ReturnType<typeof parsePrd>[number]): RalphStory {
  return {
    id: story.id,
    title: story.title,
    prd_heading_line: story.prd_heading_line,
    order: story.order,
    checked: story.checked,
    status: story.checked ? 'completed' : 'pending',
    attempts: 0,
    last_spawn_run_id: null,
    last_session_id: null,
    last_error: null,
    evidence: null,
    next_retry_not_before: null,
  }
}

export function recalcSummary(state: RalphState): void {
  let completed = 0
  let failed = 0
  let skipped = 0

  for (const story of state.stories) {
    if (story.status === 'completed') completed += 1
    if (story.status === 'failed') failed += 1
    if (story.prd_heading_line.startsWith('### [x]') && story.attempts === 0) skipped += 1
  }

  state.run_summary = { completed, failed, skipped }
}

export function getStory(state: RalphState, storyId: string): RalphStory {
  const story = state.stories.find((entry) => entry.id === storyId)
  if (!story) {
    throw new Error(`Story not found: ${storyId}`)
  }
  return story
}

export function ensureGuard(state: RalphState): NonNullable<RalphState['terminal_guard']> {
  if (!state.terminal_guard) {
    state.terminal_guard = {
      consecutive_terminal_hits: 0,
      completion_note_written: false,
      completion_note_path: null,
      first_terminal_at: null,
      last_terminal_at: null,
    }
  }
  return state.terminal_guard
}

export function syncState(args: {
  prdPath: string
  statePath: string
  worker: string
  workspaceRoot: string
  config: RalphConfig
}): RalphState {
  const prdStories = parsePrd(args.prdPath)
  if (prdStories.length === 0) {
    throw new Error('No stories found. Expected headings like: ### [ ] US-001: Title')
  }

  const existing = existsSync(args.statePath) ? loadJson<RalphState>(args.statePath) : null
  const existingMap = new Map<string, RalphStory>()
  for (const story of existing?.stories ?? []) {
    existingMap.set(story.id, story)
  }

  const mergedStories = prdStories.map((parsed) => {
    const base = baseStory(parsed)
    const previous = existingMap.get(parsed.id)
    if (previous) {
      base.status = previous.status ?? base.status
      base.attempts = previous.attempts ?? 0
      base.last_spawn_run_id = previous.last_spawn_run_id ?? null
      base.last_session_id = previous.last_session_id ?? null
      base.last_error = previous.last_error ?? null
      base.evidence = previous.evidence ?? null
      base.next_retry_not_before = previous.next_retry_not_before ?? null
    }
    if (parsed.checked) {
      base.status = 'completed'
    }
    return base
  })

  const state: RalphState = {
    version: 1,
    workspace_root: args.workspaceRoot,
    prd_path: args.prdPath,
    worker_persona: args.worker,
    created_at: existing?.created_at ?? nowIso(),
    updated_at: nowIso(),
    config: args.config,
    stories: mergedStories,
    cursor: {
      current_story_id: existing?.cursor?.current_story_id ?? null,
      last_completed_story_id: existing?.cursor?.last_completed_story_id ?? null,
    },
    run_summary: existing?.run_summary ?? { completed: 0, failed: 0, skipped: 0 },
    terminal_guard: existing?.terminal_guard,
  }

  recalcSummary(state)
  writeJson(args.statePath, state)
  return state
}

export function beginAttempt(statePath: string, storyId: string, spawnRunId: string, sessionId: string | null): RalphState {
  const state = loadJson<RalphState>(statePath)
  const story = getStory(state, storyId)

  if (story.status === 'completed') {
    throw new Error(`Cannot begin attempt for completed story ${storyId}`)
  }

  story.status = 'in_progress'
  story.attempts += 1
  story.last_spawn_run_id = spawnRunId
  story.last_session_id = sessionId
  story.last_error = null
  story.next_retry_not_before = null

  state.cursor.current_story_id = storyId
  state.updated_at = nowIso()
  recalcSummary(state)
  writeJson(statePath, state)
  return state
}

export function markComplete(statePath: string, storyId: string, evidence: string): RalphState {
  const state = loadJson<RalphState>(statePath)
  const story = getStory(state, storyId)

  story.status = 'completed'
  story.evidence = evidence
  story.last_error = null
  story.next_retry_not_before = null

  state.cursor.last_completed_story_id = storyId
  state.cursor.current_story_id = null
  state.updated_at = nowIso()
  recalcSummary(state)
  writeJson(statePath, state)
  return state
}

export function markFail(statePath: string, storyId: string, error: string): { state: RalphState; terminal: boolean } {
  const state = loadJson<RalphState>(statePath)
  const story = getStory(state, storyId)
  const config = state.config
  const attempts = story.attempts
  const terminal = attempts >= config.max_retries

  if (terminal) {
    story.status = 'failed'
    story.next_retry_not_before = null
  } else {
    story.status = 'pending'
    const delay = Math.min(config.base_backoff_seconds * (2 ** Math.max(attempts - 1, 0)), config.max_backoff_seconds)
    story.next_retry_not_before = new Date(Date.now() + delay * 1000).toISOString()
  }

  story.last_error = error
  state.cursor.current_story_id = null
  state.updated_at = nowIso()
  recalcSummary(state)
  writeJson(statePath, state)
  return { state, terminal }
}

export function nextStory(statePath: string): RalphStory | null {
  const state = loadJson<RalphState>(statePath)
  const now = Date.now()

  const stories = [...state.stories].sort((a, b) => a.order - b.order)
  for (const story of stories) {
    if (story.status !== 'pending') continue
    if (story.next_retry_not_before) {
      const notBefore = parseTs(story.next_retry_not_before).getTime()
      if (!Number.isNaN(notBefore) && notBefore > now) {
        continue
      }
    }
    return story
  }

  return null
}

export function completionNote(state: RalphState, counts: { total: number; pending: number; in_progress: number; completed: number; failed: number }): string {
  const failedItems = state.stories
    .filter((story) => story.status === 'failed')
    .map((story) => `- ${story.id}: ${story.last_error}`)
  const failedBlock = failedItems.length > 0 ? failedItems.join('\n') : '- none'

  return [
    '# Ralph Loop Completion Note',
    '',
    `- Generated at: ${nowIso()}`,
    `- PRD: ${state.prd_path ?? ''}`,
    `- Worker persona: ${state.worker_persona ?? ''}`,
    `- Last state update: ${state.updated_at ?? ''}`,
    '',
    '## Final Summary',
    `- Total stories: ${counts.total}`,
    `- Completed: ${counts.completed}`,
    `- Failed (terminal): ${counts.failed}`,
    `- Pending: ${counts.pending}`,
    `- In progress: ${counts.in_progress}`,
    '',
    '## Terminal Failures',
    failedBlock,
    '',
  ].join('\n')
}

export function computeCounts(state: RalphState): { total: number; pending: number; in_progress: number; completed: number; failed: number } {
  return state.stories.reduce(
    (acc, story) => {
      acc.total += 1
      if (story.status === 'pending') acc.pending += 1
      if (story.status === 'in_progress') acc.in_progress += 1
      if (story.status === 'completed') acc.completed += 1
      if (story.status === 'failed') acc.failed += 1
      return acc
    },
    { total: 0, pending: 0, in_progress: 0, completed: 0, failed: 0 },
  )
}
