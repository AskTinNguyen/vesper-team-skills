/**
 * Swarm Lock - File-based mutex for multi-agent coordination
 * Ported from pi-messenger/store.ts
 */
import * as fs from "node:fs";
import { join } from "node:path";
const LOCK_STALE_MS = 10_000; // 10 seconds
/**
 * Check if a process is still alive.
 */
function isProcessAlive(pid) {
    try {
        process.kill(pid, 0);
        return true;
    }
    catch {
        return false;
    }
}
/**
 * Execute a function while holding an exclusive lock.
 * Uses file-based locking with PID for stale lock detection.
 *
 * @param baseDir - Directory to place the lock file
 * @param fn - Function to execute under lock
 * @returns Result of fn()
 */
export async function withSwarmLock(baseDir, fn) {
    const lockPath = join(baseDir, "swarm.lock");
    const maxRetries = 50;
    const retryDelay = 100;
    // Ensure base directory exists
    if (!fs.existsSync(baseDir)) {
        fs.mkdirSync(baseDir, { recursive: true });
    }
    for (let i = 0; i < maxRetries; i++) {
        // Check for stale lock
        try {
            const stat = fs.statSync(lockPath);
            const ageMs = Date.now() - stat.mtimeMs;
            if (ageMs > LOCK_STALE_MS) {
                try {
                    const pidStr = fs.readFileSync(lockPath, "utf-8").trim();
                    const pid = parseInt(pidStr, 10);
                    if (!pid || !isProcessAlive(pid)) {
                        fs.unlinkSync(lockPath);
                    }
                }
                catch {
                    try {
                        fs.unlinkSync(lockPath);
                    }
                    catch {
                        // Ignore
                    }
                }
            }
        }
        catch {
            // Lock doesn't exist - good
        }
        // Try to acquire lock
        try {
            const fd = fs.openSync(lockPath, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_RDWR);
            fs.writeSync(fd, String(process.pid));
            fs.closeSync(fd);
            break; // Lock acquired!
        }
        catch (err) {
            const code = err.code;
            if (code === "EEXIST") {
                if (i === maxRetries - 1) {
                    throw new Error("Failed to acquire swarm lock after " + maxRetries + " retries");
                }
                await new Promise(resolve => setTimeout(resolve, retryDelay));
                continue;
            }
            throw err;
        }
    }
    // Execute under lock
    try {
        return await fn();
    }
    finally {
        // Release lock
        try {
            fs.unlinkSync(lockPath);
        }
        catch {
            // Ignore - might already be cleaned up
        }
    }
}
/**
 * Try to acquire lock without waiting.
 * Returns true if lock was acquired, false otherwise.
 */
export function tryAcquireLock(baseDir) {
    const lockPath = join(baseDir, "swarm.lock");
    if (!fs.existsSync(baseDir)) {
        fs.mkdirSync(baseDir, { recursive: true });
    }
    // Clean stale lock
    try {
        const stat = fs.statSync(lockPath);
        const ageMs = Date.now() - stat.mtimeMs;
        if (ageMs > LOCK_STALE_MS) {
            const pidStr = fs.readFileSync(lockPath, "utf-8").trim();
            const pid = parseInt(pidStr, 10);
            if (!pid || !isProcessAlive(pid)) {
                fs.unlinkSync(lockPath);
            }
        }
    }
    catch {
        // No lock exists
    }
    try {
        const fd = fs.openSync(lockPath, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_RDWR);
        fs.writeSync(fd, String(process.pid));
        fs.closeSync(fd);
        return true;
    }
    catch {
        return false;
    }
}
/**
 * Release a lock acquired with tryAcquireLock.
 */
export function releaseLock(baseDir) {
    const lockPath = join(baseDir, "swarm.lock");
    try {
        fs.unlinkSync(lockPath);
    }
    catch {
        // Ignore
    }
}
