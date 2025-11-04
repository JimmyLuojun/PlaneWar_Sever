"""Player progress tracking and level unlocking system.

Provides functions for loading, saving, and managing player progression
through game levels. Tracks the highest unlocked level and persists
progress to a JSON file.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import json
import os
from typing import Dict, Any

# Local
from . import settings


# ============================================================================
# Constants
# ============================================================================

# Path to the progress save file
PROGRESS_FILE_PATH: str = os.path.join(settings.BASE_DIR, "progress.json")

# Default starting level (always unlocked)
DEFAULT_MAX_UNLOCKED_LEVEL: int = 1

# JSON keys
KEY_MAX_UNLOCKED_LEVEL: str = "max_unlocked_level"


# ============================================================================
# Type Definitions
# ============================================================================

ProgressData = Dict[str, Any]


# ============================================================================
# Helper Functions
# ============================================================================


def _validate_level_number(level_number: int) -> int:
    """Ensure level number is at least the default minimum.

    Args:
        level_number: The level number to validate

    Returns:
        Validated level number (at least DEFAULT_MAX_UNLOCKED_LEVEL)
    """
    return max(level_number, DEFAULT_MAX_UNLOCKED_LEVEL)


def _create_default_progress() -> ProgressData:
    """Create default progress data structure.

    Returns:
        Dictionary with default progress values
    """
    return {KEY_MAX_UNLOCKED_LEVEL: DEFAULT_MAX_UNLOCKED_LEVEL}


# ============================================================================
# Public API Functions - Load/Save
# ============================================================================


def load_progress() -> ProgressData:
    """Load player progress from the save file.

    Reads the progress JSON file and validates the data. Returns default
    progress if the file doesn't exist or contains invalid data.

    Returns:
        Dictionary containing progress data with 'max_unlocked_level' key
    """
    if not os.path.exists(PROGRESS_FILE_PATH):
        return _create_default_progress()

    try:
        with open(PROGRESS_FILE_PATH, "r") as f:
            data = json.load(f)

        # Validate data structure
        if KEY_MAX_UNLOCKED_LEVEL not in data:
            data[KEY_MAX_UNLOCKED_LEVEL] = DEFAULT_MAX_UNLOCKED_LEVEL
        elif not isinstance(data[KEY_MAX_UNLOCKED_LEVEL], int):
            data[KEY_MAX_UNLOCKED_LEVEL] = DEFAULT_MAX_UNLOCKED_LEVEL
        else:
            # Ensure level is at least the minimum
            data[KEY_MAX_UNLOCKED_LEVEL] = _validate_level_number(
                data[KEY_MAX_UNLOCKED_LEVEL]
            )

        return data

    except (IOError, json.JSONDecodeError):
        return _create_default_progress()


def save_progress(max_unlocked_level: int) -> None:
    """Save player progress to the save file.

    Args:
        max_unlocked_level: The highest level the player has unlocked
    """
    validated_level = _validate_level_number(max_unlocked_level)
    progress_data: ProgressData = {KEY_MAX_UNLOCKED_LEVEL: validated_level}

    try:
        with open(PROGRESS_FILE_PATH, "w") as f:
            json.dump(progress_data, f, indent=4)
    except IOError:
        print(f"Error: Could not save progress to {PROGRESS_FILE_PATH}")


# ============================================================================
# Public API Functions - Progress Queries
# ============================================================================


def get_max_unlocked_level() -> int:
    """Get the highest level unlocked by the player.

    Returns:
        The maximum unlocked level number
    """
    progress_data = load_progress()
    return progress_data.get(KEY_MAX_UNLOCKED_LEVEL, DEFAULT_MAX_UNLOCKED_LEVEL)


def get_total_available_levels_count() -> int:
    """Count the total number of level definition files available.

    Scans the levels directory for level_*.json files.

    Returns:
        Number of available level files, or 0 if directory doesn't exist
    """
    if not os.path.exists(settings.LEVELS_DIR):
        print(f"Warning: Levels directory not found at {settings.LEVELS_DIR}")
        return 0

    try:
        level_files = [
            f
            for f in os.listdir(settings.LEVELS_DIR)
            if f.startswith("level_") and f.endswith(".json")
        ]
        return len(level_files)
    except OSError as e:
        print(f"Error: Could not read levels directory: {e}")
        return 0


def get_level_path(level_number: int) -> str:
    """Get the file path for a specific level's definition file.

    Args:
        level_number: The level number

    Returns:
        Full path to the level's JSON file
    """
    return os.path.join(settings.LEVELS_DIR, f"level_{level_number}.json")


# ============================================================================
# Public API Functions - Progress Updates
# ============================================================================


def unlock_level(completed_level_number: int) -> None:
    """Unlock the next level after completing a level.

    Call this when a player successfully completes a level to unlock
    access to the next level. Ensures the completed level itself is
    marked as accessible if it wasn't already.

    Args:
        completed_level_number: The level number the player just finished
    """
    current_max_unlocked = get_max_unlocked_level()
    total_available_levels = get_total_available_levels_count()

    # Ensure the completed level itself is marked as unlocked
    if completed_level_number > current_max_unlocked:
        save_progress(completed_level_number)
        current_max_unlocked = completed_level_number

    # Unlock the next level if applicable
    next_level_to_unlock = completed_level_number + 1

    if (
        next_level_to_unlock > current_max_unlocked
        and next_level_to_unlock <= total_available_levels
    ):
        save_progress(next_level_to_unlock)
        print(f"Progress: Level {next_level_to_unlock} unlocked!")
    elif (
        completed_level_number == total_available_levels
        and completed_level_number > current_max_unlocked
    ):
        # Just beat the last available level for the first time
        save_progress(completed_level_number)
        print(f"Progress: Final level {completed_level_number} access confirmed.")
