"""Tests for the deterministic video planning pipeline."""
from __future__ import annotations

import pytest

from aal.webapp.pipeline import (
    SEGMENT_DURATION_SECONDS,
    SEGMENTS_PER_VIDEO,
    RenderSegment,
    StoryboardGenerator,
    Transition,
    VideoAssembler,
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


def test_merged_video_contains_crossfades(pipeline: VideoPipeline) -> None:
    """Merged video plan includes crossfade transitions across all segments."""

    plan = pipeline.create_plan("Floating citadel with aurora-lit skies")
    merged = plan.merged_video
    assert merged.duration_seconds == SEGMENT_DURATION_SECONDS * SEGMENTS_PER_VIDEO
    assert list(merged.segment_order) == list(range(SEGMENTS_PER_VIDEO))
    assert len(merged.transitions) == SEGMENTS_PER_VIDEO - 1
    assert all(isinstance(transition, Transition) for transition in merged.transitions)
    for transition in merged.transitions:
        assert transition.style == "crossfade"
        assert transition.duration_seconds > 0
    linked_pairs = [
        (transition.from_index, transition.to_index) for transition in merged.transitions
    ]
    assert linked_pairs == [(index, index + 1) for index in range(SEGMENTS_PER_VIDEO - 1)]


def test_video_assembler_requires_sequential_indices() -> None:
    """Assembler rejects render segments that are not sequentially indexed."""

    assembler = VideoAssembler()
    segments = [
        RenderSegment(
            index=0,
            duration_seconds=SEGMENT_DURATION_SECONDS,
            palette={"red": 0, "green": 0, "blue": 0, "accent": 0},
            caption="first",
        ),
        RenderSegment(
            index=2,
            duration_seconds=SEGMENT_DURATION_SECONDS,
            palette={"red": 0, "green": 0, "blue": 0, "accent": 0},
            caption="third",
        ),
    ]

    with pytest.raises(ValueError):
        assembler.assemble(segments)
