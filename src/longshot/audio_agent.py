"""Audio planning utilities for the Longshot pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioTrack:
    """Simple audio track metadata."""

    style: str
    duration_seconds: int


def design_audio(style_hint: str, duration_seconds: int) -> AudioTrack:
    """Return deterministic audio metadata based on the style hint.

    Args:
        style_hint: Free-form style descriptor from the prompt.
        duration_seconds: Target length of the audio track.

    Returns:
        :class:`AudioTrack` metadata with a normalized style tag.
    """

    normalized = style_hint.lower().replace(" ", "-") or "ambient"
    return AudioTrack(style=normalized, duration_seconds=duration_seconds)
