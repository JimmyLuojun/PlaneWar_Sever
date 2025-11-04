"""Power-up collectibles for the PlaneWar game.

Defines the PowerUp sprite class for creating collectible items that
fall from the top of the screen. Power-ups provide temporary enhancements
like double shot, shield protection, or bomb powerups.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import random
from typing import Dict, Optional

# Third-party
import pygame

# Local
from .settings import (
    POWERUP_TYPES,
    POWERUP_WIDTH,
    POWERUP_HEIGHT,
    POWERUP_SPEED_Y,
    POWERUP_FALLBACK_COLORS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    BLUE,
)


# ============================================================================
# Type Definitions
# ============================================================================

PowerUpImages = Dict[str, pygame.Surface]
PowerUpType = str


# ============================================================================
# Constants
# ============================================================================

# Spawn position range (above screen)
SPAWN_Y_MIN: int = -100
SPAWN_Y_MAX: int = -40

# Fallback border width
FALLBACK_BORDER_WIDTH: int = 1


# ============================================================================
# Concrete Classes
# ============================================================================


class PowerUp(pygame.sprite.Sprite):
    """Collectible power-up sprite that falls from the top of the screen.

    Power-ups provide temporary enhancements when collected by the player.
    They randomly select a type (double_shot, shield, bomb) on creation
    and use pre-loaded images or fallback colored rectangles.

    Attributes:
        type: The power-up type ('double_shot', 'shield', or 'bomb')
        image: Visual representation (pre-loaded image or fallback surface)
        rect: Position and collision rectangle
        speedy: Vertical movement speed

    Example:
        >>> powerup_images = {
        ...     'double_shot': double_shot_img,
        ...     'shield': shield_img,
        ...     'bomb': bomb_img
        ... }
        >>> powerup = PowerUp(powerup_images)
        >>> all_sprites.add(powerup)
        >>> powerups.add(powerup)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self, powerup_images: PowerUpImages):
        """Initialize a random power-up.

        Args:
            powerup_images: Dictionary mapping power-up types to pre-loaded images
        """
        super().__init__()

        # Randomly select power-up type
        self.type: PowerUpType = random.choice(POWERUP_TYPES)

        # Load image or create fallback
        self.image: pygame.Surface = self._load_powerup_image(powerup_images)
        self.rect: pygame.Rect = self.image.get_rect()

        # Random horizontal position
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)

        # Start above screen
        self.rect.y = random.randint(SPAWN_Y_MIN, SPAWN_Y_MAX)

        # Vertical movement speed
        self.speedy: int = POWERUP_SPEED_Y

    # ========================================================================
    # Public Methods
    # ========================================================================

    def update(self) -> None:
        """Update power-up position and remove if off-screen.

        Called each frame by sprite group's update() method.
        Moves the power-up downward and removes it when it exits
        the bottom of the screen.
        """
        self.rect.y += self.speedy

        # Remove when it exits the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _load_powerup_image(self, powerup_images: PowerUpImages) -> pygame.Surface:
        """Load the appropriate image for this power-up type.

        Args:
            powerup_images: Dictionary mapping power-up types to pre-loaded images

        Returns:
            Power-up image surface (pre-loaded or fallback)
        """
        # Try to get pre-loaded image
        image = powerup_images.get(self.type)

        if image is not None:
            return image

        # Fallback: Create colored rectangle
        print(
            f"Warning: Failed to load power-up image '{self.type}'. "
            f"Using fallback block."
        )
        return self._create_fallback_surface()

    def _create_fallback_surface(self) -> pygame.Surface:
        """Create a fallback colored rectangle for power-up visualization.

        Returns:
            Colored surface with border
        """
        surface = pygame.Surface((POWERUP_WIDTH, POWERUP_HEIGHT))

        # Get color for this power-up type (default to blue)
        fallback_color = POWERUP_FALLBACK_COLORS.get(self.type, BLUE)
        surface.fill(fallback_color)

        # Add white border
        pygame.draw.rect(surface, WHITE, surface.get_rect(), FALLBACK_BORDER_WIDTH)

        return surface
