/**
 * OpenClaw Coordination - Task Claims
 * Ported from pi-messenger (store.ts)
 * 
 * Swarm-safe task claiming for multi-agent coordination.
 * Uses file-based mutex to prevent race conditions.
 */

import * as fs from "node:fs";
import { join } from "node:path";
import {
  type ClaimEntry,
  type CompletionEntry,
  type SpecClaims,
  type SpecCompletions,
  type AllClaims,
  type AllCompletions,
  type Dirs,
} from "./types.js";
import { withSwarmLock } from "./lock.js";

// =============================================================================
// Constants
// =============================================================================

const CLAIMS_FILE = "claims.json";
const COMPLETIONS_FILE = "completions.json";
const CLAIM_TTL_MS = 30 * 60 * 1000; // 30 minutes

// =============================================================================
// File I/O
// =============================================================================

function ensureDirSync(dir: string): void {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function readClaimsSync(dirs: Dirs): AllClaims {
  const path = join(dirs.claims, CLAIMS_FILE);
  if (!fs.existsSync(path)) return {};
  try {
    const raw = fs.readFileSync(path, "utf-8");
    const parsed = JSON.parse(raw) as AllClaims;
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // Ignore
  }
  return {};
}

function readCompletionsSync(dirs: Dirs): AllCompletions {
  const path = join(dirs.claims, COMPLETIONS_FILE);
  if (!fs.existsSync(path)) return {};
  try {
    const raw = fs.readFileSync(path, "utf-8");
    const parsed = JSON.parse(raw) as AllCompletions;
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // Ignore
  }
  return {};
}

function writeClaimsSync(dirs: Dirs, claims: AllClaims): void {
  ensureDirSync(dirs.claims);
  const target = join(dirs.claims, CLAIMS_FILE);
  const temp = join(dirs.claims, `${CLAIMS_FILE}.tmp-${process.pid}-${Date.now()}`);
  fs.writeFileSync(temp, JSON.stringify(claims, null, 2));
  fs.renameSync(temp, target);
}

function writeCompletionsSync(dirs: Dirs, completions: AllCompletions): void {
  ensureDirSync(dirs.claims);
  const target = join(dirs.claims, COMPLETIONS_FILE);
  const temp = join(dirs.claims, `${COMPLETIONS_FILE}.tmp-${process.pid}-${Date.now()}`);
  fs.writeFileSync(temp, JSON.stringify(completions, null, 2));
  fs.renameSync(temp, target);
}

// =============================================================================
// Claim Validation
// =============================================================================

/**
 * Check if a claim is stale (session expired or no heartbeat).
 * 
 * OpenClaw adaptation: Uses TTL-based approach.
 * Claims expire after CLAIM_TTL_MS if not refreshed.
 */
function isClaimStale(claim: ClaimEntry): boolean {
  const age = Date.now() - new Date(claim.claimedAt).getTime();
  return age > CLAIM_TTL_MS;
}

/**
 * Clean up stale claims from the claims object.
 * Returns the number of claims removed.
 */
function cleanupStaleClaims(claims: AllClaims): number {
  let removed = 0;
  for (const [spec, tasks] of Object.entries(claims)) {
    for (const [taskId, claim] of Object.entries(tasks)) {
      if (isClaimStale(claim)) {
        delete tasks[taskId];
        removed++;
      }
    }
    if (Object.keys(tasks).length === 0) {
      delete claims[spec];
    }
  }
  return removed;
}

/**
 * Filter out stale claims, returning a clean copy.
 */
function filterStaleClaims(claims: AllClaims): AllClaims {
  const filtered: AllClaims = {};
  for (const [spec, tasks] of Object.entries(claims)) {
    const filteredTasks: SpecClaims = {};
    for (const [taskId, claim] of Object.entries(tasks)) {
      if (!isClaimStale(claim)) {
        filteredTasks[taskId] = claim;
      }
    }
    if (Object.keys(filteredTasks).length > 0) {
      filtered[spec] = filteredTasks;
    }
  }
  return filtered;
}

/**
 * Find if an agent has any active claim.
 */
function findAgentClaim(claims: AllClaims, agent: string): { spec: string; taskId: string } | null {
  for (const [spec, tasks] of Object.entries(claims)) {
    for (const [taskId, claim] of Object.entries(tasks)) {
      if (claim.agent === agent) {
        return { spec, taskId };
      }
    }
  }
  return null;
}

// =============================================================================
// Public API
// =============================================================================

/**
 * Get all active claims (with stale claims filtered out).
 */
export function getClaims(dirs: Dirs): AllClaims {
  const claims = readClaimsSync(dirs);
  return filterStaleClaims(claims);
}

/**
 * Get claims for a specific spec file.
 */
export function getClaimsForSpec(dirs: Dirs, specPath: string): SpecClaims {
  const claims = getClaims(dirs);
  return claims[specPath] ?? {};
}

/**
 * Get all completions.
 */
export function getCompletions(dirs: Dirs): AllCompletions {
  return readCompletionsSync(dirs);
}

/**
 * Get completions for a specific spec file.
 */
export function getCompletionsForSpec(dirs: Dirs, specPath: string): SpecCompletions {
  const completions = getCompletions(dirs);
  return completions[specPath] ?? {};
}

/**
 * Get the current claim for a specific agent (if any).
 */
export function getAgentCurrentClaim(
  dirs: Dirs,
  agent: string
): { spec: string; taskId: string; reason?: string } | null {
  const claims = getClaims(dirs);
  for (const [spec, tasks] of Object.entries(claims)) {
    for (const [taskId, claim] of Object.entries(tasks)) {
      if (claim.agent === agent) {
        return { spec, taskId, reason: claim.reason };
      }
    }
  }
  return null;
}

// =============================================================================
// Claim Operations (Swarm-locked)
// =============================================================================

export type ClaimResult =
  | { success: true; claimedAt: string }
  | { success: false; error: "already_claimed"; conflict: ClaimEntry }
  | { success: false; error: "already_have_claim"; existing: { spec: string; taskId: string } };

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
export async function claimTask(
  dirs: Dirs,
  specPath: string,
  taskId: string,
  agent: string,
  sessionKey: string,
  reason?: string
): Promise<ClaimResult> {
  return withSwarmLock(dirs.base, () => {
    const claims = readClaimsSync(dirs);
    const removed = cleanupStaleClaims(claims);

    // Check if agent already has a claim
    const existing = findAgentClaim(claims, agent);
    if (existing) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "already_have_claim", existing };
    }

    // Check if task is already claimed
    const existingClaim = claims[specPath]?.[taskId];
    if (existingClaim) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "already_claimed", conflict: existingClaim };
    }

    // Create new claim
    if (!claims[specPath]) claims[specPath] = {};
    const newClaim: ClaimEntry = {
      agent,
      sessionKey,
      claimedAt: new Date().toISOString(),
      reason
    };
    claims[specPath][taskId] = newClaim;
    writeClaimsSync(dirs, claims);
    
    return { success: true, claimedAt: newClaim.claimedAt };
  });
}

