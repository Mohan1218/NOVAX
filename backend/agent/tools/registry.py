"""
ToolRegistry — central catalogue of all tools the agent can invoke.

Responsibilities:
  • Register / deregister tool instances
  • Look up tools by name
  • Export the full set of function schemas for the LLM
  • Dispatch a tool call by name + kwargs
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agent.tools.base import BaseTool

log = logging.getLogger(__name__)


class ToolRegistry:
    """Thread-safe registry of agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    # ── Registration ──────────────────────────────────────────────────
    def register(self, tool: BaseTool) -> None:
        """Add a tool to the registry.

        Raises
        ------
        ValueError
            If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Duplicate tool name '{tool.name}': "
                f"{self._tools[tool.name]} already registered."
            )
        self._tools[tool.name] = tool
        log.info("Registered tool: %s", tool.name)

    def deregister(self, name: str) -> None:
        """Remove a tool by name (no-op if absent)."""
        removed = self._tools.pop(name, None)
        if removed:
            log.info("Deregistered tool: %s", name)

    # ── Lookup ────────────────────────────────────────────────────────
    def get(self, name: str) -> BaseTool | None:
        """Return a registered tool by name, or *None*."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """Return sorted list of registered tool names."""
        return sorted(self._tools)

    # ── Schema export (for LLM) ───────────────────────────────────────
    def function_schemas(self) -> list[dict[str, Any]]:
        """Return OpenAI-style function schemas for every registered tool."""
        return [t.to_function_schema() for t in self._tools.values()]

    # ── Dispatch ──────────────────────────────────────────────────────
    async def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Look up a tool by *name* and execute it with *kwargs*.

        Returns
        -------
        dict  — the tool's result, or an error dict if the tool is unknown
                or raised an exception.
        """
        tool = self.get(name)
        if tool is None:
            return {
                "success": False,
                "output": f"Unknown tool '{name}'. Available: {self.list_tools()}",
            }

        try:
            log.debug("Calling tool '%s' with %s", name, kwargs)
            result = await tool.execute(**kwargs)
            log.debug("Tool '%s' returned: %s", name, _truncate(result))
            return result
        except Exception as exc:  # noqa: BLE001
            log.exception("Tool '%s' raised an exception", name)
            return {"success": False, "output": f"Tool error: {exc}"}

    # ── Dunder helpers ────────────────────────────────────────────────
    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ToolRegistry tools={self.list_tools()}>"


# ── Private helpers ───────────────────────────────────────────────────
def _truncate(obj: Any, limit: int = 200) -> str:
    """Truncate repr for logging."""
    s = repr(obj)
    return s if len(s) <= limit else s[:limit] + "…"
