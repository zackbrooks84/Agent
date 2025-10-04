"""Utilities for planning a deterministic workflow from a prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .config import KeyframeSpec, PipelineConfig


@dataclass(frozen=True)
class WorkflowPlan:
    """Structured plan output by the orchestrator.

    Attributes:
        prompt: Original user prompt used for planning.
        duration_seconds: Target duration for the video.
        keyframes: Ordered list of keyframe specifications that downstream
            agents will elaborate on.
    """

    prompt: str
    duration_seconds: int
    keyframes: List[KeyframeSpec]


def plan_workflow(config: PipelineConfig) -> WorkflowPlan:
    """Derive a deterministic workflow plan from the provided configuration.

    The current implementation splits the prompt into thematic fragments using
    sentence boundaries and distributes them evenly across the timeline. The
    approach avoids randomness to guarantee repeatable results for regression
    testing.

    Args:
        config: Fully resolved pipeline configuration.

    Returns:
        A :class:`WorkflowPlan` containing the ordered keyframe schedule.
    """

    sentences = _split_prompt(config.prompt)
    interval = config.duration_seconds / max(len(sentences), 1)
    keyframes = [
        KeyframeSpec(index=index, timestamp=round(interval * index, 3), description=segment)
        for index, segment in enumerate(sentences)
    ]
    if not keyframes:
        keyframes = [
            KeyframeSpec(index=0, timestamp=0.0, description=config.prompt),
        ]
    return WorkflowPlan(
        prompt=config.prompt,
        duration_seconds=config.duration_seconds,
        keyframes=keyframes,
    )


def _split_prompt(prompt: str) -> List[str]:
    """Split a prompt into stable thematic segments.

    The helper removes trailing punctuation and ensures the resulting segments
    are non-empty. Splitting uses periods and semicolons because they are
    frequent delimiters in creative prompts.
    """

    candidates = [segment.strip() for segment in prompt.replace(";", ".").split(".")]
    return [segment for segment in candidates if segment]
