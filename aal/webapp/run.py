"""Command-line entry point for serving the web application."""
from __future__ import annotations

from wsgiref.simple_server import make_server

from .app import create_app


def main() -> None:
    """Run a development WSGI server on localhost:8000."""

    app = create_app()
    with make_server("0.0.0.0", 8000, app) as httpd:
        print("Serving on http://localhost:8000")  # noqa: T201 - developer convenience
        httpd.serve_forever()


if __name__ == "__main__":
    main()
