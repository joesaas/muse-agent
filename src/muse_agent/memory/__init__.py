"""Memory: durable, user-readable, file-based (see design ch15).

Two tiers, both plain Markdown in the home directory:
  - curated long-term memory: MEMORY.md (tight, edited in place)
  - daily notes: memory/YYYY-MM-DD.md (append-only log)
Retrieval is keyword search over both tiers. Vector stores etc. can
replace the search implementation behind MemoryStore later; the file
format — the part the user owns — does not change.
"""
from muse_agent.memory.store import MemoryStore, MemoryHit

__all__ = ["MemoryStore", "MemoryHit"]
