# longshot-ai

Longshot AI is a research-oriented scaffold for chaining specialized agents
that turn a single prompt into a fully rendered video artifact. The repository
prioritizes determinism, reproducibility, and modularity so experiments can be
replayed while swapping underlying media models.

## Goals

- Orchestrate a pipeline that converts a natural-language prompt into a
  structured workflow plan.
- Produce deterministic keyframe schedules that downstream animation engines
  can consume.
- Provide lightweight adapters for animation and audio subsystems.
- Assemble intermediate outputs into a reproducible media artifact manifest.

## Repository layout

```
longshot-ai/
├── README.md
├── requirements.txt
├── src/
│   └── longshot/
│       ├── __init__.py
│       ├── animator.py
│       ├── audio_agent.py
│       ├── compositor.py
│       ├── config.py
│       ├── keyframer.py
│       └── orchestrator.py
└── tests/
    ├── __init__.py
    ├── test_keyframe_schedule.py
    └── test_pipeline_behavior.py
```

## Quickstart

Install dependencies and run the test suite to verify the scaffold:

```
pip install -r requirements.txt
pytest -q
```

## Usage

```python
from longshot.pipeline import build_pipeline, PipelineConfig

config = PipelineConfig.from_prompt(
    prompt="Epic continuous shot of a cyberpunk DJ in a neon-lit club, 120 seconds"
)
pipeline = build_pipeline(config)
artifact = pipeline.run()
print(artifact.manifest_path)
```

The default pipeline returns deterministic, metadata-only artifacts that can be
fed into external rendering engines. Integrators can subclass individual agent
adapters to call proprietary services while keeping the deterministic plan for
regression testing.

## License

This project is licensed under the MIT License.
