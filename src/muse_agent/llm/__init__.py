"""LLM provider adapters. The runtime only sees the LLMProvider protocol;
swapping models/providers never touches the agent loop."""
from muse_agent.llm.base import LLMProvider, LLMResponse
from muse_agent.llm.mock import MockProvider
from muse_agent.llm.openai_compatible import OpenAICompatibleProvider

__all__ = ["LLMProvider", "LLMResponse", "MockProvider", "OpenAICompatibleProvider"]


def build_provider(config) -> LLMProvider:
    if config.provider == "mock":
        return MockProvider(model=config.model)
    if config.provider == "openai-compatible":
        return OpenAICompatibleProvider(
            model=config.model, base_url=config.base_url,
            api_key_env=config.api_key_env)
    raise ValueError(f"unknown provider: {config.provider!r} "
                     "(expected 'mock' or 'openai-compatible')")
