import pytest
import pygame
from unittest.mock import MagicMock

from game.enemy import Enemy, EnemyBullet, EnemyBoss
from game.settings import SCREEN_HEIGHT, ENEMY_BULLET_SPEED_Y


def test_enemy_moves_down_and_kills_offscreen(mock_surface):
    # Arrange: create an Enemy and spy on kill()
    enemy = Enemy(enemy_img=mock_surface, speed_y_range=(1, 1), speed_x_range=(0, 0))
    enemy.kill = MagicMock()
    # Position just below the bottom
    enemy.rect.top = SCREEN_HEIGHT + 1

    # Act
    enemy.update()

    # Assert
    enemy.kill.assert_called_once()


def test_enemy_speed_applies(mock_surface):
    # Arrange: enemy falls at speed 3
    enemy = Enemy(enemy_img=mock_surface, speed_y_range=(3, 3), speed_x_range=(0, 0))
    original_y = enemy.rect.y

    # Act
    enemy.update()

    # Assert
    assert enemy.rect.y == original_y + 3


def test_enemy_bullet_moves_and_kills(mock_groups, monkeypatch):
    # Arrange: patch pygame.Surface to use a mock surface
    fake_surf = mock_groups['all_sprites']  # not used directly
    # Instantiate bullet and spy on kill()
    bullet = EnemyBullet(100, 50)
    bullet.kill = MagicMock()
    # Move bullet off-screen
    bullet.rect.top = SCREEN_HEIGHT + 1

    # Act
    bullet.update()

    # Assert kill() called
    bullet.kill.assert_called_once()


def test_enemy_bullet_speed(mock_groups):
    # Arrange
    bullet = EnemyBullet(0, 0)
    original_y = bullet.rect.y

    # Act
    bullet.update()

    # Assert
    assert bullet.rect.y == original_y + ENEMY_BULLET_SPEED_Y


def test_boss_added_to_group_on_init(mock_surface, mock_sounds, mock_groups):
    # Arrange
    all_sprites = mock_groups['all_sprites']
    enemy_bullets = mock_groups['enemy_bullets']
    shoot_sound = mock_sounds['boss_shoot']

    # Act
    boss = EnemyBoss(mock_surface, shoot_sound, all_sprites, enemy_bullets)

    # Assert boss was added to all_sprites
    all_sprites.add.assert_called_with(boss)


def test_boss_shoot_creates_bullet_and_plays_sound(mock_surface, mock_sounds, mock_groups):
    # Arrange
    all_sprites = mock_groups['all_sprites']
    enemy_bullets = mock_groups['enemy_bullets']
    shoot_sound = mock_sounds['boss_shoot']
    boss = EnemyBoss(mock_surface, shoot_sound, all_sprites, enemy_bullets)

    # Reset mocks
    all_sprites.add.reset_mock()
    enemy_bullets.add.reset_mock()
    shoot_sound.play.reset_mock()

    # Act
    boss.shoot()

    # Assert a bullet was added and sound played
    enemy_bullets.add.assert_called_once()
    all_sprites.add.assert_called_once()
    shoot_sound.play.assert_called_once()


def test_boss_take_damage_and_die(mock_surface, mock_sounds, mock_groups):
    # Arrange
    all_sprites = mock_groups['all_sprites']
    enemy_bullets = mock_groups['enemy_bullets']
    shoot_sound = mock_sounds['boss_shoot']
    boss = EnemyBoss(mock_surface, shoot_sound, all_sprites, enemy_bullets)
    boss.kill = MagicMock()

    # Act & Assert: boss takes damage but survives
    boss.health = 5
    boss.take_damage(3)
    assert boss.health == 2
    shoot_sound.play.assert_called_once()

    # Act & Assert: boss takes fatal damage
    shoot_sound.play.reset_mock()
    boss.take_damage(5)
    boss.kill.assert_called_once()
    shoot_sound.play.assert_called_once()
