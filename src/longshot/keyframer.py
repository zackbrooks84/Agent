"""Deterministic keyframe generation based on workflow plans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .orchestrator import WorkflowPlan


@dataclass(frozen=True)
class Keyframe:
    """Concrete keyframe representation with normalized scene tokens."""

    index: int
    timestamp: float
    tokens: List[str]


def generate_keyframes(plan: WorkflowPlan) -> List[Keyframe]:
    """Convert workflow keyframe specs into structured keyframes.

    Args:
        plan: Workflow plan produced by the orchestrator.

    Returns:
        Deterministic list of :class:`Keyframe` objects. Tokens are derived by
        lower-casing the description and splitting on whitespace to facilitate
        reproducible downstream comparisons.
    """

    keyframes: List[Keyframe] = []
    for spec in plan.keyframes:
        tokens = [token for token in spec.description.lower().split() if token]
        keyframes.append(
            Keyframe(index=spec.index, timestamp=spec.timestamp, tokens=tokens)
        )
    return keyframes
