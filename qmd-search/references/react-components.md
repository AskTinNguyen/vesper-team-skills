# QMD React Components Reference

This document provides the React component implementations for integrating QMD search into an Electron renderer process.

## State Management (Jotai Atoms)

```typescript
/**
 * Vector Search Atoms
 *
 * Simple atoms for storing vector search state.
 * Uses QMD CLI for semantic search across markdown documents.
 */

import { atom } from 'jotai'

/**
 * Search mode types supported by QMD
 */
export type SearchMode = 'keyword' | 'semantic' | 'hybrid'

/**
 * Collection info from QMD
 */
export interface CollectionInfo {
  name: string
  url: string
  pattern: string
  files: number
  updated: string
  rootPath?: string // Absolute root path for resolving relative file paths
}

/**
 * Search result from QMD
 */
export interface VectorSearchResult {
  filePath: string
  snippet: string
  score: number
  collection: string
  title?: string
}

/**
 * Search state for the vector search feature
 */
export interface SearchState {
  query: string
  mode: SearchMode
  results: VectorSearchResult[]
  error: string | null
  isSearching: boolean
}

/**
 * Main search state atom
 */
export const searchStateAtom = atom<SearchState>({
  query: '',
  mode: 'hybrid',
  results: [],
  error: null,
  isSearching: false,
})

/**
 * Collections list atom (info about registered QMD collections)
 */
export const collectionsAtom = atom<CollectionInfo[]>([])

/**
 * Add collection modal state atom
 */
export const addCollectionModalAtom = atom<boolean>(false)

/**
 * Operation types for collection management
 */
export type CollectionOperationType = 'add' | 'remove' | 'reindex'

/**
 * Collection operation state
 */
export interface CollectionOperation {
  type: CollectionOperationType
  status: 'in_progress' | 'success' | 'error'
  step?: string
  error?: string
  collectionName?: string
}

/**
 * Collection operation atom (tracks current operation in progress)
 */
export const collectionOperationAtom = atom<CollectionOperation | null>(null)
```

## Helper Functions

```typescript
/**
 * Strip ANSI escape codes from string
 * QMD outputs progress info with ANSI codes even with --json flag
 */
function stripAnsi(str: string): string {
  // eslint-disable-next-line no-control-regex
  return str.replace(/\x1b\[[0-9;]*[a-zA-Z]|\]9;[0-9;]+/g, '')
}

/**
 * Parse JSON search results from QMD CLI output
 * QMD outputs progress messages (tips, query expansion, etc.) BEFORE the JSON array
 * We need to find and extract just the JSON portion
 */
function parseSearchResults(output: string): VectorSearchResult[] {
  if (!output.trim()) {
    return []
  }

  // Strip ANSI escape codes first
  const cleaned = stripAnsi(output)

  // Find the JSON array in the output (starts with '[', ends with ']')
  const jsonStart = cleaned.indexOf('[')
  if (jsonStart === -1) {
    return []
  }

  const jsonEnd = cleaned.lastIndexOf(']')
  if (jsonEnd === -1 || jsonEnd < jsonStart) {
    return []
  }

  try {
    const jsonStr = cleaned.slice(jsonStart, jsonEnd + 1)
    const parsed = JSON.parse(jsonStr) as Array<{
      docid: string
      score: number
      file: string
      title?: string
      context?: string
      snippet?: string
    }>

    return parsed.map((item) => ({
      filePath: item.file?.replace(/^qmd:\/\/[^/]+\//, '') || '',
      score: item.score ?? 0,
      snippet: item.snippet?.replace(/@@ [^@]+ @@[^\n]*\n?/, '') || '',
      collection: item.file?.match(/^qmd:\/\/([^/]+)\//)?.[1] || 'default',
      title: item.title,
    }))
  } catch (e) {
    console.error('[VectorSearch] JSON parse error:', e)
    return []
  }
}

/**
 * Parse collection list output from QMD CLI
 * Format:
 * Collections (N):
 *
 * name (qmd://name/)
 *   Pattern:  **\/*.md
 *   Files:    123
 *   Updated:  2d ago
 */
function parseCollectionList(output: string): CollectionInfo[] {
  const collections: CollectionInfo[] = []
  const lines = output.split('\n')

  let i = 0
  while (i < lines.length) {
    const line = lines[i].trim()
    // Look for collection name line: "name (qmd://name/)"
    const nameMatch = line.match(/^(\S+)\s+\(qmd:\/\/([^/]+)\/\)$/)
    if (nameMatch) {
      const collection: CollectionInfo = {
        name: nameMatch[1],
        url: `qmd://${nameMatch[2]}/`,
        pattern: '',
        files: 0,
        updated: '',
      }
      // Parse following lines for Pattern, Files, Updated
      for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
        const subLine = lines[j].trim()
        if (subLine.startsWith('Pattern:')) {
          collection.pattern = subLine.replace('Pattern:', '').trim()
        } else if (subLine.startsWith('Files:')) {
          collection.files = parseInt(subLine.replace('Files:', '').trim()) || 0
        } else if (subLine.startsWith('Updated:')) {
          collection.updated = subLine.replace('Updated:', '').trim()
        }
      }
      collections.push(collection)
    }
    i++
  }
  return collections
}
```

## VectorSearch Component

```tsx
import { useAtom, useSetAtom } from 'jotai'
import { useEffect, useCallback } from 'react'
import { Plus } from 'lucide-react'
import {
  searchStateAtom,
  collectionsAtom,
  addCollectionModalAtom,
  type SearchMode,
  type CollectionInfo,
} from './atoms/vector-search'
import { Button } from '@/components/ui/button'
import { AddCollectionModal } from './AddCollectionModal'
import { CollectionList } from './CollectionList'

