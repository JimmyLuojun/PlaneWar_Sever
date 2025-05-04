import pytest
import pygame
import os
from unittest.mock import patch, MagicMock
from game.background import Background
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED

# Fixtures from conftest.py (e.g., mock_surface) will be available

@patch('pygame.image.load')
@patch('pygame.transform.scale')
def test_background_init_success(mock_scale, mock_load, mocker):
    """Test successful background initialization and image loading."""
    mocker.patch('os.path.exists', return_value=True)
    # Mock the loaded image and the scaled image
    mock_loaded_img = MagicMock(spec=pygame.Surface)
    mock_loaded_img.get_size.return_value = (1000, 1200) # Example original size
    mock_loaded_img.convert.return_value = mock_loaded_img # convert() returns self
    mock_load.return_value = mock_loaded_img

    mock_scaled_img = MagicMock(spec=pygame.Surface)
    mock_scaled_img.get_height.return_value = 1200 # Scaled height
    mock_scale.return_value = mock_scaled_img

    bg = Background('dummy/path/bg.jpg', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)

    mock_load.assert_called_once_with('dummy/path/bg.jpg')
    mock_loaded_img.convert.assert_called_once()
    # Check scale was called correctly (width=SCREEN_WIDTH, height calculated/adjusted)
    # The exact height depends on aspect ratio logic, check if it's called
    mock_scale.assert_called_once()
    # Check scale args: first arg is the loaded img, second is (width, height) tuple
    assert mock_scale.call_args[0][0] == mock_loaded_img
    assert mock_scale.call_args[0][1][0] == SCREEN_WIDTH # Check width
    # Height depends on aspect ratio logic, ensure it's >= SCREEN_HEIGHT
    assert mock_scale.call_args[0][1][1] >= SCREEN_HEIGHT

    assert bg.image == mock_scaled_img
    assert bg.image_height == 1200
    assert bg.y1 == 0
    assert bg.y2 == -1200 # Starts above y1

def test_background_init_file_not_found(mocker):
    """Test background initialization when image file doesn't exist."""
    mocker.patch('os.path.exists', return_value=False)
    # Patch load/scale to ensure they are NOT called
    mock_load = mocker.patch('pygame.image.load')
    mock_scale = mocker.patch('pygame.transform.scale')

    bg = Background('bad/path/bg.jpg', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)

    assert bg.image is None # Image should be None
    assert bg.image_height == 0
    assert bg.y1 == 0
    assert bg.y2 == 0
    mock_load.assert_not_called()
    mock_scale.assert_not_called()

@patch('pygame.image.load', side_effect=pygame.error("Load error"))
def test_background_init_pygame_error(mock_load, mocker):
    """Test background initialization when pygame.image.load fails."""
    mocker.patch('os.path.exists', return_value=True)
    mock_scale = mocker.patch('pygame.transform.scale')

    bg = Background('dummy/path/bg.jpg', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)

    assert bg.image is None # Image should be None on error
    mock_load.assert_called_once()
    mock_scale.assert_not_called() # Scale shouldn't be called if load fails

def test_background_update_no_image():
    """Test that update does nothing if image wasn't loaded."""
    # Create instance where image loading would fail (e.g., bad path)
    bg = Background('', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)
    initial_y1, initial_y2 = bg.y1, bg.y2
    bg.update()
    assert bg.y1 == initial_y1
    assert bg.y2 == initial_y2

@patch('pygame.image.load')
@patch('pygame.transform.scale')
def test_background_update_scrolling(mock_scale, mock_load, mocker):
    """Test the scrolling logic in update."""
    mocker.patch('os.path.exists', return_value=True)
    mock_loaded_img = MagicMock(spec=pygame.Surface); mock_loaded_img.get_size.return_value=(1000,800); mock_loaded_img.convert.return_value=mock_loaded_img
    mock_load.return_value = mock_loaded_img
    mock_scaled_img = MagicMock(spec=pygame.Surface); mock_scaled_img.get_height.return_value=800 # Example height
    mock_scale.return_value = mock_scaled_img

    scroll_speed = 5
    bg = Background('dummy/path/bg.jpg', SCREEN_WIDTH, SCREEN_HEIGHT, scroll_speed)
    assert bg.image_height == 800
    assert bg.y1 == 0
    assert bg.y2 == -800

    # First update
    bg.update()
    assert bg.y1 == 5
    assert bg.y2 == -795

    # Update many times until y1 goes off screen
    num_updates = bg.image_height // scroll_speed # Number of updates for y1 to reach image_height
    for _ in range(num_updates):
        bg.update()

    # y1 should have wrapped around
    # Expected y1 = (num_updates + 1) * scroll_speed - bg.image_height
    # Expected y2 = -bg.image_height + (num_updates + 1) * scroll_speed
    # Simpler check: y1 should now be y2 (from previous step) - image_height
    assert bg.y1 == bg.y2 - bg.image_height # Check wrap condition

    # Update until y2 goes off screen
    for _ in range(num_updates):
         bg.update()
    # y2 should have wrapped around
    assert bg.y2 == bg.y1 - bg.image_height # Check wrap condition

def test_background_draw_with_image(mock_surface):
    """Test drawing when an image is loaded."""
    # Create a background instance with a mocked image
    bg = Background('', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED) # Path doesn't matter here
    mock_img = MagicMock(spec=pygame.Surface)
    bg.image = mock_img
    bg.y1 = 10
    bg.y2 = -790

    bg.draw(mock_surface)

    # Check that blit was called twice with the correct image and coordinates
    assert mock_surface.blit.call_count == 2
    mock_surface.blit.assert_any_call(mock_img, (0, 10))
    mock_surface.blit.assert_any_call(mock_img, (0, -790))

def test_background_draw_no_image(mock_surface):
    """Test drawing the fallback when no image is loaded."""
    bg = Background('', SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED) # Force image load fail
    bg.image = None # Ensure image is None

    bg.draw(mock_surface)

    # Check that fill was called (with black) and blit was not
    mock_surface.fill.assert_called_once_with((0, 0, 0))
    mock_surface.blit.assert_not_called() 