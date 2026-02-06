#!/usr/bin/env npx ts-node --esm
/**
 * coord - CLI for multi-agent coordination
 *
 * Usage:
 *   coord reserve --patterns "src/api/" --agent "coder" --reason "work"
 *   coord release --patterns "src/api/" --agent "coder"
 *   coord mesh
 *   coord conflicts --file "src/api/auth.ts"
 */
import { parseArgs } from "node:util";
import { addReservations, removeReservations, getActiveAgents, getConflictsWithOtherAgents, } from "../dist/reservations.js";
const VERSION = "0.1.0";
function printHelp() {
    console.log(`coord v${VERSION} - Multi-agent file coordination

Commands:
  reserve     Reserve file patterns for an agent
  release     Release file patterns from an agent
  mesh        Show all active agents and reservations
  conflicts   Check if a file conflicts with any reservation

Options:
  --help, -h      Show this help
  --version, -v   Show version

Examples:
  coord reserve --patterns "src/api/" --agent "coder" --reason "working on auth"
  coord release --patterns "src/api/" --agent "coder"
  coord mesh
  coord conflicts --file "src/api/auth.ts"
`);
}
function json(data) {
    console.log(JSON.stringify(data, null, 2));
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
        json({ error: "Missing required: --patterns and --agent" });
        process.exit(1);
    }
    // Parse patterns (comma or space separated)
    const patterns = values.patterns.split(/[,\s]+/).filter(Boolean);
    try {
        const result = await addReservations(values.agent, patterns, values.reason || undefined);
        json({
            success: result.success,
            agent: values.agent,
            patterns,
            conflicts: result.conflicts || [],
        });
        process.exit(result.success ? 0 : 1);
    }
    catch (err) {
        json({ error: String(err) });
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
        json({ error: "Missing required: --patterns and --agent" });
        process.exit(1);
    }
    const patterns = values.patterns.split(/[,\s]+/).filter(Boolean);
    try {
        await removeReservations(values.agent, patterns);
        json({
            success: true,
            agent: values.agent,
            released: patterns,
        });
    }
    catch (err) {
        json({ error: String(err) });
        process.exit(1);
    }
}
async function cmdMesh() {
    try {
        const agents = await getActiveAgents();
        json({
            agents: agents.map(a => ({
                id: a.id,
                name: a.name,
                reservations: a.reservations,
                status: a.status,
                registeredAt: a.registeredAt,
            })),
            count: agents.length,
        });
    }
    catch (err) {
        json({ error: String(err) });
        process.exit(1);
    }
}
async function cmdConflicts(args) {
    const { values } = parseArgs({
        args,
        options: {
            file: { type: "string" },
            agent: { type: "string", default: "__check__" },
        },
        strict: true,
    });
    if (!values.file) {
        json({ error: "Missing required: --file" });
        process.exit(1);
    }
    try {
        const conflicts = await getConflictsWithOtherAgents(values.agent, [values.file]);
        json({
            file: values.file,
            hasConflict: conflicts.length > 0,
            conflicts: conflicts.map(c => ({
                agent: c.agentId,
                pattern: c.pattern,
                reason: c.reason,
            })),
        });
        process.exit(conflicts.length > 0 ? 1 : 0);
    }
    catch (err) {
        json({ error: String(err) });
        process.exit(1);
    }
}
async function main() {
    const args = process.argv.slice(2);
    if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
        printHelp();
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
            printHelp();
            process.exit(1);
    }
}
main().catch(err => {
    json({ error: String(err) });
    process.exit(1);
});
//# sourceMappingURL=coord.js.map