"""Tests for progress syncing behavior in game/states.py."""

from unittest.mock import patch, Mock

from game import states


import pygame
import pytest


@pytest.fixture
def deps():
    pygame.init()
    screen = Mock()
    clock = Mock()
    fonts = {"title": Mock(), "medium": Mock(), "score": Mock(), "small": Mock()}
    images = {"player": Mock(), "boss": Mock(), "enemy1": Mock()}
    sounds = {"shoot": Mock(), "explosion": Mock()}
    levels = [
        {"level_number": 1, "enemy_types": ["enemy1"]},
        {"level_number": 2, "enemy_types": ["enemy1", "enemy2"]},
    ]
    music_paths = {}
    background = Mock()
    network_client = Mock()
    network_client.is_authenticated = False
    return {
        "screen": screen,
        "clock": clock,
        "fonts": fonts,
        "images": images,
        "sounds": sounds,
        "levels": levels,
        "music_paths": music_paths,
        "background": background,
        "high_score": 0,
        "network_client": network_client,
    }


@patch("game.states.ui")
@patch("game.states.progress")
def test_login_fetches_progress(mock_progress, mock_ui, deps):
    # Arrange: login succeeds, then quit at start screen
    mock_ui.show_login_screen.return_value = ("LOGIN_SUCCESS", "tester", "ok")
    mock_ui.show_start_screen.return_value = "QUIT"

    # Mock server progress
    mock_client = deps["network_client"]
    mock_client.is_authenticated = True
    prog_res = Mock(success=True, max_unlocked_level=4)
    mock_client.get_progress.return_value = prog_res

    # Act
    states.run_state_machine(**deps)

    # Assert: save_progress called with 4
    mock_progress.save_progress.assert_called_with(4)


@patch("game.states.run_game")
@patch("game.states.ui")
@patch("game.states.progress")
def test_set_progress_after_pass(mock_progress, mock_ui, mock_run_game, deps):
    # Arrange: login -> level 1 -> pass -> end -> quit
    mock_ui.show_login_screen.return_value = ("LOGIN_SUCCESS", "tester", "ok")
    mock_ui.show_start_screen.side_effect = ["LEVEL_1", "QUIT"]
    mock_ui.show_level_start_screen.return_value = "CONTINUE"
    mock_run_game.return_value = ("PASSED", 1000, 1)
    mock_ui.show_end_screen.return_value = "QUIT"

    mock_client = deps["network_client"]
    mock_client.is_authenticated = True
    mock_progress.get_max_unlocked_level.return_value = 1

    # Act
    states.run_state_machine(**deps)

    # Assert: server set_progress called with at least 2
    assert mock_client.set_progress.called
    args, kwargs = mock_client.set_progress.call_args
    assert args[0] >= 2
