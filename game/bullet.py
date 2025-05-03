# /Users/junluo/Desktop/PlaneWar/bullet.py
import pygame
from settings import *

class Bullet(pygame.sprite.Sprite):
    """ Represents a bullet fired by the player. """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -BULLET_SPEED

    def update(self):
        """ Move the bullet up the screen. """
        self.rect.y += self.speedy
        # Kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    """ Represents a bullet fired by an enemy (specifically the boss). """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))
        self.image.fill(ENEMY_BULLET_COLOR)
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.speedy = ENEMY_BULLET_SPEED_Y

    def update(self):
        """ Move the bullet down the screen. """
        self.rect.y += self.speedy
        # Kill if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()