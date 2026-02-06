/**
 * OpenClaw Coordination - File Reservations
 * Ported from pi-messenger (store.ts)
 *
 * Handles file reservation conflicts and agent registry.
 * Adapted to use OpenClaw sessions instead of PIDs.
 */
import { type AgentRegistration, type ReservationConflict, type CoordinationState, type Dirs } from "./types.js";
export declare function invalidateAgentsCache(): void;
export declare function getRegistrationPath(state: CoordinationState, dirs: Dirs): string;
/**
 * Get all active agents (excluding self).
 * Results are cached for REGISTRY_CACHE_TTL_MS to reduce disk I/O.
 */
export declare function getActiveAgents(state: CoordinationState, dirs: Dirs): AgentRegistration[];
/**
 * Register this agent in the coordination registry.
 */
export declare function register(state: CoordinationState, dirs: Dirs): boolean;
/**
 * Update agent registration with current state.
 */
export declare function updateRegistration(state: CoordinationState, dirs: Dirs): void;
/**
 * Unregister this agent from the coordination registry.
 */
export declare function unregister(state: CoordinationState, dirs: Dirs): void;
/**
 * Check if a file path conflicts with any active agent's reservations.
 *
 * This is the core conflict detection logic - ported directly from pi-messenger.
 *
 * @param filePath - Path to check for conflicts
 * @param state - Current agent state
 * @param dirs - Coordination directories
 * @returns Array of conflicts (empty if no conflicts)
 */
export declare function getConflictsWithOtherAgents(filePath: string, state: CoordinationState, dirs: Dirs): ReservationConflict[];
/**
 * Add file reservations for this agent.
 *
 * @param patterns - Array of file patterns to reserve (e.g., ["src/api/", "package.json"])
 * @param reason - Optional reason for the reservation
 * @param state - Current agent state
 * @param dirs - Coordination directories
 */
export declare function addReservations(patterns: string[], reason: string | undefined, state: CoordinationState, dirs: Dirs): void;
/**
 * Remove file reservations for this agent.
 *
 * @param patterns - Array of file patterns to release (empty = release all)
 * @param state - Current agent state
 * @param dirs - Coordination directories
 */
export declare function removeReservations(patterns: string[], state: CoordinationState, dirs: Dirs): void;
//# sourceMappingURL=reservations.d.ts.map