"""Subagents (see design ch07).

A subagent is a full Agent with its own loop, spawned for a
self-contained task. At spawn it receives a *snapshot copy* of the
parent context (full copy, not a shared reference, not a slice) plus
its task brief; the parent keeps running, and the subagent's result
returns as an event + a return value — a handoff, not shared memory.
"""
from muse_agent.subagents.manager import SubagentManager, SubagentResult

__all__ = ["SubagentManager", "SubagentResult"]
