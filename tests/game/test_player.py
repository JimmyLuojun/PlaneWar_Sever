# tests/game/test_player.py

import pytest
import pygame
from unittest.mock import MagicMock, call, patch

# --- Attempt to import necessary game modules ---
try:
    from game.player import Player
    from game.bullet import Bullet
    from game.settings import (
        SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_STARTING_BOMBS,
        PLAYER_SHOOT_DELAY, POWERUP_DURATION, SHIELD_DURATION,
        SHIELD_VISUAL_COLOR # Make sure this is defined in settings.py!
    )
    PLAYER_BOTTOM_MARGIN = 20 # Fallback/Default
    PLAYER_DOUBLE_SHOT_OFFSET = 10 # Fallback/Default

except ImportError as e:
    pytest.skip(f"Skipping player tests due to ImportError: {e}. "
                f"Ensure tests are run from the project root "
                f"or adjust import paths.", allow_module_level=True)
except NameError as e:
     pytest.skip(f"Skipping player tests due to missing setting: {e}. "
                 f"Ensure all required constants (like SHIELD_VISUAL_COLOR) "
                 f"are defined in game/settings.py", allow_module_level=True)

# --- Module-level Pygame Setup/Teardown ---

@pytest.fixture(scope="module", autouse=True)
def pygame_setup_module():
    """Initializes Pygame and Mixer for the test module."""
    print("\n--- Initializing Pygame for Test Module ---")
    try:
        pygame.init()
        if pygame.mixer:
             pygame.mixer.init()
             print("Pygame Mixer Initialized.")
        else:
            print("Pygame Mixer module not available.")
            pygame.mixer = MagicMock()
            pygame.mixer.Sound = MagicMock()
    except Exception as e:
        print(f"\nWarning: Pygame init failed in tests: {e}")
        pygame.Surface = MagicMock()
        pygame.Rect = MagicMock()
        pygame.sprite = MagicMock()
        pygame.time = MagicMock()
        pygame.key = MagicMock()
        pygame.mouse = MagicMock()
        pygame.font = MagicMock()
        pygame.draw = MagicMock()
        if not hasattr(pygame, 'mixer'): pygame.mixer = MagicMock()
        pygame.mixer.Sound = MagicMock()

    yield # Run tests

    print("\n--- Quitting Pygame after Test Module ---")
    pygame.quit()


# --- Fixtures defined within this test file ---

@pytest.fixture
def mock_sounds_dict(mocker):
    """Fixture providing a dictionary of MagicMock sound objects."""
    sounds = {}
    sound_keys = [
        'player_shoot', 'shield_up_sound', 'shield_down_sound',
        'powerup_sound', 'bomb_sound'
    ]
    for key in sound_keys:
        mock_sound = MagicMock(spec=pygame.mixer.Sound)
        sounds[key] = mock_sound
    return sounds

@pytest.fixture
def mock_player_surface(mocker):
    """
    Fixture providing a mock pygame.Surface for the player image.
    Its get_rect() method returns a *real* pygame.Rect instance.
    """
    surf = mocker.MagicMock(spec=pygame.Surface)
    initial_width = 50 # Example size
    initial_height = 40 # Example size

    def create_real_rect(**kwargs):
        rect = pygame.Rect(0, 0, initial_width, initial_height)
        for key, value in kwargs.items():
            try:
                setattr(rect, key, value)
            except AttributeError:
                print(f"Warning: Could not set attribute '{key}' on real Rect in mock.")
        return rect

    surf.get_rect.side_effect = create_real_rect
    surf.get_width.return_value = initial_width
    surf.get_height.return_value = initial_height
    surf.copy.return_value = surf

    return surf

@pytest.fixture
def mock_groups_dict(mocker):
    """Fixture providing mocked sprite groups needed for bomb test."""
    groups = {}
    groups['enemies_group'] = MagicMock(spec=pygame.sprite.Group)
    groups['enemy_bullets_group'] = MagicMock(spec=pygame.sprite.Group)

    for group in groups.values():
        group.sprites.return_value = []
        group.add = MagicMock()
        group.remove = MagicMock()
        group.empty = MagicMock()

    return groups


