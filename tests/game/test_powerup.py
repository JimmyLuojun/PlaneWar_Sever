"""Tests for game/powerup.py - Power-up sprites."""

import pytest
from unittest.mock import patch, Mock
import pygame
from game.powerup import PowerUp
from game.settings import SCREEN_HEIGHT


class TestPowerUpInit:
    """Tests for PowerUp initialization."""

    @patch('random.choice', return_value='double_shot')
    @patch('random.randint', return_value=400)
    def test_powerup_init_random_type(self, mock_randint, mock_choice):
        """Test powerup initialization with random type selection."""
        images = {
            'double_shot': Mock(spec=pygame.Surface),
            'shield': Mock(spec=pygame.Surface),
            'bomb': Mock(spec=pygame.Surface)
        }
        for img in images.values():
            img.get_rect.return_value = pygame.Rect(0, 0, 32, 32)

        powerup = PowerUp(images)

        assert powerup.type == 'double_shot'
        assert powerup.rect.x == 400  # randint returns x position, not centerx

    def test_powerup_init_shield_type(self):
        """Test powerup initialization with shield type."""
        images = {
            'double_shot': Mock(spec=pygame.Surface),
            'shield': Mock(spec=pygame.Surface),
            'bomb': Mock(spec=pygame.Surface)
        }
        for img in images.values():
            img.get_rect.return_value = pygame.Rect(0, 0, 32, 32)

        with patch('random.choice', return_value='shield'):
            powerup = PowerUp(images)

        assert powerup.type == 'shield'

    def test_powerup_init_bomb_type(self):
        """Test powerup initialization with bomb type."""
        images = {
            'double_shot': Mock(spec=pygame.Surface),
            'shield': Mock(spec=pygame.Surface),
            'bomb': Mock(spec=pygame.Surface)
        }
        for img in images.values():
            img.get_rect.return_value = pygame.Rect(0, 0, 32, 32)

        with patch('random.choice', return_value='bomb'):
            powerup = PowerUp(images)

        assert powerup.type == 'bomb'


class TestPowerUpUpdate:
    """Tests for PowerUp.update method."""

    @patch('random.choice', return_value='double_shot')
    @patch('random.randint', return_value=400)
    def test_powerup_update_moves_down(self, mock_randint, mock_choice):
        """Test powerup moves downward."""
        images = {
            'double_shot': Mock(spec=pygame.Surface),
            'shield': Mock(spec=pygame.Surface),
            'bomb': Mock(spec=pygame.Surface)
        }
        for img in images.values():
            img.get_rect.return_value = pygame.Rect(0, 0, 32, 32)

        powerup = PowerUp(images)
        initial_y = powerup.rect.y

        powerup.update()

        assert powerup.rect.y > initial_y

    @patch('random.choice', return_value='double_shot')
    @patch('random.randint', return_value=400)
    def test_powerup_removed_when_off_screen(self, mock_randint, mock_choice):
        """Test powerup removed when off bottom of screen."""
        images = {
            'double_shot': Mock(spec=pygame.Surface),
            'shield': Mock(spec=pygame.Surface),
            'bomb': Mock(spec=pygame.Surface)
        }
        for img in images.values():
            img.get_rect.return_value = pygame.Rect(0, 0, 32, 32)

        group = pygame.sprite.Group()
        powerup = PowerUp(images)
        group.add(powerup)
        powerup.rect.top = SCREEN_HEIGHT + 10

        powerup.update()

        assert not powerup.alive()
