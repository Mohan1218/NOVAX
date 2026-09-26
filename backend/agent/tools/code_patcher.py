"""
CodePatcherTool — apply code changes to files.

Three modes:
  1. **replace** — find-and-replace a specific string in a file
  2. **insert**  — insert new lines at a given line number
  3. **rewrite** — overwrite the entire file with new content

Safety features:
  • Dry-run mode (preview diff without writing)
  • Backup creation before write
  • Path validation against project root
"""

from __future__ import annotations

import difflib
import shutil
from pathlib import Path
from typing import Any, Literal

from backend.agent.tools.base import BaseTool


class CodePatcherTool(BaseTool):
    """Apply code edits to project files."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    # ── Identity ──────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return "patch_code"

    @property
    def description(self) -> str:
        return (
            "Apply a code change to a file. Supports three modes: "
            "'replace' (find-and-replace text), 'insert' (insert lines at a "
            "position), or 'rewrite' (overwrite the entire file)."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Target file path (absolute or project-relative).",
                },
                "mode": {
                    "type": "string",
                    "enum": ["replace", "insert", "rewrite"],
                    "description": "Edit mode.",
                },
                "old_text": {
                    "type": "string",
                    "description": "(replace mode) Exact text to find and replace.",
                },
                "new_text": {
                    "type": "string",
                    "description": "(replace/insert/rewrite mode) New content.",
                },
                "line_number": {
                    "type": "integer",
                    "description": "(insert mode) 1-indexed line to insert before.",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, return a diff preview without writing. Default false.",
                },
                "create_if_missing": {
                    "type": "boolean",
                    "description": "If true and the file doesn't exist, create it. Default false.",
                },
            },
            "required": ["path", "mode", "new_text"],
        }

    # ── Execution ─────────────────────────────────────────────────────
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        raw_path: str = kwargs["path"]
        mode: str = kwargs["mode"]
        new_text: str = kwargs["new_text"]
        old_text: str | None = kwargs.get("old_text")
        line_number: int | None = kwargs.get("line_number")
        dry_run: bool = kwargs.get("dry_run", False)
        create_if_missing: bool = kwargs.get("create_if_missing", False)

        target = Path(raw_path)
        if not target.is_absolute():
            target = self._root / target
        target = target.resolve()

        # ── Path safety ───────────────────────────────────────────────
        try:
            target.relative_to(self._root)
        except ValueError:
            return {
                "success": False,
                "output": (
                    f"Refusing to edit outside project root.\n"
                    f"  file: {target}\n  root: {self._root}"
                ),
            }

        # ── Resolve mode ──────────────────────────────────────────────
        if mode == "replace":
            return await self._replace(target, old_text or "", new_text, dry_run, line_number)
        if mode == "insert":
            return await self._insert(target, new_text, line_number, dry_run)
        if mode == "rewrite":
            return await self._rewrite(target, new_text, dry_run, create_if_missing)

        return {"success": False, "output": f"Unknown mode '{mode}'."}

    # ── Mode implementations ──────────────────────────────────────────
    async def _replace(
        self,
        target: Path,
        old: str,
        new: str,
        dry_run: bool,
        line_no: int | None = None,
    ) -> dict[str, Any]:
        if not target.is_file():
            return {"success": False, "output": f"File not found: {target}"}
        if not old:
            return {"success": False, "output": "old_text is required for replace mode."}

        original = target.read_text(encoding="utf-8", errors="replace")
        if old not in original:
            return {
                "success": False,
                "output": "old_text not found in the file. Check for exact match including whitespace.",
            }

        lines = original.splitlines(keepends=True)
        if line_no is not None and 1 <= line_no <= len(lines):
            idx = line_no - 1
            if old in lines[idx]:
                lines[idx] = lines[idx].replace(old, new, 1)
                updated = "".join(lines)
            else:
                replaced = False
                for offset in range(1, len(lines)):
                    for target_idx in (idx + offset, idx - offset):
                        if 0 <= target_idx < len(lines) and old in lines[target_idx]:
                            lines[target_idx] = lines[target_idx].replace(old, new, 1)
                            updated = "".join(lines)
                            replaced = True
                            break
                    if replaced:
                        break
                if not replaced:
                    updated = original.replace(old, new, 1)
        else:
            updated = original.replace(old, new, 1)

        diff = _unified_diff(original, updated, str(target))

        if dry_run:
            return {"success": True, "output": f"Dry-run diff:\n{diff}", "diff": diff}

        _backup(target)
        target.write_text(updated, encoding="utf-8")
        return {"success": True, "output": f"Replaced text in {target.name}.\n{diff}", "diff": diff}

    async def _insert(
        self, target: Path, new: str, line_no: int | None, dry_run: bool
    ) -> dict[str, Any]:
        if not target.is_file():
            return {"success": False, "output": f"File not found: {target}"}

        original = target.read_text(encoding="utf-8", errors="replace")
        lines = original.splitlines(keepends=True)

        insert_at = (line_no or len(lines) + 1) - 1
        insert_at = max(0, min(insert_at, len(lines)))

        new_lines = new if new.endswith("\n") else new + "\n"
        lines.insert(insert_at, new_lines)
        updated = "".join(lines)
        diff = _unified_diff(original, updated, str(target))

        if dry_run:
            return {"success": True, "output": f"Dry-run diff:\n{diff}", "diff": diff}

        _backup(target)
        target.write_text(updated, encoding="utf-8")
        return {
            "success": True,
            "output": f"Inserted at line {insert_at + 1} in {target.name}.\n{diff}",
            "diff": diff,
        }

    async def _rewrite(
        self, target: Path, new: str, dry_run: bool, create: bool
    ) -> dict[str, Any]:
        if not target.exists() and not create:
            return {"success": False, "output": f"File not found: {target} (set create_if_missing=true to create)."}

        original = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
        diff = _unified_diff(original, new, str(target))

        if dry_run:
            return {"success": True, "output": f"Dry-run diff:\n{diff}", "diff": diff}

        if target.is_file():
            _backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new, encoding="utf-8")

        verb = "Created" if not original else "Rewrote"
        return {"success": True, "output": f"{verb} {target.name}.\n{diff}", "diff": diff}


# ── Helpers ───────────────────────────────────────────────────────────
def _unified_diff(old: str, new: str, filename: str) -> str:
    """Generate a unified diff string."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff) or "(no changes)"


def _backup(path: Path) -> Path:
    """Create a .bak copy before modifying."""
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak
