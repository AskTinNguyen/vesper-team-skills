/**
 * OpenClaw Coordination - Types
 * Ported from pi-messenger (lib.ts)
 */

// =============================================================================
// File Reservations
// =============================================================================

export interface FileReservation {
  pattern: string;
  reason?: string;
  since: string;
}

export interface ReservationConflict {
  path: string;
  agent: string;
  pattern: string;
  reason?: string;
  registration: AgentRegistration;
}

// =============================================================================
// Agent Registration (Adapted for OpenClaw)
// =============================================================================

export interface AgentSession {
  toolCalls: number;
  tokens: number;
  filesModified: string[];
}

export interface AgentActivity {
  lastActivityAt: string;
  currentActivity?: string;
  lastToolCall?: string;
}

export interface AgentRegistration {
  name: string;
  sessionKey: string;      // OpenClaw sessionKey (replaces pid/sessionId)
  cwd: string;
  model: string;
  startedAt: string;
  reservations?: FileReservation[];
  gitBranch?: string;
  spec?: string;
  session: AgentSession;
  activity: AgentActivity;
  statusMessage?: string;
  lastHeartbeat: string;   // For TTL-based liveness (replaces isProcessAlive)
}

export interface CoordinationState {
  agentName: string;
  sessionKey: string;
  registered: boolean;
  reservations: FileReservation[];
  model: string;
  gitBranch?: string;
  spec?: string;
  session: AgentSession;
  activity: AgentActivity;
  statusMessage?: string;
  sessionStartedAt: string;
}

export interface Dirs {
  base: string;
  registry: string;
  reservations: string;
  claims: string;
}

// =============================================================================
// Task Claims
// =============================================================================

export interface ClaimEntry {
  agent: string;
  sessionKey: string;      // OpenClaw sessionKey
  claimedAt: string;
  reason?: string;
}

export interface CompletionEntry {
  completedBy: string;
  completedAt: string;
  notes?: string;
}

export type SpecClaims = Record<string, ClaimEntry>;
export type SpecCompletions = Record<string, CompletionEntry>;
export type AllClaims = Record<string, SpecClaims>;
export type AllCompletions = Record<string, SpecCompletions>;

// =============================================================================
// Pure Utilities (Ported from pi-messenger)
// =============================================================================

/**
 * Check if file path matches a reservation pattern.
 * - Patterns ending with "/" match directory prefixes
 * - Otherwise exact match
 */
export function pathMatchesReservation(filePath: string, pattern: string): boolean {
  if (pattern.endsWith("/")) {
    return filePath.startsWith(pattern) || filePath + "/" === pattern;
  }
  return filePath === pattern;
}

/**
 * Validate agent name format.
 * Must be 1-50 chars, alphanumeric + underscore/hyphen, not starting with hyphen.
 */
export function isValidAgentName(name: string): boolean {
  if (!name || name.length > 50) return false;
  return /^[a-zA-Z0-9_][a-zA-Z0-9_-]*$/.test(name);
}

/**
 * Format relative time from ISO timestamp.
 */
export function formatRelativeTime(timestamp: string): string {
  const diff = Date.now() - new Date(timestamp).getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return "just now";
}

/**
 * Format duration in human-readable form.
 */
export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}
