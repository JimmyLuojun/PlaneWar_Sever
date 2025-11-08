"""Game controllers and logic.

Contains game loop, state machine, and game flow control logic.
Following MVC pattern - these are the Controllers.
"""

from .game_loop import run_game
from .state_machine import run_state_machine


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "run_game",
    "run_state_machine",
]
