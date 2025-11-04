"""Tests for game/enemy.py - Enemy sprites and AI."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pygame
from game.enemy import Enemy, EnemyBoss, compute_intercept_direction
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class TestComputeInterceptDirection:
    """Tests for compute_intercept_direction function."""

    def test_stationary_target(self):
        """Test intercept calculation for stationary target."""
        shoot_pos = pygame.math.Vector2(100, 100)
        target_pos = pygame.math.Vector2(200, 200)
        target_vel = pygame.math.Vector2(0, 0)
        bullet_speed = 10

        direction = compute_intercept_direction(shoot_pos, target_pos, target_vel, bullet_speed)

        assert direction is not None
        expected = (target_pos - shoot_pos).normalize()
        assert abs(direction.x - expected.x) < 0.01
        assert abs(direction.y - expected.y) < 0.01

    def test_moving_target(self):
        """Test intercept calculation for moving target."""
        shoot_pos = pygame.math.Vector2(100, 100)
        target_pos = pygame.math.Vector2(200, 200)
        target_vel = pygame.math.Vector2(5, 0)
        bullet_speed = 20

        direction = compute_intercept_direction(shoot_pos, target_pos, target_vel, bullet_speed)

        assert direction is not None
        assert direction.length() == pytest.approx(1.0, abs=0.01)

    def test_fast_target_fallback(self):
        """Test fallback to current position when target too fast to intercept."""
        shoot_pos = pygame.math.Vector2(100, 100)
        target_pos = pygame.math.Vector2(200, 200)
        target_vel = pygame.math.Vector2(50, 50)
        bullet_speed = 5

        direction = compute_intercept_direction(shoot_pos, target_pos, target_vel, bullet_speed)

        # Should return fallback direction (toward current position), not None
        assert direction is not None
        assert direction.length() == pytest.approx(1.0, abs=0.01)


class TestEnemy:
    """Tests for Enemy class."""

    @patch('random.choice', return_value=2)
    @patch('random.randint')
    def test_enemy_init(self, mock_randint, mock_choice, mock_image):
        """Test enemy initialization."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        mock_randint.side_effect = [400, -50, 3]

        enemy = Enemy(mock_image, (2, 5), (-3, 3))

        assert enemy.rect.x == 400
        assert enemy.rect.y == -50
        assert enemy.speedy == 3
        assert enemy.speedx == 2

    @patch('random.choice', return_value=2)
    @patch('random.randint', side_effect=[400, -50, 3])
    def test_enemy_update_moves_down(self, mock_randint, mock_choice, mock_image):
        """Test enemy moves downward."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        enemy = Enemy(mock_image, (2, 5), (-3, 3))
        initial_y = enemy.rect.y

        enemy.update()

        assert enemy.rect.y > initial_y

    @patch('random.choice', return_value=2)
    @patch('random.randint', side_effect=[400, -50, 3])
    def test_enemy_moves_horizontally(self, mock_randint, mock_choice, mock_image):
        """Test enemy moves horizontally."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        enemy = Enemy(mock_image, (2, 5), (-3, 3))
        initial_x = enemy.rect.x

        enemy.update()

        assert enemy.rect.x != initial_x

    @patch('random.choice', return_value=-2)
    @patch('random.randint', side_effect=[10, -50, 3])
    def test_enemy_bounces_at_left_edge(self, mock_randint, mock_choice, mock_image):
        """Test enemy bounces at left screen edge."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        enemy = Enemy(mock_image, (2, 5), (-3, 3))
        enemy.rect.left = 10
        enemy.speedx = -2

        enemy.update()

        # After moving left by 2, left becomes 8, then update again to trigger bounce
        enemy.update()
        # Now left is 6, move again
        enemy.update()
        # Now left is 4, move again
        enemy.update()
        # Now left is 2, move again
        enemy.update()
        # Now left is 0, move again
        enemy.update()
        # Now left would be -2, so it bounces and speedx becomes positive
        assert enemy.speedx > 0

    @patch('random.choice', return_value=2)
    @patch('random.randint', side_effect=[SCREEN_WIDTH - 70, -50, 3])
    def test_enemy_bounces_at_right_edge(self, mock_randint, mock_choice, mock_image):
        """Test enemy bounces at right screen edge."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        enemy = Enemy(mock_image, (2, 5), (-3, 3))
        # Set x so that after update, right edge exceeds SCREEN_WIDTH
        enemy.rect.x = SCREEN_WIDTH - 60
        enemy.speedx = 2

        enemy.update()

        # After moving right, rect.right > SCREEN_WIDTH, so it bounces
        assert enemy.speedx < 0

    @patch('random.choice', return_value=2)
    @patch('random.randint', side_effect=[400, SCREEN_HEIGHT, 3])
    def test_enemy_removed_when_off_screen(self, mock_randint, mock_choice, mock_image):
        """Test enemy removed when off bottom of screen."""
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
        enemy = Enemy(mock_image, (2, 5), (-3, 3))
        enemy.rect.top = SCREEN_HEIGHT + 10

        enemy.update()

        assert not enemy.alive()


