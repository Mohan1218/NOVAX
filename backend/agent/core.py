"""
Agent Core — the main autonomous loop.

Flow:
  1. Receive a task (bug report / QA objective)
  2. Build system prompt with tool descriptions
  3. Send to LLM
  4. If LLM requests tool calls → execute them → feed results back
  5. Repeat until LLM says "done" or max iterations reached
  6. Return the final report
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from backend.agent.config import AgentConfig
from backend.agent.llm_client import LLMClient, LLMResponse, Message
from backend.agent.prompts import build_system_prompt, build_task_prompt
from backend.agent.tools.base import BaseTool
from backend.agent.tools.registry import ToolRegistry

from backend.agent.analyzer import IssueAnalyzer, IssueReport, InputType

# ── Tools (concrete implementations) ─────────────────────────────────
from backend.agent.tools.file_reader import FileReaderTool
from backend.agent.tools.code_searcher import CodeSearcherTool
from backend.agent.tools.python_runner import PythonRunnerTool
from backend.agent.tools.test_runner import TestRunnerTool
from backend.agent.tools.code_patcher import CodePatcherTool

log = logging.getLogger(__name__)


from pathlib import Path

# ── Result object ─────────────────────────────────────────────────────
@dataclass
class AgentResult:
    """Everything the agent produced during a run."""

    task: str
    success: bool
    summary: str
    iterations: int
    history: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    report: IssueReport | None = None


# ── Agent ─────────────────────────────────────────────────────────────
class Agent:
    """Autonomous QA & Debugger Agent.

    Usage::

        config = AgentConfig()
        agent = Agent(config)
        result = await agent.run("The /api/users endpoint returns 500 on POST")
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self._cfg = config or AgentConfig()
        self._llm = LLMClient(self._cfg)
        self._registry = ToolRegistry()
        self._register_default_tools()
        self._analyzer = IssueAnalyzer(project_root=self._cfg.project_root, registry=self._registry)

    async def analyze(self, input_text: str) -> IssueReport:
        """Run the 6-step issue analysis workflow on a bug report or error log."""
        return await self._analyzer.analyze(input_text)

    # ── Tool registration ─────────────────────────────────────────────
    def _register_default_tools(self) -> None:
        """Register all built-in tools."""
        root = str(self._cfg.project_root)
        timeout = self._cfg.sandbox.timeout_seconds
        max_out = self._cfg.sandbox.max_output_bytes

        self._registry.register(FileReaderTool(project_root=root))
        self._registry.register(CodeSearcherTool(project_root=root))
        self._registry.register(PythonRunnerTool(timeout=timeout, max_output=max_out, project_root=root))
        self._registry.register(TestRunnerTool(timeout=timeout * 2, max_output=max_out, project_root=root))
        self._registry.register(CodePatcherTool(project_root=root))

        log.info("Registered %d tools: %s", len(self._registry), self._registry.list_tools())

    def register_tool(self, tool: BaseTool) -> None:
        """Register an additional custom tool."""
        self._registry.register(tool)

    def _find_test_target(self, file_path: str) -> str | None:
        """Locate test file corresponding to the target file."""
        if not file_path or file_path == "None":
            return None
        p = Path(file_path)
        root = Path(self._cfg.project_root).resolve()

        if not p.is_absolute():
            abs_p = (root / p).resolve()
        else:
            abs_p = p.resolve()

        # 1. Check same directory: test_<stem>.py
        candidate = abs_p.parent / f"test_{abs_p.name}"
        if candidate.is_file():
            try:
                return str(candidate.relative_to(root))
            except ValueError:
                return str(candidate)

        # 2. Check tests directory under project root
        candidate = root / "tests" / f"test_{abs_p.name}"
        if candidate.is_file():
            try:
                return str(candidate.relative_to(root))
            except ValueError:
                return str(candidate)

        # 3. Check for any test file matching the stem
        matches = list(root.glob(f"**/test_{abs_p.stem}.py"))
        for m in matches:
            if m.is_file():
                try:
                    return str(m.relative_to(root))
                except ValueError:
                    return str(m)

        return None

    # ── Main loop ─────────────────────────────────────────────────────
    async def run(self, task: str) -> AgentResult:
        """Execute the full agent loop for *task* and return the result."""
        log.info("Agent starting — task: %s", task[:120])

        # Build conversation
        tool_schemas = self._registry.function_schemas()
        system_prompt = build_system_prompt(tool_schemas, self._cfg.max_iterations)
        task_prompt = build_task_prompt(task, str(self._cfg.project_root))

        messages: list[Message] = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=task_prompt),
        ]
        history: list[dict[str, Any]] = []
        errors: list[str] = []

        for iteration in range(1, self._cfg.max_iterations + 1):
            log.info("── Iteration %d / %d ──", iteration, self._cfg.max_iterations)

            # ── Call LLM ──────────────────────────────────────────────
            try:
                response: LLMResponse = await self._llm.chat(messages, tools=tool_schemas)
            except Exception as exc:
                log.warning("LLM call unavailable at iteration %d: %s", iteration, exc)
                errors.append(f"LLM error (iter {iteration}): {exc}")
                break

            # Record assistant message
            assistant_msg_data: dict[str, Any] = {
                "iteration": iteration,
                "role": "assistant",
                "content": response.content,
                "tool_calls": response.tool_calls,
                "usage": response.usage,
            }
            history.append(assistant_msg_data)

            # ── No tool calls → agent is done ─────────────────────────
            if not response.has_tool_calls:
                log.info("Agent finished (no more tool calls).")
                messages.append(Message(role="assistant", content=response.content))
                break

            # ── Process tool calls ────────────────────────────────────
            # Add assistant message with tool_calls to conversation
            messages.append(Message(
                role="assistant",
                content=response.content,
                tool_calls=_format_tool_calls_for_message(response.tool_calls),
            ))

            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("arguments", {})
                call_id = tc.get("id", str(uuid.uuid4()))

                log.info("  → Tool call: %s(%s)", tool_name, _trunc(tool_args))

                result = await self._registry.call(tool_name, **tool_args)

                tool_result_data = {
                    "iteration": iteration,
                    "role": "tool",
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": result,
                }
                history.append(tool_result_data)

                # Feed result back to conversation
                messages.append(Message(
                    role="tool",
                    content=json.dumps(result, default=str),
                    tool_call_id=call_id,
                    name=tool_name,
                ))

        else:
            log.warning("Agent hit max iterations (%d).", self._cfg.max_iterations)
            errors.append(f"Reached max iterations ({self._cfg.max_iterations}).")

        # ── Build result & autonomous verification ────────────────────
        final_content = messages[-1].content if messages else ""
        has_patch = any(h.get("tool") == "patch_code" for h in history)
        report: IssueReport | None = None

        if not final_content or errors or not has_patch:
            # Autonomous execution: diagnose, patch, test, and verify
            report = await self._analyzer.analyze(task)
            errors.clear()

            if report.status == "Bug identified":
                patch_applied = False
                patch_diff = ""
                patch_info = report.details.get("patch")

                # Step 5: Call patch_code
                if patch_info and "old_text" in patch_info and "new_text" in patch_info:
                    patch_file = patch_info.get("file", report.file_path)
                    patch_line = patch_info.get("line_number")  # may be None
                    log.info("Agent applying autonomous patch to %s (line %s)...", patch_file, patch_line)
                    patch_kwargs: dict = {
                        "path": patch_file,
                        "mode": "replace",
                        "old_text": patch_info["old_text"],
                        "new_text": patch_info["new_text"],
                    }
                    if patch_line is not None:
                        patch_kwargs["line_number"] = patch_line
                    patch_res = await self._registry.call("patch_code", **patch_kwargs)
                    history.append({
                        "iteration": len(history) + 1,
                        "role": "tool",
                        "tool": "patch_code",
                        "arguments": patch_kwargs,
                        "result": patch_res,
                    })
                    patch_applied = patch_res.get("success", False)
                    patch_diff = patch_res.get("diff", "")

                # Step 6: Run Test
                test_target = self._find_test_target(report.file_path)
                test_kwargs = {"target": test_target} if test_target else {}
                log.info("Agent executing tests with target: %s...", test_target)
                test_res = await self._registry.call("run_tests", **test_kwargs)
                history.append({
                    "iteration": len(history) + 1,
                    "role": "tool",
                    "tool": "run_tests",
                    "arguments": test_kwargs,
                    "result": test_res,
                })
                tests_passed = test_res.get("success", False)
                test_output = test_res.get("output", "").strip()

                # Step 7: Check Test Result & Verify Fix
                if tests_passed:
                    verif_status = "VERIFIED ✅ — Fix verified with tests passing!"
                else:
                    verif_status = f"FAILED ❌ — Tests still failing after patch.\nOutput:\n{test_output}"

                # Step 8: Build Final Report
                final_content = (
                    f"## Summary\n\n"
                    f"STATUS:\nBug identified and fixed\n\n"
                    f"BUG:\n{report.bug}\n\n"
                    f"ROOT CAUSE:\n{report.root_cause}\n\n"
                    f"FILE:\n{report.file_path}\n\n"
                    f"PROPOSED FIX:\n{report.proposed_fix}\n\n"
                    f"FIX APPLIED:\n"
                    f"{'Patch applied successfully' if patch_applied else 'Failed to apply patch'}\n"
                    f"Diff:\n{patch_diff}\n\n"
                    f"TEST RESULT:\n{test_output}\n\n"
                    f"VERIFICATION:\n{verif_status}"
                )
                success = patch_applied and tests_passed
            else:
                final_content = report.render()
                success = False
        else:
            success = not errors and ("## Summary" in final_content or "STATUS:\nBug identified" in final_content)

        return AgentResult(
            task=task,
            success=success,
            summary=final_content,
            iterations=len([h for h in history if h.get("role") in ("assistant", "tool")]),
            history=history,
            errors=errors,
            report=report,
        )

    # ── Convenience ───────────────────────────────────────────────────
    @property
    def tools(self) -> ToolRegistry:
        """Access the tool registry (e.g. for listing registered tools)."""
        return self._registry


# ── Private helpers ───────────────────────────────────────────────────
def _format_tool_calls_for_message(
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Format tool calls for inclusion in a Message (OpenAI-style)."""
    return [
        {
            "id": tc.get("id", str(uuid.uuid4())),
            "type": "function",
            "function": {
                "name": tc["name"],
                "arguments": json.dumps(tc.get("arguments", {})),
            },
        }
        for tc in tool_calls
    ]


def _trunc(obj: Any, limit: int = 100) -> str:
    s = json.dumps(obj, default=str)
    return s if len(s) <= limit else s[:limit] + "…"
