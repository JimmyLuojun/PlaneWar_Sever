"""Configuration settings and constants for the Pygame client.

Defines constants used throughout the game client, such as screen dimensions,
colors, frame rates, speeds, asset paths, and server URLs. Loads values
from environment variables where appropriate.
"""
# /Users/junluo/Desktop/PlaneWar_Sever/game/settings.py
import pygame
import os

# --- Base Directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
IMG_DIR = os.path.join(MEDIA_DIR, 'images')
SND_DIR = os.path.join(MEDIA_DIR, 'sounds')
FONT_DIR = os.path.join(MEDIA_DIR, 'fonts')
LEVELS_DIR = os.path.join(BASE_DIR, 'levels') # Added path for levels directory

# --- Screen Dimensions ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
FPS = 60

# --- File Paths ---
PLAYER_IMG_PATH = os.path.join(IMG_DIR, "player.png")
ENEMY1_IMG_PATH = os.path.join(IMG_DIR, "Enemy1.png")
ENEMY2_IMG_PATH = os.path.join(IMG_DIR, "Enemy2.png")
ENEMY3_IMG_PATH = os.path.join(IMG_DIR, "Enemy3.png")
ENEMY4_IMG_PATH = os.path.join(IMG_DIR, "Enemy4.png")
ENEMY_BOSS_IMG_PATH = os.path.join(IMG_DIR, "Enemy_Boss.png")
POWERUP_DOUBLESHOT_IMG_PATH = os.path.join(IMG_DIR, "powerup_doubleshot.png")
POWERUP_SHIELD_IMG_PATH = os.path.join(IMG_DIR, "powerup_shield.png")
POWERUP_BOMB_IMG_PATH = os.path.join(IMG_DIR, "powerup_bomb.png")

BACKGROUND_IMG_PATH = os.path.join(IMG_DIR, "background.jpeg") # Relative path

SHOOT_SOUND_PATH = os.path.join(SND_DIR, "shoot.wav")
ENEMY_EXPLODE_SOUND_PATH = os.path.join(SND_DIR, "explode.wav")
BOSS_EXPLODE_SOUND_PATH = os.path.join(SND_DIR, "big_explosion.wav")
POWERUP_PICKUP_SOUND_PATH = os.path.join(SND_DIR, "small_powerup.wav")
WIN_SOUND_PATH = os.path.join(SND_DIR, "win.wav")
LOSE_SOUND_PATH = os.path.join(SND_DIR, "lose.wav")
BOSS_INTRO_SOUND_PATH = os.path.join(SND_DIR, "boss_intro.wav")
BOSS_HIT_SOUND_PATH = os.path.join(SND_DIR, "boss_hit.mp3")
Default_BGM_PATH = os.path.join(SND_DIR, "Dynamedion GbR - 危险_SQ.flac")
SHIELD_UP_SOUND_PATH = os.path.join(SND_DIR, "shield_up.wav")
SHIELD_DOWN_SOUND_PATH = os.path.join(SND_DIR, "shield_down.mp3")
BOMB_SOUND_PATH = os.path.join(SND_DIR, "bomb_explode.wav")
BOSS_SHOOT_SOUND_PATH = os.path.join(SND_DIR, "boss_shoot.wav")

# --- Font Settings ---
UI_FONT_PATH = os.path.join(FONT_DIR, "NotoSansSC-Regular.ttf")
FONT_SIZE_LARGE = 60
FONT_SIZE_SCORE = 36
FONT_SIZE_TITLE = 90

