"""Session assembly — the one place all subsystems are wired together.

Order matters and mirrors a real Muse-style turn (see ch19):
  1. ensure the home layout exists
  2. load identity/profile + curated memory
  3. discover skills, register tools & connectors
  4. build the system prompt from those indexes
  5. create the context window with the prompt pinned
Nothing else in the codebase constructs an Agent; new front-ends
(CLI, chat, API) all start here.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from muse_agent.config import Config
from muse_agent.connectors import ConnectorRegistry, EchoConnector
from muse_agent.context import ContextManager
from muse_agent.core.events import EventBus
from muse_agent.goals import GoalTracker
from muse_agent.home import ensure_home
from muse_agent.identity import load_profile
from muse_agent.llm import build_provider
from muse_agent.memory import MemoryStore
from muse_agent.prompts import PromptBuilder, PromptContext
from muse_agent.skills import SkillRegistry
from muse_agent.tools import ToolRegistry, builtin_tools
from muse_agent.approval import ApprovalPolicy, Approver, auto_approver


@dataclass
class Session:
    config: Config
    bus: EventBus
    context: ContextManager
    tools: ToolRegistry
    skills: SkillRegistry
    memory: MemoryStore
    connectors: ConnectorRegistry
    goals: GoalTracker
    system_prompt: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    extra_skill_dirs: list[Path] = field(default_factory=list)


def build_session(config: Config | None = None,
                  approver: Approver | None = None,
                  extra_skill_dirs: list[Path] | None = None) -> Session:
    cfg = config or Config.load()
    ensure_home(cfg.home)
    bus = EventBus()
    profile = load_profile(cfg.home)
    memory = MemoryStore(cfg.home)
    skills = SkillRegistry().discover(
        cfg.home / "skills", *(extra_skill_dirs or []))
    tools = ToolRegistry()
    for tool in builtin_tools():
        tools.register(tool)
    connectors = ConnectorRegistry()
    connectors.register(EchoConnector())
    prompt_ctx = PromptContext(
        profile_text=profile.render(),
        memory_text=memory.index_text(),
        skill_lines=skills.index_lines(),
        tool_lines=[f"{s.name} — {s.description} (risk: {s.risk})"
                    for s in tools.specs()],
    )
    system_prompt = PromptBuilder().build(prompt_ctx)
    context = ContextManager(budget_tokens=cfg.context_budget_tokens,
                             keep_recent=cfg.keep_recent_messages)
    context.set_system(system_prompt)
    session = Session(
        config=cfg, bus=bus, context=context, tools=tools, skills=skills,
        memory=memory, connectors=connectors,
        goals=GoalTracker(cfg.home / "goals.json"),
        system_prompt=system_prompt,
        extra_skill_dirs=list(extra_skill_dirs or []))
    # The approver is stored on the session via the bus payload channel
    # used by Agent; kept explicit here for front-ends to override.
    session._approver = approver or auto_approver  # type: ignore[attr-defined]
    return session
