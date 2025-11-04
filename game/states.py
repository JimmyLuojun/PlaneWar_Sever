"""
Application state machine for PlaneWar.

Encapsulates login, start, level-start, running, and end screens, handling
music, score submission, and transitions. Applies the Event-Driven Standard Order.
"""

# ==============================================================================
# Imports (dependencies)
# ==============================================================================
from __future__ import annotations

import os
from typing import Any

import pygame

from . import ui, utils, progress
from .loop import run_game
from .network_client import NetworkClient
from .settings import (
    Default_BGM_PATH,
    BGM_VOLUME,
    HIGH_SCORE_FILE_PATH,
)


# ==============================================================================
# Constants & Global Setup
# ==============================================================================
STATE_LOGIN = "LOGIN_SCREEN"
STATE_START = "START_SCREEN"
STATE_LEVEL_START = "LEVEL_START"
STATE_RUNNING = "RUNNING_LEVEL"
STATE_GAME_WON = "GAME_WON"
STATE_GAME_OVER = "GAME_OVER"
STATE_END = "END_SCREEN"


# ==============================================================================
# Orchestration Function (Core Logic)
# ==============================================================================
def run_state_machine(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    fonts: dict[str, pygame.font.Font],
    images: dict[str, Any],
    sounds: dict[str, Any],
    levels: list[dict[str, Any]],
    music_paths: dict[int, str],
    background,
    high_score: int,
    network_client: NetworkClient,
) -> None:
    """Run the high-level application state machine."""

    app_running = True
    game_state = STATE_LOGIN
    current_level_index = 0
    final_score_this_run = 0
    last_level_played = 0
    current_music_path: str | None = None
    game_result_for_screen = "LOSE"

    # Authentication display state
    logged_in_username: str | None = None
    last_login_message: str | None = None
    last_submission_status: str | None = None

    while app_running:
        # --- State: LOGIN_SCREEN ---
        if game_state == STATE_LOGIN:
            login_action, username, status_msg = ui.show_login_screen(
                screen, fonts, network_client, last_login_message
            )
            last_login_message = status_msg

            if login_action == "QUIT":
                app_running = False
            elif login_action == "LOGIN_SUCCESS":
                logged_in_username = username
                print(f"Main: Login successful for {logged_in_username}")
                # Fetch per-account progress from server and sync locally
                try:
                    if network_client.is_authenticated:
                        p = network_client.get_progress()
                        if p.success and p.max_unlocked_level:
                            progress.save_progress(int(p.max_unlocked_level))
                except Exception:
                    pass
                game_state = STATE_START
            elif login_action == "LOGIN_FAIL":
                logged_in_username = None
                print("Main: Login failed, staying on login screen.")

        # --- State: START_SCREEN ---
        elif game_state == STATE_START:
            if pygame.mixer and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            current_music_path = None

            # Show start screen with level selection
            start_result = ui.show_start_screen(screen, fonts, logged_in_username)

            if start_result == "QUIT":
                app_running = False
            elif start_result.startswith("LEVEL_"):
                # Parse selected level number
                try:
                    selected_level = int(start_result.split("_")[1])
                    # Find the index of the selected level in the levels list
                    current_level_index = None
                    for idx, level_data in enumerate(levels):
                        if level_data.get("level_number") == selected_level:
                            current_level_index = idx
                            break

                    if current_level_index is not None:
                        print(f"Starting from Level {selected_level}")
                        final_score_this_run = 0
                        last_level_played = 0
                        last_submission_status = None
                        game_state = STATE_LEVEL_START
                    else:
                        print(f"Error: Level {selected_level} not found in loaded levels")
                        game_state = STATE_START
                except (ValueError, IndexError):
                    print(f"Error: Invalid level selection format: {start_result}")
                    game_state = STATE_START

        # --- State: LEVEL_START ---
        elif game_state == STATE_LEVEL_START:
            if current_level_index < len(levels):
                level_data = levels[current_level_index]
                level_num = level_data.get("level_number", current_level_index + 1)

                # Handle music for the level
                track_to_play = music_paths.get(level_num)
                default_bgm_full_path = None
                if Default_BGM_PATH:
                    path_check = os.path.join(
                        os.path.dirname(__file__), Default_BGM_PATH
                    )
                    if os.path.exists(path_check):
                        default_bgm_full_path = path_check
                if not track_to_play and default_bgm_full_path:
                    track_to_play = default_bgm_full_path

                if track_to_play and (
                    track_to_play != current_music_path
                    or not pygame.mixer.music.get_busy()
                ):
                    if pygame.mixer and pygame.mixer.get_init():
                        print(f"Playing music: {os.path.basename(track_to_play)}")
                        try:
                            pygame.mixer.music.load(track_to_play)
                            pygame.mixer.music.set_volume(BGM_VOLUME)
                            pygame.mixer.music.play(loops=-1)
                            current_music_path = track_to_play
                        except pygame.error as e:
                            print(f"Error playing music '{track_to_play}': {e}")
                            current_music_path = None
                elif not track_to_play and current_music_path:
                    if (
                        pygame.mixer
                        and pygame.mixer.get_init()
                        and pygame.mixer.music.get_busy()
                    ):
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                    current_music_path = None

                ui.show_level_start_screen(screen, fonts, level_num, 2000)
                game_state = STATE_RUNNING
            else:
                print("Warning: Reached LEVEL_START with no more levels?")
                game_state = STATE_GAME_WON

        # --- State: RUNNING_LEVEL ---
        elif game_state == STATE_RUNNING:
            level_data = levels[current_level_index]
            level_result, score_at_level_end, ended_level_num = run_game(
                screen, clock, fonts, images, sounds, level_data, background
            )
            final_score_this_run = score_at_level_end
            last_level_played = ended_level_num

            # Submit score after each attempt (except QUIT)
            if level_result != "QUIT":
                submission_msg = None
                level_to_submit = last_level_played

                if network_client.is_authenticated:
                    print(
                        f"Attempting to submit score {final_score_this_run} for level {level_to_submit} (User: {network_client.username})"
                    )
                    result = network_client.submit_score(
                        final_score_this_run, level_to_submit
                    )
                    submission_msg = result.message
                    print(
                        f"Submission result: Success={result.success}, Message='{result.message}'"
                    )
                    last_submission_status = submission_msg
                else:
                    print(
                        "User not logged in when level ended. Checking local high score."
                    )
                    if final_score_this_run > high_score:
                        print(f"New Local High Score: {final_score_this_run}")
                        utils.save_high_score(
                            HIGH_SCORE_FILE_PATH, final_score_this_run
                        )
                        high_score = final_score_this_run
                    submission_msg = "Not logged in. Score saved locally (if new high)."
                    last_submission_status = submission_msg

            # Determine next state
            if level_result == "PASSED":
                current_level_index += 1
                if current_level_index >= len(levels):
                    game_state = STATE_GAME_WON
                else:
                    game_state = STATE_LEVEL_START
                # Update unlock progress locally and on server
                try:
                    # Determine next unlocked level number (prefer explicit level numbers if present)
                    available_level_numbers = [
                        int(ld.get("level_number", i + 1)) for i, ld in enumerate(levels)
                    ]
                    max_available = max(available_level_numbers) if available_level_numbers else last_level_played
                    candidate = min(last_level_played + 1, max_available)
                    new_max = max(progress.get_max_unlocked_level(), candidate)
                    progress.save_progress(new_max)
                    if network_client.is_authenticated:
                        network_client.set_progress(new_max)
                except Exception:
                    pass
            elif level_result == "FAILED":
                if pygame.mixer and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                current_music_path = None
                game_state = STATE_GAME_OVER
            elif level_result == "QUIT":
                app_running = False

        # --- State: GAME_WON / GAME_OVER ---
        elif game_state in (STATE_GAME_WON, STATE_GAME_OVER):
            game_result_for_screen = "WIN" if game_state == STATE_GAME_WON else "LOSE"
            print(f"Transitioning to end screen state ({game_state})")

            if pygame.mixer and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            current_music_path = None

            game_state = STATE_END

        # --- State: END_SCREEN ---
        elif game_state == STATE_END:
            player_choice = ui.show_end_screen(
                screen,
                fonts,
                game_result_for_screen,
                final_score_this_run,
                last_submission_status,
            )
            if player_choice == "QUIT":
                if network_client.is_authenticated:
                    print("Main: Logging out before quit...")
                    network_client.logout()
                app_running = False
            elif player_choice == "REPLAY":
                game_state = STATE_START
