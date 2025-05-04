# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/powerup.py
import pygame
import random
# --- Use relative import for settings ---
from .settings import *

class PowerUp(pygame.sprite.Sprite):
    """ Represents a power-up item that falls from the top. """
    def __init__(self, powerup_images): # Takes a dictionary of pre-loaded images
        super().__init__()
        # Use constants from settings
        self.type = random.choice(POWERUP_TYPES)

        # Get the correct pre-loaded image, or create a fallback surface
        self.image = powerup_images.get(self.type)
        if self.image is None:
            print(f"警告: 未能加载道具图片 '{self.type}'. 使用备用方块.") # Warning: Failed to load powerup image '{self.type}'. Using fallback block.
            self.image = pygame.Surface((POWERUP_WIDTH, POWERUP_HEIGHT))
            # Use constants from settings for fallback colors and dimensions
            fallback_color = POWERUP_FALLBACK_COLORS.get(self.type, BLUE) # Default to blue if type somehow invalid
            self.image.fill(fallback_color)
            pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 1) # Add border

        self.rect = self.image.get_rect()
        # Use constants from settings for screen width
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40) # Start above screen
        # Use constant from settings for speed
        self.speedy = POWERUP_SPEED_Y

    def update(self):
        """ Move the power-up down the screen. """
        self.rect.y += self.speedy
        # Kill if it moves off the bottom of the screen
        # Use constant from settings for screen height
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
