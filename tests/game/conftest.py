"""Common pytest fixtures for game component tests."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame


@pytest.fixture(autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_surface():
    """Create a mock pygame Surface."""
    surface = MagicMock(spec=pygame.Surface)
    surface.get_width.return_value = 800
    surface.get_height.return_value = 600
    surface.get_rect.return_value = pygame.Rect(0, 0, 800, 600)
    surface.get_at.return_value = pygame.Color(0, 0, 0)
    surface.blit = Mock()
    surface.fill = Mock()
    return surface


@pytest.fixture
def mock_image():
    """Create a mock pygame image."""
    image = MagicMock(spec=pygame.Surface)
    image.get_width.return_value = 64
    image.get_height.return_value = 64
    image.get_rect.return_value = pygame.Rect(0, 0, 64, 64)
    image.get_at.return_value = pygame.Color(0, 0, 0)
    image.convert_alpha.return_value = image
    image.set_colorkey = Mock()
    return image


@pytest.fixture
def mock_sound():
    """Create a mock pygame Sound."""
    sound = Mock(spec=pygame.mixer.Sound)
    sound.play = Mock()
    sound.set_volume = Mock()
    return sound


@pytest.fixture
def screen_dims():
    """Standard screen dimensions."""
    return {'width': 800, 'height': 600}
