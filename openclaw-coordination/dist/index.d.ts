/**
 * OpenClaw Coordination Extension
 *
 * Multi-agent coordination for OpenClaw, ported from pi-messenger.
 * Provides file reservations, task claiming, and swarm locking.
 */
export * from "./types.js";
export { withSwarmLock } from "./lock.js";
export { register, unregister, updateRegistration, getActiveAgents, getConflictsWithOtherAgents, addReservations, removeReservations, invalidateAgentsCache, } from "./reservations.js";
export { getClaims, getClaimsForSpec, getCompletions, getCompletionsForSpec, getAgentCurrentClaim, claimTask, unclaimTask, completeTask, } from "./claims.js";
export type { ClaimResult, UnclaimResult, CompleteResult, } from "./claims.js";
declare const plugin: {
    id: string;
    name: string;
    description: string;
    configSchema: {
        type: string;
        properties: {};
        additionalProperties: boolean;
    };
    register(_api: any): void;
};
export default plugin;
//# sourceMappingURL=index.d.ts.map