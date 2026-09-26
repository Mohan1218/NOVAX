"""
BaseTool — abstract base class every agent tool must inherit from.

Each tool declares:
  • name          – unique identifier used by the LLM to call it
  • description   – one-liner the LLM reads to decide when to use it
  • parameters    – JSON-schema dict describing accepted arguments
  • execute()     – the actual implementation
"""

from __future__ import annotations

import abc
from typing import Any


class BaseTool(abc.ABC):
    """Interface that every agent tool implements."""

    # ── Identity ──────────────────────────────────────────────────────
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique, snake_case tool name (e.g. 'read_file')."""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Human-readable description shown to the LLM."""

    @property
    @abc.abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON-Schema dict of accepted parameters.

        Example::

            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative file path."
                    }
                },
                "required": ["path"]
            }
        """

    # ── Execution ─────────────────────────────────────────────────────
    @abc.abstractmethod
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Run the tool and return a result dict.

        Returns
        -------
        dict with at least:
            success : bool
            output  : str   – human-readable result or error message
        """

    # ── Schema export (for LLM function-calling) ─────────────────────
    def to_function_schema(self) -> dict[str, Any]:
        """Export this tool as an OpenAI-style function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tool: {self.name}>"
