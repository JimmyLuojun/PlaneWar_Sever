import pygame
import random
from pygame.math import Vector2
from .settings import *
from .bullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    """Basic enemy that drifts down and bounces horizontally."""
    def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        min_y, max_y = speed_y_range or (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        min_x, max_x = speed_x_range or (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X)

        min_y = max(1, min_y)
        max_y = max(min_y, max_y)
        self.speedy = random.randint(min_y, max_y)

        possible_speedx = [i for i in range(min_x, max_x + 1) if i != 0]
        if not possible_speedx:
            possible_speedx = [x for x in (max_x, min_x, 1) if x != 0]
        self.speedx = random.choice(possible_speedx)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Bounce left/right
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx
            self.rect.right = min(self.rect.right, SCREEN_WIDTH)
            self.rect.left = max(self.rect.left, 0)

        # Kill if off bottom—guard against non-numeric rect.top
        try:
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()
        except TypeError:
            pass


class EnemyBoss(pygame.sprite.Sprite):
    """Big boss: enters, patrols, shoots (optionally targets player), takes damage."""
    def __init__(self, boss_img, shoot_sound, all_sprites_group, enemy_bullets_group,
                 target_player=False, player_ref=None):
        super().__init__()
        self.image_orig = boss_img
        self.image = boss_img.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = -20

        self.entry_speedy = BOSS_SPEED_Y
        self.entry_y = BOSS_ENTRY_Y
        self.speedx = BOSS_SPEED_X
        self.entered = False

        self.max_health = BOSS_MAX_HEALTH
        self.health = self.max_health
        self.shoot_delay = BOSS_SHOOT_DELAY
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_sound = shoot_sound

        self.all_sprites = all_sprites_group
        self.enemy_bullets = enemy_bullets_group

        self.target_player = target_player
        self.player_ref = player_ref if self.target_player else None

        self.all_sprites.add(self)

    def update(self):
        now = pygame.time.get_ticks()

        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.rect.centery = self.entry_y
                self.entered = True
                self.last_shot_time = now
        else:
            self.rect.x += self.speedx
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                self.speedx = -self.speedx
                self.rect.right = min(self.rect.right, SCREEN_WIDTH)
                self.rect.left = max(self.rect.left, 0)

            if now - self.last_shot_time > self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def shoot(self):
        shoot_pos = self.rect.midbottom
        direction = None

        if self.target_player and self.player_ref and self.player_ref.alive():
            try:
                player_pos = Vector2(self.player_ref.rect.center)
                bullet_start = Vector2(shoot_pos)
                direction = (player_pos - bullet_start).normalize()
            except ValueError:
                direction = Vector2(0, 1)

        bullet = EnemyBullet(shoot_pos[0], shoot_pos[1], direction=direction)
        self.all_sprites.add(bullet)
        self.enemy_bullets.add(bullet)

        if self.shoot_sound:
            try:
                self.shoot_sound.play()
            except pygame.error as e:
                print(f"Warning: Could not play boss shoot sound: {e}")

    def take_damage(self, damage):
        self.health -= damage

    def draw_health_bar(self, surf):
        if self.health <= 0:
            return
        bar_length = 100
        bar_height = 10
        x = self.rect.centerx - bar_length // 2
        y = self.rect.top - bar_height - 5

        fill = max(0, int(self.health / self.max_health * bar_length))
        border = pygame.Rect(x - 1, y - 1, bar_length + 2, bar_height + 2)
        bg_rect = pygame.Rect(x, y, bar_length, bar_height)
        fg_rect = pygame.Rect(x, y, fill, bar_height)

        pygame.draw.rect(surf, RED, bg_rect)
        pygame.draw.rect(surf, GREEN, fg_rect)
        pygame.draw.rect(surf, WHITE, border, 2)
