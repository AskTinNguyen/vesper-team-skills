#!/usr/bin/env node
/**
 * CLI for OpenClaw Coordination Extension
 *
 * Usage:
 *   coord reserve --patterns "src/api/" --agent "coder" --reason "work"
 *   coord release --patterns "src/api/" --agent "coder"
 *   coord mesh
 *   coord conflicts --file "src/api/auth.ts"
 */
import { parseArgs } from "node:util";
import { homedir } from "node:os";
import { join } from "node:path";
import { register, unregister, getActiveAgents, getConflictsWithOtherAgents, addReservations, removeReservations, } from "./reservations.js";
const VERSION = "0.1.0";
// Default coordination directory
const DEFAULT_COORD_DIR = join(homedir(), ".openclaw", "coordination");
function getDirs() {
    const base = process.env.OPENCLAW_COORD_DIR || DEFAULT_COORD_DIR;
    return {
        base,
        registry: join(base, "registry"),
        reservations: join(base, "reservations"),
        claims: join(base, "claims"),
    };
}
function createState(agentName) {
    const now = new Date().toISOString();
    const session = { toolCalls: 0, tokens: 0, filesModified: [] };
    const activity = { lastActivityAt: now };
    return {
        agentName,
        sessionKey: `cli:${agentName}:${Date.now()}`,
        registered: false,
        reservations: [],
        model: "cli",
        session,
        activity,
        sessionStartedAt: now,
    };
}
function json(data) {
    console.log(JSON.stringify(data, null, 2));
}
function showHelp() {
    console.log(`coord v${VERSION} - Multi-agent file coordination

Usage:
  coord <command> [options]

Commands:
  reserve     Reserve file patterns for an agent
  release     Release file patterns from an agent
  mesh        Show all active agents and reservations
  conflicts   Check if a file conflicts with any reservation

Options:
  --help, -h      Show this help
  --version, -v   Show version

Examples:
  coord reserve --patterns "src/api/,package.json" --agent "coder" --reason "auth work"
  coord release --patterns "src/api/" --agent "coder"
  coord mesh
  coord conflicts --file "src/api/auth.ts"
`);
}
async function cmdReserve(args) {
    const { values } = parseArgs({
        args,
        options: {
            patterns: { type: "string" },
            agent: { type: "string" },
            reason: { type: "string", default: "" },
        },
        strict: true,
    });
    if (!values.patterns || !values.agent) {
        json({ success: false, error: "Missing required: --patterns and --agent" });
        process.exit(1);
    }
    const dirs = getDirs();
    const state = createState(values.agent);
    const patternArray = values.patterns.split(",").map(p => p.trim()).filter(Boolean);
    try {
        // Register the agent
        register(state, dirs);
        // Check for conflicts first
        const conflicts = [];
        for (const pattern of patternArray) {
            const patternConflicts = getConflictsWithOtherAgents(pattern, state, dirs);
            for (const c of patternConflicts) {
                conflicts.push({ agent: c.agent, pattern: c.pattern, file: pattern });
            }
        }
        if (conflicts.length > 0) {
            json({
                success: false,
                error: "Conflicts detected",
                conflicts,
            });
            process.exit(1);
        }
        // Add reservations
        addReservations(patternArray, values.reason || undefined, state, dirs);
        json({
            success: true,
            agent: values.agent,
            reserved: patternArray,
            reason: values.reason || undefined,
        });
    }
    catch (err) {
        json({
            success: false,
            error: err instanceof Error ? err.message : String(err),
        });
        process.exit(1);
    }
}
async function cmdRelease(args) {
    const { values } = parseArgs({
        args,
        options: {
            patterns: { type: "string" },
            agent: { type: "string" },
        },
        strict: true,
    });
    if (!values.patterns || !values.agent) {
        json({ success: false, error: "Missing required: --patterns and --agent" });
        process.exit(1);
    }
    const dirs = getDirs();
    const state = createState(values.agent);
    const patternArray = values.patterns.split(",").map(p => p.trim()).filter(Boolean);
    try {
        // We need to read existing registration if any
        state.registered = true; // Assume registered to allow update
        removeReservations(patternArray, state, dirs);
        // If no reservations left, unregister
        if (state.reservations.length === 0) {
            unregister(state, dirs);
        }
        json({
            success: true,
            agent: values.agent,
            released: patternArray,
        });
    }
    catch (err) {
        json({
            success: false,
            error: err instanceof Error ? err.message : String(err),
        });
        process.exit(1);
    }
}
async function cmdMesh() {
    const dirs = getDirs();
    // Use a dummy state to query active agents
    const state = createState("__mesh_query__");
    try {
        const agents = getActiveAgents(state, dirs);
        const output = agents.map(agent => ({
            name: agent.name,
            sessionKey: agent.sessionKey,
            cwd: agent.cwd,
            model: agent.model,
            startedAt: agent.startedAt,
            lastHeartbeat: agent.lastHeartbeat,
            reservations: agent.reservations || [],
            gitBranch: agent.gitBranch,
            statusMessage: agent.statusMessage,
        }));
        json({
            agents: output,
            count: output.length,
        });
    }
    catch (err) {
        json({
            success: false,
            error: err instanceof Error ? err.message : String(err),
        });
        process.exit(1);
    }
}
async function cmdConflicts(args) {
    const { values } = parseArgs({
        args,
        options: {
            file: { type: "string" },
        },
        strict: true,
    });
    if (!values.file) {
        json({ success: false, error: "Missing required: --file" });
        process.exit(1);
    }
    const dirs = getDirs();
    // Use a check agent that won't conflict with anything
    const state = createState("__conflict_check__");
    try {
        const conflicts = getConflictsWithOtherAgents(values.file, state, dirs);
        const output = conflicts.map(c => ({
            agent: c.agent,
            pattern: c.pattern,
            reason: c.reason,
        }));
        json({
            file: values.file,
            hasConflict: conflicts.length > 0,
            conflicts: output,
        });
        process.exit(conflicts.length > 0 ? 1 : 0);
    }
    catch (err) {
        json({
            success: false,
            error: err instanceof Error ? err.message : String(err),
        });
        process.exit(1);
    }
}
async function main() {
    const args = process.argv.slice(2);
    if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
        showHelp();
        process.exit(0);
    }
    if (args.includes("--version") || args.includes("-v")) {
        console.log(VERSION);
        process.exit(0);
    }
    const command = args[0];
    const cmdArgs = args.slice(1);
    switch (command) {
        case "reserve":
            await cmdReserve(cmdArgs);
            break;
        case "release":
            await cmdRelease(cmdArgs);
            break;
        case "mesh":
            await cmdMesh();
            break;
        case "conflicts":
            await cmdConflicts(cmdArgs);
            break;
        default:
            json({ error: `Unknown command: ${command}` });
            showHelp();
            process.exit(1);
    }
}
main().catch(err => {
    json({
        success: false,
        error: err instanceof Error ? err.message : String(err),
    });
    process.exit(1);
});
//# sourceMappingURL=cli.js.map