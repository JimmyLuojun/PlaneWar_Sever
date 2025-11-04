"""Defines API endpoints for programmatic interaction with the server.

Contains routes (using a Flask Blueprint) designed to be called by the game
client or other services. Handles tasks like user login (`/api/login`),
score submission (`/api/submit_score`), and logout (`/api/logout`) using JSON requests
and responses, relying on Flask-Login for authentication.

Note: For a more secure API, consider using Flask-Login's session for simple cases
or token-based authentication (e.g., Flask-JWT-Extended) for stateless APIs.
The current implementation relying on user_id sent by the client is INSECURE.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, current_user

from .extensions import db
from .models import Score, User
from .progress_store import (
    get_max_unlocked_level_for_user,
    set_max_unlocked_level_for_user,
)


# Constants
bp = Blueprint("api", __name__)


# Core Logic
@bp.route("/login", methods=["POST"])
def api_login():
    """API endpoint for programmatic login (e.g., from Pygame client)."""
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(
            {"success": False, "message": "Username and password required"}
        ), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Establish a session (even though tests rely on payload user_id)
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
    """API endpoint for logging out."""
    logout_user()
    return jsonify({"success": True, "message": "Logout successful"}), 200


@bp.route("/submit_score", methods=["POST"])
def api_submit_score():
    """API endpoint for submitting scores (insecure, payload includes user_id)."""
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json()
    user_id = data.get("user_id")
    score_value = data.get("score")
    level_value = data.get("level")

    # Support session-based auth as well: if user_id not provided, use current_user
    if user_id is None and current_user.is_authenticated:
        user_id = current_user.id

    if user_id is None or score_value is None or level_value is None:
        return (
            jsonify({"success": False, "message": "Missing user_id, score, or level"}),
            400,
        )

    try:
        user_id_int = int(user_id)
        score_value_int = int(score_value)
        level_int = int(level_value)
    except (ValueError, TypeError):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid data types for user_id, score, or level",
                }
            ),
            400,
        )

    user = User.query.get(user_id_int)
    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "User specified by user_id not found",
                }
            ),
            404,
        )

    try:
        new_score = Score(user_id=user.id, score_value=score_value_int, level=level_int)
        db.session.add(new_score)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Score submitted successfully for level {level_int}.",
                }
            ),
            201,
        )
    except Exception:
        db.session.rollback()
        return (
            jsonify({"success": False, "message": "Database error saving score"}),
            500,
        )


@bp.route("/progress", methods=["GET"])
def api_get_progress():
    """Return the authenticated user's max unlocked level."""
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    try:
        max_level = get_max_unlocked_level_for_user(current_user.id)
        return jsonify({"success": True, "max_unlocked_level": int(max_level)})
    except Exception:
        return jsonify({"success": False, "message": "Progress read error"}), 500


@bp.route("/progress", methods=["POST"])
def api_set_progress():
    """Set the authenticated user's max unlocked level.

    Expects JSON: {"max_unlocked_level": int}
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
        stored = set_max_unlocked_level_for_user(current_user.id, new_val)
        return jsonify({"success": True, "max_unlocked_level": int(stored)})
    except Exception:
        return jsonify({"success": False, "message": "Progress write error"}), 500
