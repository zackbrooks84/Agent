# Video Planning Harness Design

## Overview

The harness simulates an adversarially robust pipeline combining a ChatGPT-like
storyboard generator with a Grok Imagine-like renderer. Both components are
implemented locally to maintain determinism and reproducibility.

## Pipeline components

- `StoryboardGenerator.generate(prompt: str) -> List[StorySegment]`
  - Deterministically tokenises the prompt, derives unique themes, and produces
    twenty segments of six seconds each.
  - Failure modes: raises `ValueError` when the prompt is empty or cannot be
    tokenised into words.
- `ImaginerRenderer.render(prompt: str, storyboard: Iterable[StorySegment])`
  - Hashes the prompt and segment indices to create synthetic colour palettes.
  - Produces captions that concatenate the storyboard title and description.

## API contract

`POST /api/generate`

Request JSON:

```json
{
  "prompt": "string"
}
```

Response JSON:

```json
{
  "storyboard": [
    {
      "index": 0,
      "duration_seconds": 6,
      "title": "Theme focus",
      "description": "Scene narrative"
    }
  ],
  "render_segments": [
    {
      "index": 0,
      "duration_seconds": 6,
      "palette": {
        "red": 0,
        "green": 0,
        "blue": 0,
        "accent": 0
      },
      "caption": "Storyboard text"
    }
  ]
}
```

All payloads are UTF-8 JSON and round-trip safe.

## Reproducibility controls

- The number of segments is fixed at twenty with six-second durations.
- Colour palettes derive from SHA-256 hashes, ensuring deterministic outputs.
- No randomness or system time influences the generated content beyond the
  elapsed time used for client-side animation.

## Future work considerations

- Integrate adversarial prompt perturbation strategies.
- Add JSONL logging when storing pipeline artefacts; none are persisted today.
- Extend tests to simulate attacker-defender loops once additional modules are
  reintroduced.
