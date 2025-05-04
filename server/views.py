"""Defines user-facing web routes and renders HTML templates.

Contains routes (using a Flask Blueprint) for the web interface of the server.
Handles requests for pages like the main index, leaderboards (overall and per-level),
and potentially game information pages. Uses Flask-Login to manage user sessions
and renders Jinja2 HTML templates.
"""
# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/views.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
# Import the service, remove direct db/model access for leaderboard if not needed elsewhere
from .leaderboard_service import get_leaderboard_by_level, get_overall_leaderboard, get_distinct_levels

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    """Redirects to overall leaderboard if logged in, otherwise to login."""
    if current_user.is_authenticated:
        # Redirect to overall leaderboard by default
        return redirect(url_for('views.leaderboard'))
    else:
        return redirect(url_for('auth.login')) # Assuming your auth blueprint is named 'auth'

# Combined route for overall and per-level leaderboards
@bp.route('/leaderboard')
@bp.route('/leaderboard/level/<int:level_num>')
@login_required # Keep login required for viewing leaderboards
def leaderboard(level_num=None):
    """Displays the leaderboard, either overall or for a specific level (Top 30)."""
    try:
        available_levels = get_distinct_levels() # Get levels for dropdown/links
        leaderboard_data = []
        leaderboard_title = ""
        current_level_filter = "Overall" # Default display filter name

        if level_num is not None:
            # Simple validation: check if the requested level exists in the list of levels with scores
            if level_num not in available_levels:
                 flash(f"Level {level_num} does not exist or has no scores.", "warning")
                 return redirect(url_for('views.leaderboard')) # Redirect to overall on invalid level

            leaderboard_data = get_leaderboard_by_level(level_num)
            leaderboard_title = f"Leaderboard - Level {level_num} (Top {len(leaderboard_data)})"
            current_level_filter = f"Level {level_num}"
        else:
            # Overall leaderboard
            leaderboard_data = get_overall_leaderboard()
            leaderboard_title = f"Overall Leaderboard (Top {len(leaderboard_data)})"
            # current_level_filter remains "Overall"

        # Pass formatted data from service to template
        return render_template('leaderboard.html',
                               title=leaderboard_title,
                               scores_data=leaderboard_data,
                               available_levels=available_levels,
                               current_level_filter=current_level_filter
                              )

    except Exception as e:
        print(f"Error loading leaderboard view: {e}")
        # import traceback; traceback.print_exc() # Good for dev
        flash("An error occurred while loading the leaderboard.", "danger")
        # Redirect to a known safe page, maybe index or user profile if they exist
        return redirect(url_for('views.index')) # Redirecting back to index is safer

@bp.route('/game')
@login_required
def game():
    """Renders the game instruction page."""
    # Ensure the template path is correct based on your file structure
    return render_template('game.html', title="How to Play")