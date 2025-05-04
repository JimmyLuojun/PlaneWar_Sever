# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/player.py
import pygame
# --- Use relative imports for modules within the 'game' package ---
from .settings import * # Import constants
from .bullet import Bullet # Import Bullet class

# PLAYER_STARTING_BOMBS is already imported via 'from .settings import *'

class Player(pygame.sprite.Sprite):
    """
    Represents the player's spaceship, handling movement, shooting,
    power-ups, bombs, and shield visuals.
    """
    def __init__(self, player_img, shoot_sound, shield_up_sound, shield_down_sound, powerup_sound, bomb_sound):
        """
        Initializes the Player sprite.

        Args:
            player_img (pygame.Surface): The image surface for the player.
            shoot_sound (pygame.mixer.Sound | None): Sound effect for shooting.
            shield_up_sound (pygame.mixer.Sound | None): Sound effect for shield activation.
            shield_down_sound (pygame.mixer.Sound | None): Sound effect for shield deactivation.
            powerup_sound (pygame.mixer.Sound | None): Sound effect for picking up any power-up.
            bomb_sound (pygame.mixer.Sound | None): Sound effect for using a bomb.
        """
        super().__init__()
        # Keep original image for reference (e.g., if rotation was added later)
        # Ensure player_img is valid before proceeding
        if not isinstance(player_img, pygame.Surface):
             raise ValueError("Invalid player image provided to Player init.")
        self.image_orig = player_img
        self.image = self.image_orig.copy() # Current image, potentially modified by shield
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 20)

        # Game state related to player
        self.score = 0 # Score managed by the player instance
        # Use constant from settings for starting bombs
        self.bomb_count = PLAYER_STARTING_BOMBS

        # Timing for shooting delay
        self.last_shot_time = pygame.time.get_ticks()
        # Use constant from settings for shoot delay
        self.shoot_delay = PLAYER_SHOOT_DELAY

        # Power-up state
        self.powerup_type = None # e.g., 'double_shot'
        self.powerup_end_time = 0 # Time when the current power-up expires
        self.shield_active = False
        self.shield_end_time = 0 # Time when the shield expires

        # Shield Visuals Configuration (can be adjusted in settings)
        self.shield_visual_radius = max(self.rect.width, self.rect.height) // 2 + 8
        # Ensure SHIELD_VISUAL_COLOR is defined in settings (e.g., (*CYAN, 100))
        try:
            # SHIELD_VISUAL_COLOR comes from 'from .settings import *'
            self.shield_visual_color = SHIELD_VISUAL_COLOR
        except NameError:
            print("Warning: SHIELD_VISUAL_COLOR not found in settings, using fallback.")
            self.shield_visual_color = (0, 255, 255, 100) # Fallback: Cyan with alpha

        # Store sound references
        self.shoot_sound = shoot_sound
        self.shield_up_sound = shield_up_sound
        self.shield_down_sound = shield_down_sound
        self.powerup_sound = powerup_sound
        self.bomb_sound = bomb_sound

    def shoot(self):
        """
        Handles player shooting logic.
        Creates and returns a list of new bullet sprites based on power-up status and shoot delay.
        Returns an empty list if shooting is not allowed (e.g., due to delay).
        """
        now = pygame.time.get_ticks()
        # Check if enough time has passed since the last shot
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            new_bullets = [] # List to hold newly created bullets

            # Create bullets based on the current power-up
            if self.powerup_type == 'double_shot':
                # Create two bullets slightly offset from the center
                bullet_left = Bullet(self.rect.centerx - 10, self.rect.top)
                bullet_right = Bullet(self.rect.centerx + 10, self.rect.top)
                new_bullets.extend([bullet_left, bullet_right])
            else:
                # Standard single shot from the center
                bullet = Bullet(self.rect.centerx, self.rect.top)
                new_bullets.append(bullet)

            # Play shoot sound if available
            if self.shoot_sound:
                try:
                    self.shoot_sound.play()
                except pygame.error as e:
                    print(f"Warning: Could not play shoot sound: {e}")

            return new_bullets # Return the list of new bullets

        return [] # Return empty list if shoot delay hasn't passed

    def update(self):
        """
        Updates player state each frame:
        - Checks and handles power-up/shield timers.
        - Updates position based on mouse movement.
        - Keeps player within screen boundaries.
        """
        now = pygame.time.get_ticks()

        # Check power-up timers and deactivate if expired
        if self.powerup_type == 'double_shot' and now > self.powerup_end_time:
            print("Double shot效果结束") # Double shot effect ended
            self.powerup_type = None
        if self.shield_active and now > self.shield_end_time:
            print("护盾效果结束") # Shield effect ended
            self.shield_active = False
            # Play shield down sound if available
            if self.shield_down_sound:
                 try:
                     self.shield_down_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play shield down sound: {e}")

        # --- Player Movement ---
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        # Set player center to mouse position
        self.rect.center = mouse_pos # Simpler way to set center

        # --- Screen Boundary Check ---
        # Prevent player from moving off-screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # Reset image to original each frame (shield is drawn separately now)
        self.image = self.image_orig.copy()


    def activate_powerup(self, type):
        """
        Activates the effect of a collected power-up based on its type.

        Args:
            type (str): The type of power-up collected (e.g., 'double_shot', 'shield', 'bomb').
        """
        print(f"激活道具: {type}") # Activated power-up
        now = pygame.time.get_ticks()

        # Apply effect based on type
        if type == 'double_shot':
            self.powerup_type = type
            # Set duration using constant from settings
            self.powerup_end_time = now + POWERUP_DURATION
        elif type == 'shield':
            self.shield_active = True
            # Set duration using constant from settings
            self.shield_end_time = now + SHIELD_DURATION
            # Play shield up sound if available
            if self.shield_up_sound:
                 try:
                     self.shield_up_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play shield up sound: {e}")
        elif type == 'bomb':
            self.bomb_count += 1 # Increment bomb count
            print(f"获得炸弹! 当前数量: {self.bomb_count}") # Obtained bomb! Current count: ...

        # Play generic power-up pickup sound if available
        if self.powerup_sound:
            try:
                self.powerup_sound.play()
            except pygame.error as e:
                print(f"Warning: Could not play powerup sound: {e}")

    # *** REFINED use_bomb method ***
    def use_bomb(self, enemies_group, enemy_bullets_group): # <-- Accept BOTH groups
        """
        Uses one bomb if available. Destroys all enemies in enemies_group
        and all enemy bullets in enemy_bullets_group.
        Decrements bomb count and plays sound effect.

        Args:
            enemies_group (pygame.sprite.Group): Group containing active enemies.
            enemy_bullets_group (pygame.sprite.Group): Group containing active enemy bullets.

        Returns:
            int: The number of enemies killed by the bomb (for scoring).
        """
        if self.bomb_count > 0:
            self.bomb_count -= 1
            print(f"使用炸弹! 剩余: {self.bomb_count}") # Used bomb! Remaining: ...

            # Play bomb sound
            if self.bomb_sound:
                 try:
                     self.bomb_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play bomb sound: {e}")

            killed_enemy_count = 0
            # Kill all regular enemies currently on screen
            # Iterating over a copy (.sprites()) is safer if killing modifies the group
            for enemy in enemies_group.sprites():
                 enemy.kill() # Removes sprite from all groups it belongs to
                 killed_enemy_count += 1

            # Kill all enemy bullets currently on screen
            for bullet in enemy_bullets_group.sprites():
                bullet.kill()

            print(f"炸弹清除了 {killed_enemy_count} 个敌人 和 所有敌方子弹.") # Bomb cleared X enemies and all enemy bullets.
            return killed_enemy_count # Return count for scoring in main game loop
        else:
            print("没有炸弹可用!") # No bombs available!
            return 0 # Return 0 if no bomb was used

    # *** ADDED draw_shield method ***
    def draw_shield(self, surface):
        """
        Draws a visual representation of the shield around the player
        onto the provided surface, if the shield is active.

        Args:
            surface (pygame.Surface): The surface to draw the shield onto (e.g., the screen).
        """
        if self.shield_active:
            try:
                # Create a temporary surface for the shield circle with alpha transparency
                # Make surface slightly larger than radius to avoid clipping
                radius = self.shield_visual_radius
                diameter = radius * 2
                # Ensure diameter is at least 1 to avoid Surface error
                if diameter < 1: diameter = 1
                shield_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

                # Draw the shield circle onto the temporary surface
                # Use color defined in settings (e.g., (*CYAN, 100) for semi-transparent cyan)
                # Ensure radius is valid for drawing
                draw_radius = max(1, radius) # Use radius of at least 1 pixel
                pygame.draw.circle(shield_surf, self.shield_visual_color, (radius, radius), draw_radius) # Draw filled circle

                # Blit the shield surface onto the main screen, centered on the player
                shield_rect = shield_surf.get_rect(center=self.rect.center)
                surface.blit(shield_surf, shield_rect)
            except NameError: # Catch if SHIELD_VISUAL_COLOR is not defined
                 print("Warning: SHIELD_VISUAL_COLOR not defined in settings. Cannot draw shield.")
            except Exception as e:
                 print(f"Error drawing shield: {e}")
