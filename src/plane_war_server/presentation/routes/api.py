"""Defines API endpoints for programmatic interaction with the server.

Presentation layer for handling HTTP requests and responses.
Delegates all business logic to service classes.
"""

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_user, logout_user

from ...infrastructure.extensions import db
from ...data.repositories import (
    LeaderboardRepository,
    ScoreRepository,
    UserRepository,
)
from ...application.services.auth_service import AuthService
from ...application.services.leaderboard_service import LeaderboardService
from ...application.services.progress_service import ProgressService
from ...application.services.score_service import (
    ScoreService,
    ScoreSubmissionError,
    UserNotFoundError,
)


# ============================================================================
# Public API - Blueprint Registration
# ============================================================================

bp = Blueprint("api", __name__)


# ============================================================================
# Helper Functions - Dependency Injection
# ============================================================================

def _auth_service() -> AuthService:
    """Create AuthService instance with repository."""
    return AuthService(UserRepository(db.session))


def _score_service() -> ScoreService:
    """Create ScoreService instance with repositories."""
    return ScoreService(UserRepository(db.session), ScoreRepository(db.session))


def _leaderboard_service() -> LeaderboardService:
    """Create LeaderboardService instance with repository."""
    return LeaderboardService(LeaderboardRepository(db.session))


def _progress_service() -> ProgressService:
    """Create ProgressService instance."""
    return ProgressService()


# ============================================================================
# Core Logic - Route Handlers
# ============================================================================

@bp.route("/login", methods=["POST"])
def api_login():
    """Handle user login via API.

    Validates credentials and creates a session.

    Returns:
        JSON response with success status and user info or error message
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    # Use AuthService instead of direct database access
    user = _auth_service().verify_login(username, password)
    if user:
        login_user(user)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "user_id": user.id,
                    "username": user.username,
                }
            ),
            200,
        )
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@bp.route("/logout", methods=["POST"])
def api_logout():
    """Handle user logout via API.

    Ends the user session.

    Returns:
        JSON response with success status
    """
    logout_user()
    return jsonify({"success": True, "message": "Logout successful"}), 200


@bp.route("/submit_score", methods=["POST"])
def api_submit_score():
    """Handle score submission via API.

    Accepts score data and saves it for a user.

    Returns:
        JSON response with success status or error message
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json() or {}
    user_id = data.get("user_id")
    score_value = data.get("score")
    level_value = data.get("level")

    # Use authenticated user if no user_id provided
    if user_id is None and current_user.is_authenticated:
        user_id = current_user.id

    if user_id is None or score_value is None or level_value is None:
        return (
            jsonify({"success": False, "message": "Missing user_id, score, or level"}),
            400,
        )

    # Validate and convert data types
    try:
        user_id_int = int(user_id)
        score_value_int = int(score_value)
        level_int = int(level_value)
    except (ValueError, TypeError):
        return (
            jsonify({"success": False, "message": "Invalid data types for user_id, score, or level"}),
            400,
        )

    # Use ScoreService instead of direct database access
    try:
        _score_service().submit_score(user_id_int, score_value_int, level_int)
        return (
            jsonify({"success": True, "message": f"Score submitted successfully for level {level_int}."}),
            201,
        )
    except UserNotFoundError:
        return (
            jsonify({"success": False, "message": "User specified by user_id not found"}),
            404,
        )
    except ValueError as e:
        return (
            jsonify({"success": False, "message": str(e)}),
            400,
        )
    except ScoreSubmissionError:
        return jsonify({"success": False, "message": "Database error saving score"}), 500


@bp.route("/progress", methods=["GET"])
def api_get_progress():
    """Get user progress (max unlocked level).

    Requires authentication.

    Returns:
        JSON response with max_unlocked_level or error message
    """
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    try:
        max_level = _progress_service().get_max_level(current_user.id)
        return jsonify({"success": True, "max_unlocked_level": int(max_level)})
    except Exception:
        return jsonify({"success": False, "message": "Progress read error"}), 500


@bp.route("/progress", methods=["POST"])
def api_set_progress():
    """Update user progress (max unlocked level).

    Requires authentication.

    Returns:
        JSON response with updated max_unlocked_level or error message
    """
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415
    data = request.get_json() or {}
    value = data.get("max_unlocked_level")
    try:
        new_val = int(value)
    except Exception:
        return jsonify({"success": False, "message": "Invalid value"}), 400
    try:
        stored = _progress_service().set_max_level(current_user.id, new_val)
        return jsonify({"success": True, "max_unlocked_level": int(stored)})
    except Exception:
        return jsonify({"success": False, "message": "Progress write error"}), 500

