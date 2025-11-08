"""Tests for game/player.py - Player sprite and controls."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pygame
from plane_war_server.game.models.player import Player
from plane_war_server.game.infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT


@pytest.fixture
def player_sounds():
    """Create mock sounds for player."""
    return {
        'shoot': Mock(),
        'shield_up': Mock(),
        'shield_down': Mock(),
        'powerup': Mock(),
        'bomb': Mock()
    }


@pytest.fixture
def mock_player_image():
    """Create mock player image."""
    img = MagicMock(spec=pygame.Surface)
    img.copy.return_value = img
    img.get_rect.return_value = pygame.Rect(0, 0, 50, 50)
    return img


class TestPlayerInit:
    """Tests for Player initialization."""

    def test_player_init_success(self, mock_player_image, player_sounds):
        """Test player initialization with valid image."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        assert player.score == 0
        assert player.shield_active == False
        assert player.bomb_count >= 0

    def test_player_init_invalid_image(self, player_sounds):
        """Test player initialization raises ValueError with invalid image."""
        with pytest.raises(ValueError):
            Player(
                None,
                player_sounds['shoot'],
                player_sounds['shield_up'],
                player_sounds['shield_down'],
                player_sounds['powerup'],
                player_sounds['bomb']
            )


class TestPlayerShoot:
    """Tests for Player.shoot method."""

    @patch('pygame.time.get_ticks')
    def test_player_shoot_single_bullet(self, mock_ticks, mock_player_image, player_sounds):
        """Test player shoots single bullet."""
        mock_ticks.side_effect = [0, 1000]  # init, then shoot
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        bullets = player.shoot()

        assert len(bullets) == 1

    @patch('pygame.time.get_ticks')
    def test_player_shoot_respects_delay(self, mock_ticks, mock_player_image, player_sounds):
        """Test player respects shoot delay."""
        mock_ticks.side_effect = [0, 1000, 1050]  # init, shoot1, shoot2 (too soon)
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        bullets1 = player.shoot()
        bullets2 = player.shoot()

        # First should work, second should be empty (too soon)
        assert len(bullets1) > 0
        assert len(bullets2) == 0

    @patch('pygame.time.get_ticks')
    def test_player_shoot_double_bullets(self, mock_ticks, mock_player_image, player_sounds):
        """Test player shoots double bullets with powerup."""
        mock_ticks.side_effect = [0, 1000]  # init, shoot
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.powerup_type = 'double_shot'
        player.powerup_end_time = 2000

        bullets = player.shoot()

        assert len(bullets) == 2


class TestPlayerUpdate:
    """Tests for Player.update method."""

    @patch('pygame.mouse.get_pos', return_value=(300, 400))
    @patch('pygame.time.get_ticks', return_value=0)
    def test_player_update_follows_mouse(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test player follows mouse position."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.update()

        assert player.rect.centerx == 300
        assert player.rect.centery == 400

    @patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    @patch('pygame.time.get_ticks', return_value=10000)
    def test_player_update_expires_shield(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test shield expires after duration."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.shield_active = True
        player.shield_end_time = 100

        player.update()

        assert player.shield_active == False

    @patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    @patch('pygame.time.get_ticks', return_value=10000)
    def test_player_update_expires_double_shot(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test double shot expires after duration."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.powerup_type = 'double_shot'
        player.powerup_end_time = 100

        player.update()

        assert player.powerup_type is None

    @patch('pygame.mouse.get_pos', return_value=(-10, SCREEN_HEIGHT // 2))
    @patch('pygame.time.get_ticks', return_value=0)
    def test_player_update_clamps_left_edge(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test player stays within left edge."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.update()

        assert player.rect.left >= 0

    @patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH + 100, SCREEN_HEIGHT // 2))
    @patch('pygame.time.get_ticks', return_value=0)
    def test_player_update_clamps_right_edge(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test player stays within right edge."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.update()

        assert player.rect.right <= SCREEN_WIDTH

    @patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH // 2, -10))
    @patch('pygame.time.get_ticks', return_value=0)
    def test_player_update_clamps_top_edge(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test player stays within top edge."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.update()

        assert player.rect.top >= 0

    @patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH // 2, SCREEN_HEIGHT + 100))
    @patch('pygame.time.get_ticks', return_value=0)
    def test_player_update_clamps_bottom_edge(self, mock_ticks, mock_mouse, mock_player_image, player_sounds):
        """Test player stays within bottom edge."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.update()

        assert player.rect.bottom <= SCREEN_HEIGHT


class TestPlayerActivatePowerup:
    """Tests for Player.activate_powerup method."""

    @patch('pygame.time.get_ticks', return_value=1000)
    def test_activate_double_shot_powerup(self, mock_ticks, mock_player_image, player_sounds):
        """Test activating double shot powerup."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.activate_powerup('double_shot')

        assert player.powerup_type == 'double_shot'
        assert player.powerup_end_time > 0

    @patch('pygame.time.get_ticks', return_value=1000)
    def test_activate_shield_powerup(self, mock_ticks, mock_player_image, player_sounds):
        """Test activating shield powerup."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )

        player.activate_powerup('shield')

        assert player.shield_active == True

    def test_activate_bomb_powerup(self, mock_player_image, player_sounds):
        """Test activating bomb powerup."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        initial_bombs = player.bomb_count

        player.activate_powerup('bomb')

        assert player.bomb_count == initial_bombs + 1


class TestPlayerDrawShield:
    """Tests for Player.draw_shield method."""

    @patch('pygame.draw.circle')
    def test_draw_shield_when_active(self, mock_draw, mock_player_image, player_sounds, mock_surface):
        """Test shield is drawn when active."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.shield_active = True

        player.draw_shield(mock_surface)

        mock_draw.assert_called_once()

    @patch('pygame.draw.circle')
    def test_draw_shield_not_drawn_when_inactive(self, mock_draw, mock_player_image, player_sounds, mock_surface):
        """Test shield not drawn when inactive."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.shield_active = False

        player.draw_shield(mock_surface)

        mock_draw.assert_not_called()


class TestPlayerUseBomb:
    """Tests for Player.use_bomb method."""

    def test_use_bomb_kills_enemies(self, mock_player_image, player_sounds):
        """Test bomb kills all enemies."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.bomb_count = 1
        enemies = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()

        # Add actual sprite enemies (mocks don't work with sprite.Group)
        for _ in range(3):
            enemy = pygame.sprite.Sprite()
            enemy.rect = pygame.Rect(0, 0, 32, 32)
            enemies.add(enemy)

        result = player.use_bomb(enemies, enemy_bullets)

        assert result == 3  # Returns count of killed enemies
        assert player.bomb_count == 0

    def test_use_bomb_no_bombs_available(self, mock_player_image, player_sounds):
        """Test bomb does nothing when none available."""
        player = Player(
            mock_player_image,
            player_sounds['shoot'],
            player_sounds['shield_up'],
            player_sounds['shield_down'],
            player_sounds['powerup'],
            player_sounds['bomb']
        )
        player.bomb_count = 0
        enemies = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()

        result = player.use_bomb(enemies, enemy_bullets)

        assert result == 0
