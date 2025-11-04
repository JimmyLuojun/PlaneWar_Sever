"""Tests for game/main.py - Main entry point and initialization."""

import os
# Set SDL to dummy mode BEFORE importing pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import pygame
from game import main


class TestMain:
    """Tests for main function."""

    @patch('game.main.run_state_machine')
    @patch('game.main.NetworkClient')
    @patch('game.main.Background')
    @patch('game.main.utils.load_high_score', return_value=1000)
    @patch('game.main.load_level_data_and_music')
    @patch('game.main.load_sounds')
    @patch('game.main.load_images')
    @patch('game.main.load_fonts')
    @patch('pygame.time.Clock')
    @patch('pygame.display.set_caption')
    @patch('pygame.display.set_mode')
    @patch('pygame.mixer.init')
    @patch('pygame.init')
    @patch('sys.exit')
    def test_main_successful_initialization(
        self,
        mock_sys_exit,
        mock_pygame_init,
        mock_mixer_init,
        mock_set_mode,
        mock_set_caption,
        mock_clock,
        mock_load_fonts,
        mock_load_images,
        mock_load_sounds,
        mock_load_levels,
        mock_load_high_score,
        mock_background,
        mock_network_client,
        mock_run_state_machine
    ):
        """Test main function successful initialization and execution."""
        # Arrange
        mock_screen = Mock(spec=pygame.Surface)
        mock_set_mode.return_value = mock_screen
        mock_clock_instance = Mock()
        mock_clock.return_value = mock_clock_instance

        mock_fonts = {'title': Mock(), 'score': Mock()}
        mock_load_fonts.return_value = mock_fonts

        mock_images = {'player': Mock(), 'enemy1': Mock()}
        mock_load_images.return_value = mock_images

        mock_sounds = {'shoot': Mock(), 'explosion': Mock()}
        mock_load_sounds.return_value = mock_sounds

        mock_levels = [{'level_number': 1}, {'level_number': 2}]
        mock_music_paths = {1: 'music1.mp3', 2: 'music2.mp3'}
        mock_load_levels.return_value = (mock_levels, mock_music_paths)

        mock_background_instance = Mock()
        mock_background.return_value = mock_background_instance

        mock_client = Mock()
        mock_client.is_authenticated = False
        mock_network_client.return_value = mock_client
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()

        mock_pygame_init.assert_called_once()
        mock_set_mode.assert_called_once()
        mock_set_caption.assert_called_once_with("PlaneWar Online")
        mock_load_fonts.assert_called_once()
        mock_load_images.assert_called_once()
        mock_load_sounds.assert_called_once()
        mock_load_levels.assert_called_once()
        mock_background.assert_called_once()
        mock_network_client.assert_called_once()
        mock_run_state_machine.assert_called_once()
        mock_sys_exit.assert_called_once()

    @patch('pygame.init')
    @patch('sys.exit')
    def test_main_pygame_init_failure(self, mock_sys_exit, mock_pygame_init):
        """Test main function handles pygame init failure."""
        # Arrange
        mock_pygame_init.side_effect = pygame.error("Init failed")
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()
        mock_sys_exit.assert_called_once_with(1)

    @patch('pygame.display.set_mode')
    @patch('pygame.init')
    @patch('pygame.quit')
    @patch('sys.exit')
    def test_main_screen_creation_failure(
        self, mock_sys_exit, mock_quit, mock_init, mock_set_mode
    ):
        """Test main function handles screen creation failure."""
        # Arrange
        mock_set_mode.side_effect = pygame.error("Display failed")
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()
        mock_quit.assert_called_once()
        mock_sys_exit.assert_called_once_with(1)

    @patch('game.main.run_state_machine')
    @patch('game.main.NetworkClient')
    @patch('game.main.Background')
    @patch('game.main.utils.load_high_score', return_value=0)
    @patch('game.main.load_level_data_and_music')
    @patch('game.main.load_sounds')
    @patch('game.main.load_images')
    @patch('game.main.load_fonts')
    @patch('pygame.time.Clock')
    @patch('pygame.display.set_caption')
    @patch('pygame.display.set_mode')
    @patch('pygame.mixer.init')
    @patch('pygame.init')
    @patch('pygame.quit')
    @patch('sys.exit')
    def test_main_logout_on_exit(
        self,
        mock_sys_exit,
        mock_quit,
        mock_pygame_init,
        mock_mixer_init,
        mock_set_mode,
        mock_set_caption,
        mock_clock,
        mock_load_fonts,
        mock_load_images,
        mock_load_sounds,
        mock_load_levels,
        mock_load_high_score,
        mock_background,
        mock_network_client,
        mock_run_state_machine
    ):
        """Test main function logs out authenticated user on exit."""
        # Arrange
        mock_screen = Mock()
        mock_set_mode.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_load_fonts.return_value = {}
        mock_load_images.return_value = {}
        mock_load_sounds.return_value = {}
        mock_load_levels.return_value = ([], {})
        mock_background.return_value = Mock()

        mock_client = Mock()
        mock_client.is_authenticated = True  # User is logged in
        mock_network_client.return_value = mock_client
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()
        mock_client.logout.assert_called_once()
        mock_quit.assert_called_once()

    @patch('game.main.run_state_machine')
    @patch('game.main.NetworkClient')
    @patch('game.main.Background')
    @patch('game.main.utils.load_high_score', return_value=5000)
    @patch('game.main.load_level_data_and_music')
    @patch('game.main.load_sounds')
    @patch('game.main.load_images')
    @patch('game.main.load_fonts')
    @patch('pygame.time.Clock')
    @patch('pygame.display.set_caption')
    @patch('pygame.display.set_mode')
    @patch('pygame.mixer')
    @patch('pygame.init')
    @patch('pygame.quit')
    @patch('sys.exit')
    def test_main_mixer_unavailable(
        self,
        mock_sys_exit,
        mock_quit,
        mock_pygame_init,
        mock_mixer,
        mock_set_mode,
        mock_set_caption,
        mock_clock,
        mock_load_fonts,
        mock_load_images,
        mock_load_sounds,
        mock_load_levels,
        mock_load_high_score,
        mock_background,
        mock_network_client,
        mock_run_state_machine
    ):
        """Test main function handles missing mixer module."""
        # Arrange
        mock_mixer = None  # Mixer not available
        mock_screen = Mock()
        mock_set_mode.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_load_fonts.return_value = {}
        mock_load_images.return_value = {}
        mock_load_sounds.return_value = {}
        mock_load_levels.return_value = ([], {})
        mock_background.return_value = Mock()

        mock_client = Mock()
        mock_client.is_authenticated = False
        mock_network_client.return_value = mock_client
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()
        # Should continue without mixer
        mock_run_state_machine.assert_called_once()
        mock_sys_exit.assert_called_once()

    @patch('game.main.run_state_machine')
    @patch('game.main.NetworkClient')
    @patch('game.main.Background')
    @patch('game.main.utils.load_high_score', return_value=2500)
    @patch('game.main.load_level_data_and_music')
    @patch('game.main.load_sounds')
    @patch('game.main.load_images')
    @patch('game.main.load_fonts')
    @patch('pygame.time.Clock')
    @patch('pygame.display.set_caption')
    @patch('pygame.display.set_mode')
    @patch('pygame.mixer.init')
    @patch('pygame.init')
    @patch('pygame.quit')
    @patch('sys.exit')
    def test_main_mixer_init_failure(
        self,
        mock_sys_exit,
        mock_quit,
        mock_pygame_init,
        mock_mixer_init,
        mock_set_mode,
        mock_set_caption,
        mock_clock,
        mock_load_fonts,
        mock_load_images,
        mock_load_sounds,
        mock_load_levels,
        mock_load_high_score,
        mock_background,
        mock_network_client,
        mock_run_state_machine
    ):
        """Test main function handles mixer initialization failure."""
        # Arrange
        mock_mixer_init.side_effect = pygame.error("Mixer init failed")
        mock_screen = Mock()
        mock_set_mode.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_load_fonts.return_value = {}
        mock_load_images.return_value = {}
        mock_load_sounds.return_value = {}
        mock_load_levels.return_value = ([], {})
        mock_background.return_value = Mock()

        mock_client = Mock()
        mock_client.is_authenticated = False
        mock_network_client.return_value = mock_client
        mock_sys_exit.side_effect = SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            main.main()
        # Should continue without sound
        mock_run_state_machine.assert_called_once()
        mock_sys_exit.assert_called_once()
