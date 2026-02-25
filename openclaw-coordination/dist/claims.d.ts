/**
 * OpenClaw Coordination - Task Claims
 * Ported from pi-messenger (store.ts)
 *
 * Swarm-safe task claiming for multi-agent coordination.
 * Uses file-based mutex to prevent race conditions.
 */
import { type ClaimEntry, type CompletionEntry, type SpecClaims, type SpecCompletions, type AllClaims, type AllCompletions, type Dirs } from "./types.js";
/**
 * Get all active claims (with stale claims filtered out).
 */
export declare function getClaims(dirs: Dirs): AllClaims;
/**
 * Get claims for a specific spec file.
 */
export declare function getClaimsForSpec(dirs: Dirs, specPath: string): SpecClaims;
/**
 * Get all completions.
 */
export declare function getCompletions(dirs: Dirs): AllCompletions;
/**
 * Get completions for a specific spec file.
 */
export declare function getCompletionsForSpec(dirs: Dirs, specPath: string): SpecCompletions;
/**
 * Get the current claim for a specific agent (if any).
 */
export declare function getAgentCurrentClaim(dirs: Dirs, agent: string): {
    spec: string;
    taskId: string;
    reason?: string;
} | null;
export type ClaimResult = {
    success: true;
    claimedAt: string;
} | {
    success: false;
    error: "already_claimed";
    conflict: ClaimEntry;
} | {
    success: false;
    error: "already_have_claim";
    existing: {
        spec: string;
        taskId: string;
    };
};
/**
 * Claim a task for an agent.
 *
 * This is a swarm-locked operation to prevent race conditions.
 * Only one agent can claim a task at a time.
 * An agent can only have one active claim at a time.
 *
 * @param dirs - Coordination directories
 * @param specPath - Path to the spec file (for grouping tasks)
 * @param taskId - Unique task identifier
 * @param agent - Agent name
 * @param sessionKey - OpenClaw session key
 * @param reason - Optional reason for claiming
 */
export declare function claimTask(dirs: Dirs, specPath: string, taskId: string, agent: string, sessionKey: string, reason?: string): Promise<ClaimResult>;
export type UnclaimResult = {
    success: true;
} | {
    success: false;
    error: "not_claimed";
} | {
    success: false;
    error: "not_your_claim";
    claimedBy: string;
};
/**
 * Release a task claim.
 *
 * @param dirs - Coordination directories
 * @param specPath - Path to the spec file
 * @param taskId - Task identifier
 * @param agent - Agent name (must match the claim owner)
 */
export declare function unclaimTask(dirs: Dirs, specPath: string, taskId: string, agent: string): Promise<UnclaimResult>;
export type CompleteResult = {
    success: true;
    completedAt: string;
} | {
    success: false;
    error: "not_claimed";
} | {
    success: false;
    error: "not_your_claim";
    claimedBy: string;
} | {
    success: false;
    error: "already_completed";
    completion: CompletionEntry;
};
/**
 * Mark a task as complete.
 *
 * This removes the claim and records a completion entry.
 *
 * @param dirs - Coordination directories
 * @param specPath - Path to the spec file
 * @param taskId - Task identifier
 * @param agent - Agent name (must match the claim owner)
 * @param notes - Optional completion notes
 */
export declare function completeTask(dirs: Dirs, specPath: string, taskId: string, agent: string, notes?: string): Promise<CompleteResult>;
//# sourceMappingURL=claims.d.ts.map