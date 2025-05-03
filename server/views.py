# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/views.py
from curses import flash
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user # Import current_user
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
        per_page = 20 # Number of scores per page

        # Query scores joined with username, ordered by score descending
        # Using paginate for easy page handling
        scores_pagination = db.session.query(Score, User.username)\
                                      .join(User, Score.user_id == User.id)\
                                      .order_by(Score.score_value.desc())\
                                      .paginate(page=page, per_page=per_page, error_out=False)

        # Calculate rank offset for the current page items
        # Rank of the first item on the page = (page - 1) * per_page + 1
        rank_offset = (scores_pagination.page - 1) * scores_pagination.per_page

        return render_template('leaderboard.html',
                               title="Leaderboard",
                               scores_data=scores_pagination.items, # List of (Score, username) tuples
                               pagination=scores_pagination, # Pagination object for controls
                               rank_offset=rank_offset) # To display correct rank number

    except Exception as e:
        print(f"Error rendering leaderboard view: {e}")
        # Optional: Show an error page
        # return render_template('error.html', message="Could not load leaderboard"), 500
        flash("Error loading leaderboard.", "danger")
        return redirect(url_for('auth.login')) # Redirect somewhere sensible