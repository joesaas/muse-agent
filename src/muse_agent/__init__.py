"""muse-agent: a modular, Muse-inspired super agent.

Design-first, stdlib-only, minimal runnable core. Every subsystem of a
personal agent (system prompt, memory, skills, tools, subagents, context
management & compression, approval, scheduling, connectors, goals) lives
in its own package with a narrow interface, so modules can be replaced
independently over the project's lifetime.
"""
__version__ = "0.1.0"
