# tests/game/test_powerup.py

import pytest
import pygame
import random
from unittest.mock import MagicMock, patch

# --- Attempt to import necessary game modules ---
try:
    # Assuming tests are run from the project root directory
    from game.powerup import PowerUp
    # Import necessary settings or define fallbacks
    from game.settings import (
        SCREEN_WIDTH, SCREEN_HEIGHT, POWERUP_SPEED_Y, POWERUP_TYPES,
        POWERUP_WIDTH, POWERUP_HEIGHT, POWERUP_FALLBACK_COLORS,
        WHITE, BLUE # Assuming BLUE is defined in settings
    )
except ImportError as e:
    pytest.skip(f"Skipping powerup tests due to ImportError: {e}. "
                f"Ensure tests are run from the project root "
                f"or adjust import paths.", allow_module_level=True)
except NameError as e:
     pytest.skip(f"Skipping powerup tests due to missing setting: {e}. "
                 f"Ensure all required constants are defined in game/settings.py",
                 allow_module_level=True)

# --- Module-level Pygame Setup/Teardown ---

@pytest.fixture(scope="module", autouse=True)
def pygame_setup_module():
    """Initializes Pygame for the test module."""
    print("\n--- Initializing Pygame for PowerUp Test Module ---")
    try:
        pygame.init()
        # Mixer not strictly needed for PowerUp, but good practice if base class uses it
        if pygame.mixer:
             pygame.mixer.init()
             print("Pygame Mixer Initialized.")
        else:
            print("Pygame Mixer module not available.")
            pygame.mixer = MagicMock() # Mock if unavailable
    except Exception as e:
        print(f"\nWarning: Pygame init failed in PowerUp tests: {e}")
        # Mock essential pygame components if init failed
        pygame.Surface = MagicMock()
        pygame.Rect = MagicMock()
        pygame.sprite = MagicMock()
        pygame.draw = MagicMock()
        if not hasattr(pygame, 'mixer'): pygame.mixer = MagicMock()

    yield # Run tests

    print("\n--- Quitting Pygame after PowerUp Test Module ---")
    pygame.quit()

# --- Fixtures ---

@pytest.fixture
def mock_surface(mocker):
    """Fixture providing a mock pygame.Surface with a real Rect."""
    surf = mocker.MagicMock(spec=pygame.Surface)
    initial_width = POWERUP_WIDTH
    initial_height = POWERUP_HEIGHT

    def create_real_rect(**kwargs):
        rect = pygame.Rect(0, 0, initial_width, initial_height)
        for key, value in kwargs.items():
            try:
                setattr(rect, key, value)
            except AttributeError:
                print(f"Warning: Could not set attr '{key}' on real Rect in mock.")
        return rect

    surf.get_rect.side_effect = create_real_rect
    surf.get_width.return_value = initial_width
    surf.get_height.return_value = initial_height
    surf.copy.return_value = surf # Assume copy might be called
    surf.fill = MagicMock() # Mock fill for fallback surface creation

    return surf

@pytest.fixture
def mock_powerup_images_dict(mock_surface):
    """Fixture providing a dictionary of mocked powerup images."""
    # Create a separate mock surface for each type for clarity
    images = {}
    for p_type in POWERUP_TYPES:
         # Each type gets its own mock surface instance from the fixture
         # Note: Re-calling the fixture creates a new mock instance each time
         images[p_type] = mock_surface # Use the same mock surface fixture for simplicity
                                       # Or create unique mocks if needed:
                                       # images[p_type] = mock_surface_factory()
    return images

# --- Test Functions ---

@patch('random.choice')
@patch('random.randint')
def test_powerup_initialization_valid_image(mock_randint, mock_choice, mock_powerup_images_dict, mock_surface):
    """Test PowerUp initialization when a valid image is provided."""
    # --- Arrange ---
    # Force random.choice to pick a specific type
    chosen_type = POWERUP_TYPES[0] # e.g., 'shield'
    mock_choice.return_value = chosen_type

    # Force random.randint to return specific coordinates
    start_x = 150
    start_y = -50
    mock_randint.side_effect = [start_x, start_y] # First call returns x, second returns y

    # Get the expected image from the mocked dictionary
    expected_image = mock_powerup_images_dict[chosen_type]

    # --- Act ---
    powerup = PowerUp(mock_powerup_images_dict)

    # --- Assert ---
    mock_choice.assert_called_once_with(POWERUP_TYPES)
    # Check randint calls: one for x, one for y
    assert mock_randint.call_count == 2
    mock_randint.assert_any_call(0, SCREEN_WIDTH - powerup.rect.width) # Check x range
    mock_randint.assert_any_call(-100, -40) # Check y range

    assert powerup.type == chosen_type
    assert powerup.image is expected_image # Should be the exact mock surface instance
    assert isinstance(powerup.rect, pygame.Rect) # Should have a real Rect
    assert powerup.rect.x == start_x
    assert powerup.rect.y == start_y
    assert powerup.speedy == POWERUP_SPEED_Y

