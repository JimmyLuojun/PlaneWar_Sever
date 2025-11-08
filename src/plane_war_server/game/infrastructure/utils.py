"""Utility functions and classes for the PlaneWar game client.

Provides the `AssetLoader` class for loading game assets (images, sounds),
along with utility functions for data persistence (high scores, level definitions).
Handles errors gracefully with fallback mechanisms.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import os
import json
import random
from typing import Optional, List, Dict, Any, Tuple, Union

# Third-party
import pygame

# Local
from .settings import WHITE


# ============================================================================
# Type Definitions
# ============================================================================

LevelData = Dict[str, Any]
LevelDataList = List[LevelData]
Color = Tuple[int, int, int]


# ============================================================================
# Constants
# ============================================================================

# --- Fallback Asset Constants ---
FALLBACK_ERROR_COLOR: Color = (200, 50, 50)  # Red-ish for missing files
FALLBACK_RANDOM_MIN: int = 50
FALLBACK_RANDOM_MAX: int = 200
FALLBACK_BORDER_WIDTH: int = 1

# --- File Handling Constants ---
DEFAULT_ENCODING: str = "utf-8"
LEVEL_FILE_EXTENSION: str = ".json"
LEVEL_NUMBER_KEY: str = "level_number"

# --- Special Values ---
COLORKEY_TOPLEFT_SAMPLE: int = -1  # Sample colorkey from image top-left pixel


# ============================================================================
# Helper Functions
# ============================================================================


def _resolve_absolute_path(path: str, base_dir: Optional[str] = None) -> str:
    """Resolve a relative path to an absolute path.

    Args:
        path: File path (relative or absolute)
        base_dir: Base directory for relative paths (defaults to this module's directory)

    Returns:
        Absolute file path
    """
    if os.path.isabs(path):
        return path

    if base_dir is None:
        base_dir = os.path.dirname(__file__)

    return os.path.join(base_dir, path)


# ============================================================================
# Concrete Classes
# ============================================================================


class AssetLoader:
    """Handles loading and processing of game assets (images, sounds).

    Provides methods for loading images with scaling and transparency,
    and loading sounds with volume control. All methods include error
    handling with fallback mechanisms.

    Example:
        >>> loader = AssetLoader()
        >>> player_img = loader.load_and_scale_image("assets/player.png", 50, 50)
        >>> shoot_sound = loader.load_sound("assets/shoot.wav", 0.5)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the asset loader.

        Args:
            base_dir: Base directory for resolving relative paths
                     (defaults to the module's directory)
        """
        self.base_dir: str = base_dir or os.path.dirname(__file__)

    # ========================================================================
    # Public Methods - Image Loading
    # ========================================================================

    def load_and_scale_image(
        self,
        path: str,
        width: int,
        height: int,
        colorkey: Optional[Union[int, Color]] = None,
        *,
        use_colorkey: bool = False,
    ) -> pygame.Surface:
        """Load, scale, and process an image with error handling.

        Args:
            path: Path to the image file (relative or absolute)
            width: Target width for scaling
            height: Target height for scaling
            colorkey: Color to treat as transparent, or -1 to sample from top-left pixel
            use_colorkey: If True, sample colorkey from top-left pixel

        Returns:
            Scaled pygame.Surface with transparency applied (or fallback surface on error)
        """
        abs_path = _resolve_absolute_path(path, self.base_dir)

        if not abs_path or not os.path.exists(abs_path):
            print(
                f"Error: Image file not found or path invalid: {abs_path}. Using fallback."
            )
            return self._create_fallback_surface(width, height, FALLBACK_ERROR_COLOR)

        try:
            image = pygame.image.load(abs_path).convert_alpha()
            scaled_image = pygame.transform.scale(image, (width, height))

            if use_colorkey:
                colorkey = COLORKEY_TOPLEFT_SAMPLE

            if colorkey is not None:
                actual_colorkey: Union[int, Color, pygame.Color] = colorkey
                if colorkey == COLORKEY_TOPLEFT_SAMPLE:
                    # Sample color from top-left pixel of original image
                    actual_colorkey = image.get_at((0, 0))
                scaled_image.set_colorkey(actual_colorkey, pygame.RLEACCEL)

            return scaled_image

        except pygame.error as e:
            print(
                f"Warning: Failed to load/process image {abs_path}: {e}. Using fallback."
            )
            return self._create_fallback_surface(
                width, height, self._random_fallback_color()
            )

    def load_sound(self, path: str, volume: float = 1.0) -> Optional[pygame.mixer.Sound]:
        """Load a sound file and set its volume.

        Args:
            path: Path to the sound file (relative or absolute)
            volume: Volume level (0.0 to 1.0)

        Returns:
            pygame.mixer.Sound object, or None if loading failed or mixer unavailable
        """
        abs_path = _resolve_absolute_path(path, self.base_dir)

        if not pygame.mixer or not pygame.mixer.get_init():
            return None

        if not abs_path or not os.path.exists(abs_path):
            print(f"Warning: Sound file not found or path invalid: {abs_path}")
            return None

        try:
            sound = pygame.mixer.Sound(abs_path)
            sound.set_volume(volume)
            return sound
        except pygame.error as e:
            print(f"Warning: Failed to load sound {abs_path}: {e}")
            return None

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _create_fallback_surface(
        self, width: int, height: int, fill_color: Optional[Color] = None
    ) -> pygame.Surface:
        """Create a fallback surface with a colored rectangle and border.

        Args:
            width: Surface width
            height: Surface height
            fill_color: Fill color for the rectangle

        Returns:
            Fallback pygame.Surface
        """
        surface = pygame.Surface((width, height))
        try:
            if fill_color is None:
                fill_color = self._random_fallback_color()
            surface.fill(fill_color)
        except Exception:
            pass
        try:
            pygame.draw.rect(surface, WHITE, surface.get_rect(), FALLBACK_BORDER_WIDTH)
        except Exception:
            pass
        return surface

    def _random_fallback_color(self) -> Color:
        """Generate a random color for fallback surfaces.

        Returns:
            Random RGB color tuple
        """
        return (
            random.randint(FALLBACK_RANDOM_MIN, FALLBACK_RANDOM_MAX),
            random.randint(FALLBACK_RANDOM_MIN, FALLBACK_RANDOM_MAX),
            random.randint(FALLBACK_RANDOM_MIN, FALLBACK_RANDOM_MAX),
        )


# ============================================================================
# Public API Functions - Data Persistence
# ============================================================================


def load_high_score(filepath: str) -> int:
    """Load the high score from a file.

    Args:
        filepath: Path to the high score file (relative or absolute)

    Returns:
        High score as integer, or 0 if file not found or on error
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                score_str = f.read().strip()
            return int(score_str) if score_str.isdigit() else 0
        else:
            return 0
    except Exception as e:
        print(f"Warning: Error loading high score from {filepath}: {e}. Returning 0.")
        return 0


def save_high_score(filepath: str, score: int) -> None:
    """Save the high score to a file.

    Args:
        filepath: Path to the high score file (relative or absolute)
        score: High score to save
    """
    try:
        with open(filepath, "w") as f:
            f.write(str(score))
        print(f"Saved new high score {score} to '{os.path.basename(filepath)}'.")
    except Exception as e:
        print(f"Error: Failed to save high score to {filepath}: {e}")


def load_level_data(levels_directory: str) -> LevelDataList:
    """Load all level definition files from a directory.

    Scans the specified directory for .json files, parses them as level
    definitions, and returns them sorted by level number.

    Args:
        levels_directory: Path to directory containing level .json files

    Returns:
        List of level data dictionaries, sorted by 'level_number' key
    """
    abs_dir = levels_directory

    if not os.path.isdir(abs_dir):
        print(f"Error: Levels directory not found: {abs_dir}")
        return []

    loaded_levels: LevelDataList = []
    print(f"--- Loading Levels from: {abs_dir} ---")

    try:
        level_files = [
            f for f in os.listdir(abs_dir) if f.endswith(LEVEL_FILE_EXTENSION)
        ]
    except OSError as e:
        print(f"Error accessing levels directory {abs_dir}: {e}")
        return []

    if not level_files:
        print(
            f"Warning: No {LEVEL_FILE_EXTENSION} level files found in the 'levels' directory!"
        )
        return []

    for filename in level_files:
        filepath = os.path.join(abs_dir, filename)
        level_data = _load_single_level_file(filepath, filename)
        if level_data is not None:
            loaded_levels.append(level_data)

    # Sort by level number
    loaded_levels.sort(key=lambda lvl: lvl.get(LEVEL_NUMBER_KEY, float("inf")))

    print(f"--- Level loading complete. Loaded {len(loaded_levels)} valid levels. ---")
    return loaded_levels


def _load_single_level_file(filepath: str, filename: Optional[str] = None) -> Optional[LevelData]:
    """Load and validate a single level definition file.

    Args:
        filepath: Absolute or relative path to the level file
        filename: Optional filename (for logging); if None, derived from filepath

    Returns:
        Level data dictionary if valid, None otherwise
    """
    try:
        if filename is None:
            filename = os.path.basename(filepath)
        with open(filepath, "r", encoding=DEFAULT_ENCODING) as f:
            level_data = json.load(f)

        if LEVEL_NUMBER_KEY in level_data and isinstance(
            level_data[LEVEL_NUMBER_KEY], int
        ):
            print(
                f"  Successfully loaded: {filename} (Level {level_data[LEVEL_NUMBER_KEY]})"
            )
            return level_data
        else:
            print(
                f"  Warning: Skipping file {filename} - missing '{LEVEL_NUMBER_KEY}' or not an integer."
            )
            return None

    except json.JSONDecodeError as e:
        print(f"  Error: Failed to parse JSON file {filename}: {e}")
        return None
    except IOError as e:
        print(f"  Error: Failed to read file {filename}: {e}")
        return None
    except Exception as e:
        print(f"  Unknown error loading level {filename}: {e}")
        return None


# ============================================================================
# Backward Compatibility API
# ============================================================================
# Maintain module-level function names for existing code that imports them

_default_loader: Optional[AssetLoader] = None


def _get_default_loader() -> AssetLoader:
    """Get or create the default module-level AssetLoader instance.

    Returns:
        Singleton AssetLoader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = AssetLoader()
    return _default_loader


def load_and_scale_image(
    path: str, width: int, height: int, colorkey: Optional[Union[int, Color]] = None
) -> pygame.Surface:
    """DEPRECATED: Use AssetLoader.load_and_scale_image() instead.

    Maintained for backward compatibility with existing code.
    """
    return _get_default_loader().load_and_scale_image(path, width, height, colorkey)


def load_sound(path: str, volume: float) -> Optional[pygame.mixer.Sound]:
    """DEPRECATED: Use AssetLoader.load_sound() instead.

    Maintained for backward compatibility with existing code.
    """
    return _get_default_loader().load_sound(path, volume)
