# /Users/junluo/Desktop/PlaneWar/main.py
import pygame
import random
import os
import sys
import time
import json

# Import game settings and classes from other modules
from settings import *
from player import Player
from bullet import Bullet, EnemyBullet
from enemy import Enemy, EnemyBoss
from powerup import PowerUp
from background import Background # <--- Import the new Background class

# --- Helper Functions (load_and_scale_image, load_sound, load_high_score, save_high_score) ---
# Keep these exactly as they were in your provided code
def load_and_scale_image(path, width, height, colorkey=None):
    """Loads, scales, handles errors, and sets transparency for an image."""
    if not path or not os.path.exists(path):
        print(f"Error: Image file not found or path invalid: {path}. Using fallback.")
        fallback = pygame.Surface((width, height))
        fallback.fill((200, 50, 50)); pygame.draw.rect(fallback, WHITE, fallback.get_rect(), 1)
        return fallback
    try:
        image = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.scale(image, (width, height))
        if colorkey is not None:
            if colorkey == -1: colorkey = scaled_image.get_at((0, 0))
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
    if not pygame.mixer or not pygame.mixer.get_init():
        print("Mixer not initialized, cannot load sound.")
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

def load_high_score(filepath):
    """Loads the high score from a file, returning 0 on error or if file not found."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                score_str = f.read().strip()
            return int(score_str) if score_str else 0
        else:
            print(f"Info: High score file not found: {filepath}. Returning 0.")
            return 0
    except (IOError, ValueError, Exception) as e:
        print(f"Warning: Error loading high score from {filepath}: {e}. Returning 0.")
        return 0

def save_high_score(filepath, score):
    """Saves the high score to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(str(score))
        print(f"Saved new high score {score} to '{os.path.basename(filepath)}'.")
    except (IOError, Exception) as e:
        print(f"Error: Failed to save high score to {filepath}: {e}")

# --- Load level data ---
# Keep this function exactly as it was
def load_level_data(levels_directory):
    """Loads all .json files from the specified directory and sorts them by level number."""
    if not os.path.isdir(levels_directory):
        print(f"Error: Levels directory not found: {levels_directory}")
        return []
    try:
        level_files = [f for f in os.listdir(levels_directory) if f.endswith('.json')]
    except OSError as e:
        print(f"Error accessing levels directory {levels_directory}: {e}")
        return []

    loaded_levels = []
    print(f"--- Loading Levels from: {levels_directory} ---")
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

# --- Screen Display Functions ---
# Keep show_start_screen, show_end_screen, show_level_start_screen as they were
def show_start_screen(screen_surf, clock_obj, title_font, score_font, high_score):
    """Displays the start screen and waits for player input."""
    if not title_font or not score_font:
        print("Error: Invalid fonts passed to show_start_screen.")
        title_font = title_font or pygame.font.SysFont(None, FONT_SIZE_TITLE)
        score_font = score_font or pygame.font.SysFont(None, FONT_SIZE_SCORE)
        if not title_font or not score_font:
             pygame.quit(); sys.exit("Critical font error in show_start_screen.")

    # *** NOTE: Consider drawing the background here too for consistency ***
    # background.draw(screen_surf) # If you pass the background object here

    screen_surf.fill(BLACK) # Keep fill for now if not drawing background yet
    try:
        title_text = title_font.render("飞机大战", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen_surf.blit(title_text, title_rect)
        high_score_text = score_font.render(f"历史最高分: {high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen_surf.blit(high_score_text, high_score_rect)
        prompt_text = score_font.render("按任意键开始游戏", True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4))
        screen_surf.blit(prompt_text, prompt_rect)
    except Exception as e:
        print(f"Error rendering start screen text: {e}")
        try:
            fallback_font = pygame.font.SysFont(None, 50)
            err_text = fallback_font.render("Press Key To Start", True, RED)
            err_rect = err_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen_surf.blit(err_text, err_rect)
        except Exception as fallback_e:
            print(f"Error rendering fallback start screen text: {fallback_e}")

    pygame.display.flip()
    waiting = True
    while waiting:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def show_end_screen(screen_surf, clock_obj, fonts, game_result, final_score):
    """Displays the game over/win screen and waits for player choice."""
    font_large = fonts.get('large') or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)

    # *** NOTE: Consider drawing the game screen *then* the overlay for a better effect ***
    # background.draw(screen_surf) # If background object is available
    # all_sprites.draw(screen_surf) # If sprite groups are available

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Semi-transparent black
    screen_surf.blit(overlay, (0, 0))

    end_text_str = "YOU WIN!" if game_result == 'WIN' else "GAME OVER"
    end_text_color = GREEN if game_result == 'WIN' else RED
    try:
        end_text = font_large.render(end_text_str, True, end_text_color)
        text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 1 // 3))
        screen_surf.blit(end_text, text_rect)
        score_text_surf = font_score.render(f"Final Score: {final_score}", True, WHITE)
        score_rect = score_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen_surf.blit(score_text_surf, score_rect)
        prompt_text_surf = font_score.render("按 [R] 重新开始 , 按 [Q] 退出", True, YELLOW)
        prompt_rect = prompt_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        screen_surf.blit(prompt_text_surf, prompt_rect)
    except Exception as e:
        print(f"Error rendering end screen text: {e}")

    pygame.display.flip()
    waiting = True
    while waiting:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("Player chose REPLAY.")
                    return 'REPLAY'
                if event.key == pygame.K_q:
                    print("Player chose QUIT.")
                    return 'QUIT'

