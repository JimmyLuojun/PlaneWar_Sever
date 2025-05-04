from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from .models import Score, User
from .extensions import db

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    """Redirects to leaderboard if logged in, otherwise to login."""
    if current_user.is_authenticated:
        return redirect(url_for('views.leaderboard'))
    else:
        return redirect(url_for('auth.login'))

@bp.route('/leaderboard')
def leaderboard():
    """Displays the main leaderboard web page with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Number of scores per page

        # Query scores joined with username, ordered by score descending
        scores_pagination = db.session.query(Score, User.username)\
                                      .join(User, Score.user_id == User.id)\
                                      .order_by(Score.score_value.desc())\
                                      .paginate(page=page, per_page=per_page, error_out=False)

        rank_offset = (scores_pagination.page - 1) * scores_pagination.per_page

        return render_template('leaderboard.html',
                               title="Leaderboard",
                               scores_data=scores_pagination.items,
                               pagination=scores_pagination,
                               rank_offset=rank_offset)

    except Exception as e:
        flash("Error loading leaderboard.", "danger")
        return redirect(url_for('auth.login'))

@bp.route('/game')
@login_required  # Ensure the user is logged in before they can play the game
def game():
    """Renders the game page where the user can play."""
    return render_template('game.html')  # Assuming you have a 'game.html' template for the game interface
