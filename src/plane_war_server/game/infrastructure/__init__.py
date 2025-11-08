"""Game infrastructure and support systems.

Contains assets loading, settings, network client, progress tracking, and utilities.
"""

from .assets import load_fonts, load_images, load_sounds, load_level_data_and_music
from .network_client import NetworkClient
from .settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "load_fonts",
    "load_images",
    "load_sounds",
    "load_level_data_and_music",
    "NetworkClient",
    "SCREEN_WIDTH",
    "SCREEN_HEIGHT",
    "FPS",
]
