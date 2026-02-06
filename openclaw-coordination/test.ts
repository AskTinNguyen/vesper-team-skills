/**
 * Basic smoke tests for coordination extension
 */

import * as fs from "node:fs";
import * as os from "node:os";
import { join } from "node:path";
import {
  type CoordinationState,
  type Dirs,
  register,
  unregister,
  addReservations,
  removeReservations,
  getConflictsWithOtherAgents,
  claimTask,
  unclaimTask,
  completeTask,
  getAgentCurrentClaim,
  getClaims,
  getCompletions,
} from "./index.js";

// Create temp test directory
const testDir = fs.mkdtempSync(join(os.tmpdir(), "coord-test-"));
console.log(`Test directory: ${testDir}`);

const dirs: Dirs = {
  base: testDir,
  registry: join(testDir, "registry"),
  reservations: join(testDir, "reservations"),
  claims: join(testDir, "claims"),
};

const state1: CoordinationState = {
  agentName: "agent1",
  sessionKey: "session-1",
  registered: false,
  reservations: [],
  model: "test-model",
  session: { toolCalls: 0, tokens: 0, filesModified: [] },
  activity: { lastActivityAt: new Date().toISOString() },
  sessionStartedAt: new Date().toISOString(),
};

const state2: CoordinationState = {
  agentName: "agent2",
  sessionKey: "session-2",
  registered: false,
  reservations: [],
  model: "test-model",
  session: { toolCalls: 0, tokens: 0, filesModified: [] },
  activity: { lastActivityAt: new Date().toISOString() },
  sessionStartedAt: new Date().toISOString(),
};

async function runTests() {
  console.log("\n=== Test 1: Registration ===");
  register(state1, dirs);
  console.log("✓ Agent1 registered");
  
  register(state2, dirs);
  console.log("✓ Agent2 registered");

  console.log("\n=== Test 2: File Reservations ===");
  addReservations(["src/api/", "package.json"], "Working on API", state1, dirs);
  console.log("✓ Agent1 reserved src/api/ and package.json");

  const conflicts = getConflictsWithOtherAgents("src/api/users.ts", state2, dirs);
  if (conflicts.length > 0) {
    console.log(`✓ Conflict detected: ${conflicts[0].agent} has reserved ${conflicts[0].pattern}`);
  } else {
    throw new Error("Expected conflict but found none");
  }

  const noConflict = getConflictsWithOtherAgents("src/lib/utils.ts", state2, dirs);
  if (noConflict.length === 0) {
    console.log("✓ No conflict for src/lib/utils.ts");
  } else {
    throw new Error("Unexpected conflict");
  }

  console.log("\n=== Test 3: Task Claiming ===");
  const claim1 = await claimTask(dirs, "plan.json", "task-1", "agent1", "session-1", "Starting task 1");
  if (claim1.success) {
    console.log(`✓ Agent1 claimed task-1 at ${claim1.claimedAt}`);
  } else {
    throw new Error("Failed to claim task-1");
  }

  const claim2 = await claimTask(dirs, "plan.json", "task-1", "agent2", "session-2", "Also want task 1");
  if (!claim2.success && claim2.error === "already_claimed") {
    console.log(`✓ Agent2 blocked from claiming task-1 (claimed by ${claim2.conflict.agent})`);
  } else {
    throw new Error("Expected claim to fail but succeeded");
  }

  const currentClaim = getAgentCurrentClaim(dirs, "agent1");
  if (currentClaim?.taskId === "task-1") {
    console.log(`✓ Agent1 current claim: ${currentClaim.taskId}`);
  } else {
    throw new Error("Expected agent1 to have task-1 claimed");
  }

  console.log("\n=== Test 4: Task Completion ===");
  const complete = await completeTask(dirs, "plan.json", "task-1", "agent1", "Task completed successfully");
  if (complete.success) {
    console.log(`✓ Agent1 completed task-1 at ${complete.completedAt}`);
  } else {
    throw new Error("Failed to complete task-1");
  }

  const completions = getCompletions(dirs);
  if (completions["plan.json"]?.["task-1"]) {
    console.log(`✓ Task-1 completion recorded`);
  } else {
    throw new Error("Completion not recorded");
  }

  const claims = getClaims(dirs);
  if (!claims["plan.json"]?.["task-1"]) {
    console.log("✓ Task-1 claim removed after completion");
  } else {
    throw new Error("Claim should have been removed");
  }

  console.log("\n=== Test 5: Cleanup ===");
  removeReservations([], state1, dirs);
  console.log("✓ Agent1 released all reservations");

  unregister(state1, dirs);
  console.log("✓ Agent1 unregistered");
  
  unregister(state2, dirs);
  console.log("✓ Agent2 unregistered");

  console.log("\n=== All Tests Passed! ===\n");

  // Cleanup test directory
  fs.rmSync(testDir, { recursive: true, force: true });
  console.log(`Cleaned up test directory: ${testDir}`);
}

runTests().catch(err => {
  console.error("\n❌ Test failed:", err);
  process.exit(1);
});
