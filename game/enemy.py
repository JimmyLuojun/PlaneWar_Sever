"""
Enemy sprite module for the PlaneWar game.

Defines enemy classes including basic drifting enemies and boss enemies with
predictive aiming capabilities. Contains the intercept trajectory algorithm
for intelligent enemy shooting. Applies the OOP Standard Order within the module.
"""

# ==============================================================================
# Imports (dependencies)
# ==============================================================================
import math
import random

import pygame
from pygame.math import Vector2

from .settings import *
from .bullet import EnemyBullet


# ==============================================================================
# Constants
# ==============================================================================
# Predictive aiming epsilon for floating point comparison
INTERCEPT_EPSILON = 1e-6


# ==============================================================================
# Helper Functions
# ==============================================================================
def compute_intercept_direction(shoot_pos, target_pos, target_vel, bullet_speed):
    """
    Compute the firing direction to intercept a moving target.

    Solves the quadratic equation: a*t^2 + b*t + c = 0
    where:
        a = |v_target|^2 - v_bullet^2
        b = 2 * r·v_target
        c = |r|^2
        r = target_pos - shoot_pos

    Takes the smallest positive root t, then computes the intercept point
    as (target_pos + v_target * t) and returns the normalized direction vector.

    Args:
        shoot_pos (Vector2): Position from which the shot is fired.
        target_pos (Vector2): Current position of the target.
        target_vel (Vector2): Velocity vector of the target.
        bullet_speed (float): Speed of the bullet.

    Returns:
        Vector2: Normalized direction vector for the bullet to intercept target.
                 Falls back to aiming at current position if no valid solution.
    """
    r = target_pos - shoot_pos
    a = target_vel.dot(target_vel) - bullet_speed**2
    b = 2 * r.dot(target_vel)
    c = r.dot(r)

    discriminant = b * b - 4 * a * c

    # No real solution or degenerate case (a ≈ 0)
    if discriminant < 0 or abs(a) < INTERCEPT_EPSILON:
        # Fall back to aiming at current target position
        return (r if r.length_squared() > 0 else Vector2(0, 1)).normalize()

    sqrt_discriminant = math.sqrt(discriminant)
    t1 = (-b + sqrt_discriminant) / (2 * a)
    t2 = (-b - sqrt_discriminant) / (2 * a)

    # Choose the smallest positive time value
    positive_times = [t for t in (t1, t2) if t > 0]
    t = min(positive_times) if positive_times else max(t1, t2)

    if t <= 0:
        # No future intercept possible, aim at current position
        return (r if r.length_squared() > 0 else Vector2(0, 1)).normalize()

    # Compute intercept point and return normalized direction
    intercept = target_pos + target_vel * t - shoot_pos
    return intercept.normalize()


# ==============================================================================
# Concrete Classes
# ==============================================================================


