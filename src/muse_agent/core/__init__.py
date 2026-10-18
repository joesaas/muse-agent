"""Core contracts shared by every module. Nothing here depends on any
other muse_agent package — this is the stable centre of the system."""
from muse_agent.core.types import (
    Event, Message, Role, ToolCall, ToolResult, ToolSpec,
)
from muse_agent.core.events import EventBus
from muse_agent.core.errors import MuseAgentError, ToolError, ApprovalDenied

__all__ = [
    "Event", "Message", "Role", "ToolCall", "ToolResult", "ToolSpec",
    "EventBus", "MuseAgentError", "ToolError", "ApprovalDenied",
]
