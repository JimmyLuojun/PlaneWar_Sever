"""Tests for game/ui.py - UI screen rendering and input handling."""

import os
# Set SDL to dummy mode BEFORE importing pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pytest
from unittest.mock import patch, Mock
import pygame
from game import ui


class TestShowLoginScreen:
    """Tests for show_login_screen function."""

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_login_screen_quit_event(self, mock_clock, mock_flip, mock_event):
        """Test login screen handles quit event."""
        mock_event.return_value = [pygame.event.Event(pygame.QUIT)]
        mock_screen = Mock()
        mock_fonts = {'medium': Mock(), 'small': Mock()}
        mock_client = Mock()

        action, username, message = ui.show_login_screen(mock_screen, mock_fonts, mock_client)

        assert action == 'QUIT'
        assert username is None
        assert message == 'User quit'

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_login_screen_escape_key(self, mock_clock, mock_flip, mock_event):
        """Test login screen handles escape key."""
        mock_event.return_value = [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})]
        mock_screen = Mock()
        mock_fonts = {'medium': Mock(), 'small': Mock()}
        mock_client = Mock()

        action, username, message = ui.show_login_screen(mock_screen, mock_fonts, mock_client)

        assert action == 'QUIT'
        assert username is None

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    @patch('pygame.time.get_ticks', return_value=0)
    def test_show_login_screen_typing(self, mock_ticks, mock_clock, mock_flip, mock_event):
        """Test login screen handles text input."""
        mock_event.side_effect = [
            [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'unicode': 'a'})],
            [pygame.event.Event(pygame.QUIT)]
        ]
        mock_screen = Mock()
        mock_fonts = {'medium': Mock(), 'small': Mock()}
        mock_client = Mock()

        action, username, message = ui.show_login_screen(mock_screen, mock_fonts, mock_client)

        assert action == 'QUIT'

    @patch('pygame.mouse.get_pos', return_value=(400, 450))
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    @patch('pygame.time.get_ticks', return_value=0)
    def test_show_login_screen_successful_login(self, mock_ticks, mock_clock, mock_flip, mock_event, mock_mouse):
        """Test login screen handles successful login."""
        mock_login_result = Mock()
        mock_login_result.success = True
        mock_login_result.username = 'testuser'
        mock_client = Mock()
        mock_client.login.return_value = mock_login_result

        # Simulate username input, password input, and login button click
        mock_event.side_effect = [
            [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t, 'unicode': 't'})],
            [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_TAB})],
            [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_p, 'unicode': 'p'})],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (400, 450), 'button': 1})],
        ]

        mock_screen = Mock()
        mock_fonts = {'medium': Mock(), 'small': Mock()}

        action, username, message = ui.show_login_screen(mock_screen, mock_fonts, mock_client)

        assert action == 'LOGIN_SUCCESS'
        assert username == 'testuser'
        assert message == 'Login successful'


class TestShowStartScreen:
    """Tests for show_start_screen function."""

    @patch('game.progress.get_max_unlocked_level', return_value=3)
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_start_screen_quit_event(self, mock_clock, mock_flip, mock_event, mock_progress):
        """Test start screen handles quit event."""
        mock_event.return_value = [pygame.event.Event(pygame.QUIT)]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'title': Mock(), 'small': Mock()}

        result = ui.show_start_screen(mock_screen, mock_fonts)

        assert result == 'QUIT'

    @patch('game.progress.get_max_unlocked_level', return_value=3)
    @patch('pygame.mouse.get_pos', return_value=(400, 300))
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_start_screen_any_key_continues(self, mock_clock, mock_flip, mock_event, mock_mouse, mock_progress):
        """Test start screen level selection."""
        # Simulate clicking on a level button (approximate position)
        mock_event.return_value = [pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (400, 300)})]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'title': Mock(), 'small': Mock()}

        result = ui.show_start_screen(mock_screen, mock_fonts)

        # Result should be LEVEL_X format
        assert result.startswith('LEVEL_')


