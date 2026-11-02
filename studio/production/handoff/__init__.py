"""Portable P2 GitHub handoff validation (no agent launcher)."""
from .protocol import prepare, verify, receive
__all__ = ("prepare", "verify", "receive")
