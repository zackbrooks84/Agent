# AAL Video Planning Harness

This repository provides a deterministic, research-grade harness for studying
storyboard generation under adversarial conditions. The current focus is an
offline simulation of a user-facing website where a prompt drives both
storyboard scripting (ChatGPT analogue) and video rendering directives (Grok
Imagine analogue). All components remain local and deterministic to keep the
continuous integration (CI) environment reproducible.

## Running the web application

```bash
python -m aal.webapp.run
```

The command launches a WSGI server on `http://localhost:8000` serving the
single-page interface. Users enter a prompt describing the desired video. The
backend produces a 2 minute plan comprised of twenty 6-second segments. These
segments are deterministically merged into a single timeline with crossfade
transitions to maintain smooth playback.

### Deterministic WebM export

The frontend renders each segment on a `<canvas>` element and then encodes
those synthetic frames into a WebM file entirely within the browser. When the
`Download Deterministic WebM` button is pressed the harness:

1. Regenerates every frame deterministically using the same drawing logic as
   the live preview.
2. Streams the frames through the `MediaRecorder` API using manual frame pushes
   when supported so the full two minute video materialises within a few
   seconds.
3. Falls back to a paced capture loop when the browser cannot accept manual
   frames, ensuring every environment still emits a valid WebM even if the
   export takes the full 120 seconds.

Researchers can inspect the storyboard, render directives, merged timeline
JSON, or the exported WebM without introducing external encoders or
nondeterministic assets.

## Tests

```bash
pytest -q
```

## Project layout

- `aal/webapp/pipeline.py` – deterministic storyboard and render planning
  logic.
- `aal/webapp/app.py` – WSGI application exposing the planning API and static
  assets.
- `aal/webapp/static/` – user interface assets (HTML, CSS, JS).
- `tests/` – unit tests covering invariants and behavioural expectations.
- `docs/design.md` – documentation of API payloads and reproducibility
  considerations.

## Safety & reproducibility

- No external network calls: pipeline relies entirely on hashing and prompt
  tokenisation.
- Deterministic outputs: identical prompts yield identical plans.
- Fixed durations: exactly twenty 6-second segments per video ensuring two
  minutes total runtime with deterministic crossfade transitions between
  segments.

## License

The repository retains its original license (see `LICENSE`).
