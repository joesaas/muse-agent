"""Deterministic offline provider — the default.

It exists so the whole system runs and can be tested with no API key.
Rules (intentionally tiny and predictable):
  - "echo: X"            -> call the echo tool with X, then report its result
  - "time" / "现在几点"   -> call the now tool, then report its result
  - "list: PATH"         -> call list_dir, then report its result
  - anything else        -> answer directly, prefixed as a mock reply
Only tool results that arrived *after* the latest user message count
as answers to it — earlier turns must never leak into a new turn.
"""
from __future__ import annotations

from muse_agent.core.types import Message, Role, ToolCall, ToolSpec
from muse_agent.llm.base import LLMResponse


class MockProvider:
    name = "mock"

    def __init__(self, model: str = "mock-1") -> None:
        self.model = model

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec]) -> LLMResponse:
        last_user_idx = max(
            (i for i, m in enumerate(messages) if m.role is Role.USER),
            default=-1)
        if last_user_idx == -1:
            return LLMResponse(text="(mock) 没有收到用户消息。")
        after = messages[last_user_idx + 1:]
        tool_results = [m for m in after if m.role is Role.TOOL]
        if tool_results:
            joined = "; ".join(f"{m.name} -> {m.content}"
                                for m in tool_results)
            return LLMResponse(text=f"工具结果：{joined}")
        text = messages[last_user_idx].content.strip()
        available = {t.name for t in tools}
        if text.lower().startswith("echo:") and "echo" in available:
            return LLMResponse(tool_calls=[ToolCall(
                name="echo", arguments={"text": text[5:].strip()})])
        if ("现在几点" in text or "time" in text.lower()) and "now" in available:
            return LLMResponse(tool_calls=[ToolCall(name="now", arguments={})])
        if text.lower().startswith("list:") and "list_dir" in available:
            return LLMResponse(tool_calls=[ToolCall(
                name="list_dir", arguments={"path": text[5:].strip() or "."})])
        return LLMResponse(
            text=f"（mock 回复）我收到了：{text}。"
                 "接入真实模型后，这里会是模型的回答。")
