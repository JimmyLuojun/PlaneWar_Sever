"""Tests for game/assets.py - Asset loading functionality."""

import pytest
from unittest.mock import patch, Mock, mock_open
import json
from plane_war_server.game.infrastructure import assets


class TestLoadFonts:
    """Tests for load_fonts function."""

    @patch('pygame.font.Font')
    @patch('os.path.exists', return_value=True)
    def test_load_fonts_success(self, mock_exists, mock_font):
        """Test successful font loading."""
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance

        fonts = assets.load_fonts()

        assert 'title' in fonts
        assert 'large' in fonts
        assert 'score' in fonts
        assert fonts['title'] == mock_font_instance

    @patch('pygame.font.SysFont')
    @patch('os.path.exists', return_value=False)
    def test_load_fonts_fallback(self, mock_exists, mock_sysfont):
        """Test font loading falls back to system font when file missing."""
        mock_sysfont_instance = Mock()
        mock_sysfont.return_value = mock_sysfont_instance

        fonts = assets.load_fonts()

        assert mock_sysfont.called
        assert fonts['title'] == mock_sysfont_instance


class TestLoadImages:
    """Tests for load_images function."""

    @patch('plane_war_server.game.infrastructure.utils.load_and_scale_image')
    def test_load_images_success(self, mock_load):
        """Test successful image loading."""
        mock_image = Mock()
        mock_load.return_value = mock_image

        images = assets.load_images()

        assert 'player' in images
        assert 'enemy1' in images
        assert 'boss' in images
        assert 'powerups' in images
        assert isinstance(images['powerups'], dict)
        assert images['player'] == mock_image

    @patch('plane_war_server.game.infrastructure.utils.load_and_scale_image', return_value=None)
    def test_load_images_handles_none(self, mock_load):
        """Test loading handles None returns gracefully."""
        images = assets.load_images()

        assert images['player'] is None


class TestLoadSounds:
    """Tests for load_sounds function."""

    @patch('pygame.mixer.get_init', return_value=True)
    @patch('plane_war_server.game.infrastructure.utils.load_sound')
    def test_load_sounds_success(self, mock_load_sound, mock_mixer_init):
        """Test successful sound loading."""
        mock_sound = Mock()
        mock_load_sound.return_value = mock_sound

        sounds = assets.load_sounds()

        assert 'player_shoot' in sounds
        assert 'enemy_explode' in sounds
        assert 'powerup_pickup' in sounds
        assert sounds['player_shoot'] == mock_sound

    @patch('pygame.mixer.get_init', return_value=False)
    def test_load_sounds_mixer_unavailable(self, mock_mixer_init):
        """Test sound loading when mixer unavailable."""
        sounds = assets.load_sounds()

        assert sounds == {}


class TestLoadLevelDataAndMusic:
    """Tests for load_level_data_and_music function."""

    @patch('plane_war_server.game.infrastructure.utils.load_level_data')
    def test_load_level_data_and_music_success(self, mock_load_data):
        """Test successful level data loading."""
        mock_level_data = [
            {'level_number': 1, 'music': 'level1.mp3'},
            {'level_number': 2, 'music': 'level2.mp3'}
        ]
        mock_load_data.return_value = mock_level_data

        levels_list, music_paths = assets.load_level_data_and_music()

        assert levels_list == mock_level_data
        assert len(levels_list) == 2
        assert isinstance(music_paths, dict)

    @patch('plane_war_server.game.infrastructure.assets.sys.exit')
    @patch('plane_war_server.game.infrastructure.assets.pygame.quit')
    @patch('plane_war_server.game.infrastructure.utils.load_level_data', return_value=[])
    def test_load_level_data_empty(self, mock_load_data, mock_quit, mock_exit):
        """Test when no levels found calls sys.exit."""
        assets.load_level_data_and_music()

        # Should call sys.exit when no levels found
        mock_exit.assert_called_once()