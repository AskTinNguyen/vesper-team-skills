/**
 * COORD-010: Unit Tests for reservations.ts
 *
 * Tests file reservation system for multi-agent coordination.
 */
// Disable gateway session checks for testing
process.env.OPENCLAW_COORD_NO_GATEWAY_CHECK = "1";
import { describe, it, after, beforeEach } from "node:test";
import * as assert from "node:assert";
import * as fs from "node:fs";
import * as path from "node:path";
import { randomBytes } from "node:crypto";
import { addReservations, removeReservations, getConflictsWithOtherAgents, register, unregister, invalidateAgentsCache, } from "../reservations.js";
// =============================================================================
// Test Helpers
// =============================================================================
function createTestDirs() {
    const tmpBase = path.join("/tmp", `coord-test-${randomBytes(8).toString("hex")}`);
    return {
        base: tmpBase,
        registry: path.join(tmpBase, "registry"),
        reservations: path.join(tmpBase, "reservations"),
        claims: path.join(tmpBase, "claims"),
    };
}
function createTestState(name) {
    return {
        agentName: name,
        sessionKey: `session-${randomBytes(8).toString("hex")}`,
        registered: false,
        reservations: [],
        model: "test-model",
        session: { toolCalls: 0, tokens: 0, filesModified: [] },
        activity: { lastActivityAt: new Date().toISOString() },
        sessionStartedAt: new Date().toISOString(),
    };
}
function cleanupDirs(dirs) {
    if (fs.existsSync(dirs.base)) {
        fs.rmSync(dirs.base, { recursive: true, force: true });
    }
}
function createMockAgent(dirs, name, reservations) {
    const regPath = path.join(dirs.registry, `${name}.json`);
    if (!fs.existsSync(dirs.registry)) {
        fs.mkdirSync(dirs.registry, { recursive: true });
    }
    const now = new Date().toISOString();
    const agent = {
        name,
        sessionKey: `mock-${name}`,
        cwd: process.cwd(),
        model: "test-model",
        startedAt: now,
        lastHeartbeat: now,
        session: { toolCalls: 0, tokens: 0, filesModified: [] },
        activity: { lastActivityAt: now },
        reservations: reservations.map(r => ({
            pattern: r.pattern,
            reason: r.reason,
            since: now,
        })),
    };
    fs.writeFileSync(regPath, JSON.stringify(agent, null, 2));
    invalidateAgentsCache();
}
// =============================================================================
// Tests: addReservations / removeReservations
// =============================================================================
describe("reservations: addReservations / removeReservations", () => {
    let dirs;
    let state;
    beforeEach(() => {
        dirs = createTestDirs();
        state = createTestState("test-agent");
        invalidateAgentsCache(); // Clear cache before each test
        register(state, dirs);
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should add single reservation", () => {
        addReservations(["src/api/"], "testing", state, dirs);
        assert.strictEqual(state.reservations.length, 1);
        assert.strictEqual(state.reservations[0].pattern, "src/api/");
        assert.strictEqual(state.reservations[0].reason, "testing");
        assert.ok(state.reservations[0].since);
    });
    it("should add multiple reservations", () => {
        addReservations(["src/api/", "package.json", "src/utils/"], "batch", state, dirs);
        assert.strictEqual(state.reservations.length, 3);
        assert.deepStrictEqual(state.reservations.map(r => r.pattern), ["src/api/", "package.json", "src/utils/"]);
    });
    it("should not add duplicate patterns", () => {
        addReservations(["src/api/"], "first", state, dirs);
        addReservations(["src/api/"], "second", state, dirs);
        assert.strictEqual(state.reservations.length, 1);
        assert.strictEqual(state.reservations[0].reason, "first"); // Keeps first
    });
    it("should remove specific reservations", () => {
        addReservations(["src/api/", "package.json", "src/utils/"], "test", state, dirs);
        removeReservations(["package.json"], state, dirs);
        assert.strictEqual(state.reservations.length, 2);
        assert.deepStrictEqual(state.reservations.map(r => r.pattern), ["src/api/", "src/utils/"]);
    });
    it("should remove all reservations when patterns is empty", () => {
        addReservations(["src/api/", "package.json"], "test", state, dirs);
        removeReservations([], state, dirs);
        assert.strictEqual(state.reservations.length, 0);
    });
    it("should handle removing non-existent patterns", () => {
        addReservations(["src/api/"], "test", state, dirs);
        removeReservations(["does-not-exist"], state, dirs);
        assert.strictEqual(state.reservations.length, 1);
        assert.strictEqual(state.reservations[0].pattern, "src/api/");
    });
});
// =============================================================================
// Tests: getConflictsWithOtherAgents
// =============================================================================
describe("reservations: getConflictsWithOtherAgents", () => {
    let dirs;
    let state;
    beforeEach(() => {
        dirs = createTestDirs();
        state = createTestState("test-agent");
        invalidateAgentsCache(); // Clear cache before each test
        register(state, dirs);
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should detect no conflicts when no other agents", () => {
        const conflicts = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(conflicts.length, 0);
    });
    it("should detect conflict with exact file match", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "package.json", reason: "updating deps" }]);
        const conflicts = getConflictsWithOtherAgents("package.json", state, dirs);
        assert.strictEqual(conflicts.length, 1);
        assert.strictEqual(conflicts[0].agent, "agent2");
        assert.strictEqual(conflicts[0].pattern, "package.json");
        assert.strictEqual(conflicts[0].reason, "updating deps");
    });
    it("should detect conflict with folder pattern", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/", reason: "refactoring API" }]);
        const conflicts = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(conflicts.length, 1);
        assert.strictEqual(conflicts[0].agent, "agent2");
        assert.strictEqual(conflicts[0].pattern, "src/api/");
    });
    it("should not conflict with non-matching paths", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/" }]);
        const noConflict1 = getConflictsWithOtherAgents("src/utils/helper.ts", state, dirs);
        const noConflict2 = getConflictsWithOtherAgents("package.json", state, dirs);
        assert.strictEqual(noConflict1.length, 0);
        assert.strictEqual(noConflict2.length, 0);
    });
    it("should detect multiple conflicts from different agents", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/", reason: "API work" }]);
        createMockAgent(dirs, "agent3", [{ pattern: "src/api/auth.ts", reason: "auth fix" }]);
        const conflicts = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(conflicts.length, 2);
        const agentNames = conflicts.map(c => c.agent).sort();
        assert.deepStrictEqual(agentNames, ["agent2", "agent3"]);
    });
    it("should not report self as conflict", () => {
        addReservations(["src/api/"], "my work", state, dirs);
        const conflicts = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(conflicts.length, 0);
    });
});
// =============================================================================
// Tests: Pattern Matching
// =============================================================================
describe("reservations: pattern matching", () => {
    let dirs;
    let state;
    beforeEach(() => {
        dirs = createTestDirs();
        state = createTestState("test-agent");
        invalidateAgentsCache(); // Clear cache before each test
        register(state, dirs);
    });
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should match folder pattern with trailing slash", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/" }]);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/auth.ts", state, dirs).length, 1);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/user.ts", state, dirs).length, 1);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/", state, dirs).length, 1);
    });
    it("should not match folder pattern with different prefix", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/" }]);
        assert.strictEqual(getConflictsWithOtherAgents("src/utils/api.ts", state, dirs).length, 0);
        assert.strictEqual(getConflictsWithOtherAgents("src/api-v2/auth.ts", state, dirs).length, 0);
    });
    it("should match exact file path only", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/auth.ts" }]);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/auth.ts", state, dirs).length, 1);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/auth.tsx", state, dirs).length, 0);
        assert.strictEqual(getConflictsWithOtherAgents("src/api/", state, dirs).length, 0);
    });
    it("should handle nested folder patterns", () => {
        createMockAgent(dirs, "agent2", [{ pattern: "src/components/ui/" }]);
        assert.strictEqual(getConflictsWithOtherAgents("src/components/ui/Button.tsx", state, dirs).length, 1);
        assert.strictEqual(getConflictsWithOtherAgents("src/components/ui/Input.tsx", state, dirs).length, 1);
        assert.strictEqual(getConflictsWithOtherAgents("src/components/Layout.tsx", state, dirs).length, 0);
    });
    it("should differentiate between folder and file with same base name", () => {
        // Test folder pattern separately
        createMockAgent(dirs, "agent2", [{ pattern: "src/api/" }]);
        const folderConflicts = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(folderConflicts.length, 1, "Folder pattern should match file inside");
        assert.strictEqual(folderConflicts[0].agent, "agent2");
        assert.strictEqual(folderConflicts[0].pattern, "src/api/");
        // Clean up and test file pattern separately
        cleanupDirs(dirs);
        dirs = createTestDirs();
        state = createTestState("test-agent");
        invalidateAgentsCache();
        register(state, dirs);
        createMockAgent(dirs, "agent3", [{ pattern: "src/api" }]);
        const noConflict = getConflictsWithOtherAgents("src/api/auth.ts", state, dirs);
        assert.strictEqual(noConflict.length, 0, "File pattern should not match file inside folder");
        const fileConflicts = getConflictsWithOtherAgents("src/api", state, dirs);
        assert.strictEqual(fileConflicts.length, 1, "File pattern should match exact file");
        assert.strictEqual(fileConflicts[0].agent, "agent3");
        assert.strictEqual(fileConflicts[0].pattern, "src/api");
    });
});
// =============================================================================
// Tests: Agent Lifecycle
// =============================================================================
describe("reservations: agent lifecycle", () => {
    let dirs;
    after(() => {
        if (dirs)
            cleanupDirs(dirs);
    });
    it("should register and unregister agent", () => {
        dirs = createTestDirs();
        const state = createTestState("lifecycle-agent");
        assert.strictEqual(state.registered, false);
        register(state, dirs);
        assert.strictEqual(state.registered, true);
        const regPath = path.join(dirs.registry, "lifecycle-agent.json");
        assert.ok(fs.existsSync(regPath));
        unregister(state, dirs);
        assert.strictEqual(state.registered, false);
        assert.ok(!fs.existsSync(regPath));
    });
    it("should persist reservations in registration", () => {
        dirs = createTestDirs();
        const state = createTestState("persist-agent");
        register(state, dirs);
        addReservations(["src/test/"], "testing", state, dirs);
        const regPath = path.join(dirs.registry, "persist-agent.json");
        const saved = JSON.parse(fs.readFileSync(regPath, "utf-8"));
        assert.ok(Array.isArray(saved.reservations));
        assert.strictEqual(saved.reservations.length, 1);
        assert.strictEqual(saved.reservations[0].pattern, "src/test/");
    });
});
//# sourceMappingURL=reservations.test.js.map