"""
PythonRunnerTool — execute Python code in a sandboxed subprocess.

Safety features:
  • Configurable timeout (default 30 s)
  • Output size cap (default 64 KB)
  • Runs in a subprocess so the agent process is never at risk
  • Captures both stdout and stderr
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from backend.agent.tools.base import BaseTool


class PythonRunnerTool(BaseTool):
    """Execute a snippet of Python code and return the output."""

    def __init__(
        self,
        timeout: int = 30,
        max_output: int = 64 * 1024,
        project_root: str | Path = ".",
    ) -> None:
        self._timeout = timeout
        self._max_output = max_output
        self._root = Path(project_root).resolve()

    # ── Identity ──────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return "run_python"

    @property
    def description(self) -> str:
        return (
            "Execute a Python code snippet in a subprocess and return "
            "stdout, stderr, and the exit code."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source code to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": f"Max seconds to wait. Default {self._timeout}.",
                },
            },
            "required": ["code"],
        }

    # ── Execution ─────────────────────────────────────────────────────
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        code: str = kwargs["code"]
        timeout: int = kwargs.get("timeout", self._timeout)

        # Write to a temp file so the subprocess gets a clean script
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="agent_run_",
            delete=False,
            dir=str(self._root),
            encoding="utf-8",
        )
        try:
            tmp.write(code)
            tmp.flush()
            tmp.close()

            import sys
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                tmp.name,
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
                    "output": f"Execution timed out after {timeout}s.",
                    "exit_code": -1,
                }

            stdout = _cap(stdout_b.decode(errors="replace"), self._max_output)
            stderr = _cap(stderr_b.decode(errors="replace"), self._max_output)
            exit_code = proc.returncode or 0

            output_parts = []
            if stdout:
                output_parts.append(f"── stdout ──\n{stdout}")
            if stderr:
                output_parts.append(f"── stderr ──\n{stderr}")
            if not output_parts:
                output_parts.append("(no output)")

            return {
                "success": exit_code == 0,
                "output": "\n".join(output_parts),
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
            }

        finally:
            Path(tmp.name).unlink(missing_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────
def _cap(text: str, limit: int) -> str:
    """Truncate text to *limit* characters, appending a marker if cut."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… (truncated)"
