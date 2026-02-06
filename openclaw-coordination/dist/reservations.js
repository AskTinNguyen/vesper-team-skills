/**
 * OpenClaw Coordination - File Reservations
 * Ported from pi-messenger (store.ts)
 *
 * Handles file reservation conflicts and agent registry.
 * Adapted to use OpenClaw sessions instead of PIDs.
 */
import * as fs from "node:fs";
import { join } from "node:path";
import { execSync } from "node:child_process";
import { pathMatchesReservation, isValidAgentName, } from "./types.js";
// =============================================================================
// Constants
// =============================================================================
const AGENT_TTL_MS = 30 * 60 * 1000; // 30 minutes
const REGISTRY_CACHE_TTL_MS = 1000; // 1 second
let agentsCache = null;
export function invalidateAgentsCache() {
    agentsCache = null;
}
// =============================================================================
// File System Helpers
// =============================================================================
function ensureDirSync(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}
function getGitBranch(cwd) {
    try {
        const result = execSync('git branch --show-current', {
            cwd,
            encoding: 'utf-8',
            timeout: 2000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();
        if (result)
            return result;
        const sha = execSync('git rev-parse --short HEAD', {
            cwd,
            encoding: 'utf-8',
            timeout: 2000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();
        return sha ? `@${sha}` : undefined;
    }
    catch {
        return undefined;
    }
}
/**
 * Check if a session is still alive by querying the OpenClaw gateway.
 * Falls back to returning true if gateway is unavailable.
 * Can be disabled via OPENCLAW_COORD_NO_GATEWAY_CHECK env var for testing.
 */
function isSessionAlive(sessionKey) {
    // Allow disabling gateway check for testing
    if (process.env.OPENCLAW_COORD_NO_GATEWAY_CHECK === "1") {
        return true;
    }
    try {
        const result = execSync(`openclaw sessions list --json 2>/dev/null`, {
            encoding: 'utf-8',
            timeout: 2000
        });
        const sessions = JSON.parse(result);
        return sessions.sessions?.some((s) => s.key === sessionKey) || false;
    }
    catch {
        // Fail open if gateway unavailable - better to allow work than block incorrectly
        return true;
    }
}
/**
 * Check if an agent registration is still alive.
 * Uses both TTL and gateway session check for robustness.
 */
function isAgentAlive(reg) {
    // First check TTL - fast path
    const age = Date.now() - new Date(reg.lastHeartbeat).getTime();
    if (age >= AGENT_TTL_MS) {
        return false;
    }
    // Then verify session is actually alive in gateway (unless disabled for testing)
    return isSessionAlive(reg.sessionKey);
}
// =============================================================================
// Registry Operations
// =============================================================================
export function getRegistrationPath(state, dirs) {
    return join(dirs.registry, `${state.agentName}.json`);
}
/**
 * Get all active agents (excluding self).
 * Results are cached for REGISTRY_CACHE_TTL_MS to reduce disk I/O.
 */
export function getActiveAgents(state, dirs) {
    const now = Date.now();
    const excludeName = state.agentName;
    const myCwd = process.cwd();
    const cacheKey = excludeName;
    // Return cached if valid
    if (agentsCache &&
        agentsCache.registryPath === dirs.registry &&
        now - agentsCache.timestamp < REGISTRY_CACHE_TTL_MS) {
        const cachedFiltered = agentsCache.filtered.get(cacheKey);
        if (cachedFiltered)
            return cachedFiltered;
        let filtered = agentsCache.allAgents.filter(a => a.name !== excludeName);
        agentsCache.filtered.set(cacheKey, filtered);
        return filtered;
    }
    // Read from disk
    const allAgents = [];
    if (!fs.existsSync(dirs.registry)) {
        agentsCache = { allAgents, filtered: new Map(), timestamp: now, registryPath: dirs.registry };
        return allAgents;
    }
    let files;
    try {
        files = fs.readdirSync(dirs.registry);
    }
    catch {
        return allAgents;
    }
    for (const file of files) {
        if (!file.endsWith(".json"))
            continue;
        try {
            const content = fs.readFileSync(join(dirs.registry, file), "utf-8");
            const reg = JSON.parse(content);
            // Clean up stale registrations
            if (!isAgentAlive(reg)) {
                try {
                    fs.unlinkSync(join(dirs.registry, file));
                }
                catch {
                    // Ignore cleanup errors
                }
                continue;
            }
            // Ensure all fields are present
            if (reg.session === undefined) {
                reg.session = { toolCalls: 0, tokens: 0, filesModified: [] };
            }
            if (reg.activity === undefined) {
                reg.activity = { lastActivityAt: reg.startedAt };
            }
            allAgents.push(reg);
        }
        catch {
            // Ignore malformed registrations
        }
    }
    // Cache the full list and create filtered result
    let filtered = allAgents.filter(a => a.name !== excludeName);
    const filteredMap = new Map();
    filteredMap.set(cacheKey, filtered);
    agentsCache = { allAgents, filtered: filteredMap, timestamp: now, registryPath: dirs.registry };
    return filtered;
}
/**
 * Register this agent in the coordination registry.
 */
export function register(state, dirs) {
    if (state.registered)
        return true;
    ensureDirSync(dirs.registry);
    if (!state.agentName) {
        throw new Error("Agent name is required");
    }
    if (!isValidAgentName(state.agentName)) {
        throw new Error(`Invalid agent name "${state.agentName}"`);
    }
    const regPath = getRegistrationPath(state, dirs);
    const gitBranch = getGitBranch(process.cwd());
    const now = new Date().toISOString();
    const registration = {
        name: state.agentName,
        sessionKey: state.sessionKey,
        cwd: process.cwd(),
        model: state.model,
        startedAt: now,
        gitBranch,
        spec: state.spec,
        session: { ...state.session },
        activity: { lastActivityAt: now },
        lastHeartbeat: now,
    };
    if (state.reservations.length > 0) {
        registration.reservations = state.reservations;
    }
    try {
        fs.writeFileSync(regPath, JSON.stringify(registration, null, 2));
    }
    catch (err) {
        const msg = err instanceof Error ? err.message : "unknown error";
        throw new Error(`Failed to register: ${msg}`);
    }
    state.registered = true;
    state.gitBranch = gitBranch;
    state.activity.lastActivityAt = now;
    invalidateAgentsCache();
    return true;
}
/**
 * Update agent registration with current state.
 */
export function updateRegistration(state, dirs) {
    if (!state.registered)
        return;
    const regPath = getRegistrationPath(state, dirs);
    if (!fs.existsSync(regPath))
        return;
    try {
        const reg = JSON.parse(fs.readFileSync(regPath, "utf-8"));
        reg.model = state.model;
        reg.reservations = state.reservations.length > 0 ? state.reservations : undefined;
        reg.spec = state.spec;
        reg.session = { ...state.session };
        reg.activity = { ...state.activity };
        reg.statusMessage = state.statusMessage;
        reg.lastHeartbeat = new Date().toISOString();
        fs.writeFileSync(regPath, JSON.stringify(reg, null, 2));
    }
    catch {
        // Ignore errors
    }
}
/**
 * Unregister this agent from the coordination registry.
 */
export function unregister(state, dirs) {
    if (!state.registered)
        return;
    try {
        fs.unlinkSync(getRegistrationPath(state, dirs));
    }
    catch {
        // Ignore errors
    }
    state.registered = false;
    invalidateAgentsCache();
}
// =============================================================================
// Conflict Detection
// =============================================================================
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
export function getConflictsWithOtherAgents(filePath, state, dirs) {
    const conflicts = [];
    const agents = getActiveAgents(state, dirs);
    for (const agent of agents) {
        if (!agent.reservations)
            continue;
        for (const res of agent.reservations) {
            if (pathMatchesReservation(filePath, res.pattern)) {
                conflicts.push({
                    path: filePath,
                    agent: agent.name,
                    pattern: res.pattern,
                    reason: res.reason,
                    registration: agent
                });
            }
        }
    }
    return conflicts;
}
/**
 * Add file reservations for this agent.
 *
 * @param patterns - Array of file patterns to reserve (e.g., ["src/api/", "package.json"])
 * @param reason - Optional reason for the reservation
 * @param state - Current agent state
 * @param dirs - Coordination directories
 */
export function addReservations(patterns, reason, state, dirs) {
    const now = new Date().toISOString();
    for (const pattern of patterns) {
        // Don't add duplicate patterns
        if (state.reservations.some(r => r.pattern === pattern)) {
            continue;
        }
        state.reservations.push({
            pattern,
            reason,
            since: now,
        });
    }
    updateRegistration(state, dirs);
}
/**
 * Remove file reservations for this agent.
 *
 * @param patterns - Array of file patterns to release (empty = release all)
 * @param state - Current agent state
 * @param dirs - Coordination directories
 */
export function removeReservations(patterns, state, dirs) {
    if (patterns.length === 0) {
        // Release all
        state.reservations = [];
    }
    else {
        // Release specific patterns
        state.reservations = state.reservations.filter(r => !patterns.includes(r.pattern));
    }
    updateRegistration(state, dirs);
}
//# sourceMappingURL=reservations.js.map