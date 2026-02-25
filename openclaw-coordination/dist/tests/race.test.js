/**
 * COORD-013: Task Claiming Race Test
 *
 * Tests that concurrent claimTask calls are properly synchronized
 * and only one agent can claim a task at a time.
 */
// Disable gateway session checks for testing
process.env.OPENCLAW_COORD_NO_GATEWAY_CHECK = "1";
import { describe, it, after, beforeEach } from "node:test";
import * as assert from "node:assert";
import * as fs from "node:fs";
import * as path from "node:path";
import { randomBytes } from "node:crypto";
import { claimTask, getClaims } from "../claims.js";
// =============================================================================
// Test Helpers
// =============================================================================
function createTestDirs() {
    const tmpBase = path.join("/tmp", `coord-race-test-${randomBytes(8).toString("hex")}`);
    return {
        base: tmpBase,
        registry: path.join(tmpBase, "registry"),
        reservations: path.join(tmpBase, "reservations"),
        claims: path.join(tmpBase, "claims"),
    };
}
function cleanupDirs(dirs) {
    if (fs.existsSync(dirs.base)) {
        fs.rmSync(dirs.base, { recursive: true, force: true });
    }
}
// =============================================================================
// Race Condition Tests
// =============================================================================
describe("claims: race condition - concurrent claiming", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should allow only 1 of 5 concurrent claims to succeed", async () => {
        const specPath = "spec.md";
        const taskId = "TASK-RACE-001";
        // Spawn 5 concurrent claim attempts
        const promises = [];
        for (let i = 1; i <= 5; i++) {
            const agent = `agent${i}`;
            const sessionKey = `session-${i}`;
            promises.push(claimTask(dirs, specPath, taskId, agent, sessionKey, `Attempt ${i}`)
                .then(result => ({ ...result, agent })));
        }
        // Wait for all attempts to complete
        const results = await Promise.all(promises);
        // Exactly 1 should succeed
        const successes = results.filter(r => r.success);
        const failures = results.filter(r => !r.success);
        assert.strictEqual(successes.length, 1, "Exactly one claim should succeed");
        assert.strictEqual(failures.length, 4, "Four claims should fail");
        // All failures should be either "already_claimed" or "already_have_claim"
        for (const failure of failures) {
            assert.strictEqual(failure.success, false);
            if (!failure.success) {
                assert.ok(failure.error === "already_claimed" || failure.error === "already_have_claim", `Expected failure error to be "already_claimed" or "already_have_claim", got "${failure.error}"`);
            }
        }
        // Verify the winner is recorded in claims file
        const claims = getClaims(dirs);
        assert.ok(claims[specPath]);
        assert.ok(claims[specPath][taskId]);
        const winner = successes[0].agent;
        assert.strictEqual(claims[specPath][taskId].agent, winner);
        console.log(`✓ Race test passed: ${winner} won out of 5 concurrent attempts`);
    });
    it("should handle 10 concurrent claims with no data corruption", async () => {
        const specPath = "spec.md";
        const taskId = "TASK-RACE-002";
        // Spawn 10 concurrent claim attempts
        const promises = [];
        for (let i = 1; i <= 10; i++) {
            const agent = `agent${i}`;
            const sessionKey = `session-${i}`;
            promises.push(claimTask(dirs, specPath, taskId, agent, sessionKey)
                .then(result => ({ ...result, agent })));
        }
        const results = await Promise.all(promises);
        const successes = results.filter(r => r.success);
        assert.strictEqual(successes.length, 1, "Exactly one claim should succeed in 10-way race");
        // Verify claims file is valid JSON (no corruption)
        const claimsPath = path.join(dirs.claims, "claims.json");
        assert.ok(fs.existsSync(claimsPath), "Claims file should exist");
        const rawData = fs.readFileSync(claimsPath, "utf-8");
        let parsed;
        try {
            parsed = JSON.parse(rawData);
        }
        catch (err) {
            assert.fail(`Claims file corrupted: ${err}`);
        }
        // Verify exactly one claim exists
        assert.ok(parsed[specPath]);
        assert.strictEqual(Object.keys(parsed[specPath]).length, 1);
        assert.ok(parsed[specPath][taskId]);
        console.log(`✓ 10-way race passed: no data corruption, winner = ${successes[0].agent}`);
    });
    it("should handle concurrent claims on different tasks", async () => {
        const specPath = "spec.md";
        // 5 agents each trying to claim a different task
        const promises = [];
        for (let i = 1; i <= 5; i++) {
            const agent = `agent${i}`;
            const taskId = `TASK-${i}`;
            const sessionKey = `session-${i}`;
            promises.push(claimTask(dirs, specPath, taskId, agent, sessionKey)
                .then(result => ({ ...result, agent, taskId })));
        }
        const results = await Promise.all(promises);
        // All should succeed (different tasks, different agents)
        const successes = results.filter(r => r.success);
        assert.strictEqual(successes.length, 5, "All 5 claims on different tasks should succeed");
        // Verify all claims are recorded
        const claims = getClaims(dirs);
        assert.strictEqual(Object.keys(claims[specPath]).length, 5);
        console.log("✓ Concurrent different-task claims: all 5 succeeded");
    });
    it("should handle mixed race: same task + different tasks", async () => {
        const specPath = "spec.md";
        const sharedTask = "TASK-SHARED";
        // 3 agents compete for same task, 2 agents claim different tasks
        const promises = [
            claimTask(dirs, specPath, sharedTask, "agent1", "session-1")
                .then(r => ({ ...r, agent: "agent1", taskId: sharedTask })),
            claimTask(dirs, specPath, sharedTask, "agent2", "session-2")
                .then(r => ({ ...r, agent: "agent2", taskId: sharedTask })),
            claimTask(dirs, specPath, sharedTask, "agent3", "session-3")
                .then(r => ({ ...r, agent: "agent3", taskId: sharedTask })),
            claimTask(dirs, specPath, "TASK-UNIQUE-1", "agent4", "session-4")
                .then(r => ({ ...r, agent: "agent4", taskId: "TASK-UNIQUE-1" })),
            claimTask(dirs, specPath, "TASK-UNIQUE-2", "agent5", "session-5")
                .then(r => ({ ...r, agent: "agent5", taskId: "TASK-UNIQUE-2" })),
        ];
        const results = await Promise.all(promises);
        // Should have 3 successes total:
        // - 1 winner for shared task
        // - 2 unique task claims
        const successes = results.filter(r => r.success);
        assert.strictEqual(successes.length, 3, "Should have 3 successes (1 shared + 2 unique)");
        // Count shared task successes
        const sharedSuccesses = successes.filter(r => r.taskId === sharedTask);
        assert.strictEqual(sharedSuccesses.length, 1, "Only 1 should win the shared task");
        // Verify unique tasks succeeded
        const uniqueSuccesses = successes.filter(r => r.taskId !== sharedTask);
        assert.strictEqual(uniqueSuccesses.length, 2, "Both unique tasks should succeed");
        console.log(`✓ Mixed race: ${sharedSuccesses[0].agent} won shared task, 2 unique tasks claimed`);
    });
    it("should be stable across multiple race rounds", async () => {
        const specPath = "spec.md";
        // Run 3 rounds of racing
        for (let round = 1; round <= 3; round++) {
            const taskId = `TASK-ROUND-${round}`;
            const promises = [];
            for (let i = 1; i <= 5; i++) {
                promises.push(claimTask(dirs, specPath, taskId, `agent${i}`, `session-${i}`));
            }
            const results = await Promise.all(promises);
            const successes = results.filter(r => r.success);
            assert.strictEqual(successes.length, 1, `Round ${round}: exactly one success expected`);
        }
        // Verify all 3 tasks are claimed with no corruption
        const claims = getClaims(dirs);
        assert.strictEqual(Object.keys(claims[specPath]).length, 3);
        console.log("✓ 3 race rounds completed: no flakiness, no corruption");
    });
});
// =============================================================================
// Stress Test (Optional but recommended)
// =============================================================================
describe("claims: stress test - high concurrency", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should handle 50 concurrent claims for same task", async () => {
        const specPath = "spec.md";
        const taskId = "TASK-STRESS";
        const concurrency = 50;
        const promises = [];
        for (let i = 1; i <= concurrency; i++) {
            promises.push(claimTask(dirs, specPath, taskId, `agent${i}`, `session-${i}`));
        }
        const results = await Promise.all(promises);
        const successes = results.filter(r => r.success);
        assert.strictEqual(successes.length, 1, "Exactly one should succeed in 50-way race");
        // Verify no corruption
        const claims = getClaims(dirs);
        assert.ok(claims[specPath]);
        assert.strictEqual(Object.keys(claims[specPath]).length, 1);
        console.log(`✓ Stress test (50 concurrent): single winner, no corruption`);
    });
});
//# sourceMappingURL=race.test.js.map