class Enemy(pygame.sprite.Sprite):
    """
    Basic enemy sprite that drifts downward and bounces horizontally.

    This enemy moves vertically down the screen while bouncing off the left
    and right edges. It self-destructs when leaving the bottom of the screen.
    """

    def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
        """
        Initialize a basic enemy.

        Args:
            enemy_img (pygame.Surface): Image for the enemy sprite.
            speed_y_range (tuple, optional): (min, max) vertical speed range.
            speed_x_range (tuple, optional): (min, max) horizontal speed range.
        """
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()

        # Random initial position (spawn above screen)
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # Random speed (vertical and horizontal)
        min_y, max_y = speed_y_range or (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        min_x, max_x = speed_x_range or (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X)
        min_y, max_y = max(1, min_y), max(min_y, max_y)
        self.speedy = random.randint(min_y, max_y)

        # Ensure non-zero horizontal speed
        xs = [i for i in range(min_x, max_x + 1) if i != 0] or [1]
        self.speedx = random.choice(xs)

    def update(self):
        """Update enemy position, handle bouncing and cleanup."""
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Bounce off left and right edges
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx *= -1

        # Remove if off bottom of screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class EnemyBoss(pygame.sprite.Sprite):
    """
    Boss enemy with entrance sequence, patrol behavior, predictive shooting,
    and health system.

    The boss enters from the top, patrols horizontally, and can use intelligent
    predictive aiming to shoot at the player's projected position.
    """

    def __init__(
        self,
        boss_img,
        shoot_sound,
        all_sprites_group,
        enemy_bullets_group,
        target_player=False,
        player_ref=None,
        fire_rate_multiplier=1.0,
        shot_count: int = 1,
        shot_spread_degrees: float = 0.0,
    ):
        """
        Initialize the boss enemy.

        Args:
            boss_img (pygame.Surface): Image for the boss sprite.
            shoot_sound (pygame.mixer.Sound): Sound effect for boss shooting.
            all_sprites_group (pygame.sprite.Group): Group for adding bullets.
            enemy_bullets_group (pygame.sprite.Group): Group for tracking bullets.
            target_player (bool): Enable predictive aiming at player.
            player_ref (Player, optional): Reference to player object for targeting.
            fire_rate_multiplier (float): Multiplier for boss fire rate (default 1.0).
                                          Values > 1.0 make boss shoot faster.
        """
        super().__init__()

        # Basic sprite attributes
        self.image = boss_img.copy()
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=-20)
        self.entry_speedy = BOSS_SPEED_Y
        self.entry_y = BOSS_ENTRY_Y
        self.speedx = BOSS_SPEED_X
        self.entered = False

        # Health and shooting
        self.health = BOSS_MAX_HEALTH
        # Apply fire rate multiplier (higher multiplier = faster shooting = lower delay)
        base_delay = BOSS_SHOOT_DELAY
        self.shoot_delay = int(base_delay / max(0.1, fire_rate_multiplier))
        self.last_shot_time = 0
        self.shoot_sound = shoot_sound

        # Sprite groups
        self.all_sprites = all_sprites_group
        self.enemy_bullets = enemy_bullets_group

        # Targeting system
        self.target_player = target_player
        self.player_ref = player_ref if target_player else None

        # Shooting pattern
        try:
            self.shot_count = max(1, int(shot_count))
        except Exception:
            self.shot_count = 1
        try:
            self.shot_spread_degrees = float(shot_spread_degrees)
        except Exception:
            self.shot_spread_degrees = 0.0

        self.all_sprites.add(self)

    def update(self):
        """Update boss behavior: entrance sequence, patrol, and shooting."""
        now = pygame.time.get_ticks()

        # Entrance sequence
        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.entered = True
                self.last_shot_time = now
        else:
            # Patrol horizontally
            self.rect.x += self.speedx
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.speedx *= -1

            # Shoot periodically
            if now - self.last_shot_time >= self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def shoot(self):
        """
        Fire a bullet, using predictive aiming if targeting is enabled.

        If target_player is True and player is alive, uses the intercept
        algorithm to predict player position. Otherwise, shoots straight down.
        """
        shoot_pos = Vector2(self.rect.midbottom)
        direction = Vector2(0, 1)  # Default: shoot straight down

        # Use predictive aiming if enabled and player is alive
        if self.target_player and self.player_ref and self.player_ref.alive():
            target_pos = Vector2(self.player_ref.rect.center)
            target_vel = getattr(self.player_ref, "velocity", Vector2(0, 0))
            direction = compute_intercept_direction(
                shoot_pos, target_pos, target_vel, ENEMY_BULLET_SPEED_Y
            )

        # Create and add bullet
        # Create one or multiple bullets (spread around base direction)
        if self.shot_count <= 1 or abs(self.shot_spread_degrees) < 1e-3:
            bullet = EnemyBullet(shoot_pos.x, shoot_pos.y, direction=direction)
            self.all_sprites.add(bullet)
            self.enemy_bullets.add(bullet)
        else:
            # Centered spread: e.g., 3 with 20deg -> angles [-20, 0, 20]
            total = self.shot_count
            if total % 2 == 1:
                # odd count: include 0 and symmetric pairs
                mids = [0]
                pairs = (total - 1) // 2
                for i in range(1, pairs + 1):
                    angle = self.shot_spread_degrees * i
                    mids.extend([-angle, angle])
                angles = mids
            else:
                # even count: symmetric pairs around 0, offset by half-step
                pairs = total // 2
                angles = []
                for i in range(1, pairs + 1):
                    angle = self.shot_spread_degrees * (i - 0.5)
                    angles.extend([-angle, angle])
            for ang in angles:
                dir_vec = direction.rotate(ang)
                b = EnemyBullet(shoot_pos.x, shoot_pos.y, direction=dir_vec)
                self.all_sprites.add(b)
                self.enemy_bullets.add(b)

        # Play sound effect
        if self.shoot_sound:
            try:
                self.shoot_sound.play()
            except pygame.error:
                pass

    def draw_health_bar(self, surf):
        """
        Draw the boss health bar above the sprite.

        Args:
            surf (pygame.Surface): Surface to draw the health bar on.
        """
        if self.health <= 0:
            return

        bar_len, bar_h = 100, 10
        x = self.rect.centerx - bar_len // 2
        y = self.rect.top - bar_h - 5
        fill = int(self.health / BOSS_MAX_HEALTH * bar_len)

        # Draw background (red), fill (green), border (white)
        pygame.draw.rect(surf, RED, (x, y, bar_len, bar_h))
        pygame.draw.rect(surf, GREEN, (x, y, fill, bar_h))
        pygame.draw.rect(surf, WHITE, (x - 1, y - 1, bar_len + 2, bar_h + 2), 2)
