"""
Web views routes
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .models import Score

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    """Home page."""
    return render_template('base.html')

@bp.route('/leaderboard')
def leaderboard():
    """Leaderboard page."""
    scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=scores)

@bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    scores = current_user.scores.order_by(Score.score.desc()).all()
    return render_template('profile.html', user=current_user, scores=scores) 