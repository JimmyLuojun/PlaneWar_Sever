"""Tests for game/states.py - Application state machine."""

import os
# Set SDL to dummy mode BEFORE importing pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame
from game import states


class TestRunStateMachine:
    """Tests for run_state_machine function."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for run_state_machine."""
        pygame.init()
        screen = Mock(spec=pygame.Surface)
        clock = Mock(spec=pygame.time.Clock)
        fonts = {'title': Mock(), 'medium': Mock(), 'score': Mock(), 'small': Mock()}
        images = {'player': Mock(), 'boss': Mock(), 'enemy1': Mock()}
        sounds = {'shoot': Mock(), 'explosion': Mock()}
        levels = [
            {'level_number': 1, 'enemy_types': ['enemy1']},
            {'level_number': 2, 'enemy_types': ['enemy1', 'enemy2']}
        ]
        music_paths = {1: 'music1.mp3', 2: 'music2.mp3'}
        background = Mock()
        high_score = 1000
        network_client = Mock()
        network_client.is_authenticated = False

        return {
            'screen': screen,
            'clock': clock,
            'fonts': fonts,
            'images': images,
            'sounds': sounds,
            'levels': levels,
            'music_paths': music_paths,
            'background': background,
            'high_score': high_score,
            'network_client': network_client
        }

    @patch('game.states.ui')
    def test_run_state_machine_login_then_quit(self, mock_ui, mock_dependencies):
        """Test state machine handles login success then quit."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('QUIT', None, 'User quit')

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        mock_ui.show_login_screen.assert_called_once()

    @patch('game.states.ui')
    def test_run_state_machine_login_success_then_level_select(self, mock_ui, mock_dependencies):
        """Test state machine handles login success and level selection."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'testuser', 'Login successful')
        mock_ui.show_start_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        mock_ui.show_login_screen.assert_called_once()
        mock_ui.show_start_screen.assert_called_once()

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_complete_level_flow(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles complete level flow."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'LEVEL_1'
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'
        # First level passed, second level passed (completes all levels)
        mock_run_game.side_effect = [('PASSED', 1000, 1), ('PASSED', 2000, 2)]
        mock_ui.show_end_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        mock_ui.show_login_screen.assert_called_once()
        mock_ui.show_start_screen.assert_called_once()
        # show_level_start_screen is called twice (once for each level)
        assert mock_ui.show_level_start_screen.call_count == 2
        # run_game is called twice (once for each level)
        assert mock_run_game.call_count == 2
        mock_ui.show_end_screen.assert_called_once()

    @patch('game.states.ui')
    def test_run_state_machine_login_fail(self, mock_ui, mock_dependencies):
        """Test state machine handles login failure."""
        # Arrange
        mock_ui.show_login_screen.side_effect = [
            ('LOGIN_FAIL', None, 'Invalid credentials'),
            ('QUIT', None, 'User quit')
        ]

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        assert mock_ui.show_login_screen.call_count == 2

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_level_failed(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles level failure."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'LEVEL_1'
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'
        mock_run_game.return_value = ('FAILED', 500, 1)  # Level failed
        mock_ui.show_end_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        mock_ui.show_end_screen.assert_called_once()
        # Check that end screen received LOSE status
        call_args = mock_ui.show_end_screen.call_args
        assert 'LOSE' in call_args[0] or 'LOSE' in str(call_args)

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_replay_after_loss(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles replay after losing."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.side_effect = ['LEVEL_1', 'QUIT']
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'
        mock_run_game.return_value = ('FAILED', 300, 1)
        mock_ui.show_end_screen.return_value = 'REPLAY'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        assert mock_ui.show_start_screen.call_count == 2

    @patch('game.states.run_game')
    @patch('game.states.ui')
    @patch('pygame.mixer')
    def test_run_state_machine_music_management(self, mock_mixer, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine manages music correctly."""
        # Arrange
        mock_music = Mock()
        mock_mixer.music = mock_music
        mock_music.get_busy.return_value = True

        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        # Music should be stopped when transitioning to start screen
        mock_music.stop.assert_called()
        mock_music.unload.assert_called()

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_level_selection_level_2(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles selection of level 2."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'LEVEL_2'  # Select level 2
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'
        mock_run_game.return_value = ('PASSED', 2000, 2)
        mock_ui.show_end_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        # Should start from level 2
        call_args = mock_run_game.call_args
        # run_game is called with positional args: (screen, clock, fonts, images, sounds, level_data, background)
        level_data = call_args[0][5]  # level_data is the 6th argument (index 5)
        assert level_data['level_number'] == 2

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_invalid_level_selection(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles invalid level selection."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.side_effect = ['LEVEL_999', 'QUIT']  # Invalid level

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        # Should return to start screen after invalid selection
        assert mock_ui.show_start_screen.call_count == 2
        # run_game should not be called
        mock_run_game.assert_not_called()

    @patch('game.states.utils')
    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_high_score_update(self, mock_ui, mock_run_game, mock_utils, mock_dependencies):
        """Test state machine updates high score."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'LEVEL_1'
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'
        mock_run_game.return_value = ('PASSED', 5000, 1)  # New high score
        mock_ui.show_end_screen.return_value = 'QUIT'

        mock_dependencies['high_score'] = 1000  # Current high score

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        # Should save new high score
        mock_utils.save_high_score.assert_called()

    @patch('game.states.run_game')
    @patch('game.states.ui')
    def test_run_state_machine_all_levels_completed(self, mock_ui, mock_run_game, mock_dependencies):
        """Test state machine handles completing all levels."""
        # Arrange
        mock_ui.show_login_screen.return_value = ('LOGIN_SUCCESS', 'player1', 'Success')
        mock_ui.show_start_screen.return_value = 'LEVEL_1'
        mock_ui.show_level_start_screen.return_value = 'CONTINUE'

        # Pass both levels
        mock_run_game.side_effect = [
            ('PASSED', 1000, 1),
            ('PASSED', 2000, 2)
        ]
        mock_ui.show_end_screen.return_value = 'QUIT'

        # Act
        states.run_state_machine(**mock_dependencies)

        # Assert
        # Should show end screen with win status
        call_args = mock_ui.show_end_screen.call_args
        assert 'WIN' in str(call_args)


class TestStateConstants:
    """Tests for state constant definitions."""

    def test_state_constants_defined(self):
        """Test all state constants are defined."""
        assert hasattr(states, 'STATE_LOGIN')
        assert hasattr(states, 'STATE_START')
        assert hasattr(states, 'STATE_LEVEL_START')
        assert hasattr(states, 'STATE_RUNNING')
        assert hasattr(states, 'STATE_GAME_WON')
        assert hasattr(states, 'STATE_GAME_OVER')
        assert hasattr(states, 'STATE_END')

    def test_state_constants_values(self):
        """Test state constants have correct values."""
        assert states.STATE_LOGIN == "LOGIN_SCREEN"
        assert states.STATE_START == "START_SCREEN"
        assert states.STATE_LEVEL_START == "LEVEL_START"
        assert states.STATE_RUNNING == "RUNNING_LEVEL"
        assert states.STATE_GAME_WON == "GAME_WON"
        assert states.STATE_GAME_OVER == "GAME_OVER"
        assert states.STATE_END == "END_SCREEN"
