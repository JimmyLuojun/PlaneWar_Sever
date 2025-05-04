import pygame
# --- Use relative imports for modules within the 'game' package ---
from .settings import *  # Import constants
from .bullet import Bullet  # Import Bullet class

class Player(pygame.sprite.Sprite):
    """
    Represents the player's spaceship, handling movement, shooting,
    power-ups, bombs, and shield visuals.
    """
    def __init__(
        self,
        player_img,
        shoot_sound,
        shield_up_sound,
        shield_down_sound,
        powerup_sound,
        bomb_sound,
    ):
        super().__init__()
        # Ensure valid image
        if not isinstance(player_img, pygame.Surface):
            raise ValueError("Invalid player image provided to Player init.")
        self.image_orig = player_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))

        # Score and bombs
        self.score = 0
        self.bomb_count = PLAYER_STARTING_BOMBS

        # Shooting
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_delay = PLAYER_SHOOT_DELAY

        # Power-ups and shield
        self.powerup_type = None
        self.powerup_end_time = 0
        self.shield_active = False
        self.shield_end_time = 0

        # Shield visuals
        self.shield_visual_radius = max(self.rect.width, self.rect.height) // 2 + 8
        try:
            self.shield_visual_color = SHIELD_VISUAL_COLOR
        except NameError:
            self.shield_visual_color = (0, 255, 255, 100)

        # Sounds
        self.shoot_sound = shoot_sound
        self.shield_up_sound = shield_up_sound
        self.shield_down_sound = shield_down_sound
        self.powerup_sound = powerup_sound
        self.bomb_sound = bomb_sound

        # Velocity tracking (for boss intercept)
        self.velocity = pygame.math.Vector2(0, 0)
        self._last_center = pygame.math.Vector2(self.rect.center)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            bullets = []
            if self.powerup_type == 'double_shot':
                left = Bullet(self.rect.centerx - 10, self.rect.top)
                right = Bullet(self.rect.centerx + 10, self.rect.top)
                bullets.extend([left, right])
            else:
                bullets.append(Bullet(self.rect.centerx, self.rect.top))

            if self.shoot_sound:
                try:
                    self.shoot_sound.play()
                except pygame.error:
                    pass
            return bullets
        return []

    def update(self):
        now = pygame.time.get_ticks()

        # Power-up expiration
        if self.powerup_type == 'double_shot' and now > self.powerup_end_time:
            self.powerup_type = None
        if self.shield_active and now > self.shield_end_time:
            self.shield_active = False
            if self.shield_down_sound:
                try:
                    self.shield_down_sound.play()
                except pygame.error:
                    pass

        # Movement via mouse
        old_center = pygame.math.Vector2(self.rect.center)
        mouse_pos = pygame.mouse.get_pos()
        self.rect.center = mouse_pos
        # Boundaries
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
        # Update velocity
        new_center = pygame.math.Vector2(self.rect.center)
        self.velocity = new_center - old_center
        self._last_center = new_center

        # Reset image
        self.image = self.image_orig.copy()

    def activate_powerup(self, type):
        now = pygame.time.get_ticks()
        if type == 'double_shot':
            self.powerup_type = type
            self.powerup_end_time = now + POWERUP_DURATION
        elif type == 'shield':
            self.shield_active = True
            self.shield_end_time = now + SHIELD_DURATION
            if self.shield_up_sound:
                try:
                    self.shield_up_sound.play()
                except pygame.error:
                    pass
        elif type == 'bomb':
            self.bomb_count += 1

        if self.powerup_sound:
            try:
                self.powerup_sound.play()
            except pygame.error:
                pass

    def use_bomb(self, enemies_group, enemy_bullets_group):
        if self.bomb_count > 0:
            self.bomb_count -= 1
            if self.bomb_sound:
                try:
                    self.bomb_sound.play()
                except pygame.error:
                    pass
            killed = 0
            for e in enemies_group.sprites():
                e.kill(); killed += 1
            for b in enemy_bullets_group.sprites():
                b.kill()
            return killed
        return 0

    def draw_shield(self, surface):
        if not self.shield_active:
            return
        radius = self.shield_visual_radius
        diameter = max(1, radius * 2)
        shield_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        draw_r = max(1, radius)
        pygame.draw.circle(shield_surf, self.shield_visual_color, (radius, radius), draw_r)
        rect = shield_surf.get_rect(center=self.rect.center)
        surface.blit(shield_surf, rect)
