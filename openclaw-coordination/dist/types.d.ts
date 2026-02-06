/**
 * OpenClaw Coordination - Types
 * Ported from pi-messenger (lib.ts)
 */
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
    sessionKey: string;
    cwd: string;
    model: string;
    startedAt: string;
    reservations?: FileReservation[];
    gitBranch?: string;
    spec?: string;
    session: AgentSession;
    activity: AgentActivity;
    statusMessage?: string;
    lastHeartbeat: string;
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
export interface ClaimEntry {
    agent: string;
    sessionKey: string;
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
/**
 * Check if file path matches a reservation pattern.
 * - Patterns ending with "/" match directory prefixes
 * - Otherwise exact match
 */
export declare function pathMatchesReservation(filePath: string, pattern: string): boolean;
/**
 * Validate agent name format.
 * Must be 1-50 chars, alphanumeric + underscore/hyphen, not starting with hyphen.
 */
export declare function isValidAgentName(name: string): boolean;
/**
 * Format relative time from ISO timestamp.
 */
export declare function formatRelativeTime(timestamp: string): string;
/**
 * Format duration in human-readable form.
 */
export declare function formatDuration(ms: number): string;
//# sourceMappingURL=types.d.ts.map