"""
LLM Client — unified interface across OpenAI, Gemini, and Anthropic.

Handles:
  • Provider-specific API calls
  • Function-calling / tool-use marshalling
  • Conversation history management
  • Streaming (optional, disabled by default)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.agent.config import AgentConfig, LLMProvider

log = logging.getLogger(__name__)


# ── Message types ─────────────────────────────────────────────────────
class Message:
    """A single turn in the conversation."""

    __slots__ = ("role", "content", "tool_calls", "tool_call_id", "name")

    def __init__(
        self,
        role: str,
        content: str = "",
        tool_calls: list[dict[str, Any]] | None = None,
        tool_call_id: str | None = None,
        name: str | None = None,
    ) -> None:
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id
        self.name = name

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            d["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            d["name"] = self.name
        return d


# ── Response wrapper ──────────────────────────────────────────────────
class LLMResponse:
    """Normalised response from any provider."""

    __slots__ = ("content", "tool_calls", "finish_reason", "usage")

    def __init__(
        self,
        content: str = "",
        tool_calls: list[dict[str, Any]] | None = None,
        finish_reason: str = "stop",
        usage: dict[str, int] | None = None,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls or []
        self.finish_reason = finish_reason
        self.usage = usage or {}

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


# ── Main client ──────────────────────────────────────────────────────
class LLMClient:
    """Provider-agnostic LLM client with function-calling support."""

    def __init__(self, config: AgentConfig) -> None:
        self._cfg = config.llm
        self._provider: LLMProvider = self._cfg.provider
        self._client: Any = None  # lazily initialised

    # ── Public API ────────────────────────────────────────────────────
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """Send messages (with optional tools) and return a normalised response."""
        if self._provider == "openai":
            return await self._chat_openai(messages, tools)
        if self._provider == "gemini":
            return await self._chat_gemini(messages, tools)
        if self._provider == "anthropic":
            return await self._chat_anthropic(messages, tools)
        raise ValueError(f"Unsupported provider: {self._provider}")

    # ── OpenAI ────────────────────────────────────────────────────────
    async def _chat_openai(
        self, messages: list[Message], tools: list[dict[str, Any]] | None
    ) -> LLMResponse:
        client = self._get_openai_client()

        kwargs: dict[str, Any] = {
            "model": self._cfg.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": self._cfg.temperature,
            "max_tokens": self._cfg.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        resp = client.chat.completions.create(**kwargs)
        choice = resp.choices[0]

        # Normalise tool calls
        tc_list = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tc_list.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tc_list,
            finish_reason=choice.finish_reason or "stop",
            usage={
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
        )

    def _get_openai_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._cfg.api_key)
        return self._client

    # ── Google Gemini ─────────────────────────────────────────────────
    async def _chat_gemini(
        self, messages: list[Message], tools: list[dict[str, Any]] | None
    ) -> LLMResponse:
        client = self._get_gemini_client()

        # Build Gemini content format
        contents = _messages_to_gemini_contents(messages)

        gen_config = {
            "temperature": self._cfg.temperature,
            "max_output_tokens": self._cfg.max_tokens,
        }

        kwargs: dict[str, Any] = {
            "contents": contents,
            "generation_config": gen_config,
        }

        # Convert tools to Gemini format
        if tools:
            import google.generativeai as genai

            gemini_tools = _openai_tools_to_gemini(tools)
            kwargs["tools"] = gemini_tools

        response = client.generate_content(**kwargs)

        # Parse response
        content = ""
        tc_list: list[dict[str, Any]] = []

        for part in response.parts:
            if hasattr(part, "text") and part.text:
                content += part.text
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                tc_list.append({
                    "id": f"gemini_{fc.name}",
                    "name": fc.name,
                    "arguments": dict(fc.args) if fc.args else {},
                })

        return LLMResponse(
            content=content,
            tool_calls=tc_list,
            finish_reason="tool_calls" if tc_list else "stop",
            usage={},
        )

    def _get_gemini_client(self) -> Any:
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self._cfg.api_key)
            self._client = genai.GenerativeModel(self._cfg.model)
        return self._client

    # ── Anthropic ─────────────────────────────────────────────────────
    async def _chat_anthropic(
        self, messages: list[Message], tools: list[dict[str, Any]] | None
    ) -> LLMResponse:
        client = self._get_anthropic_client()

        # Separate system message
        system_msg = ""
        api_messages = []
        for m in messages:
            if m.role == "system":
                system_msg += m.content + "\n"
            else:
                api_messages.append(m.to_dict())

        kwargs: dict[str, Any] = {
            "model": self._cfg.model,
            "max_tokens": self._cfg.max_tokens,
            "messages": api_messages,
            "temperature": self._cfg.temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg.strip()

        if tools:
            kwargs["tools"] = _openai_tools_to_anthropic(tools)

        resp = client.messages.create(**kwargs)

        content = ""
        tc_list: list[dict[str, Any]] = []

        for block in resp.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tc_list.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })

        return LLMResponse(
            content=content,
            tool_calls=tc_list,
            finish_reason="tool_calls" if tc_list else resp.stop_reason or "stop",
            usage={
                "prompt_tokens": resp.usage.input_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.output_tokens if resp.usage else 0,
            },
        )

    def _get_anthropic_client(self) -> Any:
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self._cfg.api_key)
        return self._client


# ── Format converters ─────────────────────────────────────────────────
def _messages_to_gemini_contents(messages: list[Message]) -> list[dict[str, Any]]:
    """Convert our Message list to Gemini's content format."""
    contents = []
    for m in messages:
        if m.role == "system":
            # Gemini handles system prompts via system_instruction,
            # but we can prepend as a user message as a fallback
            contents.append({"role": "user", "parts": [{"text": f"[System]: {m.content}"}]})
        elif m.role == "assistant":
            contents.append({"role": "model", "parts": [{"text": m.content}]})
        elif m.role == "tool":
            contents.append({
                "role": "user",
                "parts": [{"text": f"[Tool Result ({m.name})]: {m.content}"}],
            })
        else:
            contents.append({"role": "user", "parts": [{"text": m.content}]})
    return contents


def _openai_tools_to_gemini(tools: list[dict[str, Any]]) -> list[Any]:
    """Convert OpenAI-format tool schemas to Gemini function declarations."""
    import google.generativeai as genai

    declarations = []
    for t in tools:
        func = t.get("function", {})
        declarations.append(
            genai.protos.FunctionDeclaration(
                name=func["name"],
                description=func.get("description", ""),
                parameters=_json_schema_to_gemini_schema(func.get("parameters", {})),
            )
        )
    return [genai.protos.Tool(function_declarations=declarations)]


def _json_schema_to_gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Best-effort conversion of JSON Schema to Gemini's schema format."""
    return schema  # Gemini accepts a subset of JSON Schema directly


def _openai_tools_to_anthropic(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert OpenAI-format tool schemas to Anthropic format."""
    anthropic_tools = []
    for t in tools:
        func = t.get("function", {})
        anthropic_tools.append({
            "name": func["name"],
            "description": func.get("description", ""),
            "input_schema": func.get("parameters", {}),
        })
    return anthropic_tools
