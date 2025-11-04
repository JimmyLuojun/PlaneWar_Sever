"""Server package initializer.

Exposes the canonical Flask application factory used by the project.
Tests and external code should import `create_app` from `server.app`.
This module re-exports that function to avoid duplication.
"""

from .app import create_app  # re-export for convenience

__all__ = ["create_app"]
