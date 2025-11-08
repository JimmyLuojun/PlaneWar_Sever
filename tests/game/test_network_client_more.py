"""Additional tests for game/network_client.py to improve coverage."""

import json
from json import JSONDecodeError
from unittest.mock import patch, Mock

import requests

from plane_war_server.game.network_client import NetworkClient


@patch("requests.Session.post")
def test_login_json_decode_error(mock_post):
    client = NetworkClient("http://localhost:8000")
    resp = Mock()
    resp.status_code = 200
    resp.json.side_effect = JSONDecodeError("bad", "{}", 0)
    mock_post.return_value = resp
    res = client.login("u", "p")
    assert res.success is False


@patch("requests.Session.post")
def test_logout_json_decode_error(mock_post):
    client = NetworkClient("http://localhost:8000")
    resp = Mock()
    resp.status_code = 200
    resp.json.side_effect = JSONDecodeError("bad", "{}", 0)
    mock_post.return_value = resp
    client.user_id = 1
    r = client.logout()
    assert r.success is False
    assert client.user_id is None


@patch("requests.Session.post")
def test_submit_score_json_decode_error(mock_post):
    client = NetworkClient("http://localhost:8000")
    client.user_id = 2
    resp = Mock()
    resp.status_code = 200
    resp.json.side_effect = JSONDecodeError("bad", "{}", 0)
    mock_post.return_value = resp
    r = client.submit_score(10, 1)
    assert r.success is False


def test_get_progress_unauthenticated():
    client = NetworkClient("http://localhost:8000")
    res = client.get_progress()
    assert res.success is False and res.max_unlocked_level is None


@patch("requests.Session.get")
def test_get_progress_401_clears_auth(mock_get):
    client = NetworkClient("http://localhost:8000")
    client.user_id = 5
    resp = Mock()
    resp.status_code = 401
    mock_get.return_value = resp
    res = client.get_progress()
    assert res.success is False
    assert not client.is_authenticated


@patch("requests.Session.post")
def test_set_progress_401_clears_auth(mock_post):
    client = NetworkClient("http://localhost:8000")
    client.user_id = 5
    resp = Mock()
    resp.status_code = 401
    mock_post.return_value = resp
    res = client.set_progress(3)
    assert res.success is False
    assert not client.is_authenticated


@patch("requests.Session.get")
def test_get_leaderboard_json_decode_error(mock_get):
    client = NetworkClient("http://localhost:8000")
    resp = Mock()
    resp.status_code = 200
    resp.json.side_effect = JSONDecodeError("bad", "{}", 0)
    mock_get.return_value = resp
    res = client.get_leaderboard()
    assert res == []
