# /Users/junluo/Desktop/PlaneWar/enemy.py
import pygame
import random
from settings import * # Import settings for defaults
from bullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    # --- MODIFIED __init__ ---
    def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # --- Use provided speed ranges or fall back to defaults from settings.py ---
        min_y, max_y = speed_y_range if speed_y_range is not None else (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        min_x, max_x = speed_x_range if speed_x_range is not None else (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X)

        # Ensure speeds are within reasonable bounds if provided ranges are invalid
        min_y = max(1, min_y) # Min speed at least 1? Or adjust as needed
        max_y = max(min_y, max_y)

        self.speedy = random.randint(min_y, max_y)

        # Ensure speedx is not zero and within valid range
        possible_speedx = [i for i in range(min_x, max_x + 1) if i != 0]
        if not possible_speedx:
            # Fallback if range excludes non-zero (e.g., [-0, 0] or [-1, 1] fails)
            if max_x != 0: possible_speedx.append(max_x)
            elif min_x != 0: possible_speedx.append(min_x)
            else: possible_speedx.append(1) # Absolute fallback

        self.speedx = random.choice(possible_speedx)


    def update(self):
        """ Move the enemy down and bounce horizontally. """
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Bounce off the sides
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx
            # Clamp position to prevent getting stuck off-screen
            if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
            if self.rect.left < 0: self.rect.left = 0

        # Kill if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT + 10: # Add a small buffer
            self.kill()


class EnemyBoss(pygame.sprite.Sprite):
    """ Represents the Boss enemy. """
    # --- MODIFIED: Accept sprite groups, use settings constants ---
    def __init__(self, boss_img, shoot_sound, all_sprites_group, enemy_bullets_group):
        super().__init__()
        self.image_orig = boss_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = -20 # Start above screen

        # Use constants from settings
        self.entry_speedy = 1 # Can be made a setting if needed BOSS_ENTRY_SPEED_Y
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

    def update(self):
        """ Handles Boss entry, movement, and shooting checks. """
        now = pygame.time.get_ticks()

        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.rect.centery = self.entry_y # Snap to final Y
                self.entered = True
                self.last_shot_time = now # Start shooting timer only after entry
                print("Boss entry complete. Engaging!")
        else:
            # Horizontal movement
            self.rect.x += self.speedx
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                self.speedx = -self.speedx
                # Clamp position after bounce
                self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

            # Shooting Logic
            if now - self.last_shot_time > self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def shoot(self):
        """ Creates enemy bullet(s) and adds them to groups. """
        # print("Boss shooting!") # Reduced frequency log
        bullet_spawn_x = self.rect.centerx
        bullet_spawn_y = self.rect.bottom

        enemy_bullet = EnemyBullet(bullet_spawn_x, bullet_spawn_y)
        self.all_sprites.add(enemy_bullet)
        self.enemy_bullets.add(enemy_bullet)

        if self.shoot_sound:
             try:
                 self.shoot_sound.play()
             except pygame.error as e:
                 print(f"Warning: Could not play boss shoot sound: {e}")


    def draw_health_bar(self, surf):
        """ Draws the boss's health bar above it onto the provided surface. """
        if self.health > 0:
            bar_length = 100
            bar_height = 10
            fill_percent = max(0, self.health / self.max_health)
            fill_length = int(bar_length * fill_percent)
            outline_rect = pygame.Rect(self.rect.centerx - bar_length // 2,
                                       self.rect.top - bar_height - 5, # Padding above
                                       bar_length, bar_height)
            fill_rect = pygame.Rect(outline_rect.left, outline_rect.top,
                                    fill_length, bar_height)
            # Draw background (red), fill (green), and border (white)
            pygame.draw.rect(surf, RED, outline_rect)
            pygame.draw.rect(surf, GREEN, fill_rect)
            pygame.draw.rect(surf, WHITE, outline_rect, 2) # Border thickness 2