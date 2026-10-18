"""Goals & tracking (see design ch18).

Durable outcomes (goals) and concrete commitments (tracked items) are
kept as data the agent can re-read every session — not as chat text
that scrolls away. Storage is one JSON file in the home directory.
"""
from muse_agent.goals.tracker import GoalTracker, Goal, TrackedItem

__all__ = ["GoalTracker", "Goal", "TrackedItem"]
