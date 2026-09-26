"""
Prompt templates for the QA & Debugger Agent.

All system-level and chain-of-thought prompts live here so they can be
iterated on without touching the core loop.
"""

from __future__ import annotations

# ── System prompt ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are **NovaX**, an autonomous software QA & debugging agent.

Your mission is to analyse codebases, find bugs, run tests, and fix issues — \
all by yourself using the tools at your disposal.

## Available tools
{tool_descriptions}

## Workflow
1. **Understand** — Read relevant files, search the codebase, and understand \
   the reported issue or QA objective.
2. **Reproduce** — Write and run a minimal Python script or run the existing \
   test suite to confirm the bug / verify current behaviour.
3. **Diagnose** — Narrow down the root cause by reading code, adding debug \
   prints, and reasoning step-by-step.
4. **Fix** — Use the patch_code tool to apply a targeted fix. Prefer the \
   smallest change that solves the issue.
5. **Verify** — Re-run the tests (or your reproduction script) to confirm the \
   fix works and nothing else broke.
6. **Report** — Summarise what you found and what you changed.

## Rules
- Think step-by-step. Show your reasoning before each action.
- NEVER fabricate file contents — always read first.
- Prefer **replace** mode over **rewrite** when patching.
- If tests fail after your fix, iterate — do not give up.
- You have a maximum of {max_iterations} tool-call rounds.
- If you cannot solve the issue, clearly explain what you tried and why \
  you're stuck.

## Output format
After every tool call, briefly explain what you learned and what you'll \
do next. When you're finished, write a final summary under the heading \
"## Summary".
"""


# ── Tool description formatter ────────────────────────────────────────
def format_tool_descriptions(schemas: list[dict]) -> str:
    """Convert tool schemas into a readable list for the system prompt."""
    lines = []
    for schema in schemas:
        func = schema.get("function", schema)
        name = func.get("name", "?")
        desc = func.get("description", "")
        params = func.get("parameters", {}).get("properties", {})
        param_names = ", ".join(params.keys()) if params else "none"
        lines.append(f"• **{name}**({param_names}) — {desc}")
    return "\n".join(lines)


def build_system_prompt(
    tool_schemas: list[dict],
    max_iterations: int = 25,
) -> str:
    """Render the full system prompt with tool descriptions injected."""
    tool_desc = format_tool_descriptions(tool_schemas)
    return SYSTEM_PROMPT.format(
        tool_descriptions=tool_desc,
        max_iterations=max_iterations,
    )


# ── Task prompt ───────────────────────────────────────────────────────
TASK_PROMPT = """\
## Task
{task_description}

## Project root
{project_root}

Begin by understanding the issue. Read relevant files and reason about \
what might be wrong before taking any action.
"""


def build_task_prompt(task_description: str, project_root: str) -> str:
    """Render the task prompt template."""
    return TASK_PROMPT.format(
        task_description=task_description,
        project_root=project_root,
    )
