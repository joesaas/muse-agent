"""Unit tests for muse-agent. Stdlib unittest only, offline, mock LLM."""
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from muse_agent.approval import ApprovalPolicy, auto_approver, deny_approver
from muse_agent.config import Config
from muse_agent.context import (Compressor, ContextManager, load_snapshot,
                                 save_snapshot)
from muse_agent.core.types import Message, Role, ToolCall
from muse_agent.goals import GoalTracker
from muse_agent.llm import MockProvider, build_provider
from muse_agent.memory import MemoryStore
from muse_agent.runtime import build_session, Agent
from muse_agent.scheduling import CronSpec, Job, Scheduler
from muse_agent.core.events import EventBus
from muse_agent.security import redact
from muse_agent.skills import SkillRegistry, parse_frontmatter
from muse_agent.subagents import SubagentManager


def make_home() -> Path:
    return Path(tempfile.mkdtemp(prefix="muse-agent-test-"))


def make_agent(home: Path, **cfg_kwargs):
    cfg = Config(home=home, **cfg_kwargs)
    session = build_session(cfg)
    return Agent(session, build_provider(cfg)), session


class TestAgentLoop(unittest.TestCase):
    def test_plain_reply(self):
        agent, _ = make_agent(make_home())
        out = agent.run_turn("你好")
        self.assertIn("我收到了：你好", out)

    def test_tool_call_echo(self):
        agent, _ = make_agent(make_home())
        out = agent.run_turn("echo: hello tools")
        self.assertIn("echo -> hello tools", out)

    def test_tool_call_now(self):
        agent, _ = make_agent(make_home())
        out = agent.run_turn("现在几点？")
        self.assertIn("now ->", out)

    def test_no_cross_turn_tool_leak(self):
        agent, _ = make_agent(make_home())
        first = agent.run_turn("echo: first")
        second = agent.run_turn("第二轮问题")
        self.assertIn("echo -> first", first)
        self.assertIn("我收到了：第二轮问题", second)


class TestApproval(unittest.TestCase):
    def test_read_auto_write_denied_by_default_deny(self):
        policy = ApprovalPolicy(approver=deny_approver)
        call = ToolCall(name="x")
        self.assertEqual(policy.check(call, "read").value, "allow")
        self.assertEqual(policy.check(call, "write").value, "deny")
        self.assertEqual(policy.check(call, "exec").value, "deny")

    def test_auto_approver(self):
        policy = ApprovalPolicy(approver=auto_approver)
        self.assertEqual(policy.check(ToolCall(name="x"), "exec").value,
                         "allow")


class TestContext(unittest.TestCase):
    def test_compression_replaces_middle_and_keeps_recent(self):
        ctx = ContextManager(budget_tokens=50, keep_recent=2)
        ctx.set_system("sys")
        for i in range(10):
            ctx.add(Message(role=Role.USER, content=f"message {i} " * 10))
        ran = Compressor().compress_if_needed(ctx)
        self.assertTrue(ran)
        self.assertTrue(any(m.metadata.get("compressed")
                            for m in ctx.messages))
        self.assertIn("message 9", ctx.messages[-1].content)
        self.assertEqual(ctx.messages[0].content, "sys")

    def test_snapshot_roundtrip(self):
        home = make_home()
        ctx = ContextManager()
        ctx.set_system("sys")
        ctx.add_user("hello")
        save_snapshot(home, "s1", ctx)
        loaded = load_snapshot(home, "s1")
        self.assertIsNotNone(loaded)
        self.assertEqual([m.content for m in loaded.messages],
                         ["sys", "hello"])


class TestMemory(unittest.TestCase):
    def test_append_and_search(self):
        home = make_home()
        store = MemoryStore(home)
        store.append_curated("li 的生日是 3 月 23 日")
        store.append_daily("今天讨论了 muse-agent 的模块设计")
        self.assertTrue(store.search("生日"))
        hits = store.search("模块设计")
        self.assertTrue(hits and "muse-agent" in hits[0].text)


class TestSkills(unittest.TestCase):
    def test_parse_frontmatter(self):
        meta, body = parse_frontmatter(
            "---\nname: demo\ndescription: d\ntriggers: a, b\n---\nBody")
        self.assertEqual(meta["name"], "demo")
        self.assertEqual(body, "Body")

    def test_discover_example_skill(self):
        repo = Path(__file__).resolve().parents[1]
        reg = SkillRegistry().discover(repo / "examples" / "skills")
        names = [s.name for s in reg.all()]
        self.assertIn("echo-helper", names)
        self.assertTrue(reg.match("来个 echo 示例"))


class TestSubagent(unittest.TestCase):
    def test_spawn_returns_result_and_parent_untouched(self):
        home = make_home()
        agent, session = make_agent(home)
        before = len(session.context.messages)
        manager = SubagentManager(parent=session)
        result = manager.spawn("echo: 子代理完成")
        self.assertTrue(result.ok)
        self.assertIn("我是子代理" if False else "子代理完成", result.output)
        # Parent context did not gain the child's messages.
        self.assertEqual(len(session.context.messages), before)


class TestScheduling(unittest.TestCase):
    def test_cron_matches(self):
        spec = CronSpec("*/5 * * * *")
        self.assertTrue(spec.matches(datetime(2026, 10, 18, 10, 5)))
        self.assertFalse(spec.matches(datetime(2026, 10, 18, 10, 6)))
        daily = CronSpec("10 8 * * *")
        self.assertTrue(daily.matches(datetime(2026, 10, 18, 8, 10)))

    def test_scheduler_dedupes_same_minute(self):
        bus = EventBus()
        sched = Scheduler(bus)
        sched.add(Job(id="j1", spec=CronSpec("* * * * *"), prompt="p"))
        now = datetime(2026, 10, 18, 10, 0)
        self.assertEqual(len(sched.tick(now)), 1)
        self.assertEqual(len(sched.tick(now)), 0)


class TestMisc(unittest.TestCase):
    def test_redact(self):
        out = redact("api_key=sk-1234567890abcdef and token: abc")
        self.assertNotIn("sk-1234567890abcdef", out)
        self.assertIn("[已隐藏]", out)

    def test_goals_tracker(self):
        home = make_home()
        tracker = GoalTracker(home / "goals.json")
        tracker.add_goal("学完 agent 架构")
        item = tracker.add_item("推送 muse-agent")
        self.assertEqual(len(tracker.open_items()), 1)
        self.assertTrue(tracker.complete_item(item.id))
        self.assertEqual(len(tracker.open_items()), 0)
        reloaded = GoalTracker(home / "goals.json")
        self.assertEqual(len(reloaded.goals), 1)

    def test_session_prompt_has_sections(self):
        _, session = make_agent(make_home())
        prompt = session.system_prompt
        self.assertIn("Muse Agent", prompt)
        self.assertIn("## Tools", prompt)
        self.assertIn("echo", prompt)


if __name__ == "__main__":
    unittest.main()
