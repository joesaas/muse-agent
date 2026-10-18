"""Context engineering: the message window, its budget, compression
when it overflows, and snapshots so a session can be recovered."""
from muse_agent.context.manager import ContextManager, estimate_tokens
from muse_agent.context.compression import Compressor, ExtractiveSummarizer
from muse_agent.context.recovery import save_snapshot, load_snapshot

__all__ = ["ContextManager", "estimate_tokens", "Compressor",
           "ExtractiveSummarizer", "save_snapshot", "load_snapshot"]
