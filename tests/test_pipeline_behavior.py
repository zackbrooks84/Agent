"""Behavioral tests for the end-to-end pipeline."""

from __future__ import annotations

from pathlib import Path

from longshot.pipeline import PipelineConfig, build_pipeline


def test_pipeline_produces_manifest(tmp_path: Path) -> None:
    """End-to-end pipeline should produce a manifest with consistent metadata."""

    config = PipelineConfig.from_prompt(
        "DJ in neon club. Crowd reacts. Camera pulls back.", duration_seconds=90
    )
    manifest_path = tmp_path / "manifest.jsonl"
    pipeline = build_pipeline(config, manifest_path=manifest_path)
    artifacts = pipeline.run()

    assert artifacts.manifest_path == manifest_path
    assert artifacts.audio.duration_seconds == config.duration_seconds
    assert artifacts.keyframes[0].timestamp == 0.0
    assert len(artifacts.animation) == len(artifacts.keyframes) - 1
    assert artifacts.manifest.entries[-1].payload["path"] == str(manifest_path)
