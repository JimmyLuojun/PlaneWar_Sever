"""Tests for game/background.py - Scrolling background."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pygame
from plane_war_server.game.models.background import Background


class TestBackgroundInit:
    """Tests for Background initialization."""

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_init_with_valid_image(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test initialization with valid image path."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (800, 600)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)

        assert bg.screen_width == 800
        assert bg.screen_height == 600
        assert bg.scroll_speed == 2
        assert bg.y1 == 0
        assert bg.y2 == -600

    @patch('plane_war_server.game.models.background.os.path.exists', return_value=False)
    def test_init_with_missing_image(self, mock_exists):
        """Test initialization with missing image creates fallback."""
        bg = Background('missing.png', 800, 600, 2)

        # Background should still initialize even without image
        assert bg.image is None
        assert bg.screen_width == 800
        assert bg.screen_height == 600


class TestBackgroundUpdate:
    """Tests for Background.update method."""

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_update_moves_background_down(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test update moves background positions downward."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (800, 600)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)
        initial_y1 = bg.y1
        initial_y2 = bg.y2

        bg.update()

        assert bg.y1 == initial_y1 + 2
        assert bg.y2 == initial_y2 + 2

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_update_loops_y1_position(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test y1 loops when scrolling off bottom."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (800, 600)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)
        bg.y1 = 598  # Just before threshold
        initial_y2 = bg.y2

        bg.update()

        # After update, y1 becomes 600 (>= 600), so loops: y1 = (y2+2) - 600
        assert bg.y1 == (initial_y2 + 2) - 600

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_update_loops_y2_position(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test y2 loops when scrolling off bottom."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (800, 600)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)
        bg.y2 = 598  # Just before threshold
        initial_y1 = bg.y1

        bg.update()

        # After update, y2 becomes 600 (>= 600), so loops: y2 = y1 - 600
        assert bg.y2 == initial_y1 + 2 - 600  # y1 also moved by +2


class TestBackgroundDraw:
    """Tests for Background.draw method."""

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_draw_blits_both_images(self, mock_exists, mock_scale, mock_load, mock_image, mock_surface):
        """Test draw blits both background images."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (800, 600)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)
        bg.draw(mock_surface)

        assert mock_surface.blit.call_count == 2


class TestBackgroundLoadAndScaleImage:
    """Tests for Background._load_and_scale_image helper."""

    @patch('plane_war_server.game.models.background.pygame.image.load')
    @patch('plane_war_server.game.models.background.pygame.transform.scale')
    @patch('plane_war_server.game.models.background.os.path.exists', return_value=True)
    def test_scales_image_to_screen_height(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test image is scaled to match screen height."""
        # Mock the loaded image
        mock_loaded = MagicMock()
        mock_loaded.convert.return_value = mock_loaded
        mock_loaded.get_size.return_value = (400, 300)
        mock_load.return_value = mock_loaded

        # Mock the scaled image
        mock_scaled = MagicMock()
        mock_scaled.get_height.return_value = 600
        mock_scale.return_value = mock_scaled

        bg = Background('test.png', 800, 600, 2)

        # Verify scale was called with correct dimensions
        expected_ratio = 600 / 300
        expected_width = int(400 * expected_ratio)
        mock_scale.assert_called_with(mock_loaded, (expected_width, 600))