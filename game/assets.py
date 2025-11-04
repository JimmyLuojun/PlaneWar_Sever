"""
Asset and resource loading utilities for the PlaneWar Pygame client.

Provides functions to load fonts, images, sounds, and level data.
Structured using the Procedural Standard Order from CLAUDE.md.
"""

# ==============================================================================
# Imports (dependencies)
# ==============================================================================
from __future__ import annotations

import os
import sys
from typing import Any

import pygame

from . import utils
from .settings import (
    # Fonts
    UI_FONT_PATH,
    FONT_SIZE_TITLE,
    FONT_SIZE_LARGE,
    FONT_SIZE_SCORE,
    # Player
    PLAYER_IMG_PATH,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    # Enemies
    ENEMY1_IMG_PATH,
    ENEMY1_WIDTH,
    ENEMY1_HEIGHT,
    ENEMY2_IMG_PATH,
    ENEMY2_WIDTH,
    ENEMY2_HEIGHT,
    ENEMY3_IMG_PATH,
    ENEMY3_WIDTH,
    ENEMY3_HEIGHT,
    ENEMY4_IMG_PATH,
    ENEMY4_WIDTH,
    ENEMY4_HEIGHT,
    ENEMY_BOSS_IMG_PATH,
    ENEMY_BOSS_WIDTH,
    ENEMY_BOSS_HEIGHT,
    # PowerUps
    POWERUP_IMAGES,
    POWERUP_WIDTH,
    POWERUP_HEIGHT,
    # Background / Levels
    SND_DIR,
    LEVELS_DIR,
    # Sounds: paths
    SHOOT_SOUND_PATH,
    ENEMY_EXPLODE_SOUND_PATH,
    BOSS_EXPLODE_SOUND_PATH,
    POWERUP_PICKUP_SOUND_PATH,
    WIN_SOUND_PATH,
    LOSE_SOUND_PATH,
    BOSS_INTRO_SOUND_PATH,
    BOSS_HIT_SOUND_PATH,
    SHIELD_UP_SOUND_PATH,
    SHIELD_DOWN_SOUND_PATH,
    BOMB_SOUND_PATH,
    BOSS_SHOOT_SOUND_PATH,
    # Sounds: volumes
    PLAYER_SHOOT_VOLUME,
    ENEMY_EXPLODE_VOLUME,
    BOSS_EXPLODE_VOLUME,
    POWERUP_PICKUP_VOLUME,
    WIN_VOLUME,
    LOSE_VOLUME,
    BOSS_INTRO_VOLUME,
    BOSS_HIT_VOLUME,
    SHIELD_UP_VOLUME,
    SHIELD_DOWN_VOLUME,
    BOMB_VOLUME,
    BOSS_SHOOT_VOLUME,
)


# ==============================================================================
# Helper Functions (module-level utilities)
# ==============================================================================
def load_fonts() -> dict[str, pygame.font.Font]:
    """
    Load game fonts (custom or system fallback).

    Returns:
        dict[str, pygame.font.Font]: Dictionary of font objects keyed by 'title', 'large', 'score'.
    """
    fonts: dict[str, pygame.font.Font] = {}
    print("\n--- Loading Fonts ---")
    try:
        font_path = os.path.join(os.path.dirname(__file__), UI_FONT_PATH)
        if os.path.exists(font_path):
            fonts["title"] = pygame.font.Font(font_path, FONT_SIZE_TITLE)
            fonts["large"] = pygame.font.Font(font_path, FONT_SIZE_LARGE)
            fonts["score"] = pygame.font.Font(font_path, FONT_SIZE_SCORE)
            print(f"Successfully loaded font: {os.path.basename(font_path)}")
        else:
            print(
                f"Warning: Custom font not found at {font_path}. Using system default."
            )
            raise FileNotFoundError
    except Exception as e:
        print(f"Warning: Failed to load custom font ({e}). Using system default.")
        try:
            fonts["title"] = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            fonts["large"] = pygame.font.SysFont(None, FONT_SIZE_LARGE)
            fonts["score"] = pygame.font.SysFont(None, FONT_SIZE_SCORE)
            print("Loaded system default font.")
        except Exception as e_sys:
            print(f"CRITICAL ERROR: Failed to load any fonts: {e_sys}")
            pygame.quit()
            sys.exit("Font Loading Error")
    return fonts


