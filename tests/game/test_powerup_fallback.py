"""Tests for PowerUp fallback image creation when asset missing."""

from unittest.mock import patch
import pygame

from plane_war_server.game.models.powerup import PowerUp
from plane_war_server.game.infrastructure.settings import POWERUP_WIDTH, POWERUP_HEIGHT


@patch("random.choice", return_value="bomb")
def test_powerup_fallback_surface_created(mock_choice):
    images = {}  # Missing 'bomb' image forces fallback
    p = PowerUp(images)
    assert isinstance(p.image, pygame.Surface)
    assert p.image.get_width() == POWERUP_WIDTH
    assert p.image.get_height() == POWERUP_HEIGHT