@patch('random.choice')
@patch('random.randint')
@patch('pygame.draw.rect') # Patch draw.rect for fallback border
@patch('pygame.Surface', return_value=MagicMock(spec=pygame.Surface)) # Patch Surface creation
def test_powerup_initialization_fallback_image(mock_surface_class, mock_draw_rect, mock_randint, mock_choice):
    """Test PowerUp initialization using fallback image when type is missing."""
    # --- Arrange ---
    # Force random.choice to pick a specific type
    chosen_type = POWERUP_TYPES[0] # e.g., 'shield'
    mock_choice.return_value = chosen_type

    # Force random.randint for position
    start_x = 200
    start_y = -60
    mock_randint.side_effect = [start_x, start_y]

    # Create an *empty* image dictionary to force fallback
    empty_images_dict = {}

    # Configure the mock Surface instance that will be created
    mock_fallback_surface_instance = mock_surface_class.return_value
    mock_fallback_rect = MagicMock(spec=pygame.Rect) # Rect for the fallback surface
    mock_fallback_surface_instance.get_rect.return_value = mock_fallback_rect
    # Mock fill method on the instance
    mock_fallback_surface_instance.fill = MagicMock()

    # --- Act ---
    powerup = PowerUp(empty_images_dict)

    # --- Assert ---
    mock_choice.assert_called_once_with(POWERUP_TYPES)
    assert mock_randint.call_count == 2

    # Assert Surface was called to create the fallback
    mock_surface_class.assert_called_once_with((POWERUP_WIDTH, POWERUP_HEIGHT))
    assert powerup.image is mock_fallback_surface_instance # Image is the created mock

    # Assert fill was called with the correct fallback color
    expected_fallback_color = POWERUP_FALLBACK_COLORS.get(chosen_type, BLUE)
    mock_fallback_surface_instance.fill.assert_called_once_with(expected_fallback_color)

    # Assert draw.rect was called to draw the border
    mock_draw_rect.assert_called_once_with(
        mock_fallback_surface_instance, # Drawn on the fallback surface
        WHITE,                          # Border color
        mock_fallback_rect,             # Rect of the fallback surface
        1                               # Border width
    )

    # Assert rect properties are set correctly
    assert isinstance(powerup.rect, pygame.Rect) # Should still get a real Rect from the image mock
    assert powerup.rect.x == start_x
    assert powerup.rect.y == start_y
    assert powerup.speedy == POWERUP_SPEED_Y

@patch('random.choice', return_value=POWERUP_TYPES[0]) # Mock choice for predictable init
@patch('random.randint', side_effect=[100, -50])      # Mock randint for predictable init
def test_powerup_update_movement(mock_randint, mock_choice, mock_powerup_images_dict):
    """Test that update correctly moves the powerup down."""
    # --- Arrange ---
    powerup = PowerUp(mock_powerup_images_dict)
    initial_y = powerup.rect.y

    # --- Act ---
    powerup.update()

    # --- Assert ---
    assert powerup.rect.y == initial_y + POWERUP_SPEED_Y

@patch.object(PowerUp, 'kill') # Patch the kill method on the PowerUp class itself
@patch('random.choice', return_value=POWERUP_TYPES[0])
@patch('random.randint', side_effect=[100, -50])
def test_powerup_update_kill_offscreen(mock_randint, mock_choice, mock_kill, mock_powerup_images_dict):
    """Test that the powerup calls kill() when it moves off screen."""
    # --- Arrange ---
    powerup = PowerUp(mock_powerup_images_dict)
    # Manually set position just above the kill threshold
    powerup.rect.top = SCREEN_HEIGHT - POWERUP_SPEED_Y + 1

    # --- Act ---
    powerup.update() # This should move it past the threshold

    # --- Assert ---
    # Check that rect.y was updated correctly
    assert powerup.rect.top == SCREEN_HEIGHT + 1
    # Check that the kill method (mocked on the instance via patch.object) was called
    powerup.kill.assert_called_once() # kill() is inherited from Sprite, check instance mock

@patch.object(PowerUp, 'kill')
@patch('random.choice', return_value=POWERUP_TYPES[0])
@patch('random.randint', side_effect=[100, -50])
def test_powerup_update_not_killed_onscreen(mock_randint, mock_choice, mock_kill, mock_powerup_images_dict):
    """Test that the powerup does NOT call kill() when still on screen."""
    # --- Arrange ---
    powerup = PowerUp(mock_powerup_images_dict)
    # Position it somewhere clearly on screen
    powerup.rect.top = SCREEN_HEIGHT // 2

    # --- Act ---
    powerup.update()

    # --- Assert ---
    # Check that rect.y was updated correctly
    assert powerup.rect.top == SCREEN_HEIGHT // 2 + POWERUP_SPEED_Y
    # Check that the kill method was NOT called
    powerup.kill.assert_not_called()

