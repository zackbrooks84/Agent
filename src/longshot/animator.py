"""Animation planning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .keyframer import Keyframe


@dataclass(frozen=True)
class AnimationSegment:
    """Description of how to transition between two keyframes."""

    start_index: int
    end_index: int
    technique: str


def plan_animation(keyframes: List[Keyframe]) -> List[AnimationSegment]:
    """Produce animation segments connecting adjacent keyframes.

    Args:
        keyframes: Ordered keyframe list.

    Returns:
        List of :class:`AnimationSegment` covering each adjacent pair. The
        technique is selected deterministically based on index parity so unit
        tests can assert the plan.
    """

    if not keyframes:
        return []

    segments: List[AnimationSegment] = []
    for idx in range(len(keyframes) - 1):
        technique = "morph" if idx % 2 == 0 else "camera-pan"
        segments.append(
            AnimationSegment(
                start_index=keyframes[idx].index,
                end_index=keyframes[idx + 1].index,
                technique=technique,
            )
        )
    return segments
