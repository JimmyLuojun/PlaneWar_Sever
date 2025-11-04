"""Pytest configuration and fixtures for all tests."""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

# Set SDL to use dummy video driver to prevent actual windows from opening
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Import pygame AFTER setting environment variables
import pygame


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once for all tests in headless mode."""
    pygame.init()
    # Create a dummy display that won't actually show
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def mock_pygame_display():
    """Mock pygame display to prevent actual windows from appearing."""
    with patch('pygame.display.flip'):
        with patch('pygame.display.update'):
            yield


@pytest.fixture
def mock_network_client():
    """Provide a mocked NetworkClient for tests."""
    mock_client = Mock()
    mock_client.is_authenticated = False
    mock_client.login = Mock()
    mock_client.register = Mock()
    mock_client.logout = Mock()
    mock_client.submit_score = Mock()
    return mock_client
