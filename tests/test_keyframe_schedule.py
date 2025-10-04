"""Invariants for the deterministic keyframe schedule."""

from __future__ import annotations

from longshot.config import PipelineConfig
from longshot.keyframer import generate_keyframes
from longshot.orchestrator import plan_workflow


def test_keyframe_timestamps_monotonic() -> None:
    """Keyframe timestamps should be monotonic non-decreasing."""

    config = PipelineConfig.from_prompt(
        "Scene one. Scene two. Scene three.", duration_seconds=90
    )
    plan = plan_workflow(config)
    keyframes = generate_keyframes(plan)
    timestamps = [keyframe.timestamp for keyframe in keyframes]
    assert timestamps == sorted(timestamps)
    assert timestamps[0] == 0.0


def test_keyframe_count_matches_sentences() -> None:
    """Keyframe count should equal the number of sentences in the prompt."""

    prompt = "First beat. Second beat. Third beat. Fourth beat."
    config = PipelineConfig.from_prompt(prompt, duration_seconds=120)
    plan = plan_workflow(config)
    keyframes = generate_keyframes(plan)
    assert len(keyframes) == 4
