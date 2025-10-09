# Video Planning Harness Design

## Overview

The harness simulates an adversarially robust pipeline combining a ChatGPT-like
storyboard generator with a Grok Imagine-like renderer. Both components are
implemented locally to maintain determinism and reproducibility. Outputs remain
structured plans plus a deterministic WebM recording emitted by the browser via
`MediaRecorder`. During export the client replays the same drawing logic used for
the live preview, pushing frames directly into the recorder when
`CanvasCaptureMediaStreamTrack.requestFrame` is available and falling back to a
paced capture loop otherwise. The result keeps the evaluation loop lightweight
and free from external codecs while remaining usable across browsers.

## Pipeline components

- `StoryboardGenerator.generate(prompt: str) -> List[StorySegment]`
  - Deterministically tokenises the prompt, derives unique themes, and produces
    twenty segments of six seconds each.
  - Failure modes: raises `ValueError` when the prompt is empty or cannot be
    tokenised into words.
- `ImaginerRenderer.render(prompt: str, storyboard: Iterable[StorySegment])`
  - Hashes the prompt and segment indices to create synthetic colour palettes.
  - Produces captions that concatenate the storyboard title and description.
- `VideoAssembler.assemble(segments: Sequence[RenderSegment]) -> MergedVideo`
  - Validates that the twenty render segments are in sequential order.
  - Produces a deterministic two-minute timeline with uniform crossfade
    transitions to merge the segments smoothly.

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
  ],
  "merged_video": {
    "duration_seconds": 120,
    "segment_order": [0, 1, 2],
    "transitions": [
      {
        "from_index": 0,
        "to_index": 1,
        "style": "crossfade",
        "duration_seconds": 0.75
      }
    ]
  }
}
```

All payloads are UTF-8 JSON and round-trip safe.

## Reproducibility controls

- The number of segments is fixed at twenty with six-second durations.
- Colour palettes derive from SHA-256 hashes, ensuring deterministic outputs.
- No randomness or system time influences the generated content beyond the
  elapsed time used for client-side animation.
- WebM export regenerates the full frame sequence deterministically; manual
  frame pushes collapse the runtime to seconds when supported while the paced
  fallback still preserves identical imagery.

## Future work considerations

- Integrate adversarial prompt perturbation strategies.
- Add JSONL logging when storing pipeline artefacts; none are persisted today.
- Extend tests to simulate attacker-defender loops once additional modules are
  reintroduced.
