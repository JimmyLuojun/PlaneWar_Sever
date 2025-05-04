# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/main.py
import pygame
import os
import sys
import time
import random # Needed for enemy spawning logic within run_game

# --- Core Game Modules ---
from .settings import * # Settings are widely used
from .player import Player
from .enemy import Enemy, EnemyBoss
from .powerup import PowerUp
from .background import Background
# --- Helper/Management Modules ---
from . import utils         # For loading helpers
from . import ui            # For screen displays (Import the whole module)
from . import network_client as network # For API calls

# --- Game Logic Function (Kept in main for now) ---
def run_game(screen_surf, clock_obj, fonts, images, sounds, level_data, background):
    """
    Runs a single level. Spawns enemies, handles player actions, collisions,
    and level progression. Uses the Background object for drawing and updating.

    Args:
        screen_surf: The main Pygame screen surface.
        clock_obj: The Pygame clock object.
        fonts (dict): Dictionary of loaded fonts.
        images (dict): Dictionary of loaded images.
        sounds (dict): Dictionary of loaded sounds.
        level_data (dict): Configuration for the current level.
        background (Background): The background object.

    Returns:
        tuple: (str: result ('PASSED', 'FAILED', 'QUIT'), int: score, int: level_number)
    """
    level_num = level_data.get('level_number', '?')
    print(f"\n--- Starting Level {level_num} ---")

    # --- Get Level Configuration ---
    is_boss_level = level_data.get('is_boss_level', False)
    enemy_types = level_data.get('enemy_types', ['enemy1'])
    spawn_interval = level_data.get('spawn_interval', ENEMY_SPAWN_INTERVAL)
    max_on_screen = level_data.get('max_on_screen', MAX_ONSCREEN_ENEMIES)
    enemy_speed_y_range = level_data.get('enemy_speed_y_range', (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y))
    enemy_speed_x_range = level_data.get('enemy_speed_x_range', (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X))
    powerup_interval = level_data.get('powerup_interval', POWERUP_SPAWN_INTERVAL)
    boss_appear_delay_seconds = level_data.get('boss_appear_delay_seconds', 99999)

    # --- Resources ---
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE) # Fallback if needed
    player_img = images.get('player')
    boss_img = images.get('boss')
    powerup_images_dict = images.get('powerups', {})
    available_enemy_images = []
    for etype in enemy_types:
        img = images.get(etype)
        # Use the image if it's a valid Surface (even fallbacks from utils)
        if isinstance(img, pygame.Surface):
            available_enemy_images.append(img)
        else:
            print(f"Error: Image for enemy type '{etype}' is not a valid Surface in level {level_num}.")

    # --- Initialize Level State ---
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle()

    if not isinstance(player_img, pygame.Surface): # Check if player image (or fallback) exists
        print("CRITICAL ERROR: Player image not available. Exiting.")
        pygame.quit(); sys.exit("Asset Loading Error")

    # Create Player instance (pass required sounds)
    player = Player(
        player_img,
        sounds.get('player_shoot'),
        sounds.get('shield_up'),
        sounds.get('shield_down'),
        sounds.get('powerup_pickup'),
        sounds.get('bomb')
    )
    all_sprites.add(player)

    # Level State Variables
    game_over_local = False
    level_passed = False
    boss_active = False
    boss_spawned = False
    boss_defeated = False
    boss_instance = None
    enemy_spawn_timer = 0 # Frame counter for spawning regular enemies
    powerup_last_spawn_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()

    # --- Level Game Loop ---
    running_this_level = True
    while running_this_level:
        # Timing
        clock_obj.tick(FPS)
        now = pygame.time.get_ticks() # Current time in milliseconds

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT', player.score, level_num # Exit level, return score and level num

            if event.type == pygame.KEYDOWN:
                # Use bomb key defined in settings
                if event.key == BOMB_KEY and not game_over_local and player.bomb_count > 0:
                    killed_by_bomb = player.use_bomb(enemies, enemy_bullets) # Pass both groups
                    player.score += killed_by_bomb # Add score for bomb kills

        # --- Game Logic Update (only if player is alive and level not passed) ---
        if not game_over_local and not level_passed:

            # Update all sprites (player movement, bullets, enemies, powerups, boss)
            all_sprites.update() # update() methods handle movement, timers, etc.

            # Update background scrolling position
            background.update()

            # Player Shooting (check keyboard/mouse)
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                new_player_bullets = player.shoot()
                if new_player_bullets:
                    all_sprites.add(new_player_bullets)
                    bullets.add(new_player_bullets)

            # Boss Spawning Logic
            if is_boss_level and not boss_spawned and not boss_defeated:
                elapsed_seconds = (now - level_start_time) / 1000
                if elapsed_seconds >= boss_appear_delay_seconds:
                    if not isinstance(boss_img, pygame.Surface):
                        print(f"Error: Boss image missing or invalid for level {level_num}. Failing level.")
                        game_over_local = True
                    elif not boss_active:
                         boss_instance = EnemyBoss(
                            boss_img, sounds.get('boss_shoot'), all_sprites, enemy_bullets
                         )
                         all_sprites.add(boss_instance)
                         boss_group.add(boss_instance)
                         boss_active = True
                         boss_spawned = True
                         print("Boss Incoming!")
                         if sounds.get('boss_intro'):
                             try: sounds.get('boss_intro').play()
                             except pygame.error as e: print(f"Warning: Could not play boss intro sound: {e}")

            # Regular Enemy Spawning Logic
            if available_enemy_images and not (is_boss_level and boss_spawned):
                enemy_spawn_timer += 1
                if enemy_spawn_timer >= spawn_interval and len(enemies) < max_on_screen:
                    enemy_spawn_timer = 0
                    chosen_img = random.choice(available_enemy_images)
                    enemy = Enemy(chosen_img, speed_y_range=enemy_speed_y_range, speed_x_range=enemy_speed_x_range)
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            # Powerup Spawning Logic
            if now - powerup_last_spawn_time > powerup_interval:
                powerup_last_spawn_time = now
                if powerup_images_dict: # Check if the dict itself exists and isn't empty
                    powerup = PowerUp(powerup_images_dict)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

            # --- Collisions ---
            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for _ in enemy_hits: # Don't need the enemy object itself here
                player.score += 1
                if sounds.get('enemy_explode'):
                    try: sounds.get('enemy_explode').play()
                    except pygame.error as e: print(f"Warning: Could not play enemy explode sound: {e}")

            if boss_active and boss_instance:
                bullets_hitting_boss = pygame.sprite.spritecollide(boss_instance, bullets, True)
                if bullets_hitting_boss:
                    if sounds.get('boss_hit'):
                        try: sounds.get('boss_hit').play()
                        except pygame.error as e: print(f"Warning: Could not play boss hit sound: {e}")
                    boss_instance.health -= len(bullets_hitting_boss)
                    if boss_instance.health <= 0:
                        if sounds.get('boss_explode'):
                            try: sounds.get('boss_explode').play()
                            except pygame.error as e: print(f"Warning: Could not play boss explode sound: {e}")
                        if sounds.get('game_win'):
                             try: sounds.get('game_win').play()
                             except pygame.error as e: print(f"Warning: Could not play game win sound: {e}")
                        boss_instance.kill()
                        player.score += 50
                        print("Boss Defeated!")
                        boss_defeated = True
                        boss_active = False
                        boss_instance = None
                        level_passed = True

            powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit_powerup in powerup_hits:
                player.activate_powerup(hit_powerup.type)

            # --- Player Death Check ---
            if now - level_start_time > STARTUP_GRACE_PERIOD:
                 if player.alive() and not player.shield_active:
                    player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
                    player_boss_collision = pygame.sprite.spritecollide(player, boss_group, False)
                    enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
                    if player_enemy_hits or player_boss_collision or enemy_bullet_hits:
                        reason = "Enemy" if player_enemy_hits else ("Boss Collision" if player_boss_collision else "Enemy Bullet")
                        print(f"Player hit by {reason}! Level Failed!")
                        if sounds.get('player_lose'):
                            try: sounds.get('player_lose').play()
                            except pygame.error as e: print(f"Warning: Could not play player lose sound: {e}")
                        player.kill()
                        game_over_local = True

        # --- Drawing ---
        background.draw(screen_surf)
        all_sprites.draw(screen_surf)

        # Draw UI
        try:
            score_text = font_score.render(f"Score: {player.score}", True, WHITE)
            screen_surf.blit(score_text, (10, 10))
            bomb_text = font_score.render(f"Bombs: {player.bomb_count}", True, ORANGE)
            screen_surf.blit(bomb_text, (10, 40))
            level_text_surf = font_score.render(f"Level: {level_num}", True, WHITE)
            level_rect = level_text_surf.get_rect(topright=(SCREEN_WIDTH - 10, 10))
            screen_surf.blit(level_text_surf, level_rect)
        except Exception as e:
            print(f"Error rendering UI text: {e}")

        if boss_active and boss_instance:
            boss_instance.draw_health_bar(screen_surf)
        if player.shield_active:
            player.draw_shield(screen_surf)

        # Check Level End Condition
        if game_over_local or level_passed:
            running_this_level = False

        pygame.display.flip()

    # --- Level Loop Ended ---
    result = 'PASSED' if level_passed else ('FAILED' if game_over_local else 'QUIT')
    print(f"--- Level {level_num} Ended. Result: {result}, Score: {player.score} ---")
    return result, player.score, level_num


