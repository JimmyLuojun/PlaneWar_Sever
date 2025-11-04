"""Tests for server/progress_store.py - per-user progress JSON store."""

import json
import os

import pytest

from server import progress_store as ps


@pytest.fixture()
def temp_progress_file(tmp_path, monkeypatch):
    path = tmp_path / "user_progress.json"
    monkeypatch.setattr(ps, "PROGRESS_FILE", str(path))
    return path


def test_default_when_file_missing(temp_progress_file):
    # No file present -> default should be 1
    assert ps.get_max_unlocked_level_for_user(123) == 1


def test_set_and_get_persists(temp_progress_file):
    # Set value and ensure it persists
    stored = ps.set_max_unlocked_level_for_user(42, 5)
    assert stored == 5
    # New instance read
    assert ps.get_max_unlocked_level_for_user(42) == 5


def test_coerce_non_int_and_negative(temp_progress_file):
    # Negative input should not crash; default read remains 1
    assert ps.get_max_unlocked_level_for_user(7) == 1
    # Write a non-int in file and ensure loader coerces to int
    with open(ps.PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"7": "4"}, f)
    assert ps.get_max_unlocked_level_for_user(7) == 4


def test_invalid_json_graceful(temp_progress_file):
    # Write invalid JSON and ensure it falls back safely
    with open(ps.PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write("{ invalid JSON")
    assert ps.get_max_unlocked_level_for_user(99) == 1
