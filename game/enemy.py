"""Defines enemy classes, including regular enemies and bosses.

Contains the `Enemy` class for standard enemies with basic movement and
optional shooting, and the `EnemyBoss` class for more complex boss
characters with distinct movement patterns, health, and potentially multiple
attack types.
"""
# game/enemy.py

import pygame
import random
from .settings import *         # bring in SCREEN_WIDTH, SCREEN_HEIGHT, etc.
from .bullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    """Basic enemy that drifts down and bounces horizontally."""
    def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()

        # spawn at random X, just above screen
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # determine speed ranges
        min_y, max_y = speed_y_range or (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        min_x, max_x = speed_x_range or (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X)

        min_y = max(1, min_y)
        max_y = max(min_y, max_y)
        self.speedy = random.randint(min_y, max_y)

        # pick a nonzero horizontal speed
        possible_speedx = [i for i in range(min_x, max_x + 1) if i != 0]
        if not possible_speedx:
            # fallback if range excludes all nonzero
            possible_speedx = [x for x in (max_x, min_x, 1) if x != 0]
        self.speedx = random.choice(possible_speedx)


    def update(self):
        # drift
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # bounce off walls
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx
            self.rect.right = min(self.rect.right, SCREEN_WIDTH)
            self.rect.left  = max(self.rect.left, 0)

        # **Kill as soon as it's fully off-screen**
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()



class EnemyBoss(pygame.sprite.Sprite):
    """Big boss: enters from top, patrols horizontally, shoots, and can take damage."""
    def __init__(self, boss_img, shoot_sound, all_sprites_group, enemy_bullets_group):
        super().__init__()
        self.image_orig = boss_img
        self.image = boss_img.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = -20      # start off-screen

        # entry vs. patrol
        self.entry_speedy = 1
        self.entry_y      = BOSS_ENTRY_Y
        self.speedx       = BOSS_SPEED_X
        self.entered      = False

        # health & shooting
        self.max_health    = BOSS_MAX_HEALTH
        self.health        = self.max_health
        self.shoot_delay   = BOSS_SHOOT_DELAY
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_sound    = shoot_sound

        # groups
        self.all_sprites    = all_sprites_group
        self.enemy_bullets  = enemy_bullets_group

        # **immediately add self to the master group**
        self.all_sprites.add(self)

    def update(self):
        now = pygame.time.get_ticks()

        # entry phase
        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.rect.centery = self.entry_y
                self.entered = True
                self.last_shot_time = now
        else:
            # horizontal patrol
            self.rect.x += self.speedx
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                self.speedx = -self.speedx
                self.rect.right = min(self.rect.right, SCREEN_WIDTH)
                self.rect.left  = max(self.rect.left, 0)

            # time to shoot?
            if now - self.last_shot_time > self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        self.all_sprites.add(bullet)
        self.enemy_bullets.add(bullet)
        if self.shoot_sound:
            try:
                self.shoot_sound.play()
            except pygame.error:
                pass

    def take_damage(self, damage):
        """Reduce health, play sound, and kill if at 0."""
        self.health -= damage
        if self.health > 0:
            if self.shoot_sound:
                self.shoot_sound.play()
        else:
            if self.shoot_sound:
                self.shoot_sound.play()
            self.kill()

    def draw_health_bar(self, surf):
        if self.health <= 0:
            return
        bar_length = 100
        bar_height = 10
        x = self.rect.left
        y = self.rect.top - bar_height - 5

        # border
        pygame.draw.rect(surf, BLACK, (x-1, y-1, bar_length+2, bar_height+2), 1)
        # background
        pygame.draw.rect(surf, RED,   (x,   y,   bar_length,    bar_height))
        # fill
        fill = int(self.health / self.max_health * bar_length)
        pygame.draw.rect(surf, GREEN, (x,   y,   fill,          bar_height))
