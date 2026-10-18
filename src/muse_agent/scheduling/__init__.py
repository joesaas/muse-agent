"""Scheduling & background work (see design ch11).

Two mechanisms, one idea — work that wakes the agent:
  - cron: time-based jobs (a 5-field cron spec, a prompt, a target chat)
  - hooks: event-based watchers (poll a condition, wake on change)
Both deliver an Event to the bus; neither talks to the LLM directly.
"""
from muse_agent.scheduling.scheduler import CronSpec, Job, Scheduler
from muse_agent.scheduling.hooks import HookRegistry

__all__ = ["CronSpec", "Job", "Scheduler", "HookRegistry"]
