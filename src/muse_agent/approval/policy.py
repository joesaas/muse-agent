"""Risk-tiered approval.

  read  -> auto-approved (looking is free)
  write -> needs approval unless config/policy says otherwise
  exec  -> needs approval, always asked explicitly

The approver is a callback: the CLI asks the user in the terminal, a
chat front-end shows a card, tests inject auto/deny. Policy never
knows which — that separation is what makes HITL portable.
"""
from __future__ import annotations

from enum import Enum
from typing import Callable

from muse_agent.core.types import ToolCall


class RiskLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    EXEC = "exec"


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


Approver = Callable[[ToolCall, RiskLevel], bool]


def auto_approver(call: ToolCall, risk: RiskLevel) -> bool:
    return True


def deny_approver(call: ToolCall, risk: RiskLevel) -> bool:
    return False


class ApprovalPolicy:
    def __init__(self, approver: Approver,
                 auto_approve_write: bool = False) -> None:
        self.approver = approver
        self.auto_approve_write = auto_approve_write

    def check(self, call: ToolCall, risk: str) -> Decision:
        level = RiskLevel(risk)
        if level is RiskLevel.READ:
            return Decision.ALLOW
        if level is RiskLevel.WRITE and self.auto_approve_write:
            return Decision.ALLOW
        return Decision.ALLOW if self.approver(call, level) else Decision.DENY
