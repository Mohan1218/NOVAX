"""
TestRunnerTool — run pytest (or unittest) and return structured results.

Supports:
  • Running the full test suite or a specific test file / pattern
  • Parsing pytest JSON report (via pytest-json-report) if available,
    falling back to raw stdout parsing
  • Configurable timeout
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any

from backend.agent.tools.base import BaseTool


class TestRunnerTool(BaseTool):
    """Run the project's test suite and return structured results."""

    def __init__(
        self,
        timeout: int = 60,
        max_output: int = 64 * 1024,
        project_root: str | Path = ".",
    ) -> None:
        self._timeout = timeout
        self._max_output = max_output
        self._root = Path(project_root).resolve()

    # ── Identity ──────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return "run_tests"

    @property
    def description(self) -> str:
        return (
            "Run pytest on the project (or a specific test file/pattern) "
            "and return pass/fail counts with failure details."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": (
                        "Test file, directory, or pytest node-id to run. "
                        "Omit to run the full suite."
                    ),
                },
                "extra_args": {
                    "type": "string",
                    "description": "Additional CLI flags for pytest, e.g. '-x -v'.",
                },
                "timeout": {
                    "type": "integer",
                    "description": f"Max seconds. Default {self._timeout}.",
                },
            },
            "required": [],
        }

    # ── Execution ─────────────────────────────────────────────────────
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        target: str | None = kwargs.get("target")
        extra_args: str = kwargs.get("extra_args", "")
        timeout: int = kwargs.get("timeout", self._timeout)

        # Check if pytest-json-report is available
        has_json_report = _check_json_report_available()

        json_path: Path | None = None
        if has_json_report:
            json_report = tempfile.NamedTemporaryFile(
                suffix=".json", prefix="pytest_report_", delete=False,
                dir=str(self._root),
            )
            json_report.close()
            json_path = Path(json_report.name)

        # Build the pytest command
        cmd_parts = [
            "python", "-m", "pytest",
            "--tb=short",
            "-q",
        ]
        if has_json_report and json_path:
            cmd_parts.extend(["--json-report", f"--json-report-file={json_path}"])
        if extra_args:
            cmd_parts.extend(extra_args.split())
        if target:
            cmd_parts.append(target)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._root),
            )

            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return {
                    "success": False,
                    "output": f"Test run timed out after {timeout}s.",
                }

            stdout = _cap(stdout_b.decode(errors="replace"), self._max_output)
            stderr = _cap(stderr_b.decode(errors="replace"), self._max_output)

            # ── Try structured JSON report ────────────────────────────
            if json_path:
                structured = _parse_json_report(json_path)
                if structured:
                    return {
                        "success": structured["total_failed"] == 0,
                        "output": _format_structured(structured, stdout),
                        "summary": structured,
                        "raw_stdout": stdout,
                        "raw_stderr": stderr,
                    }

            # ── Fallback: parse raw pytest output ─────────────────────
            return {
                "success": (proc.returncode or 0) == 0,
                "output": stdout + ("\n" + stderr if stderr else ""),
                "exit_code": proc.returncode,
            }

        finally:
            if json_path:
                json_path.unlink(missing_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────
def _check_json_report_available() -> bool:
    """Check if pytest-json-report is installed."""
    try:
        import pytest_jsonreport  # noqa: F401
        return True
    except ImportError:
        return False

def _parse_json_report(path: Path) -> dict[str, Any] | None:
    """Parse a pytest-json-report file, returning None on failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    summary = data.get("summary", {})
    tests = data.get("tests", [])

    failures = []
    for t in tests:
        if t.get("outcome") == "failed":
            call = t.get("call", {})
            failures.append({
                "nodeid": t.get("nodeid", "?"),
                "message": call.get("longrepr", call.get("crash", {}).get("message", "")),
            })

    return {
        "total_passed": summary.get("passed", 0),
        "total_failed": summary.get("failed", 0),
        "total_skipped": summary.get("skipped", 0),
        "total_errors": summary.get("error", 0),
        "duration": summary.get("duration", 0),
        "failures": failures,
    }


def _format_structured(s: dict[str, Any], raw: str) -> str:
    """Build a concise human-readable summary from structured results."""
    lines = [
        f"✅ Passed: {s['total_passed']}  "
        f"❌ Failed: {s['total_failed']}  "
        f"⏭ Skipped: {s['total_skipped']}  "
        f"💥 Errors: {s['total_errors']}  "
        f"⏱ {s['duration']:.2f}s",
    ]

    if s["failures"]:
        lines.append("\n── Failure details ──")
        for f in s["failures"]:
            lines.append(f"\n• {f['nodeid']}")
            # Limit failure message length
            msg = str(f["message"])[:2000]
            lines.append(msg)

    return "\n".join(lines)


def _cap(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… (truncated)"
