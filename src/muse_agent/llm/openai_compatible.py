"""OpenAI-compatible chat-completions adapter (stdlib urllib only).

This is the *adapter seam* for real models: any endpoint speaking the
OpenAI chat API works. Tool-calling follows the same wire format.
It is deliberately small; provider-specific quirks belong in new
adapter modules, not in the runtime.
"""
from __future__ import annotations

import json
import os
import urllib.request

from muse_agent.core.errors import ConfigError
from muse_agent.core.types import Message, ToolCall, ToolSpec
from muse_agent.llm.base import LLMResponse


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(self, model: str, base_url: str, api_key_env: str) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec]) -> LLMResponse:
        key = os.environ.get(self.api_key_env)
        if not key:
            raise ConfigError(
                f"environment variable {self.api_key_env} is not set; "
                "the provider reads the key by name and never stores it")
        body = {
            "model": self.model,
            "messages": [{"role": m.role.value, "content": m.content}
                         for m in messages],
        }
        if tools:
            body["tools"] = [{
                "type": "function",
                "function": {"name": t.name, "description": t.description,
                             "parameters": t.parameters or
                             {"type": "object", "properties": {}}},
            } for t in tools]
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choice = data["choices"][0]["message"]
        calls = []
        for c in choice.get("tool_calls") or []:
            fn = c["function"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(name=fn["name"], arguments=args,
                                  id=c.get("id") or ToolCall(name="x").id))
        return LLMResponse(text=choice.get("content") or "",
                           tool_calls=calls,
                           usage=data.get("usage") or {})
