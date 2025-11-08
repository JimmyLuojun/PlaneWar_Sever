"""Scrolling background handler for the PlaneWar game.

Defines the Background class responsible for loading, scrolling, and
rendering the game's background image. Implements seamless vertical
scrolling with dual-image positioning for continuous movement.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import os
from typing import Optional

# Third-party
import pygame

# Local
from ..infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK

# ========================================
# Constants
# ============================================================================

# Minimum height multiplier to ensure smooth scrolling
MIN_HEIGHT_MULTIPLIER: float = 1.0


# ============================================================================
# Concrete Classes
# ============================================================================


class Background:
    """Manages loading, scrolling, and rendering of the game's background.

    Handles background image loading with automatic scaling to match screen
    dimensions. Implements seamless vertical scrolling using two image
    instances positioned end-to-end that continuously loop.

    Attributes:
        screen_width: Width of the game screen
        screen_height: Height of the game screen
        scroll_speed: Vertical scroll speed in pixels per frame
        image: Scaled background image surface (None if load failed)
        image_height: Height of the scaled image
        y1: Vertical position of first image instance
        y2: Vertical position of second image instance

    Example:
        >>> background = Background(
        ...     "game/media/images/background.jpeg",
        ...     SCREEN_WIDTH,
        ...     SCREEN_HEIGHT,
        ...     2
        ... )
        >>> # In game loop:
        >>> background.update()
        >>> background.draw(screen)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(
        self, image_path: str, screen_width: int, screen_height: int, scroll_speed: int
    ):
        """Initialize the background handler.

        Args:
            image_path: Full path to the background image file
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            scroll_speed: Vertical scroll speed (pixels per frame)
        """
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.scroll_speed: int = scroll_speed
        self.image: Optional[pygame.Surface] = None
        self.image_height: int = 0
        self.y1: float = 0.0
        self.y2: float = 0.0  # Positioned above y1 initially

        self._load_and_scale_image(image_path)

    # ========================================================================
    # Public Methods
    # ========================================================================

    def update(self) -> None:
        """Update vertical positions for scrolling effect.

        Called each frame to move both image instances downward.
        When an image scrolls completely off-screen at the bottom,
        it is repositioned above the other image for seamless looping.
        """
        if not self.image:
            return  # Do nothing if image wasn't loaded

        # Move both images down
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed

        # Loop first image when it scrolls off bottom
        if self.y1 >= self.image_height:
            self.y1 = self.y2 - self.image_height

        # Loop second image when it scrolls off bottom
        if self.y2 >= self.image_height:
            self.y2 = self.y1 - self.image_height

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the background onto the given surface.

        Args:
            surface: The surface to draw on (usually the game screen)
        """
        if self.image:
            surface.blit(self.image, (0, self.y1))
            surface.blit(self.image, (0, self.y2))
        else:
            # Fallback: Fill with black if image failed to load
            surface.fill(BLACK)

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _load_and_scale_image(self, image_path: str) -> None:
        """Load and scale the background image.

        Validates the image path, loads the image, and scales it to match
        the screen width while maintaining aspect ratio. Ensures the height
        is at least equal to screen height for seamless scrolling.

        Args:
            image_path: Path to the background image file
        """
        if not image_path or not os.path.exists(image_path):
            print(
                f"Warning: Background image not found: {image_path}. "
                f"Background will be black."
            )
            return

        try:
            # Load using convert() for better performance (opaque backgrounds)
            loaded_image = pygame.image.load(image_path).convert()

            # Calculate scaled dimensions maintaining aspect ratio
            original_width, original_height = loaded_image.get_size()
            aspect_ratio = original_height / original_width
            scaled_height = int(self.screen_width * aspect_ratio)

            # Ensure height is sufficient for scrolling
            if scaled_height < self.screen_height:
                print(
                    f"Info: Background height ({scaled_height}) < screen height "
                    f"({self.screen_height}). Adjusting to match."
                )
                scaled_height = self.screen_height

            # Scale the image
            self.image = pygame.transform.scale(
                loaded_image, (self.screen_width, scaled_height)
            )
            self.image_height = self.image.get_height()

            # Position second image above the first for seamless loop
            self.y2 = -self.image_height

            print(f"Successfully loaded background: {os.path.basename(image_path)}")

        except pygame.error as e:
            print(
                f"Error loading/scaling background {image_path}: {e}. "
                f"Background will be black."
            )
            self.image = None
