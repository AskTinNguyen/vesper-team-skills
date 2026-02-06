/**
 * OpenClaw Coordination Extension
 *
 * Multi-agent coordination for OpenClaw, ported from pi-messenger.
 * Provides file reservations, task claiming, and swarm locking.
 */

// Export types
export * from "./types.js";

// Export lock utilities
export { withSwarmLock } from "./lock.js";

// Export reservation functions
export {
  register,
  unregister,
  updateRegistration,
  getActiveAgents,
  getConflictsWithOtherAgents,
  addReservations,
  removeReservations,
  invalidateAgentsCache,
} from "./reservations.js";

// Export claim functions
export {
  getClaims,
  getClaimsForSpec,
  getCompletions,
  getCompletionsForSpec,
  getAgentCurrentClaim,
  claimTask,
  unclaimTask,
  completeTask,
} from "./claims.js";

// Export result type guards
export type {
  ClaimResult,
  UnclaimResult,
  CompleteResult,
} from "./claims.js";

// Plugin interface for OpenClaw
const plugin = {
  id: "coordination",
  name: "coordination",
  description: "Multi-agent coordination for OpenClaw (file reservations, task claiming)",
  configSchema: {
    type: "object",
    properties: {},
    additionalProperties: false,
  },
  register(_api: any) {
    // Coordination is a library extension — no tools to register.
  },
};

export default plugin;
