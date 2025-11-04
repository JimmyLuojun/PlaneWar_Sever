"""Tests for game/utils.py - Utility functions and asset loading."""

import pytest
from unittest.mock import patch, mock_open, Mock
import json
import os
import pygame
from game.utils import (
    AssetLoader,
    load_high_score,
    save_high_score,
    load_level_data,
    _load_single_level_file,
    _resolve_absolute_path
)


class TestAssetLoader:
    """Tests for AssetLoader class."""

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    @patch('os.path.exists', return_value=True)
    def test_load_and_scale_image_success(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test loading and scaling image successfully."""
        mock_load.return_value = mock_image
        mock_scale.return_value = mock_image
        loader = AssetLoader()

        result = loader.load_and_scale_image('test.png', 64, 64)

        assert result == mock_image
        mock_scale.assert_called_once_with(mock_image, (64, 64))

    @patch('os.path.exists', return_value=False)
    @patch('pygame.Surface')
    def test_load_and_scale_image_fallback(self, mock_surface, mock_exists):
        """Test fallback when image file missing."""
        mock_surface_instance = Mock()
        mock_surface.return_value = mock_surface_instance
        loader = AssetLoader()

        result = loader.load_and_scale_image('missing.png', 64, 64)

        assert result == mock_surface_instance

    @patch('pygame.image.load', side_effect=pygame.error)
    @patch('os.path.exists', return_value=True)
    @patch('pygame.Surface')
    def test_load_and_scale_image_pygame_error(self, mock_surface, mock_exists, mock_load):
        """Test fallback on pygame error."""
        mock_surface_instance = Mock()
        mock_surface.return_value = mock_surface_instance
        loader = AssetLoader()

        result = loader.load_and_scale_image('corrupt.png', 64, 64)

        assert result == mock_surface_instance

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    @patch('os.path.exists', return_value=True)
    def test_load_and_scale_image_with_colorkey(self, mock_exists, mock_scale, mock_load, mock_image):
        """Test loading image with colorkey transparency."""
        mock_load.return_value = mock_image
        mock_scale.return_value = mock_image
        mock_image.get_at.return_value = pygame.Color(255, 0, 255)
        loader = AssetLoader()

        result = loader.load_and_scale_image('test.png', 64, 64, use_colorkey=True)

        mock_image.set_colorkey.assert_called()

    @patch('pygame.mixer.Sound')
    @patch('os.path.exists', return_value=True)
    def test_load_sound_success(self, mock_exists, mock_sound_class, mock_sound):
        """Test loading sound successfully."""
        mock_sound_class.return_value = mock_sound
        loader = AssetLoader()

        result = loader.load_sound('test.wav', 0.5)

        assert result == mock_sound
        mock_sound.set_volume.assert_called_once_with(0.5)

    @patch('os.path.exists', return_value=False)
    def test_load_sound_file_missing(self, mock_exists):
        """Test loading sound returns None when file missing."""
        loader = AssetLoader()

        result = loader.load_sound('missing.wav')

        assert result is None

    @patch('pygame.mixer.Sound', side_effect=pygame.error)
    @patch('os.path.exists', return_value=True)
    def test_load_sound_mixer_unavailable(self, mock_exists, mock_sound):
        """Test loading sound returns None when mixer unavailable."""
        loader = AssetLoader()

        result = loader.load_sound('test.wav')

        assert result is None

    @patch('pygame.Surface')
    @patch('pygame.draw.rect')
    def test_create_fallback_surface(self, mock_draw, mock_surface_class):
        """Test creating fallback surface."""
        mock_surface_instance = Mock()
        mock_surface_class.return_value = mock_surface_instance
        loader = AssetLoader()

        result = loader._create_fallback_surface(64, 64)

        assert result == mock_surface_instance
        mock_draw.assert_called()

    @patch('random.randint', return_value=128)
    def test_random_fallback_color(self, mock_randint):
        """Test generating random fallback color."""
        loader = AssetLoader()

        color = loader._random_fallback_color()

        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)


class TestLoadHighScore:
    """Tests for load_high_score function."""

    @patch('builtins.open', new_callable=mock_open, read_data='5000')
    @patch('os.path.exists', return_value=True)
    def test_load_high_score_success(self, mock_exists, mock_file):
        """Test loading high score from file."""
        result = load_high_score('highscore.txt')

        assert result == 5000

    @patch('os.path.exists', return_value=False)
    def test_load_high_score_file_missing(self, mock_exists):
        """Test loading high score returns 0 when file missing."""
        result = load_high_score('highscore.txt')

        assert result == 0

    @patch('builtins.open', new_callable=mock_open, read_data='invalid')
    @patch('os.path.exists', return_value=True)
    def test_load_high_score_invalid_data(self, mock_exists, mock_file):
        """Test loading high score returns 0 for invalid data."""
        result = load_high_score('highscore.txt')

        assert result == 0


class TestSaveHighScore:
    """Tests for save_high_score function."""

    @patch('builtins.open', new_callable=mock_open)
    def test_save_high_score_success(self, mock_file):
        """Test saving high score to file."""
        save_high_score('highscore.txt', 6000)

        mock_file.assert_called_once_with('highscore.txt', 'w')
        handle = mock_file()
        handle.write.assert_called_once_with('6000')

    @patch('builtins.open', side_effect=IOError)
    def test_save_high_score_io_error(self, mock_file):
        """Test saving high score handles IO error gracefully."""
        try:
            save_high_score('highscore.txt', 6000)
        except IOError:
            pytest.fail("save_high_score should handle IOError gracefully")


class TestLoadLevelData:
    """Tests for load_level_data function."""

    @patch('os.listdir', return_value=['level1.json', 'level2.json'])
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"level_number": 1, "music": "level1.mp3"}')
    def test_load_level_data_success(self, mock_file, mock_exists, mock_listdir):
        """Test loading level data from directory."""
        result = load_level_data('levels')

        assert len(result) == 2

    @patch('os.path.exists', return_value=False)
    def test_load_level_data_directory_missing(self, mock_exists):
        """Test loading level data when directory missing."""
        result = load_level_data('missing')

        assert result == []

    @patch('os.listdir', return_value=['level1.json', 'readme.txt'])
    @patch('os.path.exists', return_value=True)
    def test_load_level_data_filters_non_json(self, mock_exists, mock_listdir):
        """Test loading level data filters non-JSON files."""
        with patch('game.utils._load_single_level_file', return_value={'level_number': 1}):
            result = load_level_data('levels')

        assert len(result) == 1

    @patch('os.listdir', return_value=['level2.json', 'level1.json', 'level3.json'])
    @patch('os.path.exists', return_value=True)
    def test_load_level_data_sorts_by_level_number(self, mock_exists, mock_listdir):
        """Test level data is sorted by level_number."""
        with patch('game.utils._load_single_level_file', side_effect=[
            {'level_number': 2},
            {'level_number': 1},
            {'level_number': 3}
        ]):
            result = load_level_data('levels')

        assert result[0]['level_number'] == 1
        assert result[1]['level_number'] == 2
        assert result[2]['level_number'] == 3


class TestLoadSingleLevelFile:
    """Tests for _load_single_level_file function."""

    @patch('builtins.open', new_callable=mock_open, read_data='{"level_number": 1, "music": "level1.mp3"}')
    def test_load_single_level_file_success(self, mock_file):
        """Test loading single level file successfully."""
        result = _load_single_level_file('level1.json')

        assert result['level_number'] == 1
        assert result['music'] == 'level1.mp3'

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_single_level_file_invalid_json(self, mock_file):
        """Test loading single level file with invalid JSON returns None."""
        result = _load_single_level_file('invalid.json')

        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='{"music": "level1.mp3"}')
    def test_load_single_level_file_missing_level_number(self, mock_file):
        """Test loading level file without level_number returns None."""
        result = _load_single_level_file('incomplete.json')

        assert result is None

    @patch('builtins.open', side_effect=IOError)
    def test_load_single_level_file_io_error(self, mock_file):
        """Test loading level file handles IO error."""
        result = _load_single_level_file('error.json')

        assert result is None


class TestResolveAbsolutePath:
    """Tests for _resolve_absolute_path function."""

    def test_resolve_absolute_path_already_absolute(self):
        """Test resolving already absolute path."""
        abs_path = '/absolute/path/to/file.mp3'
        result = _resolve_absolute_path(abs_path, 'levels')

        assert result == abs_path

    def test_resolve_absolute_path_relative(self):
        """Test resolving relative path."""
        rel_path = 'music/level1.mp3'
        base_dir = '/game/levels'

        result = _resolve_absolute_path(rel_path, base_dir)

        assert result == os.path.join(base_dir, rel_path)