def load_images() -> dict[str, pygame.Surface | dict[str, pygame.Surface]]:
    """
    Load all game images (player, enemies, powerups).

    Returns:
        dict[str, pygame.Surface | dict[str, pygame.Surface]]: Dictionary of image surfaces keyed by type names.
    """
    images: dict[str, pygame.Surface | dict[str, pygame.Surface]] = {}
    print("\n--- Loading Images ---")
    try:
        images["player"] = utils.load_and_scale_image(
            PLAYER_IMG_PATH, PLAYER_WIDTH, PLAYER_HEIGHT
        )

        # Load enemy images
        enemy_image_configs = {
            "enemy1": (ENEMY1_IMG_PATH, ENEMY1_WIDTH, ENEMY1_HEIGHT),
            "enemy2": (ENEMY2_IMG_PATH, ENEMY2_WIDTH, ENEMY2_HEIGHT),
            "enemy3": (ENEMY3_IMG_PATH, ENEMY3_WIDTH, ENEMY3_HEIGHT),
            "enemy4": (ENEMY4_IMG_PATH, ENEMY4_WIDTH, ENEMY4_HEIGHT),
            "boss": (ENEMY_BOSS_IMG_PATH, ENEMY_BOSS_WIDTH, ENEMY_BOSS_HEIGHT),
        }
        for key, (path, w, h) in enemy_image_configs.items():
            images[key] = utils.load_and_scale_image(path, w, h)

        # Load powerup images
        images["powerups"] = {}
        for type_key, path in POWERUP_IMAGES.items():
            images["powerups"][type_key] = utils.load_and_scale_image(
                path, POWERUP_WIDTH, POWERUP_HEIGHT
            )

        print("--- Image Loading Complete ---")
    except Exception as e:
        print(f"CRITICAL ERROR during image loading: {e}")
        pygame.quit()
        sys.exit("Image Loading Error")
    return images


def load_sounds() -> dict[str, pygame.mixer.Sound]:
    """
    Load all game sound effects.

    Returns:
        dict[str, pygame.mixer.Sound]: Dictionary of pygame.mixer.Sound objects keyed by sound name.
                                        Returns empty dict if mixer unavailable.
    """
    sounds: dict[str, pygame.mixer.Sound] = {}
    print("\n--- Loading Sounds ---")
    if pygame.mixer and pygame.mixer.get_init():
        sound_configs = {
            "player_shoot": (SHOOT_SOUND_PATH, PLAYER_SHOOT_VOLUME),
            "enemy_explode": (ENEMY_EXPLODE_SOUND_PATH, ENEMY_EXPLODE_VOLUME),
            "boss_explode": (BOSS_EXPLODE_SOUND_PATH, BOSS_EXPLODE_VOLUME),
            "powerup_pickup": (POWERUP_PICKUP_SOUND_PATH, POWERUP_PICKUP_VOLUME),
            "game_win": (WIN_SOUND_PATH, WIN_VOLUME),
            "player_lose": (LOSE_SOUND_PATH, LOSE_VOLUME),
            "boss_intro": (BOSS_INTRO_SOUND_PATH, BOSS_INTRO_VOLUME),
            "boss_hit": (BOSS_HIT_SOUND_PATH, BOSS_HIT_VOLUME),
            "shield_up": (SHIELD_UP_SOUND_PATH, SHIELD_UP_VOLUME),
            "shield_down": (SHIELD_DOWN_SOUND_PATH, SHIELD_DOWN_VOLUME),
            "bomb": (BOMB_SOUND_PATH, BOMB_VOLUME),
            "boss_shoot": (BOSS_SHOOT_SOUND_PATH, BOSS_SHOOT_VOLUME),
        }
        loaded_count = 0
        for key, (path, vol) in sound_configs.items():
            snd = utils.load_sound(path, vol)
            if snd:
                sounds[key] = snd
                loaded_count += 1
        print(f"--- Sound Loading Complete ({loaded_count} sounds loaded) ---")
    else:
        print("--- Sound Loading Skipped (Mixer not available or failed to init) ---")
    return sounds


def load_level_data_and_music() -> tuple[list[dict[str, Any]], dict[int, str]]:
    """
    Load level configuration data and prepare music paths.

    Returns:
        tuple[list[dict[str, Any]], dict[int, str]]: (levels_list, music_paths_dict)
            - levels_list: List of level configuration dictionaries
            - music_paths_dict: Dict mapping level_number to full music file path
    """
    # Load level data
    levels = utils.load_level_data(LEVELS_DIR)
    if not levels:
        print("CRITICAL ERROR: No level data found.")
        pygame.quit()
        sys.exit("Level Data Error")
    else:
        print(f"--- Levels Loaded: {len(levels)} ---")

    # Prepare music paths
    music_paths: dict[int, str] = {}
    print("\n--- Checking Level Music Paths ---")
    for level_cfg in levels:
        level_num = level_cfg.get("level_number")
        music_filename = level_cfg.get("music")
        if level_num is not None and music_filename:
            full_music_path = os.path.join(
                os.path.dirname(__file__), SND_DIR, music_filename
            )
            if os.path.exists(full_music_path):
                music_paths[level_num] = full_music_path
                print(f"  Found music for Level {level_num}: {music_filename}")
            else:
                print(
                    f"  Warning: Music file '{music_filename}' for Level {level_num} not found at {full_music_path}"
                )

    return levels, music_paths
