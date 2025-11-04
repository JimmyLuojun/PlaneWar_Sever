"""Extra tests for EnemyBoss multi-shot spread behavior."""

from unittest.mock import Mock, MagicMock
import pygame

from game.enemy import EnemyBoss


def test_boss_triple_shot_spread_creates_three_bullets(mock_image):
    mock_sound = Mock()
    mock_sprites = MagicMock()
    mock_bullets = MagicMock()
    mock_image.copy.return_value = mock_image
    mock_image.get_rect.return_value = pygame.Rect(0, 0, 100, 100)

    boss = EnemyBoss(
        mock_image,
        mock_sound,
        mock_sprites,
        mock_bullets,
        target_player=False,
        shot_count=3,
        shot_spread_degrees=20,
    )

    boss.entered = True
    # Reset adds to ignore boss self-add during init
    mock_sprites.add.reset_mock()
    mock_bullets.add.reset_mock()
    # Call shoot directly to bypass shoot_delay timing
    boss.shoot()

    # Expect 3 bullets added to both groups
    assert mock_sprites.add.call_count == 3
    assert mock_bullets.add.call_count == 3
