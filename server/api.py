# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/api.py
"""Defines API endpoints for programmatic interaction with the server.

Contains routes (using a Flask Blueprint) designed to be called by the game
client or other services. Handles tasks like user login (`/api/login`),
score submission (`/api/submit_score`), and logout (`/api/logout`) using JSON requests
and responses, relying on Flask-Login for authentication.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user # Import Flask-Login functions
from .models import User, Score # Make sure Score is imported
from .extensions import db

# Note: For a more secure API, consider using Flask-Login's session for simple cases
# or token-based authentication (e.g., Flask-JWT-Extended) for stateless APIs.
# The current implementation relying on user_id sent by the client is INSECURE.

bp = Blueprint('api', __name__, url_prefix='/api') # Added url_prefix for clarity

@bp.route('/login', methods=['POST'])
def api_login():
    """API endpoint for programmatic login (e.g., from Pygame client)."""
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Use Flask-Login to establish a session
        login_user(user) # Creates the secure session cookie
        print(f"User {user.username} logged in successfully via API.")
        # Return success, no need to send user_id anymore. Client relies on session cookie.
        return jsonify({
            "success": True,
            "message": "Login successful",
            "username": user.username # Still useful to return username for client UI
            }), 200
    else:
        print(f"API login failed for username: {username}")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

# Example logout endpoint (optional, but good practice)
@bp.route('/logout', methods=['POST'])
@login_required # Ensure user is logged in to log out
def api_logout():
    """API endpoint for logging out."""
    username = current_user.username # Get username before logging out
    logout_user() # Clears the session cookie
    print(f"User {username} logged out via API.")
    return jsonify({"success": True, "message": "Logout successful"}), 200

@bp.route('/submit_score', methods=['POST'])
@login_required # <<< ADDED: Ensures only logged-in users can submit scores
def api_submit_score():
    """
    API endpoint for submitting scores from the game client.
    Uses Flask-Login session for authentication.
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json()
    # user_id = data.get('user_id') # <<< REMOVED: Do not trust user_id from client
    score_value = data.get('score')
    level_from_payload = data.get('level')

    # --- Updated Validation (No longer checks for user_id from payload) ---
    # current_user is guaranteed to be valid by @login_required
    if score_value is None or level_from_payload is None:
         # Simplified error message as user_id is implicitly handled by login
         return jsonify({"success": False, "message": "Missing score or level"}), 400

    try:
        score_value_int = int(score_value)
        level_int = int(level_from_payload)
    except (ValueError, TypeError):
         return jsonify({"success": False, "message": "Invalid data types for score or level"}), 400

    # --- Secure Authentication via Flask-Login ---
    # current_user is provided by Flask-Login based on the valid session cookie
    user = current_user
    # --- End Secure Authentication ---

    # Create and save the score using the authenticated user's ID
    try:
        new_score = Score(user_id=user.id, # <<< Use current_user.id
                          score_value=score_value_int,
                          level=level_int) # Field name 'level' confirmed correct from models.py
        db.session.add(new_score)
        db.session.commit()
        print(f"Score {score_value_int} for user {user.username} (ID: {user.id}) on Level {level_int} saved.")
        return jsonify({"success": True, "message": f"Score submitted successfully for level {level_int}."}), 201 # 201 Created
    except Exception as e:
        db.session.rollback()
        print(f"Error saving score for user {user.username} (ID: {user.id}) on level {level_int}: {e}")
        return jsonify({"success": False, "message": "Database error saving score"}), 500

