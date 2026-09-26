"""
CodeSearcherTool — search a codebase by keyword, regex, or glob.

Supports:
  • Literal string search (default)
  • Regex search
  • File-type filtering (e.g. "*.py")
  • Case-insensitive mode
  • Context lines around each match
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Any

from backend.agent.tools.base import BaseTool


class CodeSearcherTool(BaseTool):
    """Search across files in the project for a pattern."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    # ── Identity ──────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return "search_code"

    @property
    def description(self) -> str:
        return (
            "Search files in the project for a text pattern or regex. "
            "Returns matching lines with file paths and line numbers."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search string or regex pattern.",
                },
                "is_regex": {
                    "type": "boolean",
                    "description": "Treat query as a regex pattern. Default false.",
                },
                "case_insensitive": {
                    "type": "boolean",
                    "description": "Ignore case. Default false.",
                },
                "file_glob": {
                    "type": "string",
                    "description": "Glob to filter files, e.g. '*.py'. Default: all text files.",
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Number of lines of context around each match. Default 2.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of matches to return. Default 50.",
                },
            },
            "required": ["query"],
        }

    # ── Execution ─────────────────────────────────────────────────────
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        query: str = kwargs["query"]
        is_regex: bool = kwargs.get("is_regex", False)
        case_insensitive: bool = kwargs.get("case_insensitive", False)
        file_glob: str | None = kwargs.get("file_glob")
        context_lines: int = kwargs.get("context_lines", 2)
        max_results: int = kwargs.get("max_results", 50)

        # Compile pattern
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            pattern = re.compile(query if is_regex else re.escape(query), flags)
        except re.error as exc:
            return {"success": False, "output": f"Invalid regex: {exc}"}

        matches: list[dict[str, Any]] = []

        for filepath in _walk_text_files(self._root, file_glob):
            try:
                text = filepath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            lines = text.splitlines()
            for line_no, line in enumerate(lines, start=1):
                if pattern.search(line):
                    # Gather context
                    ctx_start = max(line_no - 1 - context_lines, 0)
                    ctx_end = min(line_no + context_lines, len(lines))
                    context_block = "\n".join(
                        f"{i + 1:>6} | {lines[i]}"
                        for i in range(ctx_start, ctx_end)
                    )

                    rel_path = filepath.relative_to(self._root)
                    matches.append({
                        "file": str(rel_path),
                        "line": line_no,
                        "match": line.strip(),
                        "context": context_block,
                    })

                    if len(matches) >= max_results:
                        break

            if len(matches) >= max_results:
                break

        if not matches:
            return {"success": True, "output": "No matches found.", "matches": []}

        # Build readable summary
        summary_parts = [f"Found {len(matches)} match(es):\n"]
        for m in matches:
            summary_parts.append(
                f"── {m['file']}:{m['line']} ──\n{m['context']}\n"
            )

        return {
            "success": True,
            "output": "\n".join(summary_parts),
            "matches": matches,
            "total": len(matches),
            "capped": len(matches) >= max_results,
        }


# ── Helpers ───────────────────────────────────────────────────────────
_SKIP_DIRS = frozenset({
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".eggs", "*.egg-info",
})


def _walk_text_files(root: Path, glob_pattern: str | None) -> list[Path]:
    """Recursively yield text files, skipping VCS / build directories."""
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIRS and not d.endswith(".egg-info")
        ]

        for fname in filenames:
            if glob_pattern and not fnmatch.fnmatch(fname, glob_pattern):
                continue
            fp = Path(dirpath) / fname
            # Quick binary check — skip files with null bytes in first 512 B
            try:
                head = fp.read_bytes()[:512]
                if b"\x00" in head:
                    continue
            except OSError:
                continue
            results.append(fp)

    return results
