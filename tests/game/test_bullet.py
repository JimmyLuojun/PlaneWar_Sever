# tests/game/test_bullet.py
import pytest
import pygame
from unittest.mock import MagicMock, patch
from game.bullet import Bullet, EnemyBullet
# Assuming settings are in tests/../game/settings.py relative to tests
# If not, adjust the import path accordingly.
# It's often better to explicitly import needed constants
# instead of using '*'.
# Example: from game.settings import (SCREEN_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT,
#                                   BULLET_SPEED, YELLOW, ENEMY_BULLET_WIDTH, ...)
from game.settings import *

# Helper function to create a mock rect with specific attributes
# (Keep this function as it is)
def create_mock_rect(mocker, **kwargs):
    """Creates a MagicMock Rect and sets attributes from kwargs."""
    rect = mocker.MagicMock(spec=pygame.Rect)
    # Set default attributes that might be accessed
    rect.x = 0
    rect.y = 0
    rect.width = kwargs.get('width', 10) # Use provided or default size
    rect.height = kwargs.get('height', 10)

    # Apply keyword arguments passed to the mock get_rect (like center, top, etc.)
    # This simulates pygame's behavior more closely
    for key, value in kwargs.items():
        setattr(rect, key, value)

    # Update related attributes based on initial kwargs (simplified calculation)
    # Note: This is a simplified model. Real pygame.Rect updates are more complex.
    # We prioritize setting the explicitly provided kwargs first.
    if 'center' in kwargs:
        rect.centerx = kwargs['center'][0]
        rect.centery = kwargs['center'][1]
        rect.x = rect.centerx - rect.width // 2
        rect.y = rect.centery - rect.height // 2
    elif 'centerx' in kwargs:
        rect.x = kwargs['centerx'] - rect.width // 2
        if 'centery' not in kwargs: # Estimate centery if not given
            rect.centery = rect.y + rect.height // 2
    elif 'centery' in kwargs:
        rect.y = kwargs['centery'] - rect.height // 2
        if 'centerx' not in kwargs: # Estimate centerx if not given
             rect.centerx = rect.x + rect.width // 2
    # Apply other positioning attributes if center wasn't the primary setter
    if 'center' not in kwargs:
        if 'top' in kwargs:
            rect.y = kwargs['top']
        elif 'bottom' in kwargs:
            rect.y = kwargs['bottom'] - rect.height
        if 'left' in kwargs:
            rect.x = kwargs['left']
        elif 'right' in kwargs:
            rect.x = kwargs['right'] - rect.width

    # Ensure all related attributes are consistent after applying kwargs
    rect.right = rect.x + rect.width
    rect.left = rect.x
    rect.bottom = rect.y + rect.height
    rect.top = rect.y
    rect.centerx = rect.x + rect.width // 2
    rect.centery = rect.y + rect.height // 2
    rect.center = (rect.centerx, rect.centery)

    return rect

# --- Player Bullet Tests ---