export type UnclaimResult =
  | { success: true }
  | { success: false; error: "not_claimed" }
  | { success: false; error: "not_your_claim"; claimedBy: string };

/**
 * Release a task claim.
 * 
 * @param dirs - Coordination directories
 * @param specPath - Path to the spec file
 * @param taskId - Task identifier
 * @param agent - Agent name (must match the claim owner)
 */
export async function unclaimTask(
  dirs: Dirs,
  specPath: string,
  taskId: string,
  agent: string
): Promise<UnclaimResult> {
  return withSwarmLock(dirs.base, () => {
    const claims = readClaimsSync(dirs);
    const removed = cleanupStaleClaims(claims);

    const claim = claims[specPath]?.[taskId];
    if (!claim) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "not_claimed" };
    }
    if (claim.agent !== agent) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "not_your_claim", claimedBy: claim.agent };
    }

    delete claims[specPath][taskId];
    if (Object.keys(claims[specPath]).length === 0) {
      delete claims[specPath];
    }
    writeClaimsSync(dirs, claims);
    
    return { success: true };
  });
}

export type CompleteResult =
  | { success: true; completedAt: string }
  | { success: false; error: "not_claimed" }
  | { success: false; error: "not_your_claim"; claimedBy: string }
  | { success: false; error: "already_completed"; completion: CompletionEntry };

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
export async function completeTask(
  dirs: Dirs,
  specPath: string,
  taskId: string,
  agent: string,
  notes?: string
): Promise<CompleteResult> {
  return withSwarmLock(dirs.base, () => {
    const claims = readClaimsSync(dirs);
    const completions = readCompletionsSync(dirs);
    const removed = cleanupStaleClaims(claims);

    // Check if already completed
    const existingCompletion = completions[specPath]?.[taskId];
    if (existingCompletion) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "already_completed", completion: existingCompletion };
    }

    // Check if claimed
    const claim = claims[specPath]?.[taskId];
    if (!claim) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "not_claimed" };
    }
    if (claim.agent !== agent) {
      if (removed > 0) writeClaimsSync(dirs, claims);
      return { success: false, error: "not_your_claim", claimedBy: claim.agent };
    }

    // Remove claim
    delete claims[specPath][taskId];
    if (Object.keys(claims[specPath]).length === 0) {
      delete claims[specPath];
    }

    // Record completion
    if (!completions[specPath]) completions[specPath] = {};
    const completion: CompletionEntry = {
      completedBy: agent,
      completedAt: new Date().toISOString(),
      notes
    };
    completions[specPath][taskId] = completion;

    // Write completions first (more important to record), then claims
    writeCompletionsSync(dirs, completions);
    writeClaimsSync(dirs, claims);
    
    return { success: true, completedAt: completion.completedAt };
  });
}
