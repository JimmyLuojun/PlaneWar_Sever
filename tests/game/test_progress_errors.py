"""Additional tests for game/progress.py error paths."""

import json
from pathlib import Path

import pytest

from plane_war_server.game.infrastructure import progress


@pytest.fixture()
def temp_progress(monkeypatch, tmp_path):
    p = tmp_path / "progress.json"
    monkeypatch.setattr(progress, "PROGRESS_FILE_PATH", str(p))
    return p


def test_load_progress_invalid_json_defaults(temp_progress):
    Path(progress.PROGRESS_FILE_PATH).write_text("{ invalid", encoding="utf-8")
    data = progress.load_progress()
    assert data[progress.KEY_MAX_UNLOCKED_LEVEL] == progress.DEFAULT_MAX_UNLOCKED_LEVEL