class TestEnemyBoss:
    """Tests for EnemyBoss class."""

    @patch('pygame.time.get_ticks', return_value=0)
    def test_boss_init(self, mock_ticks, mock_image):
        """Test boss initialization."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)

        assert boss.health > 0
        assert boss.entered == False
        assert hasattr(boss, 'speedx')
        assert hasattr(boss, 'entry_speedy')

    @patch('pygame.time.get_ticks', return_value=0)
    def test_boss_entry_sequence(self, mock_ticks, mock_image):
        """Test boss entry sequence movement."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)
        initial_y = boss.rect.y

        boss.update()

        # Boss should move downward during entry
        assert boss.rect.y > initial_y or boss.entered

    @patch('pygame.time.get_ticks', return_value=0)
    def test_boss_transitions_to_active(self, mock_ticks, mock_image):
        """Test boss transitions to active state after entry."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)

        # Force boss to entry position
        boss.rect.centery = boss.entry_y + 10

        boss.update()

        # Boss should be marked as entered
        assert boss.entered == True

    @patch('pygame.time.get_ticks', return_value=0)
    def test_boss_patrol_movement(self, mock_ticks, mock_image):
        """Test boss patrol movement."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)
        boss.entered = True
        initial_x = boss.rect.x

        boss.update()

        # Boss should move horizontally when entered
        assert boss.rect.x != initial_x

    @patch('pygame.time.get_ticks', return_value=0)
    def test_boss_patrol_bounces_at_edges(self, mock_ticks, mock_image):
        """Test boss bounces at screen edges during patrol."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)
        boss.entered = True
        boss.rect.right = SCREEN_WIDTH + 10
        boss.speedx = 2

        boss.update()

        # Boss should reverse direction at right edge
        assert boss.speedx < 0

    @patch('pygame.time.get_ticks', return_value=3000)
    def test_boss_shoot_creates_bullet(self, mock_ticks, mock_image):
        """Test boss shoot creates enemy bullet."""
        mock_sound = Mock()
        mock_sprites = MagicMock()
        mock_bullets = MagicMock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)
        boss.entered = True
        boss.last_shot_time = 0

        boss.update()

        # Boss should have attempted to shoot
        assert boss.last_shot_time > 0

    @patch('pygame.time.get_ticks', return_value=3000)
    def test_boss_shoot_with_target(self, mock_ticks, mock_image):
        """Test boss shoots at target position."""
        mock_sound = Mock()
        mock_sprites = MagicMock()
        mock_bullets = MagicMock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        mock_player = Mock()
        mock_player.rect = pygame.Rect(400, 500, 64, 64)
        # velocity needs to be a Vector2 for compute_intercept_direction
        mock_player.velocity = pygame.math.Vector2(5, 0)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets,
                        target_player=True, player_ref=mock_player)
        boss.entered = True
        boss.last_shot_time = 0

        boss.update()

        # Boss should have shot
        assert boss.last_shot_time > 0

    @patch('pygame.time.get_ticks', return_value=3000)
    def test_boss_shoot_straight_down(self, mock_ticks, mock_image):
        """Test boss shoots straight down without target."""
        mock_sound = Mock()
        mock_sprites = MagicMock()
        mock_bullets = MagicMock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets,
                        target_player=False)
        boss.entered = True
        boss.last_shot_time = 0

        boss.update()

        # Boss should have shot straight down
        assert boss.last_shot_time > 0

    @patch('pygame.draw.rect')
    def test_boss_draw_health_bar(self, mock_draw_rect, mock_surface, mock_image):
        """Test boss health bar drawing."""
        mock_sound = Mock()
        mock_sprites = Mock()
        mock_bullets = Mock()
        mock_image.copy.return_value = mock_image
        mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

        boss = EnemyBoss(mock_image, mock_sound, mock_sprites, mock_bullets)

        boss.draw_health_bar(mock_surface)

        # Should have drawn rectangles for health bar (background, fill, border = 3 calls)
        assert mock_draw_rect.call_count == 3
