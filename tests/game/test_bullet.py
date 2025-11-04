"""Tests for game/bullet.py - Bullet sprites."""

import pytest
from unittest.mock import patch, Mock
import pygame
from game.bullet import Bullet, EnemyBullet
from game.settings import SCREEN_HEIGHT, SCREEN_WIDTH


class TestBullet:
    """Tests for Bullet class (player bullets)."""

    def test_bullet_init(self):
        """Test bullet initialization."""
        bullet = Bullet(100, 200)

        assert bullet.rect.centerx == 100
        assert bullet.rect.centery == 200
        assert hasattr(bullet, 'speedy')

    def test_bullet_update_moves_upward(self):
        """Test bullet moves upward."""
        bullet = Bullet(100, 200)
        initial_y = bullet.rect.y

        bullet.update()

        assert bullet.rect.y < initial_y

    def test_bullet_removed_when_off_screen(self):
        """Test bullet is removed when moving off top of screen."""
        bullet = Bullet(100, -10)

        bullet.update()

        assert not bullet.alive()


class TestEnemyBullet:
    """Tests for EnemyBullet class."""

    def test_enemy_bullet_init_default_direction(self):
        """Test enemy bullet initialization with default direction."""
        bullet = EnemyBullet(100, 200)

        assert bullet.rect.centerx == 100
        assert bullet.rect.top == 200
        assert bullet.velocity.x == 0
        assert bullet.velocity.y > 0  # Moving downward

    def test_enemy_bullet_init_custom_direction(self):
        """Test enemy bullet initialization with custom direction."""
        custom_dir = pygame.math.Vector2(1, 1).normalize()
        bullet = EnemyBullet(100, 200, custom_dir)

        # velocity = direction * speed, so check velocity direction matches
        assert bullet.velocity.x > 0
        assert bullet.velocity.y > 0
        # Check the velocity is in the same direction as custom_dir
        normalized_velocity = bullet.velocity.normalize()
        assert abs(normalized_velocity.x - custom_dir.x) < 0.01
        assert abs(normalized_velocity.y - custom_dir.y) < 0.01

    def test_enemy_bullet_update_moves_by_direction(self):
        """Test enemy bullet moves according to direction vector."""
        bullet = EnemyBullet(100, 200, pygame.math.Vector2(0, 1))
        initial_y = bullet.pos.y

        bullet.update()

        assert bullet.pos.y > initial_y
        assert bullet.rect.centery == int(bullet.pos.y)

    def test_enemy_bullet_removed_when_off_screen_bottom(self):
        """Test enemy bullet removed when off bottom."""
        bullet = EnemyBullet(100, SCREEN_HEIGHT + 10)

        bullet.update()

        assert not bullet.alive()

    def test_enemy_bullet_removed_when_off_screen_top(self):
        """Test enemy bullet removed when off top."""
        bullet = EnemyBullet(100, -10)

        bullet.update()

        assert not bullet.alive()

    def test_enemy_bullet_removed_when_off_screen_left(self):
        """Test enemy bullet removed when off left edge."""
        bullet = EnemyBullet(-10, 100)

        bullet.update()

        assert not bullet.alive()

    def test_enemy_bullet_removed_when_off_screen_right(self):
        """Test enemy bullet removed when off right edge."""
        bullet = EnemyBullet(SCREEN_WIDTH + 10, 100)

        bullet.update()

        assert not bullet.alive()

    def test_enemy_bullet_diagonal_movement(self):
        """Test enemy bullet moves diagonally with proper direction."""
        direction = pygame.math.Vector2(1, 1).normalize()
        bullet = EnemyBullet(100, 100, direction)
        initial_x = bullet.pos.x
        initial_y = bullet.pos.y

        bullet.update()

        assert bullet.pos.x > initial_x
        assert bullet.pos.y > initial_y
