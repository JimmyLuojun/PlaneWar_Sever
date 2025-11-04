"""Fixtures for server-side tests.

Sets up a test Flask app, client, and database session to be used by
other test modules. This ensures a clean, isolated environment for each test.
"""

import pytest

from server.app import create_app
from server.config import TestConfig
from server.extensions import db as _db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app):
    """A database for the app."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.remove()
    _db.drop_all()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()