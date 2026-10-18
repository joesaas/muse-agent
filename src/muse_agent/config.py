"""Configuration: environment + optional config.toml, nothing else.

Secrets are never stored in config. Only the *name* of an environment
variable holding a key may be configured (see security/credentials.py).
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    home: Path = field(default_factory=lambda: Path.home() / ".muse-agent")
    provider: str = "mock"                 # mock | openai-compatible
    model: str = "mock-1"
    base_url: str = "https://api.openai.com/v1"
    api_key_env: str = "OPENAI_API_KEY"
    context_budget_tokens: int = 32_000    # compress above this
    keep_recent_messages: int = 12         # never compressed away
    max_steps: int = 12                    # agent-loop step cap per turn
    auto_approve_write: bool = False       # HITL default: ask

    @classmethod
    def load(cls, home: Path | None = None) -> "Config":
        cfg = cls()
        if home is not None:
            cfg.home = home
        env_home = os.environ.get("MUSE_AGENT_HOME")
        if env_home:
            cfg.home = Path(env_home).expanduser()
        file_cfg: dict = {}
        cfg_file = cfg.home / "config.toml"
        if cfg_file.exists():
            file_cfg = tomllib.loads(cfg_file.read_text(encoding="utf-8"))
        env_map = {
            "provider": "MUSE_AGENT_PROVIDER", "model": "MUSE_AGENT_MODEL",
            "base_url": "MUSE_AGENT_BASE_URL", "api_key_env": "MUSE_AGENT_API_KEY_ENV",
        }
        for key, env_name in env_map.items():
            if key in file_cfg:
                setattr(cfg, key, file_cfg[key])
            if os.environ.get(env_name):
                setattr(cfg, key, os.environ[env_name])
        for key in ("context_budget_tokens", "keep_recent_messages", "max_steps"):
            if key in file_cfg:
                setattr(cfg, key, int(file_cfg[key]))
        if "auto_approve_write" in file_cfg:
            cfg.auto_approve_write = bool(file_cfg["auto_approve_write"])
        return cfg
