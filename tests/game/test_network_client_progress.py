"""Tests for progress endpoints integration in NetworkClient (mocked HTTP)."""

from unittest.mock import patch, Mock

from plane_war_server.game.network_client import NetworkClient


@patch("requests.Session.get")
def test_get_progress_success(mock_get):
    client = NetworkClient("http://localhost:8000")
    client.user_id = 5  # mark as authenticated
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"success": True, "max_unlocked_level": 4}
    mock_get.return_value = mock_resp

    res = client.get_progress()
    assert res.success and res.max_unlocked_level == 4


@patch("requests.Session.post")
def test_set_progress_success(mock_post):
    client = NetworkClient("http://localhost:8000")
    client.user_id = 5
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"success": True, "max_unlocked_level": 6}
    mock_post.return_value = mock_resp

    res = client.set_progress(6)
    assert res.success and res.max_unlocked_level == 6