def show_level_start_screen(screen_surf, clock_obj, font, level_number):
    """Displays the level transition screen."""
    if not font: font = pygame.font.SysFont(None, FONT_SIZE_LARGE) # Fallback

    # *** NOTE: Consider drawing the background here too ***
    # background.draw(screen_surf) # If background object is available

    screen_surf.fill(BLACK) # Keep fill for now
    try:
        level_text = font.render(f"Level {level_number}", True, WHITE)
        text_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen_surf.blit(level_text, text_rect)
    except Exception as e:
        print(f"Error rendering level start screen text: {e}")
    pygame.display.flip()
    pygame.time.wait(1500) # Pause for 1.5 seconds


# --- MODIFIED Game Logic Function (run_game) ---
# Added background object parameter
def run_game(screen_surf, clock_obj, fonts, images, sounds, level_data, background):
    """
    Runs a single level. Spawns enemies, handles player actions, collisions,
    and level progression. Uses the Background object for drawing and updating.
    """
    level_num = level_data.get('level_number', '?')
    print(f"\n--- Starting Level {level_num} ---")

    # Get Level Configuration (Using defaults from settings if not specified)
    is_boss_level = level_data.get('is_boss_level', False)
    enemy_types = level_data.get('enemy_types', ['enemy1']) # Default to enemy1 if not specified
    spawn_interval = level_data.get('spawn_interval', ENEMY_SPAWN_INTERVAL)
    max_on_screen = level_data.get('max_on_screen', MAX_ONSCREEN_ENEMIES)
    # Use tuple ranges for speed if provided, otherwise use defaults from settings
    enemy_speed_y_range = level_data.get('enemy_speed_y_range', (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y))
    enemy_speed_x_range = level_data.get('enemy_speed_x_range', (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X))
    powerup_interval = level_data.get('powerup_interval', POWERUP_SPAWN_INTERVAL)
    boss_appear_delay_seconds = level_data.get('boss_appear_delay_seconds', 99999) # Very long delay if not set

    # Resources
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    player_img = images.get('player')
    boss_img = images.get('boss') # Get boss image by 'boss' key
    powerup_images_dict = images.get('powerups', {}) # Get the dict of powerup images
    # Filter available enemy images based on level data and loaded images
    available_enemy_images = []
    for etype in enemy_types:
        img = images.get(etype) # Try to get image using the type name as key (e.g., 'enemy1', 'enemy2')
        if img:
            available_enemy_images.append(img)
        else:
            print(f"Warning: Image for enemy type '{etype}' defined in level {level_num} not found in loaded images.")

    # Initialize Level State
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle() # Use GroupSingle for the boss

    if not player_img:
        print("CRITICAL ERROR: Player image not loaded. Exiting.")
        pygame.quit()
        sys.exit("Asset Loading Error")

    # Create Player instance (pass necessary sounds)
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
    boss_instance = None # To hold the boss sprite object
    enemy_spawn_timer = 0 # Frame counter for spawning regular enemies
    powerup_last_spawn_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()

    # --- Level Game Loop ---
    running_this_level = True
    while running_this_level:
        # Timing
        delta_time = clock_obj.tick(FPS) / 1000.0 # Time since last frame in seconds
        now = pygame.time.get_ticks() # Current time in milliseconds

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT', player.score # Exit level, return score
            if event.type == pygame.KEYDOWN:
                # Use bomb key defined in settings
                if event.key == BOMB_KEY and not game_over_local and player.bomb_count > 0:
                    killed_by_bomb = player.use_bomb(enemies, enemy_bullets) # Pass both groups
                    player.score += killed_by_bomb # Add score for bomb kills
                    # Bomb sound is handled within player.use_bomb()

        # --- Game Logic Update (only if player is alive and level not passed) ---
        if not game_over_local and not level_passed:

            # Update all sprites (player movement, bullets, enemies, powerups)
            all_sprites.update() # Pass delta_time if needed by sprites: all_sprites.update(delta_time)

            # --- Background Update ---
            background.update() # Update background scrolling position

            # Player Shooting (check keyboard/mouse)
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            # Allow shooting with space or left mouse click
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                new_player_bullets = player.shoot() # shoot() handles delay and powerups
                if new_player_bullets: # Could return None or []
                    for bullet in new_player_bullets:
                        all_sprites.add(bullet)
                        bullets.add(bullet)

            # Boss Spawning Logic
            if is_boss_level and not boss_spawned:
                elapsed_seconds = (now - level_start_time) / 1000
                if elapsed_seconds >= boss_appear_delay_seconds:
                    print(f"Boss appear delay reached ({boss_appear_delay_seconds}s). Spawning Boss!")
                    if not boss_img:
                        print(f"Error: Boss image missing for boss level {level_num}. Failing level.")
                        game_over_local = True # Treat as failure if boss can't spawn
                    else:
                        # Create boss instance (pass necessary resources)
                        boss_instance = EnemyBoss(
                            boss_img,
                            sounds.get('boss_shoot'),
                            all_sprites, # Group for adding bullets
                            enemy_bullets # Group to add bullets to
                            # Add health from settings if EnemyBoss takes it: BOSS_MAX_HEALTH
                        )
                        all_sprites.add(boss_instance)
                        boss_group.add(boss_instance) # Add to the single group
                        boss_active = True
                        boss_spawned = True
                        print("Boss Incoming!")
                        # Play boss intro sound if available
                        if sounds.get('boss_intro'):
                            try: sounds.get('boss_intro').play()
                            except pygame.error as e: print(f"Warning: Could not play boss intro sound: {e}")

            # Regular Enemy Spawning Logic
            # Spawn only if there are defined enemy types for the level and images loaded
            if available_enemy_images:
                enemy_spawn_timer += 1 # Increment frame counter
                # Check interval and max on screen limit
                if enemy_spawn_timer >= spawn_interval and len(enemies) < max_on_screen:
                    enemy_spawn_timer = 0 # Reset timer
                    chosen_img = random.choice(available_enemy_images)
                    # Create enemy with speed ranges from level data/settings
                    enemy = Enemy(chosen_img, speed_y_range=enemy_speed_y_range, speed_x_range=enemy_speed_x_range)
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            # Powerup Spawning Logic
            if now - powerup_last_spawn_time > powerup_interval:
                powerup_last_spawn_time = now
                # Check if powerup images were loaded successfully
                if powerup_images_dict:
                    # Create powerup instance (PowerUp class needs access to images dict)
                    powerup = PowerUp(powerup_images_dict) # Pass the dict
                    all_sprites.add(powerup)
                    powerups.add(powerup)

            # --- Collisions ---
            # Player Bullets vs Regular Enemies
            # groupcollide(group1, group2, dokill1, dokill2) -> dict {sprite1: [collided_sprites2]}
            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True) # Kill both enemy and bullet
            for enemy_hit in enemy_hits: # Iterate through the enemies that were hit
                player.score += 1 # Or some score based on enemy type
                # Play explosion sound
                if sounds.get('enemy_explode'):
                    try: sounds.get('enemy_explode').play()
                    except pygame.error as e: print(f"Warning: Could not play enemy explode sound: {e}")
                # Optional: Spawn explosion animation here

            # Player Bullets vs Boss
            if boss_active and boss_instance: # Check if boss exists and is active
                # spritecollide(sprite, group, dokill) -> list [collided_sprites]
                bullets_hitting_boss = pygame.sprite.spritecollide(boss_instance, bullets, True) # Kill the bullets
                if bullets_hitting_boss:
                    # Play boss hit sound
                    if sounds.get('boss_hit'):
                        try: sounds.get('boss_hit').play()
                        except pygame.error as e: print(f"Warning: Could not play boss hit sound: {e}")
                    # Reduce boss health (assuming boss has a health attribute)
                    boss_instance.health -= len(bullets_hitting_boss) # Decrease by number of bullets hit
                    # Optional: Add visual feedback like flashing

                    # Check if boss is defeated
                    if boss_instance.health <= 0:
                        # Play boss explosion sound
                        if sounds.get('boss_explode'):
                            try: sounds.get('boss_explode').play()
                            except pygame.error as e: print(f"Warning: Could not play boss explode sound: {e}")
                        # Play win sound immediately (or maybe after a short delay/animation)
                        if sounds.get('game_win'):
                            try: sounds.get('game_win').play()
                            except pygame.error as e: print(f"Warning: Could not play game win sound: {e}")

                        boss_instance.kill() # Remove boss sprite
                        player.score += 50 # Add boss bonus score
                        print("Boss Defeated!")
                        boss_defeated = True
                        boss_active = False
                        boss_instance = None # Clear the instance variable
                        level_passed = True # Set level passed flag

            # Player vs Powerups
            # spritecollide(sprite, group, dokill)
            powerup_hits = pygame.sprite.spritecollide(player, powerups, True) # Kill the powerup on collision
            for hit_powerup in powerup_hits:
                # Player class handles activating the powerup effect and playing sound
                player.activate_powerup(hit_powerup.type)

            # --- Player Death Check ---
            # Check only after grace period
            if now - level_start_time > STARTUP_GRACE_PERIOD:
                 # Check only if player is alive and shield is not active
                 if player.alive() and not player.shield_active:
                    # Player vs Regular Enemies
                    player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True) # Kill enemy on collision

                    # Player vs Boss Collision (use the single boss group)
                    player_boss_collision = pygame.sprite.spritecollide(player, boss_group, False) # Don't kill boss on collision

                    # Player vs Enemy Bullets
                    enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True) # Kill the bullet

                    # If any collision occurred
                    if player_enemy_hits or player_boss_collision or enemy_bullet_hits:
                        reason = "Enemy" if player_enemy_hits else ("Boss Collision" if player_boss_collision else "Boss Bullet")
                        print(f"Player hit by {reason}! Level Failed!")
                        # Play player lose/death sound
                        if sounds.get('player_lose'):
                            try: sounds.get('player_lose').play()
                            except pygame.error as e: print(f"Warning: Could not play player lose sound: {e}")
                        player.kill() # Remove player sprite
                        # Optional: Start death animation/sequence
                        game_over_local = True # Set game over flag for this level

        # --- Drawing ---
        # *** Draw background FIRST using the background object ***
        background.draw(screen_surf)

        # Draw all sprites (player, enemies, bullets, powerups, boss) onto the screen
        all_sprites.draw(screen_surf)

        # Draw UI elements (Score, Bombs, Level, etc.) on top
        try:
            score_text = font_score.render(f"Score: {player.score}", True, WHITE)
            screen_surf.blit(score_text, (10, 10)) # Top-left corner
            bomb_text = font_score.render(f"Bombs: {player.bomb_count}", True, ORANGE)
            screen_surf.blit(bomb_text, (10, 40)) # Below score
            level_text_surf = font_score.render(f"Level: {level_num}", True, WHITE)
            # Position level text top-right
            level_rect = level_text_surf.get_rect(topright=(SCREEN_WIDTH - 10, 10))
            screen_surf.blit(level_text_surf, level_rect)
        except Exception as e:
            print(f"Error rendering UI text: {e}")

        # Draw Boss Health Bar if boss is active
        if boss_active and boss_instance:
            # Assuming the boss object has a method to draw its health bar
            boss_instance.draw_health_bar(screen_surf)

        # Draw Player Shield visual if active
        if player.shield_active:
            # player.draw_shield(screen_surf) # FIX: Commented out - Player class needs this method
            pass # Keep shield logic but don't draw until method exists in Player

        # --- Check Level End Condition ---
        # Level ends if player died or the level objective (boss defeat) was met
        if game_over_local or level_passed:
            running_this_level = False # Exit the level loop

        # Update the display
        pygame.display.flip()

    # --- Level Loop Ended ---
    # Determine result based on flags
    result = 'PASSED' if level_passed else ('FAILED' if game_over_local else 'QUIT') # QUIT is handled by event loop return
    print(f"--- Level {level_num} Ended. Result: {result}, Score: {player.score} ---")
    # Optional short pause before transitioning
    # time.sleep(1.0)
    return result, player.score


