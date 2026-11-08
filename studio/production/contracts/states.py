"""Side-effect-free role and evidence-gated review transitions."""
from __future__ import annotations
import re

_TRANSITIONS: dict[tuple[str, str], str] = {
    ("draft", "ready"): "planner",
    ("ready", "assigned"): "planner",
    ("assigned", "producing"): "worker",
    ("producing", "prepared"): "worker",
    ("prepared", "technical_verified"): "reviewer",
    ("technical_verified", "creative_review"): "reviewer",
    ("creative_review", "accepted"): "human",
    ("accepted", "delivered"): "reviewer",
    ("creative_review", "revision_requested"): "human",
}
_ACTIVE = {"draft", "ready", "assigned", "producing", "prepared", "technical_verified", "creative_review", "accepted"}
_EVIDENCE = re.compile(r"^(task|artifact|ci|review|delivery):[a-zA-Z0-9][a-zA-Z0-9._-]{0,120}$")


def next_state(current: str, *, requested: str, actor_role: str, evidence_ref: str | None) -> str:
    """A returned state is only a validated proposal, never a stored approval."""
    if not isinstance(evidence_ref, str) or not _EVIDENCE.fullmatch(evidence_ref):
        raise ValueError("Transition requires a safe evidence reference")
    if requested in ("blocked", "cancelled") and current in _ACTIVE:
        if actor_role not in ("planner", "reviewer", "human"):
            raise ValueError("Actor cannot halt task")
        return requested
    if _TRANSITIONS.get((current, requested)) != actor_role:
        raise ValueError("Invalid state transition or actor role")
    if requested in ("accepted", "revision_requested") and not evidence_ref.startswith("review:"):
        raise ValueError("Human review evidence required")
    if requested == "delivered" and not evidence_ref.startswith("delivery:"):
        raise ValueError("Delivery proof required")
    return requested
