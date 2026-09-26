"""
FileReaderTool — reads the contents of a file on disk.

Supports:
  • Full file reads
  • Line-range reads (start_line / end_line)
  • Automatic encoding detection (UTF-8 with fallback)
  • Binary file guard (rejects non-text files)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from backend.agent.tools.base import BaseTool


class FileReaderTool(BaseTool):
    """Read a source file and return its contents."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    # ── Identity ──────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Read the contents of a file. Optionally specify start_line and "
            "end_line to read a specific range of lines (1-indexed, inclusive)."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or project-relative file path.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "First line to read (1-indexed). Omit for full file.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Last line to read (1-indexed, inclusive). Omit for full file.",
                },
            },
            "required": ["path"],
        }

    # ── Execution ─────────────────────────────────────────────────────
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        raw_path: str = kwargs["path"]
        start: int | None = kwargs.get("start_line")
        end: int | None = kwargs.get("end_line")

        # Resolve against project root
        target = Path(raw_path)
        if not target.is_absolute():
            target = self._root / target
        target = target.resolve()

        # ── Safety checks ─────────────────────────────────────────────
        if not target.exists():
            return {"success": False, "output": f"File not found: {target}"}

        if not target.is_file():
            return {"success": False, "output": f"Not a file: {target}"}

        if _is_binary(target):
            return {"success": False, "output": f"Binary file, cannot read: {target}"}

        # ── Read ──────────────────────────────────────────────────────
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return {"success": False, "output": f"Read error: {exc}"}

        lines = text.splitlines(keepends=True)
        total = len(lines)

        # Apply line range
        if start is not None or end is not None:
            s = max((start or 1) - 1, 0)
            e = min(end or total, total)
            lines = lines[s:e]
            range_info = f" (lines {s + 1}–{e} of {total})"
        else:
            range_info = f" ({total} lines)"

        content = "".join(lines)

        # Truncate huge files to avoid flooding the LLM context
        max_chars = 80_000
        truncated = False
        if len(content) > max_chars:
            content = content[:max_chars]
            truncated = True

        return {
            "success": True,
            "output": content,
            "path": str(target),
            "total_lines": total,
            "range": range_info,
            "truncated": truncated,
        }


# ── Helpers ───────────────────────────────────────────────────────────
_BINARY_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".pyc", ".pyd", ".class", ".jar",
    ".woff", ".woff2", ".ttf", ".eot",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".sqlite", ".db",
})


def _is_binary(path: Path) -> bool:
    """Heuristic: check extension, then sniff first 8 KB for null bytes."""
    if path.suffix.lower() in _BINARY_EXTENSIONS:
        return True
    try:
        chunk = path.read_bytes()[:8192]
        return b"\x00" in chunk
    except OSError:
        return False
