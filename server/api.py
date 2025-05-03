# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/api.py
from flask import Blueprint, request, jsonify
from .models import User, Score
from .extensions import db

# Note: For a more secure API, consider using Flask-Login's session for simple cases
# or token-based authentication (e.g., Flask-JWT-Extended) for stateless APIs.
# The current implementation relying on user_id sent by the client is INSECURE.

bp = Blueprint('api', __name__)

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
        # Return user details needed by the client
        # In a token-based system, you'd return a token here instead of user_id.
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username
            }), 200
    else:
        # Generic message for security (don't reveal if username exists)
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@bp.route('/submit_score', methods=['POST'])
def api_submit_score():
    """
    API endpoint for submitting scores from the game client.

    !! SECURITY WARNING: This endpoint is insecure as it trusts the user_id sent by the client.
    !! It should require proper authentication (e.g., a session cookie or an auth token).
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 415

    data = request.get_json()
    user_id = data.get('user_id')
    score_value = data.get('score')
    level = data.get('level_reached') # Optional

    # Basic Validation
    if user_id is None or score_value is None:
         return jsonify({"success": False, "message": "Missing user_id or score"}), 400

    try:
        user_id = int(user_id)
        score_value = int(score_value)
        if level is not None:
            level = int(level)
    except (ValueError, TypeError):
         return jsonify({"success": False, "message": "Invalid data types for user_id, score, or level"}), 400

    # --- Authentication Check (INSECURE METHOD) ---
    # In a real app, you'd verify a token or session here instead of just trusting the user_id.
    user = db.session.get(User, user_id)
    if not user:
         # Although the user_id might be fake, respond as if the user wasn't found
         # to avoid confirming valid user IDs exist based on score submission attempts.
         # However, for this *insecure* example, we return 404.
         # A secure version would likely return 401 Unauthorized if the token/session was invalid.
         return jsonify({"success": False, "message": "User not found"}), 404
    # --- End Insecure Authentication Check ---


    # Create and save the score
    try:
        new_score = Score(user_id=user.id, # Use user.id found from the (insecure) check
                          score_value=score_value,
                          level_reached=level)
        db.session.add(new_score)
        db.session.commit()
        print(f"Score {score_value} for user {user.username} (ID: {user.id}) saved.")
        return jsonify({"success": True, "message": "Score submitted successfully"}), 201
    except Exception as e:
        db.session.rollback() # Rollback in case of error during commit
        print(f"Error saving score for user {user_id}: {e}")
        return jsonify({"success": False, "message": "Database error saving score"}), 500


@bp.route('/leaderboard', methods=['GET'])
def api_get_leaderboard():
    """API endpoint to get leaderboard data (e.g., for display within Pygame)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        # Ensure limit is reasonable
        limit = max(1, min(limit, 100)) # Limit between 1 and 100

        scores = db.session.query(Score, User.username)\
                           .join(User, Score.user_id == User.id)\
                           .order_by(Score.score_value.desc())\
                           .limit(limit)\
                           .all()

        leaderboard_data = [
            {
                "rank": i + 1,
                "username": username,
                "score": score.score_value,
                "date": score.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') # Standard format
            }
            for i, (score, username) in enumerate(scores)
        ]
        return jsonify(leaderboard_data), 200
    except Exception as e:
        print(f"Error fetching API leaderboard: {e}")
        return jsonify({"success": False, "message": "Error fetching leaderboard"}), 500