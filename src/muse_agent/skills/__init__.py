"""Skills: reusable playbooks as folders with a SKILL.md (see ch08).

A skill is data, not code: a name, a description (used for matching),
optional trigger keywords, and a Markdown body the agent follows.
Skills are discovered from directories, indexed into the prompt
(name + description only), and loaded in full only when used —
progressive disclosure keeps the context budget for the task.
"""
from muse_agent.skills.loader import Skill, load_skill_file, parse_frontmatter
from muse_agent.skills.registry import SkillRegistry

__all__ = ["Skill", "load_skill_file", "parse_frontmatter", "SkillRegistry"]
