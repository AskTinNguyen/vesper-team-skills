#!/usr/bin/env bun

import { readFileSync } from 'fs'

function usage(): never {
  console.error(`Usage:
  json.ts count
  json.ts jsonl
  json.ts field <path> [default]
  json.ts join <path> <subpath> <separator> [default]
  json.ts stringify-stdin
  json.ts task-metadata <file> <metadata-key>
  json.ts task-pr-info <file>
  json.ts task-link-info <file>`)
  process.exit(1)
}

function readStdin(): Promise<string> {
  return new Response(Bun.stdin.stream()).text()
}

function parseJson(input: string): unknown {
  return JSON.parse(input)
}

function getByPath(value: unknown, path: string): unknown {
  if (!path) return value
  const segments = path.split('.').filter(Boolean)
  let current: unknown = value
  for (const segment of segments) {
    if (current == null || typeof current !== 'object') {
      return undefined
    }
    current = (current as Record<string, unknown>)[segment]
  }
  return current
}

function printScalar(value: unknown, fallback = ''): void {
  if (value == null) {
    process.stdout.write(fallback)
    return
  }
  if (typeof value === 'string') {
    process.stdout.write(value)
    return
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    process.stdout.write(String(value))
    return
  }
  process.stdout.write(JSON.stringify(value))
}

function extractTaskJson(filePath: string): Record<string, unknown> {
  return JSON.parse(readFileSync(filePath, 'utf8')) as Record<string, unknown>
}

function findMetadataNumber(description: string, metadataKey: string): number | null {
  const pattern = new RegExp(`${metadataKey}=(\\d+)`)
  const match = description.match(pattern)
  if (!match) return null
  return Number(match[1])
}

async function main() {
  const [command, ...args] = process.argv.slice(2)
  if (!command) usage()

  if (command === 'count') {
    const value = parseJson(await readStdin())
    if (!Array.isArray(value)) {
      throw new Error('count expects a JSON array on stdin')
    }
    process.stdout.write(String(value.length))
    return
  }

  if (command === 'jsonl') {
    const value = parseJson(await readStdin())
    if (!Array.isArray(value)) {
      throw new Error('jsonl expects a JSON array on stdin')
    }
    for (const item of value) {
      process.stdout.write(`${JSON.stringify(item)}\n`)
    }
    return
  }

  if (command === 'field') {
    const [path, fallback = ''] = args
    if (!path) usage()
    const value = parseJson(await readStdin())
    printScalar(getByPath(value, path), fallback)
    return
  }

  if (command === 'join') {
    const [path, subpath, separator, fallback = ''] = args
    if (!path || subpath == null || separator == null) usage()
    const value = parseJson(await readStdin())
    const items = getByPath(value, path)
    if (!Array.isArray(items) || items.length === 0) {
      process.stdout.write(fallback)
      return
    }
    const joined = items
      .map(item => getByPath(item, subpath))
      .filter((item): item is string | number | boolean => item != null && (typeof item === 'string' || typeof item === 'number' || typeof item === 'boolean'))
      .map(String)
      .join(separator)
    process.stdout.write(joined || fallback)
    return
  }

  if (command === 'stringify-stdin') {
    process.stdout.write(JSON.stringify(await readStdin()))
    return
  }

  if (command === 'task-metadata') {
    const [filePath, metadataKey] = args
    if (!filePath || !metadataKey) usage()
    const task = extractTaskJson(filePath)
    const description = typeof task.description === 'string' ? task.description : ''
    const value = findMetadataNumber(description, metadataKey)
    if (value != null) {
      process.stdout.write(String(value))
    }
    return
  }

  if (command === 'task-pr-info') {
    const [filePath] = args
    if (!filePath) usage()
    const task = extractTaskJson(filePath)
    const description = typeof task.description === 'string' ? task.description : ''
    const prNumber = findMetadataNumber(description, 'pr_number')
    if (prNumber == null) {
      return
    }
    process.stdout.write(JSON.stringify({
      task_id: typeof task.id === 'string' ? task.id : '',
      subject: typeof task.subject === 'string' ? task.subject : '',
      status: typeof task.status === 'string' ? task.status : '',
      pr_number: prNumber,
    }))
    return
  }

  if (command === 'task-link-info') {
    const [filePath] = args
    if (!filePath) usage()
    const task = extractTaskJson(filePath)
    if (task.status === 'completed') {
      return
    }
    const description = typeof task.description === 'string' ? task.description : ''
    const prNumber = findMetadataNumber(description, 'pr_number')
    const issueNumber = findMetadataNumber(description, 'issue_number')
    if (prNumber == null && issueNumber == null) {
      return
    }
    process.stdout.write(JSON.stringify({
      task_id: typeof task.id === 'string' ? task.id : '',
      subject: typeof task.subject === 'string' ? task.subject : '',
      github_type: prNumber != null ? 'pr' : 'issue',
      github_number: prNumber ?? issueNumber,
    }))
    return
  }

  usage()
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
