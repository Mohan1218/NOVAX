"""
Agent configuration — centralised settings for LLM, tools, and sandbox.

Reads from environment variables (.env) with sensible defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


# ── Supported providers ───────────────────────────────────────────────
LLMProvider = Literal["openai", "gemini", "anthropic"]


@dataclass(frozen=True)
class LLMConfig:
    """Settings for the backing LLM."""

    provider: LLMProvider = os.getenv("LLM_PROVIDER", "gemini")  # type: ignore[assignment]
    model: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    api_key: str = os.getenv("LLM_API_KEY", "")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))


@dataclass(frozen=True)
class SandboxConfig:
    """Settings for the Python / test runner sandbox."""

    timeout_seconds: int = int(os.getenv("SANDBOX_TIMEOUT", "30"))
    max_output_bytes: int = int(os.getenv("SANDBOX_MAX_OUTPUT", str(64 * 1024)))


@dataclass(frozen=True)
class AgentConfig:
    """Top-level agent configuration."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)

    # Maximum tool-call iterations before the agent gives up
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "25"))

    # Root of the project the agent is inspecting / debugging
    project_root: Path = Path(os.getenv("PROJECT_ROOT", "."))

    # Logging
    log_level: str = os.getenv("AGENT_LOG_LEVEL", "INFO")
