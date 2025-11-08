"""Plane War Server package.

Provides the Flask application factory and layered architecture modules.
"""

from .main import create_app

__all__ = ["create_app"]

