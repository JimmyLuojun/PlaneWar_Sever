"""Tests for game/explosion.py - Explosion visual effects."""

import pytest
from unittest.mock import patch, Mock
import pygame
from plane_war_server.game.models.explosion import Explosion, create_explosion


class TestExplosionInit:
    """Tests for Explosion initialization."""

    @patch('pygame.time.get_ticks', return_value=0)
    def test_explosion_init_small(self, mock_ticks):
        """Test small explosion initialization."""
        explosion = Explosion(100, 200, 'small')

        assert explosion.rect.centerx == 100
        assert explosion.rect.centery == 200
        assert explosion.explosion_type == 'small'
        assert explosion.start_time == 0

    @patch('pygame.time.get_ticks', return_value=0)
    def test_explosion_init_medium(self, mock_ticks):
        """Test medium explosion initialization."""
        explosion = Explosion(100, 200, 'medium')

        assert explosion.explosion_type == 'medium'

    @patch('pygame.time.get_ticks', return_value=0)
    def test_explosion_init_large(self, mock_ticks):
        """Test large explosion initialization."""
        explosion = Explosion(100, 200, 'large')

        assert explosion.explosion_type == 'large'

    @patch('pygame.time.get_ticks', return_value=0)
    def test_explosion_init_bomb(self, mock_ticks):
        """Test bomb explosion initialization."""
        explosion = Explosion(100, 200, 'bomb')

        assert explosion.explosion_type == 'bomb'


class TestExplosionUpdate:
    """Tests for Explosion.update method."""

    @patch('pygame.time.get_ticks')
    def test_explosion_updates_visual(self, mock_ticks):
        """Test explosion visual updates over time."""
        mock_ticks.side_effect = [0, 100]  # start, then update
        group = pygame.sprite.Group()
        explosion = Explosion(100, 200, 'small')
        group.add(explosion)

        explosion.update()

        # Should still be alive at 100ms (duration is 500ms)
        assert explosion.alive()

    @patch('pygame.time.get_ticks')
    def test_explosion_expires_after_duration(self, mock_ticks):
        """Test explosion is removed after duration."""
        mock_ticks.side_effect = [0, 600]  # start, then after duration
        explosion = Explosion(100, 200, 'small')

        explosion.update()

        # Should be killed after 600ms (duration is 500ms)
        assert not explosion.alive()

    @patch('pygame.time.get_ticks')
    def test_explosion_stays_alive_within_duration(self, mock_ticks):
        """Test explosion stays alive within duration."""
        mock_ticks.side_effect = [0, 100]
        group = pygame.sprite.Group()
        explosion = Explosion(100, 200, 'small')
        group.add(explosion)

        explosion.update()

        assert explosion.alive()


class TestExplosionVisual:
    """Tests for Explosion visual creation."""

    @patch('pygame.time.get_ticks', return_value=0)
    def test_create_explosion_surface(self, mock_ticks):
        """Test explosion surface creation."""
        explosion = Explosion(100, 200, 'small')
        surface = explosion._create_explosion_surface(20)

        assert isinstance(surface, pygame.Surface)
        assert surface.get_width() == 20
        assert surface.get_height() == 20

    @patch('pygame.time.get_ticks')
    def test_update_explosion_visual_expands_size(self, mock_ticks):
        """Test explosion size expands over time."""
        mock_ticks.side_effect = [0, 250]
        explosion = Explosion(100, 200, 'small')
        initial_size = explosion.image.get_width()

        explosion.update()

        # After update, explosion should have grown
        new_size = explosion.image.get_width()
        assert new_size >= initial_size


class TestCreateExplosionFunction:
    """Tests for create_explosion helper function."""

    @patch('pygame.time.get_ticks', return_value=0)
    def test_create_explosion_adds_to_groups(self, mock_ticks):
        """Test create_explosion adds to multiple sprite groups."""
        group1 = pygame.sprite.Group()
        group2 = pygame.sprite.Group()

        explosion = create_explosion(100, 200, 'medium', (group1, group2))

        assert explosion in group1
        assert explosion in group2

    @patch('pygame.time.get_ticks', return_value=0)
    def test_create_explosion_returns_explosion_instance(self, mock_ticks):
        """Test create_explosion returns Explosion instance."""
        group = pygame.sprite.Group()
        explosion = create_explosion(100, 200, 'small', (group,))

        assert isinstance(explosion, Explosion)
        assert explosion.rect.centerx == 100
        assert explosion.rect.centery == 200
        assert explosion.explosion_type == 'small'
