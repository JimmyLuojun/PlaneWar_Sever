"""Compatibility wrapper for the game network client API.

This module re-exports the `NetworkClient` and related result dataclasses from
`plane_war_server.game.infrastructure.network_client` so that existing imports
(`from plane_war_server.game.network_client import NetworkClient`) continue to
work. Prefer importing from `.infrastructure.network_client` in new code.
"""

# ============================================================================
# Imports
# ============================================================================

from .infrastructure.network_client import (
    NetworkClient,
    LoginResult,
    LogoutResult,
    SubmitResult,
    ProgressResult,
    api_login_user,
    api_logout_user,
    api_submit_score,
    api_get_leaderboard,
    check_login_status,
)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "NetworkClient",
    "LoginResult",
    "LogoutResult",
    "SubmitResult",
    "ProgressResult",
    "api_login_user",
    "api_logout_user",
    "api_submit_score",
    "api_get_leaderboard",
    "check_login_status",
]