# --- Sprite Dimensions ---
PLAYER_WIDTH = 55
PLAYER_HEIGHT = 45
ENEMY1_WIDTH = 45
ENEMY1_HEIGHT = 35
ENEMY2_WIDTH = 45
ENEMY2_HEIGHT = 55
ENEMY3_WIDTH = 60
ENEMY3_HEIGHT = 35
ENEMY4_WIDTH = 50
ENEMY4_HEIGHT = 50
ENEMY_BOSS_WIDTH = 120
ENEMY_BOSS_HEIGHT = 90
POWERUP_WIDTH = 40
POWERUP_HEIGHT = 40
BULLET_WIDTH = 5
BULLET_HEIGHT = 12
ENEMY_BULLET_WIDTH = 8
ENEMY_BULLET_HEIGHT = 15

# --- Game Constants (Defaults / Global) ---
PLAYER_SHOOT_DELAY = 150
BULLET_SPEED = 10             # <<< --- ADDED THIS LINE (Player bullet speed) --- >>>
ENEMY_SHOOT_DELAY = 500     # Delay (ms) between enemy shots
ENEMY_SPAWN_INTERVAL = 60
ENEMY_MIN_SPEED_Y = 1
ENEMY_MAX_SPEED_Y = 4
ENEMY_MIN_SPEED_X = -2
ENEMY_MAX_SPEED_X = 2
MAX_ONSCREEN_ENEMIES = 15

BOSS_SPAWN_SCORE = 99999
BOSS_ENTRY_Y = 100
BOSS_SPEED_X = 3
BOSS_SPEED_Y = 1           # Vertical speed for the boss (if used)
BOSS_SHOOT_DELAY = 1500
BOSS_MAX_HEALTH = 50
ENEMY_BULLET_SPEED_Y = 12

STARTUP_GRACE_PERIOD = 1500
PLAYER_STARTING_BOMBS = 3 # Define how many bombs the player starts with
POWERUP_SPAWN_INTERVAL = 8000
POWERUP_DURATION = 5000
SHIELD_DURATION = 7000
POWERUP_SPEED_Y = 3
BOMB_KEY = pygame.K_b

BACKGROUND_SCROLL_SPEED = 2 # Pixels per frame, adjust as desired

# --- PowerUp Types ---
POWERUP_TYPES = ['double_shot', 'shield', 'bomb']
POWERUP_IMAGES = {
    'double_shot': POWERUP_DOUBLESHOT_IMG_PATH,
    'shield': POWERUP_SHIELD_IMG_PATH,
    'bomb': POWERUP_BOMB_IMG_PATH
}
POWERUP_FALLBACK_COLORS = {
    'double_shot': (0, 0, 255), # BLUE
    'shield': (0, 255, 255), # CYAN
    'bomb': (255, 165, 0) # ORANGE
}

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
ENEMY_BULLET_COLOR = RED
SHIELD_VISUAL_COLOR = (*CYAN, 100) # Tuple unpacking to add alpha

# --- Mixer Settings ---
MIXER_FREQUENCY = 44100
MIXER_SIZE = -16
MIXER_CHANNELS = 32
MIXER_BUFFER = 512

# --- Sound Volumes ---
PLAYER_SHOOT_VOLUME = 0.25
ENEMY_EXPLODE_VOLUME = 0.4
BOSS_EXPLODE_VOLUME = 0.6
POWERUP_PICKUP_VOLUME = 0.5
WIN_VOLUME = 0.7
LOSE_VOLUME = 0.7
BOSS_INTRO_VOLUME = 0.6
BOSS_HIT_VOLUME = 0.5
SHIELD_UP_VOLUME = 0.5
SHIELD_DOWN_VOLUME = 0.5
BOMB_VOLUME = 0.7
BOSS_SHOOT_VOLUME = 0.5
BGM_VOLUME = 0.3

# --- High Score File Path ---
HIGH_SCORE_FILE_PATH = os.path.join(BASE_DIR, "highscore.txt")

# --- Server API URL ---
# Define the base URL for the Flask server API
# Make sure the port matches the one your Flask server is running on!
SERVER_API_URL = "http://127.0.0.1:5000/api" # Default development URL

# --- Enemy Settings ---
ENEMY_SPAWN_RANGE_Y = (50, 200)

