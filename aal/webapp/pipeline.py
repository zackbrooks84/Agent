"""Pipeline components for deterministic storyboard and video plan generation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, Iterable, List, Sequence

SEGMENT_DURATION_SECONDS = 6
TOTAL_VIDEO_SECONDS = 120
SEGMENTS_PER_VIDEO = TOTAL_VIDEO_SECONDS // SEGMENT_DURATION_SECONDS


@dataclass(frozen=True)
class StorySegment:
    """Represents a storyboard segment.

    Attributes:
        index: Zero-based index of the segment within the video timeline.
        duration_seconds: Duration for which the segment should play.
        title: Short title summarising the segment.
        description: Narration or on-screen direction for the segment.
    """

    index: int
    duration_seconds: int
    title: str
    description: str


@dataclass(frozen=True)
class RenderSegment:
    """Rendering instructions for a storyboard segment.

    Attributes:
        index: Zero-based index aligning with the storyboard segment.
        duration_seconds: Duration of the rendered clip.
        palette: Mapping describing the synthetic colour palette for the segment.
        caption: Text that should be overlaid during rendering.
    """

    index: int
    duration_seconds: int
    palette: Dict[str, int]
    caption: str


@dataclass(frozen=True)
class VideoPlan:
    """Complete video plan consisting of storyboard and render information."""

    storyboard: Sequence[StorySegment]
    render_segments: Sequence[RenderSegment]


class StoryboardGenerator:
    """Produces deterministic storyboard segments for a given prompt.

    The generator is intentionally lightweight and does not rely on
    proprietary APIs. Instead it tokenises the prompt, derives key scenes
    using hashing, and creates a flowing storyboard covering the full
    timeline.
    """

    def __init__(self, *, segment_duration: int = SEGMENT_DURATION_SECONDS) -> None:
        self._segment_duration = segment_duration

    def generate(self, prompt: str) -> List[StorySegment]:
        """Generate a storyboard from a prompt.

        Args:
            prompt: User-provided description of the desired narrative.

        Returns:
            Deterministic list of ``StorySegment`` objects covering the full
            120 second runtime.

        Raises:
            ValueError: If ``prompt`` is empty or whitespace.
        """

        if not prompt or prompt.strip() == "":
            raise ValueError("Prompt must contain non-whitespace characters.")

        sanitized_prompt = " ".join(prompt.strip().split())
        words = sanitized_prompt.split(" ")
        if not words:
            raise ValueError("Prompt tokenisation failed; provide text content.")

        primary_themes = self._derive_themes(words)
        segments: List[StorySegment] = []
        for index in range(SEGMENTS_PER_VIDEO):
            theme = primary_themes[index % len(primary_themes)]
            segment_words = self._rolling_window(words, index)
            title = f"{theme.title()} focus"
            description = (
                f"Scene {index + 1}: Emphasise {theme} with elements {', '.join(segment_words)}."
            )
            segments.append(
                StorySegment(
                    index=index,
                    duration_seconds=self._segment_duration,
                    title=title,
                    description=description,
                )
            )
        return segments

    def _derive_themes(self, words: Sequence[str]) -> List[str]:
        unique_words: List[str] = []
        seen = set()
        for word in words:
            normalised = word.lower()
            if normalised not in seen and normalised.isalpha():
                seen.add(normalised)
                unique_words.append(normalised)
        if not unique_words:
            unique_words = ["concept"]
        return unique_words

    def _rolling_window(self, words: Sequence[str], offset: int) -> List[str]:
        window_size = 4
        return [words[(offset + i) % len(words)] for i in range(window_size)]


class ImaginerRenderer:
    """Derives deterministic render instructions emulating a video model.

    The renderer simulates a 6-second clip generation akin to Grok Imagine
    while remaining fully offline. Each segment receives a pseudo-random
    colour palette derived from the prompt and segment index.
    """

    def __init__(self, *, segment_duration: int = SEGMENT_DURATION_SECONDS) -> None:
        self._segment_duration = segment_duration

    def render(self, prompt: str, storyboard: Iterable[StorySegment]) -> List[RenderSegment]:
        """Create render segments for a storyboard.

        Args:
            prompt: Original prompt used for hashing.
            storyboard: Iterable of storyboard segments.

        Returns:
            List of ``RenderSegment`` objects matching the storyboard order.
        """

        seed_material = sha256(prompt.encode("utf-8")).hexdigest()
        render_segments: List[RenderSegment] = []
        for segment in storyboard:
            palette = self._colour_palette(seed_material, segment.index)
            caption = f"{segment.title}: {segment.description}"
            render_segments.append(
                RenderSegment(
                    index=segment.index,
                    duration_seconds=self._segment_duration,
                    palette=palette,
                    caption=caption,
                )
            )
        return render_segments

    def _colour_palette(self, seed_material: str, index: int) -> Dict[str, int]:
        material = f"{seed_material}:{index}".encode("utf-8")
        digest = sha256(material).hexdigest()
        red = int(digest[0:2], 16)
        green = int(digest[2:4], 16)
        blue = int(digest[4:6], 16)
        accent = int(digest[6:8], 16)
        return {"red": red, "green": green, "blue": blue, "accent": accent}


class VideoPipeline:
    """Coordinates storyboard and render simulation for 2-minute videos."""

    def __init__(self) -> None:
        self._storyboard = StoryboardGenerator()
        self._renderer = ImaginerRenderer()

    def create_plan(self, prompt: str) -> VideoPlan:
        """Create a video plan for the provided prompt."""

        storyboard = self._storyboard.generate(prompt)
        render_segments = self._renderer.render(prompt, storyboard)
        return VideoPlan(storyboard=storyboard, render_segments=render_segments)


__all__ = [
    "ImaginerRenderer",
    "RenderSegment",
    "SEGMENT_DURATION_SECONDS",
    "SEGMENTS_PER_VIDEO",
    "StorySegment",
    "StoryboardGenerator",
    "TOTAL_VIDEO_SECONDS",
    "VideoPipeline",
]