@pytest.fixture
def player_instance(mock_player_surface, mock_sounds_dict, mocker):
    """Fixture to create a Player instance with mocks for testing."""
    mocker.patch('pygame.time.get_ticks', return_value=10000)
    mocker.patch('pygame.mouse.get_pos', return_value=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    player = Player(
        player_img=mock_player_surface,
        shoot_sound=mock_sounds_dict['player_shoot'],
        shield_up_sound=mock_sounds_dict['shield_up_sound'],
        shield_down_sound=mock_sounds_dict['shield_down_sound'],
        powerup_sound=mock_sounds_dict['powerup_sound'],
        bomb_sound=mock_sounds_dict['bomb_sound']
    )

    assert isinstance(player.rect, pygame.Rect), "Player rect should be a real pygame.Rect"
    assert player.rect.centerx == SCREEN_WIDTH // 2, "Initial centerx mismatch"
    assert player.rect.bottom == SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN, "Initial bottom mismatch"
    assert player.bomb_count == PLAYER_STARTING_BOMBS
    assert player.score == 0
    assert player.powerup_type is None
    assert not player.shield_active

    return player


# --- Test Functions ---

def test_player_initial_state(player_instance):
    """Test the initial state attributes of the player (already checked in fixture)."""
    assert player_instance is not None
    assert player_instance.score == 0
    assert player_instance.bomb_count == PLAYER_STARTING_BOMBS
    assert player_instance.powerup_type is None
    assert player_instance.shield_active is False
    assert player_instance.rect.centerx == SCREEN_WIDTH // 2
    assert player_instance.rect.bottom == SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN

@patch('game.player.Bullet', spec=True)
def test_player_shoot_single(mock_bullet_class, player_instance, mock_sounds_dict, mocker):
    """Test shooting a single bullet when allowed."""
    start_time = player_instance.last_shot_time
    mocker.patch('pygame.time.get_ticks', return_value=start_time + PLAYER_SHOOT_DELAY + 1)

    center_x = player_instance.rect.centerx
    top_y = player_instance.rect.top

    new_bullets = player_instance.shoot()

    assert len(new_bullets) == 1
    mock_bullet_class.assert_called_once_with(center_x, top_y)
    mock_sounds_dict['player_shoot'].play.assert_called_once()
    assert player_instance.last_shot_time == start_time + PLAYER_SHOOT_DELAY + 1

@patch('game.player.Bullet', spec=True)
def test_player_shoot_double(mock_bullet_class, player_instance, mock_sounds_dict, mocker):
    """Test shooting double bullets when powerup active."""
    start_time = player_instance.last_shot_time
    mocker.patch('pygame.time.get_ticks', return_value=start_time + PLAYER_SHOOT_DELAY + 1)
    player_instance.activate_powerup('double_shot')
    mock_sounds_dict['powerup_sound'].play.reset_mock()

    center_x = player_instance.rect.centerx
    top_y = player_instance.rect.top

    new_bullets = player_instance.shoot()

    assert len(new_bullets) == 2
    assert mock_bullet_class.call_count == 2
    calls = [
        call(center_x - PLAYER_DOUBLE_SHOT_OFFSET, top_y),
        call(center_x + PLAYER_DOUBLE_SHOT_OFFSET, top_y)
    ]
    mock_bullet_class.assert_has_calls(calls, any_order=True)
    mock_sounds_dict['player_shoot'].play.assert_called_once()
    assert player_instance.last_shot_time == start_time + PLAYER_SHOOT_DELAY + 1


@patch('game.player.Bullet', spec=True)
def test_player_shoot_delay(mock_bullet_class, player_instance, mock_sounds_dict, mocker):
    """Test that shooting is prevented by the delay."""
    start_time = player_instance.last_shot_time
    mocker.patch('pygame.time.get_ticks', return_value=start_time + PLAYER_SHOOT_DELAY - 1)

    new_bullets = player_instance.shoot()

    assert len(new_bullets) == 0
    mock_bullet_class.assert_not_called()
    mock_sounds_dict['player_shoot'].play.assert_not_called()

def test_player_activate_powerup_bomb(player_instance, mock_sounds_dict):
    """Test activating the bomb powerup."""
    initial_bombs = player_instance.bomb_count
    player_instance.activate_powerup('bomb')
    assert player_instance.bomb_count == initial_bombs + 1
    mock_sounds_dict['powerup_sound'].play.assert_called_once()

def test_player_activate_powerup_shield(player_instance, mock_sounds_dict, mocker):
    """Test activating the shield powerup."""
    start_time = 20000
    mocker.patch('pygame.time.get_ticks', return_value=start_time)
    player_instance.activate_powerup('shield')
    assert player_instance.shield_active is True
    assert player_instance.shield_end_time == start_time + SHIELD_DURATION
    mock_sounds_dict['powerup_sound'].play.assert_called_once()
    mock_sounds_dict['shield_up_sound'].play.assert_called_once()

def test_player_activate_powerup_double_shot(player_instance, mock_sounds_dict, mocker):
    """Test activating the double_shot powerup."""
    start_time = 30000
    mocker.patch('pygame.time.get_ticks', return_value=start_time)
    player_instance.activate_powerup('double_shot')
    assert player_instance.powerup_type == 'double_shot'
    assert player_instance.powerup_end_time == start_time + POWERUP_DURATION
    mock_sounds_dict['powerup_sound'].play.assert_called_once()

def test_player_update_timers_expire(player_instance, mock_sounds_dict, mocker):
    """Test that powerups expire after duration."""
    start_time = 10000
    mock_ticks = mocker.patch('pygame.time.get_ticks', return_value=start_time)

    player_instance.activate_powerup('shield')
    player_instance.activate_powerup('double_shot')
    mock_sounds_dict['powerup_sound'].play.reset_mock()
    mock_sounds_dict['shield_up_sound'].play.reset_mock()
    mock_sounds_dict['shield_down_sound'].play.reset_mock()

    mock_ticks.return_value = start_time + POWERUP_DURATION + 1
    player_instance.update()
    assert player_instance.shield_active is True
    assert player_instance.powerup_type is None
    mock_sounds_dict['shield_down_sound'].play.assert_not_called()

    mock_ticks.return_value = start_time + SHIELD_DURATION + 1
    player_instance.update()
    assert player_instance.shield_active is False
    assert player_instance.powerup_type is None
    mock_sounds_dict['shield_down_sound'].play.assert_called_once()

def test_player_update_movement(player_instance, mocker):
    """Test player movement follows mouse and stays in bounds."""
    mock_mouse_get_pos = mocker.patch('pygame.mouse.get_pos')
    player_rect = player_instance.rect

    target_pos = (300, 400)
    mock_mouse_get_pos.return_value = target_pos
    player_instance.update()
    assert player_rect.center == target_pos
    assert 0 < player_rect.left < player_rect.right < SCREEN_WIDTH
    assert 0 < player_rect.top < player_rect.bottom < SCREEN_HEIGHT

    mock_mouse_get_pos.return_value = (-50, 400)
    player_instance.update()
    assert player_rect.left == 0

    mock_mouse_get_pos.return_value = (SCREEN_WIDTH + 100, 400)
    player_instance.update()
    assert player_rect.right == SCREEN_WIDTH

    mock_mouse_get_pos.return_value = (300, -50)
    player_instance.update()
    assert player_rect.top == 0

    mock_mouse_get_pos.return_value = (300, SCREEN_HEIGHT + 50)
    player_instance.update()
    assert player_rect.bottom == SCREEN_HEIGHT

def test_player_use_bomb_success(player_instance, mock_groups_dict, mock_sounds_dict, mocker):
    """Test using a bomb when available."""
    player_instance.bomb_count = PLAYER_STARTING_BOMBS
    initial_bombs = player_instance.bomb_count
    assert initial_bombs > 0

    mock_enemy1 = MagicMock(spec=pygame.sprite.Sprite)
    mock_enemy2 = MagicMock(spec=pygame.sprite.Sprite)
    mock_bullet1 = MagicMock(spec=pygame.sprite.Sprite)

    enemies_group = mock_groups_dict['enemies_group']
    enemy_bullets_group = mock_groups_dict['enemy_bullets_group']

    enemies_group.sprites.return_value = [mock_enemy1, mock_enemy2]
    enemy_bullets_group.sprites.return_value = [mock_bullet1]

    killed_count = player_instance.use_bomb(enemies_group, enemy_bullets_group)

    assert player_instance.bomb_count == initial_bombs - 1
    assert killed_count == 2
    mock_enemy1.kill.assert_called_once()
    mock_enemy2.kill.assert_called_once()
    mock_bullet1.kill.assert_called_once()
    mock_sounds_dict['bomb_sound'].play.assert_called_once()

def test_player_use_bomb_no_bombs(player_instance, mock_groups_dict, mock_sounds_dict):
    """Test using a bomb when none are available."""
    player_instance.bomb_count = 0

    enemies_group = mock_groups_dict['enemies_group']
    enemy_bullets_group = mock_groups_dict['enemy_bullets_group']
    enemies_group.sprites.return_value = []
    enemy_bullets_group.sprites.return_value = []

    killed_count = player_instance.use_bomb(enemies_group, enemy_bullets_group)

    assert player_instance.bomb_count == 0
    assert killed_count == 0
    mock_sounds_dict['bomb_sound'].play.assert_not_called()


# Patch pygame.draw.circle where it's used (globally or within Player module)
@patch('pygame.draw.circle')
@patch('pygame.Surface', spec=True) # Patch the CLASS pygame.Surface
def test_player_draw_shield_when_active(mock_surface_class, mock_draw_circle, player_instance, mocker):
    """Test that the shield is drawn only when active."""

    # --- Configure the MOCK INSTANCE that the patched Surface CLASS will return ---
    mock_shield_surface_instance = mock_surface_class.return_value
    mock_temp_rect = MagicMock(spec=pygame.Rect) # Mock the rect returned by get_rect
    mock_shield_surface_instance.get_rect.return_value = mock_temp_rect

    # Mock the target surface to draw onto
    # REMOVED spec=pygame.Surface because pygame.Surface is already patched here
    mock_target_surface = MagicMock()
    # We still need to mock the blit method on this target mock
    mock_target_surface.blit = MagicMock()

    # --- Test Case 1: Shield NOT active ---
    player_instance.shield_active = False
    player_instance.draw_shield(mock_target_surface)

    mock_draw_circle.assert_not_called()
    mock_surface_class.assert_not_called()
    mock_target_surface.blit.assert_not_called()

    # Reset mocks
    mock_draw_circle.reset_mock()
    mock_surface_class.reset_mock()
    mock_target_surface.blit.reset_mock() # Reset blit on target
    mock_shield_surface_instance.get_rect.reset_mock()


    # --- Test Case 2: Shield IS active ---
    player_instance.shield_active = True
    player_instance.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # --- Call the actual method ---
    player_instance.draw_shield(mock_target_surface)

    # --- Assertions ---
    # 1. Assert the Surface CLASS was called correctly
    expected_radius = player_instance.shield_visual_radius
    expected_diameter = max(1, expected_radius * 2)
    mock_surface_class.assert_called_once_with(
        (expected_diameter, expected_diameter), pygame.SRCALPHA
    )

    # 2. Assert draw.circle was called correctly on the INSTANCE
    draw_radius = max(1, expected_radius)
    mock_draw_circle.assert_called_once_with(
        mock_shield_surface_instance, SHIELD_VISUAL_COLOR,
        (expected_radius, expected_radius), draw_radius
        # Add width arg if needed: , shield_line_width
    )

    # 3. Assert get_rect was called on the INSTANCE
    mock_shield_surface_instance.get_rect.assert_called_once_with(
        center=player_instance.rect.center
    )

    # 4. Assert blit was called on the TARGET surface
    mock_target_surface.blit.assert_called_once_with(
        mock_shield_surface_instance, mock_temp_rect
    )