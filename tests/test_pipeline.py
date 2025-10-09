"""Tests for the deterministic video planning pipeline."""
from __future__ import annotations

import pytest

from aal.webapp.pipeline import (
    SEGMENT_DURATION_SECONDS,
    SEGMENTS_PER_VIDEO,
    StoryboardGenerator,
    VideoPipeline,
)


@pytest.fixture()
def pipeline() -> VideoPipeline:
    return VideoPipeline()


def test_segments_cover_full_duration(pipeline: VideoPipeline) -> None:
    """The storyboard spans exactly two minutes using 6 second segments."""

    plan = pipeline.create_plan("Calm ocean sunrise journey with drones")
    assert len(plan.storyboard) == SEGMENTS_PER_VIDEO
    assert all(segment.duration_seconds == SEGMENT_DURATION_SECONDS for segment in plan.storyboard)
    total_duration = sum(segment.duration_seconds for segment in plan.storyboard)
    assert total_duration == SEGMENT_DURATION_SECONDS * SEGMENTS_PER_VIDEO


def test_storyboard_is_deterministic() -> None:
    """Identical prompts yield identical storyboard output."""

    generator = StoryboardGenerator()
    prompt = "Explorers traverse neon forests and floating cities"
    first = generator.generate(prompt)
    second = generator.generate(prompt)
    assert first == second


def test_empty_prompt_rejected(pipeline: VideoPipeline) -> None:
    """Empty prompts trigger validation errors."""

    with pytest.raises(ValueError):
        pipeline.create_plan("   ")
