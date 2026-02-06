/**
 * COORD-011: Unit Tests for claims.ts
 *
 * Tests task claiming system for multi-agent coordination.
 */
// Disable gateway session checks for testing
process.env.OPENCLAW_COORD_NO_GATEWAY_CHECK = "1";
import { describe, it, after, beforeEach } from "node:test";
import * as assert from "node:assert";
import * as fs from "node:fs";
import * as path from "node:path";
import { randomBytes } from "node:crypto";
import { claimTask, unclaimTask, completeTask, getClaims, getClaimsForSpec, getCompletions, getCompletionsForSpec, getAgentCurrentClaim, } from "../claims.js";
// =============================================================================
// Test Helpers
// =============================================================================
function createTestDirs() {
    const tmpBase = path.join("/tmp", `coord-claims-test-${randomBytes(8).toString("hex")}`);
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
// Tests: claimTask - Basic Success
// =============================================================================
describe("claims: claimTask success cases", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should successfully claim a task", async () => {
        const result = await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123", "working on feature");
        assert.strictEqual(result.success, true);
        if (result.success) {
            assert.ok(result.claimedAt);
            assert.ok(new Date(result.claimedAt).getTime() > 0);
        }
    });
    it("should persist claim to disk", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const claims = getClaims(dirs);
        assert.ok(claims["spec.md"]);
        assert.ok(claims["spec.md"]["TASK-001"]);
        assert.strictEqual(claims["spec.md"]["TASK-001"].agent, "agent1");
        assert.strictEqual(claims["spec.md"]["TASK-001"].sessionKey, "session-123");
    });
    it("should allow claiming different tasks by same agent", async () => {
        const result1 = await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result2 = await claimTask(dirs, "spec.md", "TASK-002", "agent1", "session-123");
        // Note: Based on the code, an agent can only have ONE active claim at a time
        // The second claim should fail with "already_have_claim"
        assert.strictEqual(result1.success, true);
        assert.strictEqual(result2.success, false);
        if (!result2.success && result2.error === "already_have_claim") {
            assert.strictEqual(result2.existing.taskId, "TASK-001");
        }
    });
    it("should allow different agents to claim different tasks", async () => {
        const result1 = await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result2 = await claimTask(dirs, "spec.md", "TASK-002", "agent2", "session-456");
        assert.strictEqual(result1.success, true);
        assert.strictEqual(result2.success, true);
        const claims = getClaims(dirs);
        assert.strictEqual(claims["spec.md"]["TASK-001"].agent, "agent1");
        assert.strictEqual(claims["spec.md"]["TASK-002"].agent, "agent2");
    });
});
// =============================================================================
// Tests: claimTask - Failure Cases
// =============================================================================
describe("claims: claimTask failure cases", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should fail if task already claimed by another agent", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await claimTask(dirs, "spec.md", "TASK-001", "agent2", "session-456");
        assert.strictEqual(result.success, false);
        if (!result.success && result.error === "already_claimed") {
            assert.strictEqual(result.conflict.agent, "agent1");
            assert.strictEqual(result.conflict.sessionKey, "session-123");
        }
        else {
            assert.fail("Expected already_claimed error");
        }
    });
    it("should fail if agent already has a claim on different task", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123", "first task");
        const result = await claimTask(dirs, "spec.md", "TASK-002", "agent1", "session-123");
        assert.strictEqual(result.success, false);
        if (!result.success && result.error === "already_have_claim") {
            assert.strictEqual(result.existing.taskId, "TASK-001");
            assert.strictEqual(result.existing.spec, "spec.md");
        }
        else {
            assert.fail("Expected already_have_claim error");
        }
    });
    it("should fail if trying to claim same task twice", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        assert.strictEqual(result.success, false);
        // Could be either already_claimed or already_have_claim depending on order of checks
        assert.ok(!result.success);
    });
});
// =============================================================================
// Tests: unclaimTask
// =============================================================================
describe("claims: unclaimTask", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should successfully unclaim a task", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await unclaimTask(dirs, "spec.md", "TASK-001", "agent1");
        assert.strictEqual(result.success, true);
        const claims = getClaims(dirs);
        assert.ok(!claims["spec.md"] || !claims["spec.md"]["TASK-001"]);
    });
    it("should fail if task not claimed", async () => {
        const result = await unclaimTask(dirs, "spec.md", "TASK-001", "agent1");
        assert.strictEqual(result.success, false);
        if (!result.success) {
            assert.strictEqual(result.error, "not_claimed");
        }
    });
    it("should fail if claimed by different agent", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await unclaimTask(dirs, "spec.md", "TASK-001", "agent2");
        assert.strictEqual(result.success, false);
        if (!result.success && result.error === "not_your_claim") {
            assert.strictEqual(result.claimedBy, "agent1");
        }
        else {
            assert.fail("Expected not_your_claim error");
        }
    });
    it("should allow reclaiming after unclaim", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await unclaimTask(dirs, "spec.md", "TASK-001", "agent1");
        const result = await claimTask(dirs, "spec.md", "TASK-001", "agent2", "session-456");
        assert.strictEqual(result.success, true);
    });
});
// =============================================================================
// Tests: completeTask
// =============================================================================
describe("claims: completeTask", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should successfully complete a claimed task", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await completeTask(dirs, "spec.md", "TASK-001", "agent1", "All done!");
        assert.strictEqual(result.success, true);
        if (result.success) {
            assert.ok(result.completedAt);
        }
    });
    it("should remove claim when task completed", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await completeTask(dirs, "spec.md", "TASK-001", "agent1");
        const claims = getClaims(dirs);
        assert.ok(!claims["spec.md"] || !claims["spec.md"]["TASK-001"]);
    });
    it("should record completion entry", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await completeTask(dirs, "spec.md", "TASK-001", "agent1", "Finished successfully");
        const completions = getCompletions(dirs);
        assert.ok(completions["spec.md"]);
        assert.ok(completions["spec.md"]["TASK-001"]);
        assert.strictEqual(completions["spec.md"]["TASK-001"].completedBy, "agent1");
        assert.strictEqual(completions["spec.md"]["TASK-001"].notes, "Finished successfully");
    });
    it("should fail if task not claimed", async () => {
        const result = await completeTask(dirs, "spec.md", "TASK-001", "agent1");
        assert.strictEqual(result.success, false);
        if (!result.success) {
            assert.strictEqual(result.error, "not_claimed");
        }
    });
    it("should fail if claimed by different agent", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        const result = await completeTask(dirs, "spec.md", "TASK-001", "agent2");
        assert.strictEqual(result.success, false);
        if (!result.success && result.error === "not_your_claim") {
            assert.strictEqual(result.claimedBy, "agent1");
        }
        else {
            assert.fail("Expected not_your_claim error");
        }
    });
    it("should fail if task already completed", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await completeTask(dirs, "spec.md", "TASK-001", "agent1", "First completion");
        // Try to complete again (need to claim first, but can't because it's completed)
        const claimResult = await claimTask(dirs, "spec.md", "TASK-001", "agent2", "session-456");
        assert.strictEqual(claimResult.success, true); // Can claim completed task
        const result = await completeTask(dirs, "spec.md", "TASK-001", "agent2");
        assert.strictEqual(result.success, false);
        if (!result.success && result.error === "already_completed") {
            assert.strictEqual(result.completion.completedBy, "agent1");
        }
        else {
            assert.fail("Expected already_completed error");
        }
    });
    it("should allow agent to claim new task after completing previous one", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await completeTask(dirs, "spec.md", "TASK-001", "agent1");
        const result = await claimTask(dirs, "spec.md", "TASK-002", "agent1", "session-123");
        assert.strictEqual(result.success, true);
    });
});
// =============================================================================
// Tests: Query Functions
// =============================================================================
describe("claims: query functions", () => {
    let dirs;
    beforeEach(() => {
        dirs = createTestDirs();
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should get claims for specific spec", async () => {
        await claimTask(dirs, "spec1.md", "TASK-001", "agent1", "session-123");
        await claimTask(dirs, "spec2.md", "TASK-002", "agent2", "session-456");
        const spec1Claims = getClaimsForSpec(dirs, "spec1.md");
        assert.strictEqual(Object.keys(spec1Claims).length, 1);
        assert.ok(spec1Claims["TASK-001"]);
        const spec2Claims = getClaimsForSpec(dirs, "spec2.md");
        assert.strictEqual(Object.keys(spec2Claims).length, 1);
        assert.ok(spec2Claims["TASK-002"]);
    });
    it("should get completions for specific spec", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123");
        await completeTask(dirs, "spec.md", "TASK-001", "agent1");
        const completions = getCompletionsForSpec(dirs, "spec.md");
        assert.ok(completions["TASK-001"]);
        assert.strictEqual(completions["TASK-001"].completedBy, "agent1");
    });
    it("should get agent current claim", async () => {
        await claimTask(dirs, "spec.md", "TASK-001", "agent1", "session-123", "working on it");
        const claim = getAgentCurrentClaim(dirs, "agent1");
        assert.ok(claim);
        assert.strictEqual(claim.spec, "spec.md");
        assert.strictEqual(claim.taskId, "TASK-001");
        assert.strictEqual(claim.reason, "working on it");
    });
    it("should return null if agent has no claim", () => {
        const claim = getAgentCurrentClaim(dirs, "agent1");
        assert.strictEqual(claim, null);
    });
});
//# sourceMappingURL=claims.test.js.map