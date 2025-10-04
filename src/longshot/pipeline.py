"""High-level pipeline wiring for the Longshot AI scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .animator import AnimationSegment, plan_animation
from .audio_agent import AudioTrack, design_audio
from .compositor import Manifest, compose_manifest
from .config import PipelineConfig
from .keyframer import Keyframe, generate_keyframes
from .orchestrator import WorkflowPlan, plan_workflow


@dataclass(frozen=True)
class PipelineArtifacts:
    """Container for the artifacts returned by the pipeline."""

    plan: WorkflowPlan
    keyframes: tuple[Keyframe, ...]
    animation: tuple[AnimationSegment, ...]
    audio: AudioTrack
    manifest: Manifest
    manifest_path: Path


class Pipeline:
    """Deterministic orchestration pipeline."""

    def __init__(self, config: PipelineConfig, *, manifest_path: Path | None = None) -> None:
        """Store configuration and derived manifest path.

        Args:
            config: Pipeline configuration.
            manifest_path: Optional path for downstream manifest persistence. A
                default inside the current working directory is used when
                omitted.
        """

        self._config = config
        self._manifest_path = manifest_path or Path("artifacts/manifest.jsonl")

    @property
    def config(self) -> PipelineConfig:
        """Return the pipeline configuration."""

        return self._config

    def run(self) -> PipelineArtifacts:
        """Execute the pipeline end to end returning deterministic artifacts."""

        plan = plan_workflow(self._config)
        keyframes = tuple(generate_keyframes(plan))
        animation = tuple(plan_animation(list(keyframes)))
        audio_style_hint = plan.keyframes[0].description if plan.keyframes else self._config.prompt
        audio = design_audio(audio_style_hint, self._config.duration_seconds)
        manifest = compose_manifest(
            keyframes,
            animation,
            audio,
            manifest_path=self._manifest_path,
        )
        return PipelineArtifacts(
            plan=plan,
            keyframes=keyframes,
            animation=animation,
            audio=audio,
            manifest=manifest,
            manifest_path=self._manifest_path,
        )


def build_pipeline(config: PipelineConfig, *, manifest_path: Path | None = None) -> Pipeline:
    """Construct a :class:`Pipeline` with the provided configuration."""

    return Pipeline(config=config, manifest_path=manifest_path)