# Patch pygame.Surface specifically where it's used in the bullet module
@patch('game.bullet.pygame.Surface')
def test_player_bullet_init(mock_pygame_surface_class, mocker):
    """Test player Bullet initialization sets rect position correctly."""
    start_x, start_y = 100, 200
    # --- Configure the MOCK INSTANCE returned by the PATCHED CLASS ---
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    # Configure the get_rect method of the INSTANCE
    # Use the helper to create a mock rect configured as needed
    mock_rect = create_mock_rect(mocker, center=(start_x, start_y), width=BULLET_WIDTH, height=BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect
    # Tell the PATCHED CLASS what instance to return when called
    mock_pygame_surface_class.return_value = mock_surf_instance
    # --- End Configuration ---

    bullet = Bullet(start_x, start_y)

    # Check the patched CLASS was called to create the surface
    mock_pygame_surface_class.assert_called_once_with((BULLET_WIDTH, BULLET_HEIGHT))
    # Check fill was called on the INSTANCE returned by the class
    bullet.image.fill.assert_called_once_with(YELLOW)
    # Check get_rect was called on the INSTANCE with the correct arguments
    bullet.image.get_rect.assert_called_once_with(center=(start_x, start_y))

    # Check rect position was set correctly via the mock rect
    assert bullet.rect is mock_rect # Ensure the bullet is using the mock rect we configured
    assert bullet.rect.center == (start_x, start_y)
    assert bullet.rect.x == start_x - BULLET_WIDTH // 2
    assert bullet.rect.y == start_y - BULLET_HEIGHT // 2

    assert bullet.speedy == -BULLET_SPEED
    assert isinstance(bullet, pygame.sprite.Sprite)

@patch('game.bullet.pygame.Surface')
def test_player_bullet_update_move(mock_pygame_surface_class, mocker):
    """Test player Bullet movement updates rect.y correctly."""
    start_x, start_y = 100, 200
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, center=(start_x, start_y), width=BULLET_WIDTH, height=BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    bullet = Bullet(start_x, start_y)
    initial_y = bullet.rect.y # Store the initial numerical value of y
    bullet.update()
    # Assert the numerical value of y has changed as expected
    assert bullet.rect.y == initial_y - BULLET_SPEED

@patch('game.bullet.pygame.Surface')
def test_player_bullet_update_kill_offscreen_top(mock_pygame_surface_class, mocker):
    """Test player Bullet killing itself when off-screen top."""
    start_x, start_y = 100, 10
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    # Initial position near top, but still on screen
    mock_rect_instance = create_mock_rect(mocker, center=(start_x, start_y), width=BULLET_WIDTH, height=BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    bullet = Bullet(start_x, start_y)
    bullet.kill = MagicMock() # Mock kill method

    # Manually move bullet off screen (rect.bottom < 0) AFTER initialization
    bullet.rect.bottom = -5 # Set attribute directly on the mock rect
    bullet.update()
    bullet.kill.assert_called_once()

@patch('game.bullet.pygame.Surface')
def test_player_bullet_update_no_kill_onscreen(mock_pygame_surface_class, mocker):
    """Test player Bullet does not kill itself when on-screen."""
    start_x, start_y = 100, 50
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, center=(start_x, start_y), width=BULLET_WIDTH, height=BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    bullet = Bullet(start_x, start_y)
    bullet.kill = MagicMock()

    # Ensure bullet is on screen (rect.bottom > 0)
    bullet.rect.bottom = 10
    assert bullet.rect.bottom > 0 # Pre-condition check
    bullet.update()
    bullet.kill.assert_not_called()

# --- EnemyBullet Tests ---

@patch('game.bullet.pygame.Surface')
def test_enemy_bullet_init(mock_pygame_surface_class, mocker):
    """Test enemy Bullet initialization sets rect position correctly."""
    start_x, start_y = 150, 50
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, centerx=start_x, top=start_y, width=ENEMY_BULLET_WIDTH, height=ENEMY_BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    ebullet = EnemyBullet(start_x, start_y)

    mock_pygame_surface_class.assert_called_once_with((ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))
    ebullet.image.fill.assert_called_once_with(ENEMY_BULLET_COLOR)
    ebullet.image.get_rect.assert_called_once_with(centerx=start_x, top=start_y)

    assert ebullet.rect is mock_rect_instance # Ensure the mock rect is used
    assert ebullet.rect.centerx == start_x
    assert ebullet.rect.top == start_y
    assert ebullet.rect.x == start_x - ENEMY_BULLET_WIDTH // 2
    assert ebullet.rect.y == start_y

    assert ebullet.speedy == ENEMY_BULLET_SPEED_Y
    assert isinstance(ebullet, pygame.sprite.Sprite)

@patch('game.bullet.pygame.Surface')
def test_enemy_bullet_update_move(mock_pygame_surface_class, mocker):
    """Test enemy Bullet movement updates rect.y correctly."""
    start_x, start_y = 150, 50
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, centerx=start_x, top=start_y, width=ENEMY_BULLET_WIDTH, height=ENEMY_BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    ebullet = EnemyBullet(start_x, start_y)
    initial_y = ebullet.rect.y # Store initial numerical value
    ebullet.update()
    # Assert numerical value change
    assert ebullet.rect.y == initial_y + ENEMY_BULLET_SPEED_Y

@patch('game.bullet.pygame.Surface')
def test_enemy_bullet_update_kill_offscreen_bottom(mock_pygame_surface_class, mocker):
    """Test enemy Bullet killing itself when off-screen bottom."""
    start_x = 150
    # Start slightly above the bottom edge
    start_y = SCREEN_HEIGHT - 10
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, centerx=start_x, top=start_y, width=ENEMY_BULLET_WIDTH, height=ENEMY_BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    ebullet = EnemyBullet(start_x, start_y)
    ebullet.kill = MagicMock()

    # Manually move bullet off screen bottom (rect.top > SCREEN_HEIGHT) AFTER init
    ebullet.rect.top = SCREEN_HEIGHT + 5
    ebullet.update()
    ebullet.kill.assert_called_once()

@patch('game.bullet.pygame.Surface')
def test_enemy_bullet_update_no_kill_onscreen(mock_pygame_surface_class, mocker):
    """Test enemy Bullet does not kill itself when on-screen."""
    start_x = 150
    start_y = SCREEN_HEIGHT - 50 # Start well within screen bottom
    # FIX: Remove spec=pygame.Surface here
    mock_surf_instance = MagicMock()
    mock_rect_instance = create_mock_rect(mocker, centerx=start_x, top=start_y, width=ENEMY_BULLET_WIDTH, height=ENEMY_BULLET_HEIGHT)
    mock_surf_instance.get_rect.return_value = mock_rect_instance
    mock_pygame_surface_class.return_value = mock_surf_instance

    ebullet = EnemyBullet(start_x, start_y)
    ebullet.kill = MagicMock()

    # Position is clearly on screen (rect.top < SCREEN_HEIGHT)
    # e.g. after one update it might be at SCREEN_HEIGHT - 50 + ENEMY_BULLET_SPEED_Y
    assert ebullet.rect.top < SCREEN_HEIGHT # Pre-condition check
    ebullet.update()
    # Make sure it's still on screen after update (assuming reasonable speed/height)
    assert ebullet.rect.top < SCREEN_HEIGHT
    ebullet.kill.assert_not_called()