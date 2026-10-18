"""Command-line front-end.

Front-ends are interchangeable: this CLI, a future chat adapter or an
HTTP API all build a Session the same way and only differ in how they
render output and ask for approval.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from muse_agent.config import Config
from muse_agent.core.types import ToolCall
from muse_agent.approval import RiskLevel
from muse_agent.home import ensure_home
from muse_agent.llm import build_provider
from muse_agent.runtime import Agent, build_session
from muse_agent.subagents import SubagentManager


def _ask_approval(call: ToolCall, risk: RiskLevel) -> bool:
    if not sys.stdin.isatty():
        return False
    answer = input(f"[审批] 允许调用 {call.name}（风险 {risk.value}）"
                   f"参数 {call.arguments}？[y/N] ").strip().lower()
    return answer in ("y", "yes")


def _agent_for(session) -> Agent:
    return Agent(session, build_provider(session.config))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="muse-agent",
        description="A modular, Muse-inspired super agent (design-first, runnable core).")
    parser.add_argument("--home", type=Path, default=None,
                        help="agent home directory (default ~/.muse-agent)")
    parser.add_argument("--provider", default=None,
                        help="mock (default, offline) | openai-compatible")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init", help="create the home directory layout")
    p_run = sub.add_parser("run", help="run one turn and print the reply")
    p_run.add_argument("text", nargs="+")
    sub.add_parser("chat", help="interactive REPL")
    sub.add_parser("doctor", help="show home, modules, skills, tools, connectors")
    sub.add_parser("prompt", help="print the assembled system prompt")
    p_skills = sub.add_parser("skills", help="list discovered skills")
    p_mem = sub.add_parser("memory", help="search memory")
    p_mem.add_argument("query", nargs="+")
    p_sub = sub.add_parser("subagent", help="spawn a subagent for one task")
    p_sub.add_argument("task", nargs="+")
    sub.add_parser("demo", help="run a scripted demo: tool call + subagent")

    args = parser.parse_args(argv)
    config = Config.load(home=args.home)
    if args.provider:
        config.provider = args.provider

    if args.cmd == "init":
        created = ensure_home(config.home)
        print(f"home: {config.home}")
        print("created: " + (", ".join(p.name for p in created) or "（已存在，无新建）"))
        return 0

    repo_skills = Path.cwd() / "examples" / "skills"
    extra = [repo_skills] if repo_skills.is_dir() else []
    session = build_session(config, approver=_ask_approval,
                            extra_skill_dirs=extra)

    if args.cmd in (None, "run"):
        text = " ".join(args.text) if args.cmd == "run" else "你好"
        print(_agent_for(session).run_turn(text))
        return 0
    if args.cmd == "chat":
        agent = _agent_for(session)
        print("muse-agent chat — 输入 exit 退出")
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if line in ("exit", "quit", "/exit"):
                break
            if line:
                print(agent.run_turn(line))
        return 0
    if args.cmd == "doctor":
        print(f"home:       {config.home}")
        print(f"provider:   {config.provider} (model {config.model})")
        print(f"session:    {session.id}")
        print(f"context:    budget {config.context_budget_tokens} tokens, "
              f"{session.context.total_tokens()} used by system prompt")
        print(f"skills:     {', '.join(s.name for s in session.skills.all()) or '（无）'}")
        print(f"tools:      {', '.join(session.tools.names())}")
        for st in session.connectors.statuses():
            print(f"connector:  {st.name} — {'connected' if st.connected else 'not connected'} ({st.detail})")
        print(f"goals:      {len(session.goals.goals)} goals, "
              f"{len(session.goals.open_items())} open tracked items")
        return 0
    if args.cmd == "prompt":
        print(session.system_prompt)
        return 0
    if args.cmd == "skills":
        for skill in session.skills.all():
            print(f"{skill.name} — {skill.description}")
        return 0
    if args.cmd == "memory":
        hits = session.memory.search(" ".join(args.query))
        for hit in hits:
            print(f"{hit.source}:{hit.line}  {hit.text}")
        if not hits:
            print("（无匹配）")
        return 0
    if args.cmd == "subagent":
        manager = SubagentManager(parent=session)
        result = manager.spawn(" ".join(args.task))
        print(result.output)
        return 0 if result.ok else 1
    if args.cmd == "demo":
        agent = _agent_for(session)
        print("— 1) 普通对话")
        print(agent.run_turn("你能做什么？"))
        print("— 2) 工具调用（echo）")
        print(agent.run_turn("echo: 工具调用走通了"))
        print("— 3) 工具调用（now）")
        print(agent.run_turn("现在几点？"))
        print("— 4) 子代理")
        manager = SubagentManager(parent=session)
        print(manager.spawn("echo: 我是子代理，我完成了任务").output)
        print("— demo 完成")
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
