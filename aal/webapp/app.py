"""Minimal WSGI application serving the deterministic video planning UI."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable

from .pipeline import VideoPipeline

ASSET_DIR = Path(__file__).resolve().parent / "static"


class WebApplication:
    """Simple WSGI application exposing the storyboard pipeline."""

    def __init__(self, pipeline: VideoPipeline | None = None) -> None:
        self._pipeline = pipeline or VideoPipeline()

    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        if method == "GET" and path == "/":
            return self._serve_asset("index.html", "text/html", start_response)
        if method == "GET" and path.startswith("/static/"):
            asset = path.replace("/static/", "")
            return self._serve_asset(asset, _content_type_for(asset), start_response)
        if method == "POST" and path == "/api/generate":
            return self._handle_generate(environ, start_response)

        start_response("404 NOT FOUND", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    def _serve_asset(self, name: str, content_type: str, start_response: Callable) -> Iterable[bytes]:
        asset_path = ASSET_DIR / name
        if not asset_path.is_file():
            start_response("404 NOT FOUND", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Asset not found"]
        payload = asset_path.read_bytes()
        start_response("200 OK", [("Content-Type", content_type), ("Content-Length", str(len(payload)))])
        return [payload]

    def _handle_generate(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        try:
            length = int(environ.get("CONTENT_LENGTH", "0"))
        except ValueError:
            length = 0
        body = environ.get("wsgi.input").read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive path
            start_response("400 BAD REQUEST", [("Content-Type", "application/json")])
            return [json.dumps({"error": f"Invalid JSON: {exc}"}).encode("utf-8")]

        prompt = str(payload.get("prompt", ""))
        try:
            plan = self._pipeline.create_plan(prompt)
        except ValueError as exc:
            start_response("400 BAD REQUEST", [("Content-Type", "application/json")])
            return [json.dumps({"error": str(exc)}).encode("utf-8")]

        response = {
            "storyboard": [
                {
                    "index": segment.index,
                    "duration_seconds": segment.duration_seconds,
                    "title": segment.title,
                    "description": segment.description,
                }
                for segment in plan.storyboard
            ],
            "render_segments": [
                {
                    "index": segment.index,
                    "duration_seconds": segment.duration_seconds,
                    "palette": segment.palette,
                    "caption": segment.caption,
                }
                for segment in plan.render_segments
            ],
            "merged_video": {
                "duration_seconds": plan.merged_video.duration_seconds,
                "segment_order": list(plan.merged_video.segment_order),
                "transitions": [
                    {
                        "from_index": transition.from_index,
                        "to_index": transition.to_index,
                        "style": transition.style,
                        "duration_seconds": transition.duration_seconds,
                    }
                    for transition in plan.merged_video.transitions
                ],
            },
        }
        payload_bytes = json.dumps(response).encode("utf-8")
        start_response(
            "200 OK",
            [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(payload_bytes))),
            ],
        )
        return [payload_bytes]


def _content_type_for(asset_name: str) -> str:
    if asset_name.endswith(".js"):
        return "application/javascript"
    if asset_name.endswith(".css"):
        return "text/css"
    return "text/plain; charset=utf-8"


def create_app() -> WebApplication:
    """Factory returning the WSGI application instance."""

    return WebApplication()


__all__ = ["WebApplication", "create_app"]