# ==============================================================================
# --- Main Application Entry Point ---
# ==============================================================================
def main():
    """Initializes Pygame, loads assets, handles game states (login, play, end)."""
    print("--- Pygame Initialization ---")
    try:
        pygame.init()
        # Initialize mixer only if module is available
        if pygame.mixer:
            print("Initializing Mixer...")
            try:
                pygame.mixer.init(frequency=MIXER_FREQUENCY, size=MIXER_SIZE, channels=MIXER_CHANNELS, buffer=MIXER_BUFFER)
                print("Pygame Mixer Initialized Successfully")
            except pygame.error as mix_err:
                 print(f"Warning: Failed to initialize mixer: {mix_err}. Sound disabled.")
        else:
            print("Warning: Mixer module not available. Sound disabled.")
    except pygame.error as e:
        print(f"ERROR: Pygame Initialization Failed: {e}"); sys.exit(1)

    # Setup Screen & Clock
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PlaneWar Online")
        clock = pygame.time.Clock()
    except pygame.error as e:
        print(f"ERROR: Failed to set up screen: {e}"); pygame.quit(); sys.exit(1)

    # --- Load Assets Directly (using utils) ---
    # Fonts
    fonts = {}
    print("\n--- Loading Fonts ---")
    try:
        font_path = os.path.join(os.path.dirname(__file__), UI_FONT_PATH)
        if os.path.exists(font_path):
            fonts['title'] = pygame.font.Font(font_path, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.Font(font_path, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.Font(font_path, FONT_SIZE_SCORE)
            print(f"Successfully loaded font: {os.path.basename(font_path)}")
        else:
             print(f"Warning: Custom font not found at {font_path}. Using system default.")
             raise FileNotFoundError
    except Exception as e:
        print(f"Warning: Failed to load custom font ({e}). Using system default.")
        try:
            fonts['title'] = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.SysFont(None, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.SysFont(None, FONT_SIZE_SCORE)
            print("Loaded system default font.")
        except Exception as e_sys:
            print(f"CRITICAL ERROR: Failed to load any fonts: {e_sys}"); pygame.quit(); sys.exit("Font Loading Error")

    # Images
    images = {}
    print("\n--- Loading Images ---")
    try:
        images['player'] = utils.load_and_scale_image(PLAYER_IMG_PATH, PLAYER_WIDTH, PLAYER_HEIGHT)
        enemy_image_configs = {
            'enemy1': (ENEMY1_IMG_PATH, ENEMY1_WIDTH, ENEMY1_HEIGHT),
            'enemy2': (ENEMY2_IMG_PATH, ENEMY2_WIDTH, ENEMY2_HEIGHT),
            'enemy3': (ENEMY3_IMG_PATH, ENEMY3_WIDTH, ENEMY3_HEIGHT),
            'enemy4': (ENEMY4_IMG_PATH, ENEMY4_WIDTH, ENEMY4_HEIGHT),
            'boss':   (ENEMY_BOSS_IMG_PATH, ENEMY_BOSS_WIDTH, ENEMY_BOSS_HEIGHT),
        }
        for key, (path, w, h) in enemy_image_configs.items():
             images[key] = utils.load_and_scale_image(path, w, h) # Store image or fallback

        images['powerups'] = {}
        for type_key, path in POWERUP_IMAGES.items():
            images['powerups'][type_key] = utils.load_and_scale_image(path, POWERUP_WIDTH, POWERUP_HEIGHT) # Store image or fallback
        print("--- Image Loading Complete ---")
    except Exception as e:
        print(f"CRITICAL ERROR during image loading: {e}"); pygame.quit(); sys.exit("Image Loading Error")

    # Sounds
    sounds = {}
    print("\n--- Loading Sounds ---")
    if pygame.mixer and pygame.mixer.get_init(): # Check if mixer initialized successfully
        sound_configs = {
            'player_shoot': (SHOOT_SOUND_PATH, PLAYER_SHOOT_VOLUME), 'enemy_explode': (ENEMY_EXPLODE_SOUND_PATH, ENEMY_EXPLODE_VOLUME),
            'boss_explode': (BOSS_EXPLODE_SOUND_PATH, BOSS_EXPLODE_VOLUME), 'powerup_pickup': (POWERUP_PICKUP_SOUND_PATH, POWERUP_PICKUP_VOLUME),
            'game_win': (WIN_SOUND_PATH, WIN_VOLUME), 'player_lose': (LOSE_SOUND_PATH, LOSE_VOLUME),
            'boss_intro': (BOSS_INTRO_SOUND_PATH, BOSS_INTRO_VOLUME), 'boss_hit': (BOSS_HIT_SOUND_PATH, BOSS_HIT_VOLUME),
            'shield_up': (SHIELD_UP_SOUND_PATH, SHIELD_UP_VOLUME), 'shield_down': (SHIELD_DOWN_SOUND_PATH, SHIELD_DOWN_VOLUME),
            'bomb': (BOMB_SOUND_PATH, BOMB_VOLUME), 'boss_shoot': (BOSS_SHOOT_SOUND_PATH, BOSS_SHOOT_VOLUME),
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


    # --- Create Background Instance ---
    print("\n--- Initializing Background ---")
    background = Background(BACKGROUND_IMG_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)

    # --- Load Level Data ---
    LEVELS = utils.load_level_data(LEVELS_DIR)
    if not LEVELS:
        print("CRITICAL ERROR: No level data found."); pygame.quit(); sys.exit("Level Data Error")

    # --- Prepare Music Paths ---
    music_paths = {}
    print("\n--- Checking Level Music Paths ---")
    for level_cfg in LEVELS:
        level_num = level_cfg.get('level_number')
        music_filename = level_cfg.get('music')
        if level_num is not None and music_filename:
            full_music_path = os.path.join(os.path.dirname(__file__), SND_DIR, music_filename)
            if os.path.exists(full_music_path):
                music_paths[level_num] = full_music_path
                print(f"  Found music for Level {level_num}: {music_filename}")
            else:
                print(f"  Warning: Music file '{music_filename}' for Level {level_num} not found at {full_music_path}")

    # --- Load Local High Score ---
    high_score = utils.load_high_score(HIGH_SCORE_FILE_PATH)
    print(f"\n--- Local High Score Loaded: {high_score} ---")

    # --- Application State ---
    app_running = True
    game_state = 'LOGIN_SCREEN'
    current_level_index = 0
    final_score_this_run = 0
    last_level_played = 0
    current_music_path = None
    is_logged_in = False
    logged_in_user_id = None
    logged_in_username = None
    last_login_message = None
    last_submission_status = None

    # --- Main Game Loop ---
    while app_running:

        # --- State: LOGIN_SCREEN ---
        if game_state == 'LOGIN_SCREEN':
            login_result, user_id, username, status_msg = ui.show_login_screen(screen, clock, fonts)
            last_login_message = status_msg # Store message

            if login_result == 'QUIT':
                 app_running = False
            elif login_result is True:
                 is_logged_in = True
                 logged_in_user_id = user_id
                 logged_in_username = username
                 print(f"Logged in as User ID: {user_id}, Username: {username}")
                 game_state = 'START_SCREEN'
            elif login_result is False:
                 print("Login failed, staying on login screen.")
                 game_state = 'LOGIN_SCREEN' # Stay on login

        # --- State: START_SCREEN ---
        elif game_state == 'START_SCREEN':
            if pygame.mixer and pygame.mixer.music.get_busy():
                 pygame.mixer.music.stop(); pygame.mixer.music.unload()
            current_music_path = None
            ui.show_start_screen(screen, clock, fonts, high_score, logged_in_username)
            current_level_index = 0
            final_score_this_run = 0
            last_submission_status = None
            game_state = 'LEVEL_START'

        # --- State: LEVEL_START ---
        elif game_state == 'LEVEL_START':
            if current_level_index < len(LEVELS):
                level_data = LEVELS[current_level_index]
                level_num = level_data.get('level_number', current_level_index + 1)

                # Music Handling
                track_to_play = music_paths.get(level_num)
                default_bgm_full_path = None
                if Default_BGM_PATH:
                    path_check = os.path.join(os.path.dirname(__file__), Default_BGM_PATH)
                    if os.path.exists(path_check): default_bgm_full_path = path_check
                if not track_to_play and default_bgm_full_path: track_to_play = default_bgm_full_path

                if track_to_play and (track_to_play != current_music_path or not pygame.mixer.music.get_busy()):
                    if pygame.mixer and pygame.mixer.get_init():
                        print(f"Playing music: {os.path.basename(track_to_play)}")
                        try:
                            pygame.mixer.music.load(track_to_play); pygame.mixer.music.set_volume(BGM_VOLUME); pygame.mixer.music.play(loops=-1)
                            current_music_path = track_to_play
                        except pygame.error as e: print(f"Error playing music '{track_to_play}': {e}"); current_music_path = None
                elif not track_to_play and current_music_path:
                     if pygame.mixer and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                         pygame.mixer.music.stop(); pygame.mixer.music.unload()
                     current_music_path = None

                ui.show_level_start_screen(screen, clock, fonts, level_num)
                game_state = 'RUNNING_LEVEL'
            else:
                game_state = 'GAME_WON'

        # --- State: RUNNING_LEVEL ---
        elif game_state == 'RUNNING_LEVEL':
            level_data = LEVELS[current_level_index]
            level_result, score_at_level_end, ended_level_num = run_game(
                screen, clock, fonts, images, sounds, level_data, background
            )
            final_score_this_run = score_at_level_end
            last_level_played = ended_level_num

            if level_result == 'PASSED':
                current_level_index += 1
                if current_level_index >= len(LEVELS): game_state = 'GAME_WON'
                else: game_state = 'LEVEL_START'
            elif level_result == 'FAILED': game_state = 'GAME_OVER'
            elif level_result == 'QUIT': app_running = False

        # --- State: GAME_WON / GAME_OVER ---
        elif game_state in ('GAME_WON', 'GAME_OVER'):
            game_result_for_screen = 'WIN' if game_state == 'GAME_WON' else 'LOSE'
            print(f"Game ended: {game_state}")

            if pygame.mixer and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop(); pygame.mixer.music.unload()
            current_music_path = None

            # Score Submission
            submission_msg = None
            level_to_submit = last_level_played
            if is_logged_in and logged_in_user_id is not None:
                print(f"Submitting score {final_score_this_run} for user ID {logged_in_user_id}, level {level_to_submit}")
                success, msg = network.api_submit_score(logged_in_user_id, final_score_this_run, level_to_submit)
                submission_msg = msg
            else:
                if final_score_this_run > high_score:
                    print(f"New Local High Score: {final_score_this_run}")
                    utils.save_high_score(HIGH_SCORE_FILE_PATH, final_score_this_run)
                    high_score = final_score_this_run
                submission_msg = "Not logged in. Score saved locally (if new high)."

            last_submission_status = submission_msg
            game_state = 'END_SCREEN'

        # --- State: END_SCREEN ---
        elif game_state == 'END_SCREEN':
            player_choice = ui.show_end_screen(
                screen, clock, fonts, game_result_for_screen, final_score_this_run, last_submission_status
            )
            if player_choice == 'QUIT': app_running = False
            elif player_choice == 'REPLAY': game_state = 'START_SCREEN'

    # --- Game Exit ---
    print("Exiting PlaneWar.")
    pygame.quit()
    sys.exit()

# --- Script Execution Guard ---
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
         print(f"\nAn unexpected error occurred during game execution: {e}")
         # import traceback; traceback.print_exc() # Uncomment for detailed traceback
         if pygame.get_init(): pygame.quit()
         sys.exit(1)
