/**
 * Swarm Lock - File-based mutex for multi-agent coordination
 * Ported from pi-messenger/store.ts
 */
/**
 * Execute a function while holding an exclusive lock.
 * Uses file-based locking with PID for stale lock detection.
 *
 * @param baseDir - Directory to place the lock file
 * @param fn - Function to execute under lock
 * @returns Result of fn()
 */
export declare function withSwarmLock<T>(baseDir: string, fn: () => T | Promise<T>): Promise<T>;
/**
 * Try to acquire lock without waiting.
 * Returns true if lock was acquired, false otherwise.
 */
export declare function tryAcquireLock(baseDir: string): boolean;
/**
 * Release a lock acquired with tryAcquireLock.
 */
export declare function releaseLock(baseDir: string): void;
//# sourceMappingURL=lock.d.ts.map