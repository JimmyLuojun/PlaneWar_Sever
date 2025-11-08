"""Configuration settings and constants for the PlaneWar game client.

Defines all constants used throughout the game client, including screen dimensions,
colors, frame rates, speeds, asset paths, and server URLs. Organized into logical
sections for easy maintenance and reference.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import os
from typing import Dict, Tuple, Final

# Third-party
import pygame


# ============================================================================
# Constants - Environment & Paths
# ============================================================================

# --- Base Directories ---
# BASE_DIR now points to the game directory (parent of infrastructure/)
BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_DIR: Final[str] = os.path.join(BASE_DIR, "media")
IMG_DIR: Final[str] = os.path.join(MEDIA_DIR, "images")
SND_DIR: Final[str] = os.path.join(MEDIA_DIR, "sounds")
FONT_DIR: Final[str] = os.path.join(MEDIA_DIR, "fonts")

LEVELS_DIR: Final[str] = os.path.join(BASE_DIR, "levels")

# --- Data Files ---
DATA_DIR: Final[str] = os.path.join(BASE_DIR, "data")
HIGH_SCORE_FILE_PATH: Final[str] = os.path.join(DATA_DIR, "highscore.txt")
PROGRESS_FILE_PATH: Final[str] = os.path.join(DATA_DIR, "progress.json")


# ============================================================================
# Constants - Network
# ============================================================================

# Server API base URL (must match Flask server port)
SERVER_API_URL: Final[str] = "http://127.0.0.1:8000/api"


# ============================================================================
# Constants - Screen & Display
# ============================================================================

# --- Screen Dimensions ---
SCREEN_WIDTH: Final[int] = 1000
SCREEN_HEIGHT: Final[int] = 600
FPS: Final[int] = 60

# --- Background ---
BACKGROUND_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "background.jpeg")
BACKGROUND_SCROLL_SPEED: Final[int] = 2  # Pixels per frame


# ============================================================================
# Constants - Colors
# ============================================================================

# --- Basic Colors ---
BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
WHITE: Final[Tuple[int, int, int]] = (255, 255, 255)
RED: Final[Tuple[int, int, int]] = (255, 0, 0)
GREEN: Final[Tuple[int, int, int]] = (0, 255, 0)
GREY: Final[Tuple[int, int, int]] = (128, 128, 128)
YELLOW: Final[Tuple[int, int, int]] = (255, 255, 0)
BLUE: Final[Tuple[int, int, int]] = (0, 0, 255)
CYAN: Final[Tuple[int, int, int]] = (0, 255, 255)
ORANGE: Final[Tuple[int, int, int]] = (255, 165, 0)

# --- Gameplay Colors ---
ENEMY_BULLET_COLOR: Final[Tuple[int, int, int]] = RED
SHIELD_VISUAL_COLOR: Final[Tuple[int, int, int, int]] = (*CYAN, 100)  # RGBA with alpha


# ============================================================================
# Constants - Fonts
# ============================================================================

UI_FONT_PATH: Final[str] = os.path.join(FONT_DIR, "NotoSansSC-Regular.ttf")
FONT_SIZE_LARGE: Final[int] = 60
FONT_SIZE_SCORE: Final[int] = 36
FONT_SIZE_TITLE: Final[int] = 90


# ============================================================================
# Constants - Player
# ============================================================================

# --- Player Sprite ---
PLAYER_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "player.png")
PLAYER_WIDTH: Final[int] = 55
PLAYER_HEIGHT: Final[int] = 45

# --- Player Gameplay ---
PLAYER_SHOOT_DELAY: Final[int] = 150  # milliseconds
PLAYER_STARTING_BOMBS: Final[int] = 3
STARTUP_GRACE_PERIOD: Final[int] = 1500  # milliseconds of invincibility at game start

# --- Player Bullet ---
BULLET_WIDTH: Final[int] = 5
BULLET_HEIGHT: Final[int] = 12
BULLET_SPEED: Final[int] = 10  # pixels per frame

# --- Player Controls ---
BOMB_KEY: Final[int] = pygame.K_b


# ============================================================================
# Constants - Enemies
# ============================================================================

# --- Enemy Sprites ---
ENEMY1_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "Enemy1.png")
ENEMY2_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "Enemy2.png")
ENEMY3_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "Enemy3.png")
ENEMY4_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "Enemy4.png")

# --- Enemy Dimensions ---
ENEMY1_WIDTH: Final[int] = 45
ENEMY1_HEIGHT: Final[int] = 35
ENEMY2_WIDTH: Final[int] = 45
ENEMY2_HEIGHT: Final[int] = 55
ENEMY3_WIDTH: Final[int] = 60
ENEMY3_HEIGHT: Final[int] = 35
ENEMY4_WIDTH: Final[int] = 50
ENEMY4_HEIGHT: Final[int] = 50

# --- Enemy Behavior ---
ENEMY_MIN_SPEED_Y: Final[int] = 1  # pixels per frame
ENEMY_MAX_SPEED_Y: Final[int] = 4
ENEMY_MIN_SPEED_X: Final[int] = -2
ENEMY_MAX_SPEED_X: Final[int] = 2
ENEMY_SPAWN_INTERVAL: Final[int] = 60  # frames
ENEMY_SPAWN_RANGE_Y: Final[Tuple[int, int]] = (50, 200)  # spawn Y range
MAX_ONSCREEN_ENEMIES: Final[int] = 15

# --- Enemy Combat ---
ENEMY_SHOOT_DELAY: Final[int] = 500  # milliseconds
ENEMY_BULLET_WIDTH: Final[int] = 8
ENEMY_BULLET_HEIGHT: Final[int] = 15
ENEMY_BULLET_SPEED_Y: Final[int] = 12  # pixels per frame


# ============================================================================
# Constants - Boss
# ============================================================================

# --- Boss Sprite ---
ENEMY_BOSS_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "Enemy_Boss.png")
ENEMY_BOSS_WIDTH: Final[int] = 120
ENEMY_BOSS_HEIGHT: Final[int] = 90

# --- Boss Behavior ---
BOSS_SPAWN_SCORE: Final[int] = 99999  # Score threshold for boss spawn
BOSS_ENTRY_Y: Final[int] = 100  # Y position after entry
BOSS_SPEED_X: Final[int] = 3  # Horizontal patrol speed
BOSS_SPEED_Y: Final[int] = 1  # Vertical entry speed

# --- Boss Combat ---
BOSS_MAX_HEALTH: Final[int] = 50
BOSS_SHOOT_DELAY: Final[int] = 1500  # milliseconds


# ============================================================================
# Constants - PowerUps
# ============================================================================

# --- PowerUp Sprites ---
POWERUP_DOUBLESHOT_IMG_PATH: Final[str] = os.path.join(
    IMG_DIR, "powerup_doubleshot.png"
)
POWERUP_SHIELD_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "powerup_shield.png")
POWERUP_BOMB_IMG_PATH: Final[str] = os.path.join(IMG_DIR, "powerup_bomb.png")

# --- PowerUp Dimensions ---
POWERUP_WIDTH: Final[int] = 40
POWERUP_HEIGHT: Final[int] = 40

# --- PowerUp Behavior ---
POWERUP_SPAWN_INTERVAL: Final[int] = 8000  # milliseconds
POWERUP_SPEED_Y: Final[int] = 3  # pixels per frame
POWERUP_DURATION: Final[int] = 5000  # milliseconds (double_shot)
SHIELD_DURATION: Final[int] = 7000  # milliseconds (shield)

# --- PowerUp Types & Configuration ---
POWERUP_TYPES: Final[Tuple[str, str, str]] = ("double_shot", "shield", "bomb")

POWERUP_IMAGES: Final[Dict[str, str]] = {
    "double_shot": POWERUP_DOUBLESHOT_IMG_PATH,
    "shield": POWERUP_SHIELD_IMG_PATH,
    "bomb": POWERUP_BOMB_IMG_PATH,
}

POWERUP_FALLBACK_COLORS: Final[Dict[str, Tuple[int, int, int]]] = {
    "double_shot": BLUE,
    "shield": CYAN,
    "bomb": ORANGE,
}


# ============================================================================
# Constants - Explosions
# ============================================================================

# --- Explosion Types ---
EXPLOSION_TYPE_SMALL: Final[str] = "small"  # Regular enemy explosion
EXPLOSION_TYPE_MEDIUM: Final[str] = "medium"  # Larger enemy explosion
EXPLOSION_TYPE_LARGE: Final[str] = "large"  # Boss explosion
EXPLOSION_TYPE_BOMB: Final[str] = "bomb"  # Bomb powerup explosion

# --- Explosion Dimensions ---
EXPLOSION_SMALL_SIZE: Final[int] = 30  # Small explosion radius
EXPLOSION_MEDIUM_SIZE: Final[int] = 50  # Medium explosion radius
EXPLOSION_LARGE_SIZE: Final[int] = 80  # Large explosion radius
EXPLOSION_BOMB_SIZE: Final[int] = 120  # Bomb explosion radius

# --- Explosion Duration ---
EXPLOSION_DURATION: Final[int] = 300  # milliseconds - how long explosion stays visible

# --- Explosion Colors ---
EXPLOSION_SMALL_COLOR: Final[Tuple[int, int, int]] = ORANGE
EXPLOSION_MEDIUM_COLOR: Final[Tuple[int, int, int]] = RED
EXPLOSION_LARGE_COLOR: Final[Tuple[int, int, int]] = (255, 100, 0)  # Deep orange
EXPLOSION_BOMB_COLOR: Final[Tuple[int, int, int]] = (
    255,
    255,
    100,
)  # Bright yellow-white

# --- Explosion Animation Frames ---
EXPLOSION_FRAME_COUNT: Final[int] = 5  # Number of animation frames (size expansion)


# ============================================================================
# Constants - Audio Settings
# ============================================================================

# --- Mixer Configuration ---
MIXER_FREQUENCY: Final[int] = 44100
MIXER_SIZE: Final[int] = -16
MIXER_CHANNELS: Final[int] = 32
MIXER_BUFFER: Final[int] = 512

# --- Sound File Paths ---
SHOOT_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "shoot.wav")
ENEMY_EXPLODE_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "explode.wav")
BOSS_EXPLODE_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "big_explosion.wav")
BOSS_SHOOT_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "boss_shoot.wav")
BOSS_HIT_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "boss_hit.mp3")
BOSS_INTRO_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "boss_intro.wav")
POWERUP_PICKUP_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "small_powerup.wav")
SHIELD_UP_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "shield_up.wav")
SHIELD_DOWN_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "shield_down.mp3")
BOMB_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "bomb_explode.wav")
WIN_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "win.wav")
LOSE_SOUND_PATH: Final[str] = os.path.join(SND_DIR, "lose.wav")
Default_BGM_PATH: Final[str] = os.path.join(SND_DIR, "Dynamedion GbR - 危险_SQ.flac")

# --- Sound Volumes (0.0 to 1.0) ---
PLAYER_SHOOT_VOLUME: Final[float] = 0.25
ENEMY_EXPLODE_VOLUME: Final[float] = 0.4
BOSS_EXPLODE_VOLUME: Final[float] = 0.6
BOSS_SHOOT_VOLUME: Final[float] = 0.5
BOSS_HIT_VOLUME: Final[float] = 0.5
BOSS_INTRO_VOLUME: Final[float] = 0.6
POWERUP_PICKUP_VOLUME: Final[float] = 0.5
SHIELD_UP_VOLUME: Final[float] = 0.5
SHIELD_DOWN_VOLUME: Final[float] = 0.5
BOMB_VOLUME: Final[float] = 0.7
WIN_VOLUME: Final[float] = 0.7
LOSE_VOLUME: Final[float] = 0.7
BGM_VOLUME: Final[float] = 0.3
