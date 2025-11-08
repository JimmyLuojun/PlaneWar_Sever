"""Tests for server/config.py configuration and get_config."""

import os

from plane_war_server.config import get_config, DevelopmentConfig, ProductionConfig, TestConfig


def test_get_config_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    assert get_config() is DevelopmentConfig


def test_get_config_production(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    cfg = get_config()
    assert cfg is ProductionConfig


def test_get_config_testing(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "testing")
    assert get_config() is TestConfig
