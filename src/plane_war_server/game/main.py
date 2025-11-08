"""
Main entry point for the PlaneWar Pygame client.

Slim bootstrap that initializes Pygame, loads assets, and starts the
application state machine. Applies the Procedural Standard Order.
"""

# ==============================================================================
# Imports (dependencies)
# ==============================================================================
from __future__ import annotations

import os
import sys

import pygame

from .infrastructure import utils
from .infrastructure.assets import load_fonts, load_images, load_sounds, load_level_data_and_music
from .infrastructure.network_client import NetworkClient
from .infrastructure.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BACKGROUND_IMG_PATH,
    BACKGROUND_SCROLL_SPEED,
    HIGH_SCORE_FILE_PATH,
    MIXER_FREQUENCY,
    MIXER_SIZE,
    MIXER_CHANNELS,
    MIXER_BUFFER,
)
from .models.background import Background
from .controllers.state_machine import run_state_machine

# Re-export run_game for tests/compatibility
from .controllers.game_loop import run_game  # noqa: F401


# ==============================================================================
# Main Function (Entry Point)
# ==============================================================================
def main() -> None:
    """Initialize Pygame, load assets, and run the application state machine."""
    # Pygame initialization
    print("--- Pygame Initialization ---")
    try:
        pygame.init()
        if pygame.mixer:
            print("Initializing Mixer...")
            try:
                pygame.mixer.init(
                    frequency=MIXER_FREQUENCY,
                    size=MIXER_SIZE,
                    channels=MIXER_CHANNELS,
                    buffer=MIXER_BUFFER,
                )
                print("Pygame Mixer Initialized Successfully")
            except pygame.error as mix_err:
                print(
                    f"Warning: Failed to initialize mixer: {mix_err}. Sound disabled."
                )
        else:
            print("Warning: Mixer module not available. Sound disabled.")
    except pygame.error as e:
        print(f"ERROR: Pygame Initialization Failed: {e}")
        sys.exit(1)

    # Screen & Clock
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PlaneWar Online")
        clock = pygame.time.Clock()
    except pygame.error as e:
        print(f"ERROR: Failed to set up screen: {e}")
        pygame.quit()
        sys.exit(1)

    # Assets
    fonts = load_fonts()
    images = load_images()
    sounds = load_sounds()
    levels, music_paths = load_level_data_and_music()

    # Background
    print("\n--- Initializing Background ---")
    background = Background(
        BACKGROUND_IMG_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED
    )

    # Local High Score
    high_score = utils.load_high_score(HIGH_SCORE_FILE_PATH)
    print(f"\n--- Local High Score Loaded: {high_score} ---")

    # Network Client
    network_client = NetworkClient()
    print("--- Network Client Initialized ---")

    # Run Application State Machine
    run_state_machine(
        screen=screen,
        clock=clock,
        fonts=fonts,
        images=images,
        sounds=sounds,
        levels=levels,
        music_paths=music_paths,
        background=background,
        high_score=high_score,
        network_client=network_client,
    )

    # Exit
    print("Exiting PlaneWar.")
    if network_client.is_authenticated:
        print("Main: Logging out on application exit...")
        network_client.logout()
    pygame.quit()
    sys.exit()


# ==============================================================================
# Script Execution Guard
# ==============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn unexpected error occurred during game execution: {e}")
        import traceback

        traceback.print_exc()
        if pygame.get_init():
            pygame.quit()
        sys.exit(1)
