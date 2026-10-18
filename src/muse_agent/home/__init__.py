"""The home directory layout (see design ch10): everything the agent
knows lives in plain files under one directory the user owns."""
from muse_agent.home.layout import ensure_home, HOME_FILES

__all__ = ["ensure_home", "HOME_FILES"]
