"""Manifest composition utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from .animator import AnimationSegment
from .audio_agent import AudioTrack
from .keyframer import Keyframe


@dataclass(frozen=True)
class ManifestEntry:
    """Single artifact entry in the composed manifest."""

    kind: str
    payload: dict


@dataclass(frozen=True)
class Manifest:
    """Composable manifest that can be serialized to JSON in calling code."""

    entries: tuple[ManifestEntry, ...]


def compose_manifest(
    keyframes: Iterable[Keyframe],
    segments: Iterable[AnimationSegment],
    audio: AudioTrack,
    *,
    manifest_path: Path,
) -> Manifest:
    """Combine pipeline outputs into a manifest structure.

    Args:
        keyframes: Sequence of generated keyframes.
        segments: Sequence of animation segments.
        audio: Planned audio track metadata.
        manifest_path: Filesystem location where downstream code should persist
            the manifest. No write occurs in this function to preserve purity.

    Returns:
        Manifest describing the pipeline outputs.
    """

    keyframe_tuple: Tuple[Keyframe, ...] = tuple(keyframes)
    segment_tuple: Tuple[AnimationSegment, ...] = tuple(segments)

    entries = [
        ManifestEntry(
            kind="keyframes",
            payload={
                "count": len(keyframe_tuple),
            },
        ),
        ManifestEntry(
            kind="animation_segments",
            payload={
                "count": len(segment_tuple),
            },
        ),
        ManifestEntry(
            kind="audio",
            payload={
                "style": audio.style,
                "duration_seconds": audio.duration_seconds,
            },
        ),
        ManifestEntry(
            kind="manifest_reference",
            payload={
                "path": str(manifest_path),
            },
        ),
    ]
    return Manifest(entries=tuple(entries))
