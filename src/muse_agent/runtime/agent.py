"""The agent loop (see design ch05).

Inner loop, per user turn:
    compress-if-needed -> ask LLM -> (tool calls? gate, run, re-inject
    and repeat) -> final text.
Outer loop: events (messages, cron, hooks, subagent returns) wake this
loop; they never bypass it. Interruption is a flag checked each step.

Every step publishes events and saves a recovery snapshot, so a turn
is observable and resumable by construction.
"""
from __future__ import annotations

from muse_agent.approval import ApprovalPolicy, Decision
from muse_agent.context import Compressor, save_snapshot
from muse_agent.core.types import Message, Role
from muse_agent.llm import LLMProvider
from muse_agent.runtime.session import Session


class Agent:
    def __init__(self, session: Session, provider: LLMProvider,
                 compressor: Compressor | None = None) -> None:
        self.session = session
        self.provider = provider
        self.compressor = compressor or Compressor()
        approver = getattr(session, "_approver", None)
        from muse_agent.approval import auto_approver
        self.policy = ApprovalPolicy(
            approver=approver or auto_approver,
            auto_approve_write=session.config.auto_approve_write)
        self._interrupted = False

    def interrupt(self) -> None:
        """User interrupt wins over any in-flight step (checked per step)."""
        self._interrupted = True

    def run_turn(self, user_text: str) -> str:
        ctx = self.session.context
        bus = self.session.bus
        self._interrupted = False
        bus.emit("turn.started", session_id=self.session.id, text=user_text)
        ctx.add_user(user_text)
        final = ""
        for step in range(self.session.config.max_steps):
            if self._interrupted:
                final = "(已打断)"
                bus.emit("turn.interrupted", session_id=self.session.id)
                break
            if self.compressor.compress_if_needed(ctx):
                bus.emit("context.compressed", session_id=self.session.id)
            response = self.provider.complete(ctx.messages,
                                              self.session.tools.specs())
            if response.tool_calls:
                ctx.add(Message(
                    role=Role.ASSISTANT, content=response.text or "",
                    metadata={"tool_call_ids":
                              [c.id for c in response.tool_calls]}))
                for call in response.tool_calls:
                    spec = self.session.tools.get(call.name).spec
                    decision = self.policy.check(call, spec.risk)
                    bus.emit("tool.requested", name=call.name,
                             decision=decision.value)
                    if decision is Decision.DENY:
                        result_text = (f"approval denied for tool "
                                       f"{call.name}; the action was not run")
                        ctx.add(Message(role=Role.TOOL, content=result_text,
                                        name=call.name,
                                        tool_call_id=call.id))
                        continue
                    result = self.session.tools.execute(call)
                    bus.emit("tool.finished", name=call.name, ok=result.ok)
                    ctx.add(Message(role=Role.TOOL, content=result.output,
                                    name=call.name, tool_call_id=call.id))
                save_snapshot(self.session.config.home,
                              self.session.id, ctx)
                continue
            final = response.text
            ctx.add(Message(role=Role.ASSISTANT, content=final))
            save_snapshot(self.session.config.home, self.session.id, ctx)
            break
        else:
            final = "(已达到本轮最大步数，任务未完成；进度已保存，可继续。)"
            ctx.add(Message(role=Role.ASSISTANT, content=final))
        bus.emit("turn.finished", session_id=self.session.id)
        return final
