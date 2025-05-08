# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/progress.py
import json
import os
from . import settings  # To get the progress file path and LEVELS_DIR

# Path to the progress file
PROGRESS_FILE_PATH = os.path.join(settings.BASE_DIR, "progress.json")
DEFAULT_MAX_UNLOCKED_LEVEL = 1 # Players always have access to level 1

def load_progress():
    """
    Loads the player's progress, specifically the highest unlocked level.
    Returns a dictionary containing progress data. Defaults to level 1 if no file or valid data.
    """
    if not os.path.exists(PROGRESS_FILE_PATH):
        return {"max_unlocked_level": DEFAULT_MAX_UNLOCKED_LEVEL}
    try:
        with open(PROGRESS_FILE_PATH, 'r') as f:
            data = json.load(f)
            if "max_unlocked_level" not in data or not isinstance(data["max_unlocked_level"], int):
                data["max_unlocked_level"] = DEFAULT_MAX_UNLOCKED_LEVEL
            elif data["max_unlocked_level"] < DEFAULT_MAX_UNLOCKED_LEVEL:
                 data["max_unlocked_level"] = DEFAULT_MAX_UNLOCKED_LEVEL
            return data
    except (IOError, json.JSONDecodeError):
        return {"max_unlocked_level": DEFAULT_MAX_UNLOCKED_LEVEL}

def save_progress(max_unlocked_level_to_save):
    """
    Saves the player's progress, specifically the highest unlocked level.
    Args:
        max_unlocked_level_to_save (int): The highest level the player has unlocked.
    """
    if max_unlocked_level_to_save < DEFAULT_MAX_UNLOCKED_LEVEL:
        max_unlocked_level_to_save = DEFAULT_MAX_UNLOCKED_LEVEL

    progress_data = {"max_unlocked_level": max_unlocked_level_to_save}
    try:
        with open(PROGRESS_FILE_PATH, 'w') as f:
            json.dump(progress_data, f, indent=4)
    except IOError:
        print(f"Error: Could not save progress to {PROGRESS_FILE_PATH}")

def get_max_unlocked_level():
    """
    Gets the highest level unlocked by the player.
    """
    progress_data = load_progress()
    return progress_data.get("max_unlocked_level", DEFAULT_MAX_UNLOCKED_LEVEL)

def unlock_level(completed_level_number):
    """
    Call this when a player successfully completes a level.
    It unlocks the *next* level if it's higher than the current max.
    Also ensures the completed level itself is marked as accessible if it wasn't.
    Args:
        completed_level_number (int): The level number the player just finished.
    """
    current_max_unlocked = get_max_unlocked_level()
    total_available_levels = get_total_available_levels_count() # Renamed for clarity

    # Ensure the completed level itself is considered "unlocked"
    if completed_level_number > current_max_unlocked:
        save_progress(completed_level_number)
        current_max_unlocked = completed_level_number # Update for next check

    # Unlock the next level if applicable
    next_level_to_unlock = completed_level_number + 1
    if next_level_to_unlock > current_max_unlocked and next_level_to_unlock <= total_available_levels:
        save_progress(next_level_to_unlock)
        print(f"Progress: Level {next_level_to_unlock} unlocked!")
    elif completed_level_number == total_available_levels and completed_level_number > current_max_unlocked:
        # Case: just beat the last available level, and it was newly unlocked
        save_progress(completed_level_number)
        print(f"Progress: Final level {completed_level_number} access confirmed.")


def get_total_available_levels_count():
    """
    Determines the total number of level_X.json files in the levels directory.
    """
    if not os.path.exists(settings.LEVELS_DIR):
        print(f"Warning: Levels directory not found at {settings.LEVELS_DIR}")
        return 0

    level_files = [f for f in os.listdir(settings.LEVELS_DIR)
                   if f.startswith("level_") and f.endswith(".json")]
    return len(level_files)

def get_level_path(level_number):
    """Returns the path to a specific level's JSON file."""
    return os.path.join(settings.LEVELS_DIR, f"level_{level_number}.json")