export function VectorSearch() {
  const [state, setState] = useAtom(searchStateAtom)
  const [collections, setCollections] = useAtom(collectionsAtom)
  const setAddCollectionModalOpen = useSetAtom(addCollectionModalAtom)

  // Helper to resolve relative file paths to absolute
  const resolveAbsolutePath = useCallback(
    (filePath: string, collection: string): string => {
      const collectionInfo = collections.find((c) => c.name === collection)
      if (collectionInfo?.rootPath && !filePath.startsWith('/')) {
        return `${collectionInfo.rootPath}/${filePath}`
      }
      return filePath
    },
    [collections]
  )

  // Load collections on mount
  useEffect(() => {
    Promise.all([
      window.electronAPI.vectorSearchExecute(['collection', 'list']),
      window.electronAPI.vectorSearchGetConfig(),
    ])
      .then(([{ stdout }, config]) => {
        // Build a map of collection name -> root path from the config
        const rootPathMap = new Map<string, string>()
        if (config?.collections) {
          for (const c of config.collections) {
            rootPathMap.set(c.name, c.path)
          }
        }

        if (stdout) {
          const parsed = parseCollectionList(stdout)
          // Merge root paths from config into collection info
          const withRootPaths = parsed.map((c) => ({
            ...c,
            rootPath: rootPathMap.get(c.name),
          }))
          setCollections(withRootPaths)
        }
      })
      .catch((err) => {
        console.error('[VectorSearch] Failed to load collections:', err)
      })
  }, [setCollections])

  // Search function
  const search = useCallback(async () => {
    if (!state.query.trim()) return
    setState((s) => ({ ...s, isSearching: true, error: null }))

    const cmd =
      state.mode === 'keyword'
        ? 'search'
        : state.mode === 'semantic'
          ? 'vsearch'
          : 'query'

    try {
      const { stdout, stderr } = await window.electronAPI.vectorSearchExecute([
        cmd,
        '-n',
        '20',
        '--json',
        state.query,
      ])

      const results = parseSearchResults(stdout || '')

      if (results.length === 0 && stderr && !stdout?.includes('[')) {
        setState((s) => ({ ...s, isSearching: false, error: stderr }))
        return
      }

      setState((s) => ({ ...s, isSearching: false, results }))
    } catch (err) {
      setState((s) => ({
        ...s,
        isSearching: false,
        error: err instanceof Error ? err.message : 'Search failed',
      }))
    }
  }, [state.query, state.mode, setState])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        search()
      }
    },
    [search]
  )

  const handleQueryChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setState((s) => ({ ...s, query: e.target.value }))
    },
    [setState]
  )

  const handleModeChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setState((s) => ({ ...s, mode: e.target.value as SearchMode }))
    },
    [setState]
  )

  const handleViewDocument = useCallback(
    (filePath: string, collection: string) => {
      const absolutePath = resolveAbsolutePath(filePath, collection)
      // Navigate to document view - implement your navigation logic
      console.log('View document:', absolutePath)
    },
    [resolveAbsolutePath]
  )

  return (
    <div className="flex flex-col h-full p-4">
      {/* Search Input */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={state.query}
          onChange={handleQueryChange}
          onKeyDown={handleKeyDown}
          placeholder="Search docs..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <select value={state.mode} onChange={handleModeChange} className="px-3 py-2 border rounded">
          <option value="hybrid">Hybrid</option>
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
        </select>
        <button
          onClick={search}
          disabled={state.isSearching}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {state.isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Error */}
      {state.error && (
        <div className="p-3 mb-4 bg-red-100 text-red-700 rounded">{state.error}</div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-y-auto">
        {state.results.map((result, i) => (
          <div
            key={`${result.filePath}-${i}`}
            className="p-3 border-b cursor-pointer hover:bg-gray-50"
            onClick={() => handleViewDocument(result.filePath, result.collection)}
          >
            <div className="font-medium">
              {result.title || result.filePath.split('/').pop()}
            </div>
            <div className="text-sm text-gray-500 truncate">{result.filePath}</div>
            {result.snippet && (
              <div className="text-sm mt-1 line-clamp-2">{result.snippet}</div>
            )}
            <div className="text-xs text-gray-400 mt-1">
              Score: {result.score.toFixed(2)}
              {result.collection && ` | ${result.collection}`}
            </div>
          </div>
        ))}
      </div>

      {/* Collections Section */}
      <div className="mt-4 pt-4 border-t space-y-3">
        <CollectionList />
        <Button
          variant="outline"
          size="sm"
          onClick={() => setAddCollectionModalOpen(true)}
          className="w-full"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Collection
        </Button>
      </div>

      <AddCollectionModal />
    </div>
  )
}
```

## AddCollectionModal Component

```tsx
import { useState, useCallback } from 'react'
import { useAtom } from 'jotai'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  addCollectionModalAtom,
  collectionOperationAtom,
  collectionsAtom,
} from './atoms/vector-search'

export function AddCollectionModal() {
  const [isOpen, setIsOpen] = useAtom(addCollectionModalAtom)
  const [operation, setOperation] = useAtom(collectionOperationAtom)
  const [, setCollections] = useAtom(collectionsAtom)

  const [folderPath, setFolderPath] = useState('')
  const [collectionName, setCollectionName] = useState('')
  const [filePattern, setFilePattern] = useState('**/*.md')

  const isSubmitting = operation?.type === 'add' && operation?.status === 'in_progress'

  const handleSelectFolder = useCallback(async () => {
    const path = await window.electronAPI.openFolderDialog()
    if (path) {
      setFolderPath(path)
      // Auto-derive collection name from folder name
      const name = path.split('/').pop() || 'collection'
      setCollectionName(name)
    }
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!folderPath || !collectionName) {
      toast.error('Please select a folder and provide a collection name')
      return
    }

    const toastId = toast.loading('Adding collection...')

    try {
      // Step 1: Add the collection
      setOperation({ type: 'add', status: 'in_progress', step: 'Adding collection...' })

      await window.electronAPI.vectorSearchExecute([
        'collection',
        'add',
        folderPath,
        '--name',
        collectionName,
        '--mask',
        filePattern,
      ])

      // Step 2: Run embedding to index documents
      toast.loading('Indexing documents...', { id: toastId })
      setOperation({ type: 'add', status: 'in_progress', step: 'Indexing documents...' })

      await window.electronAPI.vectorSearchExecute(['embed'])

      // Step 3: Refresh collections list
      const [listResult, config] = await Promise.all([
        window.electronAPI.vectorSearchExecute(['collection', 'list']),
        window.electronAPI.vectorSearchGetConfig(),
      ])

      if (listResult.stdout) {
        const rootPathMap = new Map<string, string>()
        if (config?.collections) {
          for (const c of config.collections) {
            rootPathMap.set(c.name, c.path)
          }
        }
        const parsed = parseCollectionList(listResult.stdout)
        setCollections(
          parsed.map((c) => ({ ...c, rootPath: rootPathMap.get(c.name) }))
        )
      }

      setOperation({ type: 'add', status: 'success' })
      toast.success(`Collection '${collectionName}' added successfully`, { id: toastId })
      setIsOpen(false)
    } catch (err) {
      setOperation({
        type: 'add',
        status: 'error',
        error: err instanceof Error ? err.message : 'Failed',
      })
      toast.error(err instanceof Error ? err.message : 'Failed', { id: toastId })
    }
  }, [folderPath, collectionName, filePattern, setOperation, setCollections, setIsOpen])

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Collection</DialogTitle>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="folder">Folder</Label>
            <div className="flex gap-2">
              <Input
                id="folder"
                value={folderPath}
                onChange={(e) => setFolderPath(e.target.value)}
                placeholder="/path/to/documents"
                disabled={isSubmitting}
              />
              <Button variant="outline" onClick={handleSelectFolder} disabled={isSubmitting}>
                Browse
              </Button>
            </div>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="name">Collection Name</Label>
            <Input
              id="name"
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              placeholder="my-docs"
              disabled={isSubmitting}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="pattern">File Pattern</Label>
            <Input
              id="pattern"
              value={filePattern}
              onChange={(e) => setFilePattern(e.target.value)}
              placeholder="**/*.md"
              disabled={isSubmitting}
            />
            <p className="text-xs text-gray-500">
              Glob pattern for files to index (e.g., **/*.md, **/*.txt)
            </p>
          </div>

          {isSubmitting && operation?.step && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              {operation.step}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !folderPath || !collectionName}
          >
            {isSubmitting ? 'Adding...' : 'Add Collection'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

## CollectionList Component

```tsx
import { useCallback } from 'react'
import { useAtom } from 'jotai'
import { toast } from 'sonner'
import { Trash2, RefreshCw, FolderOpen } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  collectionsAtom,
  collectionOperationAtom,
  type CollectionInfo,
} from './atoms/vector-search'

export function CollectionList() {
  const [collections, setCollections] = useAtom(collectionsAtom)
  const [operation, setOperation] = useAtom(collectionOperationAtom)

  const isOperationInProgress = operation?.status === 'in_progress'

  const refreshCollections = useCallback(async () => {
    const [listResult, config] = await Promise.all([
      window.electronAPI.vectorSearchExecute(['collection', 'list']),
      window.electronAPI.vectorSearchGetConfig(),
    ])

    if (listResult.stdout) {
      const rootPathMap = new Map<string, string>()
      if (config?.collections) {
        for (const c of config.collections) {
          rootPathMap.set(c.name, c.path)
        }
      }
      const parsed = parseCollectionList(listResult.stdout)
      setCollections(parsed.map((c) => ({ ...c, rootPath: rootPathMap.get(c.name) })))
    }
  }, [setCollections])

  const handleRemove = useCallback(
    async (collection: CollectionInfo) => {
      const toastId = toast.loading(`Removing collection '${collection.name}'...`)

      try {
        setOperation({ type: 'remove', status: 'in_progress', collectionName: collection.name })

        await window.electronAPI.vectorSearchExecute([
          'collection',
          'remove',
          collection.name,
        ])

        await refreshCollections()

        setOperation({ type: 'remove', status: 'success' })
        toast.success(`Collection '${collection.name}' removed`, { id: toastId })
      } catch (err) {
        setOperation({ type: 'remove', status: 'error', error: String(err) })
        toast.error(String(err), { id: toastId })
      }
    },
    [setOperation, refreshCollections]
  )

  const handleReindex = useCallback(
    async (collection: CollectionInfo) => {
      const toastId = toast.loading(`Re-indexing collection '${collection.name}'...`)

      try {
        setOperation({ type: 'reindex', status: 'in_progress', collectionName: collection.name })

        // Use 'update' for incremental re-indexing
        await window.electronAPI.vectorSearchExecute(['update'])

        await refreshCollections()

        setOperation({ type: 'reindex', status: 'success' })
        toast.success(`Collection '${collection.name}' re-indexed`, { id: toastId })
      } catch (err) {
        setOperation({ type: 'reindex', status: 'error', error: String(err) })
        toast.error(String(err), { id: toastId })
      }
    },
    [setOperation, refreshCollections]
  )

  if (collections.length === 0) {
    return null
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium">Collections ({collections.length})</div>
      <div className="space-y-1">
        {collections.map((collection) => {
          const isThisOperating =
            isOperationInProgress && operation?.collectionName === collection.name

          return (
            <div
              key={collection.name}
              className="flex items-center justify-between p-2 rounded-md bg-gray-50 hover:bg-gray-100"
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <FolderOpen className="w-4 h-4 text-gray-400 shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-sm truncate">{collection.name}</div>
                  <div className="text-xs text-gray-500 truncate">
                    {collection.files} files · {collection.pattern} · {collection.updated || 'never'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-7 h-7"
                  onClick={() => handleReindex(collection)}
                  disabled={isOperationInProgress}
                  title="Re-index collection"
                >
                  <RefreshCw
                    className={`w-3.5 h-3.5 ${isThisOperating && operation?.type === 'reindex' ? 'animate-spin' : ''}`}
                  />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-7 h-7 text-red-500 hover:text-red-600 hover:bg-red-50"
                  onClick={() => handleRemove(collection)}
                  disabled={isOperationInProgress}
                  title="Remove collection"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Preload Bridge

Add these methods to your preload script to expose the IPC calls to the renderer:

```typescript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  vectorSearchExecute: (args: string[]) =>
    ipcRenderer.invoke('vector-search:execute', args),
  vectorSearchGetConfig: () => ipcRenderer.invoke('vector-search:get-config'),
  openFolderDialog: () => ipcRenderer.invoke('dialog:open-folder'),
})
```

## Window Type Declaration

```typescript
// global.d.ts
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

interface ElectronAPI {
  vectorSearchExecute: (args: string[]) => Promise<VectorSearchExecuteResult>
  vectorSearchGetConfig: () => Promise<VectorSearchConfig>
  openFolderDialog: () => Promise<string | null>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
```
