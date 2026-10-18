"""Security & credentials (see design ch12).

Rules enforced here, not by convention:
  - secrets are read by name from the environment at call time
  - secret values are never written to memory, logs or snapshots
  - anything printed can pass through redact() first
"""
from muse_agent.security.credentials import CredentialStore
from muse_agent.security.redaction import redact

__all__ = ["CredentialStore", "redact"]
