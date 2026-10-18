from __future__ import annotations

import copy
from dataclasses import dataclass, field

from muse_agent.context import ContextManager
from muse_agent.core.types import Message, Role
from muse_agent.llm import build_provider
from muse_agent.runtime.agent import Agent
from muse_agent.runtime.session import Session, build_session


@dataclass
class SubagentResult:
    task: str
    output: str
    session_id: str
    ok: bool = True


@dataclass
class SubagentManager:
    """Spawns child agents in-process (the reference implementation).

    Depth is capped (default 2, mirroring production practice) — a
    subagent's subagents cannot spawn further. A threaded/remote
    executor can replace run() behind this same interface.
    """

    parent: Session
    depth: int = 0
    max_depth: int = 2
    results: list[SubagentResult] = field(default_factory=list)

    def spawn(self, task: str) -> SubagentResult:
        if self.depth >= self.max_depth:
            return SubagentResult(task=task, ok=False,
                                  output="(超过最大子代理深度，未执行)",
                                  session_id="")
        child_session = build_session(
            config=self.parent.config,
            approver=getattr(self.parent, "_approver", None),
            extra_skill_dirs=self.parent.extra_skill_dirs)
        # Snapshot copy: deep-copy the parent's messages into the child.
        # The child may compress or extend its copy freely; the parent
        # context is never mutated by the child.
        snapshot = copy.deepcopy(self.parent.context.messages)
        child_ctx = ContextManager(
            budget_tokens=self.parent.config.context_budget_tokens,
            keep_recent=self.parent.config.keep_recent_messages)
        child_ctx.messages = snapshot
        child_ctx.add(Message(
            role=Role.SYSTEM,
            content=f"你是一个子代理。你的任务是：{task}\n"
                    "只做这件事，做完给出简洁、完整的结果交回主代理。"))
        child_session.context = child_ctx
        child = Agent(child_session, build_provider(self.parent.config))
        self.parent.bus.emit("subagent.spawned", task=task,
                             child_session=child_session.id)
        output = child.run_turn(task)
        result = SubagentResult(task=task, output=output,
                                session_id=child_session.id)
        self.results.append(result)
        self.parent.bus.emit("subagent.finished", task=task,
                             child_session=child_session.id)
        return result
