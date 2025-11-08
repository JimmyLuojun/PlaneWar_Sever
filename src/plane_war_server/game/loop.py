"""Compatibility shim exposing game-level symbols expected by tests.

This module intentionally re-exports selected runtime symbols so tests can
patch `plane_war_server.game.loop.Enemy` while the main loop references it.
"""

# ============================================================================
# Imports
# ============================================================================

from .models.enemy import Enemy  # Re-exported for monkeypatching in tests


# ============================================================================
# Public API
# ============================================================================

__all__ = ["Enemy"]

