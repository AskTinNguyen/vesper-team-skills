/**
 * QMD IPC Handler - Main Process Implementation
 *
 * This module provides secure execution of QMD CLI commands from an Electron main process.
 * Key security features:
 * - Subcommand allowlist validation
 * - Argument sanitization to prevent shell injection
 * - Safe execution via execFile (shell: false)
 * - Graceful ENOENT handling with helpful install message
 */

import { ipcMain } from 'electron'
import { execFile } from 'child_process'
import { homedir } from 'os'
import path from 'path'
import fs from 'fs'
import fsPromises from 'fs/promises'
import yaml from 'js-yaml'

// IPC Channel constants
const IPC_CHANNELS = {
  VECTOR_SEARCH_EXECUTE: 'vector-search:execute',
  VECTOR_SEARCH_GET_CONFIG: 'vector-search:get-config',
}

// Type definitions
interface VectorSearchExecuteResult {
  stdout: string
  stderr: string
}

interface VectorSearchCollectionConfig {
  name: string
  path: string
  pattern: string
}

interface VectorSearchConfig {
  collections: VectorSearchCollectionConfig[]
}

/**
 * Sanitize CLI arguments to prevent shell injection
 * Removes dangerous shell metacharacters and limits length
 */
function sanitizeArg(arg: string): string {
  // Remove shell metacharacters that could allow command injection:
  // ` - backtick (command substitution)
  // $ - variable expansion and $() command substitution
  // () - subshell and command grouping
  // {} - brace expansion
  // | - pipe
  // ; - command separator
  // & - background operator and &&
  // \n \r \0 - newlines and null bytes
  return arg.replace(/[`$(){}|;&\n\r\0]/g, '').slice(0, 1000)
}

/**
 * Resolve QMD binary path
 * Checks common installation locations since Electron may not have full PATH
 */
function resolveQmdPath(): string {
  const home = homedir()
  const qmdPaths = [
    path.join(home, '.bun/bin/qmd'),
    path.join(home, '.local/bin/qmd'),
    '/usr/local/bin/qmd',
    '/opt/homebrew/bin/qmd',
    'qmd', // fallback to PATH lookup
  ]

  for (const p of qmdPaths) {
    if (p !== 'qmd' && fs.existsSync(p)) {
      return p
    }
  }
  return 'qmd' // Fallback - let execFile try PATH
}

/**
 * Register QMD IPC handlers
 * Call this once during app initialization
 */
export function registerQmdIpcHandlers(): void {
  // Execute QMD CLI command
  ipcMain.handle(
    IPC_CHANNELS.VECTOR_SEARCH_EXECUTE,
    async (_event, args: string[]): Promise<VectorSearchExecuteResult> => {
      // Validate subcommand against allowlist
      const allowedSubcommands = [
        'search',
        'vsearch',
        'query',
        'collection',
        'ls',
        'status',
        'embed',
        'update',
      ]
      const subcommand = args[0]?.toLowerCase()
      if (!subcommand || !allowedSubcommands.includes(subcommand)) {
        return { stdout: '', stderr: `Invalid QMD subcommand: ${subcommand}` }
      }

      // Sanitize all arguments
      const sanitized = args.map((arg) => sanitizeArg(arg))

      // Resolve QMD binary path
      const qmdPath = resolveQmdPath()

      // Longer timeout for embed operations (can take minutes for large collections)
      const timeout = subcommand === 'embed' ? 300000 : 60000

      // Ensure PATH includes common bin directories
      const home = homedir()
      const env = {
        ...process.env,
        PATH: `${home}/.bun/bin:${home}/.local/bin:/usr/local/bin:/opt/homebrew/bin:${process.env.PATH || ''}`,
      }

      return new Promise<VectorSearchExecuteResult>((resolve) => {
        execFile(
          qmdPath,
          sanitized,
          { shell: false, timeout, env },
          (error, stdout, stderr) => {
            if (error && (error as NodeJS.ErrnoException).code === 'ENOENT') {
              resolve({
                stdout: '',
                stderr:
                  'QMD not installed. Run: bun install -g https://github.com/tobi/qmd',
              })
            } else if (error) {
              resolve({
                stdout: '',
                stderr: stderr || error.message,
              })
            } else {
              resolve({ stdout, stderr })
            }
          }
        )
      })
    }
  )

  // Get QMD config (collection root paths)
  ipcMain.handle(
    IPC_CHANNELS.VECTOR_SEARCH_GET_CONFIG,
    async (): Promise<VectorSearchConfig> => {
      const configPath = path.join(homedir(), '.config', 'qmd', 'index.yml')

      try {
        const content = await fsPromises.readFile(configPath, 'utf-8')
        const config = yaml.load(content) as {
          collections?: Record<string, { path: string; pattern: string }>
        }

        const collections: VectorSearchCollectionConfig[] = []

        if (config?.collections) {
          for (const [name, info] of Object.entries(config.collections)) {
            if (info && typeof info.path === 'string') {
              collections.push({
                name,
                path: info.path,
                pattern: info.pattern || '**/*.md',
              })
            }
          }
        }

        return { collections }
      } catch (error) {
        console.warn('Failed to read QMD config:', error)
        return { collections: [] }
      }
    }
  )
}

// Preload bridge - add to your preload script:
// vectorSearchExecute: (args: string[]) =>
//   ipcRenderer.invoke('vector-search:execute', args),
// vectorSearchGetConfig: () =>
//   ipcRenderer.invoke('vector-search:get-config'),
