"""Starter config template inspired by canvas-org/meta-agent.

Keep changes small and evidence-driven.
"""

from claude_agent_sdk import ClaudeAgentOptions
from meta_agent.run_context import RunContext


def build_options(ctx: RunContext) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            # "append": "Insert one targeted behavioral rule here.",
        },
        tools={"type": "preset", "preset": "claude_code"},
        cwd=ctx.cwd,
        model=ctx.model,
        permission_mode="bypassPermissions",
        max_turns=200,
        max_budget_usd=10.0,
        thinking={"type": "adaptive"},
    )
