"""Configuration objects for the Longshot AI pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for a specific agent in the pipeline.

    Attributes:
        name: Canonical name of the agent implementation.
        model: Optional model identifier or version tag.
    """

    name: str
    model: str | None = None


@dataclass(frozen=True)
class KeyframeSpec:
    """Declarative description of a keyframe produced by the orchestrator."""

    index: int
    timestamp: float
    description: str


@dataclass(frozen=True)
class PipelineConfig:
    """Container for the end-to-end pipeline configuration.

    Attributes:
        prompt: User provided natural-language description.
        duration_seconds: Target duration for the final video.
        agents: Ordered list of agent configurations to execute.
        seed: RNG seed used to keep pipeline outputs deterministic.
    """

    prompt: str
    duration_seconds: int
    agents: List[AgentConfig] = field(default_factory=list)
    seed: int = 42

    @classmethod
    def from_prompt(
        cls,
        prompt: str,
        duration_seconds: int | None = None,
        *,
        seed: int = 42,
    ) -> "PipelineConfig":
        """Derive a default pipeline configuration from a free-form prompt.

        Args:
            prompt: High-level description of the desired video.
            duration_seconds: Optional target duration. Defaults to 60 seconds when
                unspecified.
            seed: RNG seed used to keep deterministic outputs.

        Returns:
            A fully populated :class:`PipelineConfig` with default agents.
        """

        clean_prompt = prompt.strip()
        if not clean_prompt:
            raise ValueError("prompt must be a non-empty string")

        duration = duration_seconds or 60
        if duration <= 0:
            raise ValueError("duration_seconds must be positive")

        agents = [
            AgentConfig(name="orchestrator", model="gpt-5"),
            AgentConfig(name="keyframer", model="nano-banana-v1"),
            AgentConfig(name="animator", model="kling-2.1"),
            AgentConfig(name="audio", model="riffusion"),
            AgentConfig(name="compositor", model="ffmpeg"),
        ]

        return cls(
            prompt=clean_prompt,
            duration_seconds=duration,
            agents=agents,
            seed=seed,
        )
