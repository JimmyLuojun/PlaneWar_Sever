"""Bullet classes for the PlaneWar game.

Defines bullet sprite classes for both player and enemy projectiles.
Player bullets move straight upward, while enemy bullets support
directional movement using vector-based velocity.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
from typing import Optional, Tuple

# Third-party
import pygame
from pygame.math import Vector2

# Local
from ..infrastructure.settings import (
    BULLET_WIDTH,
    BULLET_HEIGHT,
    BULLET_SPEED,
    ENEMY_BULLET_WIDTH,
    ENEMY_BULLET_HEIGHT,
    ENEMY_BULLET_SPEED_Y,
    ENEMY_BULLET_COLOR,
    YELLOW,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


# ============================================================================
# Type Definitions
# ============================================================================

Direction = Vector2
Position = Tuple[float, float]


# ============================================================================
# Constants
# ============================================================================

# Default direction for enemy bullets (straight down)
DEFAULT_ENEMY_BULLET_DIRECTION: Direction = Vector2(0, 1)


# ============================================================================
# Concrete Classes
# ============================================================================


class Bullet(pygame.sprite.Sprite):
    """Player bullet sprite that moves straight upward.

    Bullets are fired from the player's position and move upward at a
    constant speed. They are automatically removed when they leave the
    screen at the top.

    Attributes:
        image: The visual representation (yellow rectangle)
        rect: Position and collision rectangle
        speedy: Vertical movement speed (negative = upward)

    Example:
        >>> bullet = Bullet(player.rect.centerx, player.rect.top)
        >>> all_sprites.add(bullet)
        >>> player_bullets.add(bullet)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self, x: float, y: float):
        """Initialize a player bullet.

        Args:
            x: Horizontal center position
            y: Vertical center position
        """
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -BULLET_SPEED  # Negative for upward movement

    # ========================================================================
    # Public Methods
    # ========================================================================

    def update(self) -> None:
        """Update bullet position and remove if off-screen.

        Called each frame by sprite group's update() method.
        Moves the bullet upward and removes it when it exits the top of screen.
        """
        self.rect.y += self.speedy

        # Remove bullet when it exits the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    """Enemy bullet sprite with directional movement support.

    Enemy bullets can move in any direction, not just straight down.
    Uses Vector2 for precise floating-point position tracking and
    supports both straight and angled shots.

    Attributes:
        image: The visual representation (red rectangle)
        rect: Position and collision rectangle
        pos: High-precision floating-point position (Vector2)
        speed: Base movement speed (pixels per frame)
        velocity: Direction and speed combined (Vector2)

    Example:
        >>> # Straight down
        >>> bullet1 = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)

        >>> # Angled shot toward player
        >>> direction = (player_pos - enemy_pos).normalize()
        >>> bullet2 = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom, direction)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self, x: float, y: float, direction: Optional[Direction] = None):
        """Initialize an enemy bullet.

        Args:
            x: Horizontal center position
            y: Top position
            direction: Normalized direction vector, or None for straight down
        """
        super().__init__()
        self.image = pygame.Surface((ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))
        self.image.fill(ENEMY_BULLET_COLOR)
        self.rect = self.image.get_rect(centerx=x, top=y)

        # Use Vector2 for floating-point precision movement
        self.pos: Vector2 = Vector2(self.rect.center)
        self.speed: float = ENEMY_BULLET_SPEED_Y

        # Set velocity based on direction
        if direction is None:
            # Default: straight down
            self.velocity: Vector2 = DEFAULT_ENEMY_BULLET_DIRECTION * self.speed
        else:
            # Angled shot (assumes direction is normalized)
            self.velocity = direction * self.speed

    # ========================================================================
    # Public Methods
    # ========================================================================

    def update(self) -> None:
        """Update bullet position and remove if off-screen.

        Called each frame by sprite group's update() method.
        Moves the bullet based on its velocity vector and removes it
        when it exits the screen boundaries.
        """
        # Update position using floating-point arithmetic
        self.pos += self.velocity

        # Sync rect position with floating-point position
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Remove bullet if it exits screen boundaries
        if self._is_off_screen():
            self.kill()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _is_off_screen(self) -> bool:
        """Check if bullet has exited the screen boundaries.

        Returns:
            True if bullet is completely off-screen, False otherwise
        """
        # Check horizontal boundaries
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            return True

        # Check vertical boundary (bottom)
        if self.rect.top > SCREEN_HEIGHT:
            return True

        return False
