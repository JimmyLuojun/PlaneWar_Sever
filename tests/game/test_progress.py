"""Tests for game/progress.py - Progress tracking and level unlocking."""

import pytest
from unittest.mock import patch, mock_open, Mock
import json
import os
from game import progress


class TestLoadProgress:
    """Tests for load_progress function."""

    @patch('builtins.open', new_callable=mock_open, read_data='{"max_unlocked_level": 3}')
    @patch('os.path.exists', return_value=True)
    def test_load_progress_success(self, mock_exists, mock_file):
        """Test loading progress from valid file."""
        result = progress.load_progress()

        assert result == {"max_unlocked_level": 3}

    @patch('os.path.exists', return_value=False)
    def test_load_progress_file_missing(self, mock_exists):
        """Test loading progress when file missing returns default."""
        result = progress.load_progress()

        assert result == {"max_unlocked_level": 1}

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('os.path.exists', return_value=True)
    def test_load_progress_invalid_json(self, mock_exists, mock_file):
        """Test loading progress with invalid JSON returns default."""
        result = progress.load_progress()

        assert result == {"max_unlocked_level": 1}


class TestSaveProgress:
    """Tests for save_progress function."""

    @patch('builtins.open', new_callable=mock_open)
    def test_save_progress_success(self, mock_file):
        """Test saving progress to file."""
        progress.save_progress(5)

        mock_file.assert_called_once()
        handle = mock_file()
        written_data = ''.join([call.args[0] for call in handle.write.call_args_list])
        data = json.loads(written_data)
        assert data == {"max_unlocked_level": 5}

    @patch('builtins.open', side_effect=IOError)
    def test_save_progress_io_error(self, mock_file):
        """Test saving progress handles IO errors gracefully."""
        try:
            progress.save_progress(5)
        except IOError:
            pytest.fail("save_progress should handle IOError gracefully")


class TestGetMaxUnlockedLevel:
    """Tests for get_max_unlocked_level function."""

    @patch('game.progress.load_progress', return_value={"max_unlocked_level": 4})
    def test_get_max_unlocked_level(self, mock_load):
        """Test getting max unlocked level."""
        result = progress.get_max_unlocked_level()

        assert result == 4


class TestGetTotalAvailableLevelsCount:
    """Tests for get_total_available_levels_count function."""

    @patch('game.progress.os.listdir', return_value=['level_1.json', 'level_2.json', 'level_3.json'])
    @patch('game.progress.os.path.exists', return_value=True)
    def test_get_total_available_levels_count_success(self, mock_exists, mock_listdir):
        """Test counting level files."""
        result = progress.get_total_available_levels_count()

        assert result == 3

    @patch('game.progress.os.path.exists', return_value=False)
    def test_get_total_available_levels_count_missing_dir(self, mock_exists):
        """Test counting levels when directory missing."""
        result = progress.get_total_available_levels_count()

        assert result == 0

    @patch('game.progress.os.listdir', return_value=['level_1.json', 'readme.txt', 'level_2.json'])
    @patch('game.progress.os.path.exists', return_value=True)
    def test_get_total_available_levels_count_filters_non_json(self, mock_exists, mock_listdir):
        """Test counting only JSON files."""
        result = progress.get_total_available_levels_count()

        assert result == 2


class TestGetLevelPath:
    """Tests for get_level_path function."""

    def test_get_level_path(self):
        """Test generating level file path."""
        result = progress.get_level_path(3)

        assert result.endswith('levels/level_3.json')


class TestUnlockLevel:
    """Tests for unlock_level function."""

    @patch('game.progress.get_total_available_levels_count', return_value=5)
    @patch('game.progress.get_max_unlocked_level', return_value=2)
    @patch('game.progress.save_progress')
    def test_unlock_level_unlocks_next_level(self, mock_save, mock_get_max, mock_count):
        """Test unlocking next level after completing current."""
        progress.unlock_level(2)

        mock_save.assert_called_once_with(3)

    @patch('game.progress.get_total_available_levels_count', return_value=5)
    @patch('game.progress.get_max_unlocked_level', return_value=5)
    @patch('game.progress.save_progress')
    def test_unlock_level_already_at_max(self, mock_save, mock_get_max, mock_count):
        """Test unlocking when already at max level."""
        progress.unlock_level(4)

        assert not mock_save.called

    @patch('game.progress.get_total_available_levels_count', return_value=3)
    @patch('game.progress.get_max_unlocked_level', return_value=3)
    @patch('game.progress.save_progress')
    def test_unlock_level_at_final_level(self, mock_save, mock_get_max, mock_count):
        """Test completing final level doesn't unlock beyond."""
        progress.unlock_level(3)

        assert not mock_save.called

    @patch('game.progress.get_total_available_levels_count', return_value=5)
    @patch('game.progress.get_max_unlocked_level', return_value=1)
    @patch('game.progress.save_progress')
    def test_unlock_level_with_zero(self, mock_save, mock_get_max, mock_count):
        """Test unlocking with zero doesn't unlock next level."""
        progress.unlock_level(0)

        # Should not save since 0 is not a valid completed level
        assert not mock_save.called


class TestValidateLevelNumber:
    """Tests for _validate_level_number function."""

    def test_validate_level_number_valid(self):
        """Test validating valid level number returns it unchanged."""
        result = progress._validate_level_number(5)
        assert result == 5

    def test_validate_level_number_zero(self):
        """Test validating zero returns default minimum."""
        result = progress._validate_level_number(0)
        assert result >= 1  # Should be at least the default

    def test_validate_level_number_negative(self):
        """Test validating negative number returns default minimum."""
        result = progress._validate_level_number(-1)
        assert result >= 1  # Should be at least the default


class TestCreateDefaultProgress:
    """Tests for _create_default_progress function."""

    def test_create_default_progress(self):
        """Test creating default progress data."""
        result = progress._create_default_progress()

        assert result == {"max_unlocked_level": 1}