class TestShowEndScreen:
    """Tests for show_end_screen function."""

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_end_screen_quit_event(self, mock_clock, mock_flip, mock_event):
        """Test end screen handles quit event."""
        mock_event.return_value = [pygame.event.Event(pygame.QUIT)]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'small': Mock()}

        result = ui.show_end_screen(mock_screen, mock_fonts, 'WIN', 5000, 'Submitted')

        assert result == 'QUIT'

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_end_screen_replay(self, mock_clock, mock_flip, mock_event):
        """Test end screen handles replay key."""
        mock_event.return_value = [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_r})]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'small': Mock()}

        result = ui.show_end_screen(mock_screen, mock_fonts, 'WIN', 5000, 'Submitted')

        assert result == 'REPLAY'

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_end_screen_escape(self, mock_clock, mock_flip, mock_event):
        """Test end screen handles escape key."""
        mock_event.return_value = [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'small': Mock()}

        result = ui.show_end_screen(mock_screen, mock_fonts, 'LOSE', 3000, 'Failed')

        assert result == 'QUIT'

    @patch('pygame.event.get', return_value=[])
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_show_end_screen_win_status(self, mock_clock, mock_flip, mock_event):
        """Test end screen displays win status."""
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock(), 'small': Mock()}
        mock_fonts['large'].render = Mock(return_value=Mock())
        mock_fonts['medium'].render = Mock(return_value=Mock())
        mock_fonts['small'].render = Mock(return_value=Mock())

        # Run one iteration then quit
        mock_event.side_effect = [[], [pygame.event.Event(pygame.QUIT)]]

        result = ui.show_end_screen(mock_screen, mock_fonts, 'WIN', 5000, 'Submitted')

        assert result == 'QUIT'


class TestShowLevelStartScreen:
    """Tests for show_level_start_screen function."""

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    @patch('pygame.time.get_ticks', side_effect=[0, 2500])
    def test_show_level_start_screen_auto_advance(self, mock_ticks, mock_clock, mock_flip, mock_event):
        """Test level start screen auto-advances after delay."""
        mock_event.return_value = []
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock()}

        result = ui.show_level_start_screen(mock_screen, mock_fonts, 1, 2000)

        assert result == 'START_LEVEL'

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    @patch('pygame.time.get_ticks', return_value=0)
    def test_show_level_start_screen_quit_event(self, mock_ticks, mock_clock, mock_flip, mock_event):
        """Test level start screen handles quit event."""
        mock_event.return_value = [pygame.event.Event(pygame.QUIT)]
        mock_screen = Mock()
        mock_fonts = {'large': Mock(), 'medium': Mock()}

        result = ui.show_level_start_screen(mock_screen, mock_fonts, 1, 2000)

        assert result == 'QUIT'


class TestHelperFunctions:
    """Tests for UI helper functions."""

    @patch('pygame.draw.rect')
    def test_draw_input_box(self, mock_draw):
        """Test drawing input box."""
        mock_screen = Mock()
        mock_font = Mock()
        mock_font.render = Mock(return_value=Mock())

        ui._draw_input_box(mock_screen, mock_font, 'test', 100, 200, 300, True, False, 0)

        assert mock_draw.called

    @patch('pygame.Surface')
    def test_create_semi_transparent_overlay(self, mock_surface):
        """Test creating semi-transparent overlay."""
        mock_surface_instance = Mock()
        mock_surface.return_value = mock_surface_instance

        result = ui._create_semi_transparent_overlay(800, 600)

        assert result == mock_surface_instance

    def test_determine_message_color_success(self):
        """Test determining message color for success."""
        color = ui._determine_message_color('success', True)

        assert color == (0, 255, 0)

    def test_determine_message_color_error(self):
        """Test determining message color for error."""
        color = ui._determine_message_color('error', True)

        assert color == (255, 100, 100)

    def test_determine_status_color_submitted(self):
        """Test determining status color for submitted."""
        color = ui._determine_status_color('Submitted successfully')

        assert color == (100, 255, 100)

    def test_determine_status_color_failed(self):
        """Test determining status color for failed."""
        color = ui._determine_status_color('Submission failed')

        assert color == (255, 150, 150)

    def test_determine_status_color_offline(self):
        """Test determining status color for offline."""
        color = ui._determine_status_color('Saved locally (offline)')

        assert color == (200, 200, 100)
