# Vesper Electron File Locations

## Main Process (`apps/electron/src/main/`)

| File | Purpose |
|------|---------|
| `index.ts` | App lifecycle, initialization, quit handling |
| `ipc.ts` | IPC handler registration |
| `sessions.ts` | SessionManager for agent conversations |
| `window-manager.ts` | Window creation and management |
| `scheduler.ts` | Cron scheduling service (reference implementation) |
| `logger.ts` | Logging utilities |
| `notifications.ts` | Native notification handling |

## Preload (`apps/electron/src/preload/`)

| File | Purpose |
|------|---------|
| `index.ts` | Bridge exposing main process APIs to renderer |

## Shared Types (`apps/electron/src/shared/`)

| File | Purpose |
|------|---------|
| `types.ts` | All TypeScript interfaces, IPC channels, ElectronAPI |
| `routes.ts` | Route builders for navigation |
| `route-parser.ts` | Route string parsing to NavigationState |

## Renderer (`apps/electron/src/renderer/`)

| Directory | Purpose |
|-----------|---------|
| `components/` | React components |
| `components/app-shell/` | Main app layout, sidebar, navigation |
| `components/ui/` | Reusable UI primitives (Radix-based) |
| `components/scheduler/` | Scheduler feature (reference implementation) |
| `contexts/` | React contexts (NavigationContext, etc.) |
| `hooks/` | Custom React hooks |
| `atoms/` | Jotai atoms for state management |

## UI Components Available

Located in `src/renderer/components/ui/`:

- `button.tsx` - Button with variants
- `dialog.tsx` - Modal dialogs
- `dropdown-menu.tsx` - Dropdown menus
- `input.tsx` - Text input
- `textarea.tsx` - Multi-line text
- `select.tsx` - Select dropdown
- `switch.tsx` - Toggle switch
- `tooltip.tsx` - Tooltips
- `label.tsx` - Form labels

## Data Storage

Per-workspace data stored in:
```
~/.craft-agent/workspaces/{workspaceId}/
├── schedules.json      # Scheduler data
├── sessions/           # Agent session data
└── sources/            # Source configurations
```
