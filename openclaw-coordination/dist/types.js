/**
 * OpenClaw Coordination - Types
 * Ported from pi-messenger (lib.ts)
 */
// =============================================================================
// Pure Utilities (Ported from pi-messenger)
// =============================================================================
/**
 * Check if file path matches a reservation pattern.
 * - Patterns ending with "/" match directory prefixes
 * - Otherwise exact match
 */
export function pathMatchesReservation(filePath, pattern) {
    if (pattern.endsWith("/")) {
        return filePath.startsWith(pattern) || filePath + "/" === pattern;
    }
    return filePath === pattern;
}
/**
 * Validate agent name format.
 * Must be 1-50 chars, alphanumeric + underscore/hyphen, not starting with hyphen.
 */
export function isValidAgentName(name) {
    if (!name || name.length > 50)
        return false;
    return /^[a-zA-Z0-9_][a-zA-Z0-9_-]*$/.test(name);
}
/**
 * Format relative time from ISO timestamp.
 */
export function formatRelativeTime(timestamp) {
    const diff = Date.now() - new Date(timestamp).getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    if (hours > 0)
        return `${hours}h ago`;
    if (minutes > 0)
        return `${minutes}m ago`;
    return "just now";
}
/**
 * Format duration in human-readable form.
 */
export function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    if (hours > 0)
        return `${hours}h ${minutes % 60}m`;
    if (minutes > 0)
        return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
}
//# sourceMappingURL=types.js.map