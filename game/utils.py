# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/utils.py

import pygame
import os
import json
import random
from .settings import WHITE  # Import necessary constants

# --- Asset Loading Helpers ---

def load_and_scale_image(path, width, height, colorkey=None):
    """Loads, scales, handles errors, and sets transparency for an image."""
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)

    if not path or not os.path.exists(path):
        print(f"Error: Image file not found or path invalid: {path}. Using fallback.")
        fallback = pygame.Surface((width, height))
        fallback.fill((200, 50, 50))
        pygame.draw.rect(fallback, WHITE, fallback.get_rect(), 1)
        return fallback

    try:
        image = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.scale(image, (width, height))
        if colorkey is not None:
            if colorkey == -1:  # Special value: sample top-left from original image
                colorkey = image.get_at((0, 0))
            scaled_image.set_colorkey(colorkey, pygame.RLEACCEL)
        return scaled_image
    except pygame.error as e:
        print(f"Warning: Failed to load/process image {path}: {e}. Using fallback.")
        fallback = pygame.Surface((width, height))
        fallback.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        pygame.draw.rect(fallback, WHITE, fallback.get_rect(), 1)
        return fallback

def load_sound(path, volume):
    """Loads a sound file, sets volume, and handles errors."""
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)

    if not pygame.mixer or not pygame.mixer.get_init():
        return None
    if not path or not os.path.exists(path):
        print(f"Warning: Sound file not found or path invalid: {path}")
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"Warning: Failed to load sound {path}: {e}")
        return None

# --- Data Handling Helpers ---

def load_high_score(filepath):
    """Loads the high score from a file, returning 0 on error or if file not found."""
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.path.dirname(__file__), filepath)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                score_str = f.read().strip()
            return int(score_str) if score_str.isdigit() else 0
        else:
            return 0
    except Exception as e:
        print(f"Warning: Error loading high score from {filepath}: {e}. Returning 0.")
        return 0

def save_high_score(filepath, score):
    """Saves the high score to a file."""
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.path.dirname(__file__), filepath)
    try:
        with open(filepath, 'w') as f:
            f.write(str(score))
        print(f"Saved new high score {score} to '{os.path.basename(filepath)}'.")
    except Exception as e:
        print(f"Error: Failed to save high score to {filepath}: {e}")

def load_level_data(levels_directory):
    """Loads all .json files from the specified directory and sorts them by level number."""
    if not os.path.isabs(levels_directory):
        levels_directory = os.path.join(os.path.dirname(__file__), levels_directory)

    if not os.path.isdir(levels_directory):
        print(f"Error: Levels directory not found: {levels_directory}")
        return []

    loaded_levels = []
    print(f"--- Loading Levels from: {levels_directory} ---")
    try:
        level_files = [f for f in os.listdir(levels_directory) if f.endswith('.json')]
    except OSError as e:
        print(f"Error accessing levels directory {levels_directory}: {e}")
        return []

    if not level_files:
        print("Warning: No .json level files found in the 'levels' directory!")
        return []

    for filename in level_files:
        filepath = os.path.join(levels_directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            if 'level_number' in level_data and isinstance(level_data['level_number'], int):
                loaded_levels.append(level_data)
                print(f"  Successfully loaded: {filename} (Level {level_data['level_number']})")
            else:
                print(f"  Warning: Skipping file {filename} - missing 'level_number' or not an integer.")
        except json.JSONDecodeError as e:
            print(f"  Error: Failed to parse JSON file {filename}: {e}")
        except IOError as e:
            print(f"  Error: Failed to read file {filename}: {e}")
        except Exception as e:
            print(f"  Unknown error loading level {filename}: {e}")

    loaded_levels.sort(key=lambda lvl: lvl.get('level_number', float('inf')))
    print(f"--- Level loading complete. Loaded {len(loaded_levels)} valid levels. ---")
    return loaded_levels
