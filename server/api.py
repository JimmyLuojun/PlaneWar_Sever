"""
API routes for game data
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from .models import Score
from .extensions import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/scores', methods=['POST'])
@login_required
def submit_score():
    """Submit a new score."""
    data = request.get_json()
    
    if not data or 'score' not in data or 'level' not in data:
        return jsonify({'error': 'Missing score or level data'}), 400
        
    score = Score(
        score=data['score'],
        level=data['level'],
        user_id=current_user.id
    )
    
    db.session.add(score)
    db.session.commit()
    
    return jsonify({'message': 'Score submitted successfully'}), 201

@bp.route('/leaderboard')
def get_leaderboard():
    """Get the top scores."""
    scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    
    leaderboard = [{
        'username': score.user.username,
        'score': score.score,
        'level': score.level,
        'date': score.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for score in scores]
    
    return jsonify(leaderboard)

@bp.route('/user/scores')
@login_required
def get_user_scores():
    """Get the current user's scores."""
    scores = current_user.scores.order_by(Score.score.desc()).all()
    
    user_scores = [{
        'score': score.score,
        'level': score.level,
        'date': score.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for score in scores]
    
    return jsonify(user_scores) 