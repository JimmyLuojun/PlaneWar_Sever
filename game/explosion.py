"""Explosion visual effects for the PlaneWar game.

Defines the Explosion sprite class for creating visual explosion effects
when enemies, bosses, or bombs are destroyed. Explosions have timed durations
and animated expansion effects.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
from typing import Dict, Tuple, Final, Any

# Third-party
import pygame

# Local
from .settings import (
    EXPLOSION_TYPE_SMALL,
    EXPLOSION_TYPE_MEDIUM,
    EXPLOSION_TYPE_LARGE,
    EXPLOSION_TYPE_BOMB,
    EXPLOSION_SMALL_SIZE,
    EXPLOSION_MEDIUM_SIZE,
    EXPLOSION_LARGE_SIZE,
    EXPLOSION_BOMB_SIZE,
    EXPLOSION_SMALL_COLOR,
    EXPLOSION_MEDIUM_COLOR,
    EXPLOSION_LARGE_COLOR,
    EXPLOSION_BOMB_COLOR,
    EXPLOSION_DURATION,
    EXPLOSION_FRAME_COUNT,
)


# ============================================================================
# Type Definitions
# ============================================================================

Color = Tuple[int, int, int]
ExplosionType = str


# ============================================================================
# Constants
# ============================================================================

# Mapping explosion types to their properties
EXPLOSION_SIZES: Final[Dict[str, int]] = {
    EXPLOSION_TYPE_SMALL: EXPLOSION_SMALL_SIZE,
    EXPLOSION_TYPE_MEDIUM: EXPLOSION_MEDIUM_SIZE,
    EXPLOSION_TYPE_LARGE: EXPLOSION_LARGE_SIZE,
    EXPLOSION_TYPE_BOMB: EXPLOSION_BOMB_SIZE,
}

EXPLOSION_COLORS: Final[Dict[str, Color]] = {
    EXPLOSION_TYPE_SMALL: EXPLOSION_SMALL_COLOR,
    EXPLOSION_TYPE_MEDIUM: EXPLOSION_MEDIUM_COLOR,
    EXPLOSION_TYPE_LARGE: EXPLOSION_LARGE_COLOR,
    EXPLOSION_TYPE_BOMB: EXPLOSION_BOMB_COLOR,
}


# ============================================================================
# Concrete Classes
# ============================================================================


class Explosion(pygame.sprite.Sprite):
    """Visual explosion effect sprite with timed duration and animation.

    Creates a circular explosion effect that expands over time and
    automatically removes itself after the duration expires. Supports
    different explosion types (small, medium, large, bomb) with varying
    sizes and colors.

    Attributes:
        image: The visual representation (circular explosion)
        rect: Position and collision rectangle
        explosion_type: Type of explosion ('small', 'medium', 'large', 'bomb')
        start_time: Timestamp when explosion was created
        max_size: Final size of the explosion
        color: RGB color of the explosion
        current_frame: Current animation frame (0 to EXPLOSION_FRAME_COUNT-1)

    Example:
        >>> explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 'small')
        >>> all_sprites.add(explosion)
        >>> explosions.add(explosion)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(
        self, x: float, y: float, explosion_type: ExplosionType = EXPLOSION_TYPE_SMALL
    ):
        """Initialize an explosion effect.

        Args:
            x: Horizontal center position
            y: Vertical center position
            explosion_type: Type of explosion (default: 'small')
        """
        super().__init__()

        self.explosion_type: ExplosionType = explosion_type
        self.start_time: int = pygame.time.get_ticks()
        self.max_size: int = EXPLOSION_SIZES.get(explosion_type, EXPLOSION_SMALL_SIZE)
        self.color: Color = EXPLOSION_COLORS.get(explosion_type, EXPLOSION_SMALL_COLOR)
        self.current_frame: int = 0

        # Start with initial size (will expand in update)
        initial_size = max(5, self.max_size // EXPLOSION_FRAME_COUNT)
        self.image: pygame.Surface = self._create_explosion_surface(initial_size)
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.center_x: float = x
        self.center_y: float = y

    # ========================================================================
    # Public Methods
    # ========================================================================

    def update(self) -> None:
        """Update explosion animation and remove if duration expired.

        Called each frame by sprite group's update() method.
        Animates the explosion by expanding its size frame by frame,
        and removes the sprite when the duration has elapsed.
        """
        now = pygame.time.get_ticks()
        elapsed_time = now - self.start_time

        # Check if explosion has expired
        if elapsed_time >= EXPLOSION_DURATION:
            self.kill()
            return

        # Calculate which animation frame we're on
        frame_duration = EXPLOSION_DURATION // EXPLOSION_FRAME_COUNT
        new_frame = min(elapsed_time // frame_duration, EXPLOSION_FRAME_COUNT - 1)

        # Update visual if frame changed
        if new_frame != self.current_frame:
            self.current_frame = new_frame
            self._update_explosion_visual()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _update_explosion_visual(self) -> None:
        """Update the explosion visual based on current animation frame."""
        # Calculate size for current frame (expands from small to max)
        size_step = self.max_size / EXPLOSION_FRAME_COUNT
        current_size = int((self.current_frame + 1) * size_step)

        # Create new surface with updated size
        self.image = self._create_explosion_surface(current_size)
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))

    def _create_explosion_surface(self, size: int) -> pygame.Surface:
        """Create a circular explosion surface with given size.

        Args:
            size: Diameter of the explosion circle

        Returns:
            pygame.Surface with circular explosion drawn on it
        """
        # Create surface with alpha channel for transparency
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Draw filled circle
        radius = size // 2
        pygame.draw.circle(surface, self.color, (radius, radius), radius)

        # Add a brighter inner circle for more visual interest
        if radius > 5:
            inner_radius = max(1, radius // 3)
            # Brighten the color for inner circle
            bright_color = tuple(min(255, c + 50) for c in self.color)
            pygame.draw.circle(surface, bright_color, (radius, radius), inner_radius)

        return surface


# ============================================================================
# Helper Functions
# ============================================================================


def create_explosion(
    x: float, y: float, explosion_type: ExplosionType, sprite_groups: Tuple[Any, ...]
) -> Explosion:
    """Create an explosion and add it to sprite groups.

    Convenience function for creating explosions and adding them to
    multiple sprite groups in one call.

    Args:
        x: Horizontal center position
        y: Vertical center position
        explosion_type: Type of explosion
        sprite_groups: Tuple of sprite groups to add the explosion to

    Returns:
        The created Explosion instance

    Example:
        >>> explosion = create_explosion(
        ...     enemy.rect.centerx,
        ...     enemy.rect.centery,
        ...     'small',
        ...     (all_sprites, explosions)
        ... )
    """
    explosion = Explosion(x, y, explosion_type)
    for group in sprite_groups:
        group.add(explosion)
    return explosion
