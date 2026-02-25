/**
 * Unit tests for lock.ts
 * Run with: node --test tests/lock.test.ts
 */
import { test } from "node:test";
import { strict as assert } from "node:assert";
import * as fs from "node:fs";
import * as path from "node:path";
import { withSwarmLock, tryAcquireLock, releaseLock } from "../lock.js";
const TEST_DIR = path.join(process.cwd(), "test-locks");
// Cleanup helper
function cleanupTestDir() {
    if (fs.existsSync(TEST_DIR)) {
        const files = fs.readdirSync(TEST_DIR);
        for (const file of files) {
            fs.unlinkSync(path.join(TEST_DIR, file));
        }
        fs.rmdirSync(TEST_DIR);
    }
}
test("withSwarmLock serializes concurrent calls", async () => {
    cleanupTestDir();
    const results = [];
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    // Launch 3 concurrent operations that should serialize
    const promises = [
        withSwarmLock(TEST_DIR, async () => {
            results.push(1);
            await delay(50);
            results.push(1);
        }),
        withSwarmLock(TEST_DIR, async () => {
            results.push(2);
            await delay(50);
            results.push(2);
        }),
        withSwarmLock(TEST_DIR, async () => {
            results.push(3);
            await delay(50);
            results.push(3);
        }),
    ];
    await Promise.all(promises);
    // Results should be pairs: [X, X, Y, Y, Z, Z] not interleaved
    assert.equal(results.length, 6);
    assert.equal(results[0], results[1], "First operation should complete atomically");
    assert.equal(results[2], results[3], "Second operation should complete atomically");
    assert.equal(results[4], results[5], "Third operation should complete atomically");
    cleanupTestDir();
});
test("withSwarmLock cleans up stale locks", async () => {
    cleanupTestDir();
    const lockPath = path.join(TEST_DIR, "swarm.lock");
    // Ensure directory exists
    if (!fs.existsSync(TEST_DIR)) {
        fs.mkdirSync(TEST_DIR, { recursive: true });
    }
    // Create a stale lock (>10s old, with fake PID)
    fs.writeFileSync(lockPath, "99999999");
    // Wait a tiny bit to ensure it's "old" (Node may have millisecond precision)
    // Modify the mtime to be 11 seconds ago
    const oldTime = Date.now() - 11000;
    fs.utimesSync(lockPath, oldTime / 1000, oldTime / 1000);
    // This should succeed by cleaning the stale lock
    let executed = false;
    await withSwarmLock(TEST_DIR, async () => {
        executed = true;
    });
    assert.equal(executed, true, "Should execute after cleaning stale lock");
    cleanupTestDir();
});
test("withSwarmLock creates and deletes lock file", async () => {
    cleanupTestDir();
    const lockPath = path.join(TEST_DIR, "swarm.lock");
    // Lock should not exist initially
    assert.equal(fs.existsSync(lockPath), false, "Lock should not exist before");
    let lockExistedDuringExecution = false;
    await withSwarmLock(TEST_DIR, async () => {
        lockExistedDuringExecution = fs.existsSync(lockPath);
    });
    assert.equal(lockExistedDuringExecution, true, "Lock should exist during execution");
    assert.equal(fs.existsSync(lockPath), false, "Lock should be cleaned up after");
    cleanupTestDir();
});
test("tryAcquireLock returns immediately", () => {
    cleanupTestDir();
    const acquired = tryAcquireLock(TEST_DIR);
    assert.equal(acquired, true, "Should acquire lock on first attempt");
    const acquiredAgain = tryAcquireLock(TEST_DIR);
    assert.equal(acquiredAgain, false, "Should fail to acquire already-held lock");
    releaseLock(TEST_DIR);
    const acquiredAfterRelease = tryAcquireLock(TEST_DIR);
    assert.equal(acquiredAfterRelease, true, "Should acquire after release");
    releaseLock(TEST_DIR);
    cleanupTestDir();
});
test("releaseLock cleans up lock file", () => {
    cleanupTestDir();
    const lockPath = path.join(TEST_DIR, "swarm.lock");
    tryAcquireLock(TEST_DIR);
    assert.equal(fs.existsSync(lockPath), true, "Lock should exist after acquire");
    releaseLock(TEST_DIR);
    assert.equal(fs.existsSync(lockPath), false, "Lock should be removed after release");
    cleanupTestDir();
});
test("withSwarmLock handles errors and still releases lock", async () => {
    cleanupTestDir();
    const lockPath = path.join(TEST_DIR, "swarm.lock");
    try {
        await withSwarmLock(TEST_DIR, async () => {
            throw new Error("Intentional error");
        });
        assert.fail("Should have thrown error");
    }
    catch (err) {
        assert.equal(err.message, "Intentional error");
    }
    // Lock should still be cleaned up even after error
    assert.equal(fs.existsSync(lockPath), false, "Lock should be cleaned up after error");
    cleanupTestDir();
});