# ==============================================================================
# --- Main Application Entry Point ---
# ==============================================================================
def main():
    """Initializes Pygame, loads all assets, creates game objects, and runs the main game loop."""
    print("--- Pygame Initialization ---")
    try:
        pygame.init()
        # Initialize mixer with settings
        if pygame.mixer and not pygame.mixer.get_init():
            print("Initializing Mixer...")
            pygame.mixer.init(frequency=MIXER_FREQUENCY, size=MIXER_SIZE, channels=MIXER_CHANNELS, buffer=MIXER_BUFFER)
            print("Pygame Mixer Initialized Successfully")
        elif not pygame.mixer:
            print("Warning: Mixer module not available. No sound will be played.")
    except pygame.error as e:
        print(f"ERROR: Pygame/Mixer Initialization Failed: {e}")
        sys.exit(1)

    # Setup Screen & Clock
    try:
        # Use dimensions from settings
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("飞机大战 - 多关卡版")
        clock = pygame.time.Clock()
    except pygame.error as e:
        print(f"ERROR: Failed to set up screen: {e}")
        pygame.quit()
        sys.exit(1)

    # --- Load Fonts ---
    fonts = {}
    print("\n--- Loading Fonts ---")
    try:
        # Use font path and sizes from settings
        if UI_FONT_PATH and os.path.exists(UI_FONT_PATH):
            fonts['title'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_SCORE)
            print(f"Successfully loaded font: {os.path.basename(UI_FONT_PATH)}")
        else:
             if UI_FONT_PATH: # Only raise error if a path was set but not found
                 raise FileNotFoundError(f"Custom font not found: {UI_FONT_PATH}")
             else: # If UI_FONT_PATH was None/empty, just proceed to fallback
                 print("Info: No custom font path set. Using system default.")
                 raise Exception("Triggering fallback") # Use generic exception to go to fallback
    except Exception as e:
        print(f"Warning: Failed to load custom font ({e}). Using system default.")
        try:
            # Use font sizes from settings for fallback
            fonts['title'] = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.SysFont(None, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.SysFont(None, FONT_SIZE_SCORE)
            print("Loaded system default font.")
        except Exception as e_sys:
            print(f"CRITICAL ERROR: Failed to load any fonts: {e_sys}")
            pygame.quit()
            sys.exit("Font Loading Error")

    # --- Load General Assets (Images & Sounds) ---
    images = {}
    sounds = {}
    music_paths = {} # Store paths to level-specific music files
    print("\n--- Loading General Assets ---")
    try:
        # --- Load Background (Handled by Background class instance later) ---
        # We only need the path and speed from settings now.

        # Load Player Image
        images['player'] = load_and_scale_image(PLAYER_IMG_PATH, PLAYER_WIDTH, PLAYER_HEIGHT)
        if not images['player']: raise ValueError("Failed to load essential player image.")

        # Load Enemy Images (using keys that match enemy types in levels/settings)
        # Ensure keys here ('enemy1', 'enemy2', etc.) match those used in level JSONs
        enemy_image_configs = {
            'enemy1': (ENEMY1_IMG_PATH, ENEMY1_WIDTH, ENEMY1_HEIGHT),
            'enemy2': (ENEMY2_IMG_PATH, ENEMY2_WIDTH, ENEMY2_HEIGHT),
            'enemy3': (ENEMY3_IMG_PATH, ENEMY3_WIDTH, ENEMY3_HEIGHT),
            'enemy4': (ENEMY4_IMG_PATH, ENEMY4_WIDTH, ENEMY4_HEIGHT),
            'boss':   (ENEMY_BOSS_IMG_PATH, ENEMY_BOSS_WIDTH, ENEMY_BOSS_HEIGHT), # Use 'boss' key
        }
        for key, (path, w, h) in enemy_image_configs.items():
             img = load_and_scale_image(path, w, h)
             if img:
                 images[key] = img
             # Optionally check if essential images loaded:
             # if key == 'boss' and not img: raise ValueError("Failed to load essential boss image.")

        # Load Powerup Images into a sub-dictionary
        images['powerups'] = {}
        # POWERUP_IMAGES is now defined in settings.py
        for type_key, path in POWERUP_IMAGES.items():
            img = load_and_scale_image(path, POWERUP_WIDTH, POWERUP_HEIGHT)
            if img:
                images['powerups'][type_key] = img
            else:
                print(f"Warning: Failed to load powerup image for type '{type_key}' at path: {path}")

        # Load Sound Effects (using constants from settings)
        sound_configs = {
            'player_shoot': (SHOOT_SOUND_PATH, PLAYER_SHOOT_VOLUME),
            'enemy_explode': (ENEMY_EXPLODE_SOUND_PATH, ENEMY_EXPLODE_VOLUME),
            'boss_explode': (BOSS_EXPLODE_SOUND_PATH, BOSS_EXPLODE_VOLUME),
            'powerup_pickup': (POWERUP_PICKUP_SOUND_PATH, POWERUP_PICKUP_VOLUME),
            'game_win': (WIN_SOUND_PATH, WIN_VOLUME),
            'player_lose': (LOSE_SOUND_PATH, LOSE_VOLUME),
            'boss_intro': (BOSS_INTRO_SOUND_PATH, BOSS_INTRO_VOLUME),
            'boss_hit': (BOSS_HIT_SOUND_PATH, BOSS_HIT_VOLUME),
            'shield_up': (SHIELD_UP_SOUND_PATH, SHIELD_UP_VOLUME),
            'shield_down': (SHIELD_DOWN_SOUND_PATH, SHIELD_DOWN_VOLUME),
            'bomb': (BOMB_SOUND_PATH, BOMB_VOLUME),
            'boss_shoot': (BOSS_SHOOT_SOUND_PATH, BOSS_SHOOT_VOLUME),
        }
        for key, (path, vol) in sound_configs.items():
            snd = load_sound(path, vol)
            if snd:
                sounds[key] = snd
            # else: print(f"Warning: Sound '{key}' failed to load from {path}") # load_sound already warns

        print("--- General Assets Loaded ---")

    except Exception as e:
        print(f"CRITICAL ERROR during asset loading: {e}")
        pygame.quit()
        sys.exit("Asset Loading Error")

    # --- Create Background Instance ---
    # Moved after screen setup and asset path definition
    print("\n--- Initializing Background ---")
    background = Background(BACKGROUND_IMG_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_SCROLL_SPEED)
    # The Background class handles its own loading errors internally

    # --- Load Level Data ---
    # Use LEVELS_DIR from settings
    LEVELS = load_level_data(LEVELS_DIR)
    if not LEVELS:
        print("CRITICAL ERROR: No level data found or loaded. Exiting.")
        pygame.quit()
        sys.exit("Level Data Error")

    # --- Prepare Music Paths (after loading LEVELS) ---
    print("\n--- Checking Level Music Paths ---")
    for level_cfg in LEVELS:
        level_num = level_cfg.get('level_number')
        music_filename = level_cfg.get('music') # e.g., "level1.ogg" or null
        if level_num is not None and music_filename:
            # Use SND_DIR from settings
            full_music_path = os.path.join(SND_DIR, music_filename)
            if os.path.exists(full_music_path):
                music_paths[level_num] = full_music_path
                print(f"  Found music for Level {level_num}: {music_filename}")
            else:
                print(f"  Warning: Music file '{music_filename}' for Level {level_num} not found at {full_music_path}")

    # --- Load High Score ---
    # Use HIGH_SCORE_FILE_PATH from settings
    high_score = load_high_score(HIGH_SCORE_FILE_PATH)
    print(f"\n--- High Score Loaded: {high_score} ---")

    # --- Application State Machine ---
    app_running = True
    game_state = 'START_SCREEN'
    current_level_index = 0
    final_score_this_run = 0
    current_music_path = None # Track the path of the music currently playing

    # --- Main Game Loop ---
    while app_running:

        # --- State: START_SCREEN ---
        if game_state == 'START_SCREEN':
            # Stop music before showing start screen
            if pygame.mixer and pygame.mixer.music.get_busy():
                 pygame.mixer.music.stop()
                 pygame.mixer.music.unload() # Unload previous track
            current_music_path = None
            # Show screen and wait for key press
            # Pass fonts and high score
            show_start_screen(screen, clock, fonts.get('title'), fonts.get('score'), high_score)
            # Reset for new game attempt
            current_level_index = 0
            final_score_this_run = 0
            game_state = 'LEVEL_START' # Proceed to first level prep

        # --- State: LEVEL_START ---
        elif game_state == 'LEVEL_START':
            if current_level_index < len(LEVELS):
                level_data = LEVELS[current_level_index]
                level_num = level_data.get('level_number', current_level_index + 1) # Use index+1 as fallback level num

                # --- Handle Music for the Level ---
                track_to_play = music_paths.get(level_num) # Specific track for this level?
                # If no specific track, try default BGM path from settings
                if not track_to_play:
                    if Default_BGM_PATH and os.path.exists(Default_BGM_PATH):
                         track_to_play = Default_BGM_PATH
                    # else: print(f"Level {level_num}: No specific or default music found.")

                # Play if track found and different from current, or if music is not playing
                if track_to_play and (track_to_play != current_music_path or not pygame.mixer.music.get_busy()):
                    if pygame.mixer and pygame.mixer.get_init():
                        print(f"Playing music: {os.path.basename(track_to_play)}")
                        try:
                            pygame.mixer.music.load(track_to_play)
                            pygame.mixer.music.set_volume(BGM_VOLUME) # Use volume from settings
                            pygame.mixer.music.play(loops=-1) # Loop indefinitely
                            current_music_path = track_to_play
                        except pygame.error as e:
                            print(f"Error playing music '{track_to_play}': {e}")
                            current_music_path = None # Reset path if loading failed
                # Stop if no track for this level but music was playing
                elif not track_to_play and current_music_path:
                     if pygame.mixer and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                         pygame.mixer.music.stop()
                         pygame.mixer.music.unload()
                     current_music_path = None
                # --- End Music Handling ---

                # Show transition screen (pass large font)
                show_level_start_screen(screen, clock, fonts.get('large'), level_num)
                game_state = 'RUNNING_LEVEL' # Start playing the level
            else:
                # All levels completed successfully
                game_state = 'GAME_WON'

        # --- State: RUNNING_LEVEL ---
        elif game_state == 'RUNNING_LEVEL':
            level_data = LEVELS[current_level_index]
            # Run the actual level gameplay, passing the background object
            level_result, score_at_level_end = run_game(
                screen, clock, fonts, images, sounds, level_data, background
            )
            final_score_this_run = score_at_level_end # Record score achieved in this run

            # Process level outcome
            if level_result == 'PASSED':
                current_level_index += 1 # Move to next level index
                # Check if that was the last level
                if current_level_index < len(LEVELS):
                    game_state = 'LEVEL_START' # Go to prep for next level
                else:
                    game_state = 'GAME_WON' # All levels done
            elif level_result == 'FAILED':
                game_state = 'GAME_OVER' # Player lost
            elif level_result == 'QUIT':
                app_running = False # Player quit mid-game

        # --- State: GAME_WON ---
        elif game_state == 'GAME_WON':
            print("Congratulations! You beat all levels!")
            game_result_for_screen = 'WIN' # Set result for end screen
            game_state = 'END_SCREEN' # Go to end screen

        # --- State: GAME_OVER ---
        elif game_state == 'GAME_OVER':
            print("Game Over!")
            game_result_for_screen = 'LOSE' # Set result for end screen
            game_state = 'END_SCREEN' # Go to end screen

        # --- State: END_SCREEN ---
        elif game_state == 'END_SCREEN':
            # Stop music before showing end screen
            if pygame.mixer and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            current_music_path = None

            # Check & Save High Score
            if final_score_this_run > high_score:
                print(f"New High Score: {final_score_this_run}")
                # Use path from settings
                save_high_score(HIGH_SCORE_FILE_PATH, final_score_this_run)
                high_score = final_score_this_run # Update score shown on start screen if replaying

            # Show End Screen and get player choice (pass fonts, result, score)
            player_choice = show_end_screen(screen, clock, fonts, game_result_for_screen, final_score_this_run)
            if player_choice == 'QUIT':
                app_running = False
            elif player_choice == 'REPLAY':
                game_state = 'START_SCREEN' # Loop back to start

    # --- Game Exit ---
    print("Exiting PlaneWar.")
    pygame.quit()
    sys.exit()

# --- Script Execution Guard ---
if __name__ == '__main__':
    main() # Run the main function when the script is executed
