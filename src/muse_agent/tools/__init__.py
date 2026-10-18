"""Tools: named, described, risk-labelled capabilities the LLM may call.
A tool is a ToolSpec (what the model sees) + a handler (what runs)."""
from muse_agent.tools.base import Tool, ToolHandler
from muse_agent.tools.registry import ToolRegistry
from muse_agent.tools.builtin import builtin_tools

__all__ = ["Tool", "ToolHandler", "ToolRegistry", "builtin_tools"]
