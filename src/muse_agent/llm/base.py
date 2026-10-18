"""The provider contract.

One method: complete(messages, tools) -> LLMResponse.
A response is either final text, tool calls, or both. Providers must be
stateless — all conversation state lives in context/, owned by runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from muse_agent.core.types import Message, ToolCall, ToolSpec


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)


class LLMProvider(Protocol):
    name: str
    model: str

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec]) -> LLMResponse:
        ...
