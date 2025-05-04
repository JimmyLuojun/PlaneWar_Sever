# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/bullet.py
import pygame
# *** ADD Vector2 for potential use, though not strictly needed if direction passed in ***
from pygame.math import Vector2
from .settings import *

# --- Bullet Class (No changes needed) ---
class Bullet(pygame.sprite.Sprite):
    """ Represents a bullet fired by the player. """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# --- EnemyBullet Class (MODIFIED) ---
class EnemyBullet(pygame.sprite.Sprite):
    """ Represents a bullet fired by an enemy (straight or angled). """
    # *** MODIFIED __init__ signature ***
    def __init__(self, x, y, direction=None): # Added optional direction vector
        super().__init__()
        self.image = pygame.Surface((ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))
        self.image.fill(ENEMY_BULLET_COLOR)
        self.rect = self.image.get_rect(centerx=x, top=y)

        # Use Vector2 for float-precision movement
        self.pos = Vector2(self.rect.center)
        self.speed = ENEMY_BULLET_SPEED_Y # Base speed

        if direction is None:
            # straight down
            self.velocity = Vector2(0, self.speed)
        else:
            # angled shot (direction must be normalized)
            self.velocity = direction * self.speed

    # *** MODIFIED update method ***
    def update(self):
        """ Move the bullet based on its velocity. """
        # 1) Float arithmetic via __add__
        self.pos = self.pos + self.velocity
        # 2) Force rect.center into a real (x, y) tuple
        self.rect.center = (self.pos.x, self.pos.y)

        # 3) Kill off the sides first...
        try:
            if self.rect.right  < 0 or \
               self.rect.left   > SCREEN_WIDTH:
                self.kill()
                return
        except TypeError:
            pass
        # ...then kill off the bottom
        try:
            if self.rect.top    > SCREEN_HEIGHT:
                self.kill()
                return
        except TypeError:
            pass