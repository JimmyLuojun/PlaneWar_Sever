"""Defines user-facing web routes and renders HTML templates."""

import logging

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ...infrastructure.extensions import db
from ...data.repositories import LeaderboardRepository
from ...application.services.leaderboard_service import LeaderboardService


bp = Blueprint("views", __name__)
logger = logging.getLogger(__name__)


def _leaderboard_service() -> LeaderboardService:
    return LeaderboardService(LeaderboardRepository(db.session))


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("views.leaderboard"))
    else:
        return redirect(url_for("auth.login"))


@bp.route("/leaderboard")
@bp.route("/leaderboard/level/<int:level_num>")
@login_required
def leaderboard(level_num=None):
    try:
        svc = _leaderboard_service()
        available_levels = svc.get_available_levels()
        leaderboard_data = []
        leaderboard_title = ""
        current_level_filter = "Overall"

        if level_num is not None:
            if level_num not in available_levels:
                flash(f"Level {level_num} does not exist or has no scores.", "warning")
                return redirect(url_for("views.leaderboard"))

            leaderboard_data = svc.get_leaderboard_by_level(level_num)
            leaderboard_title = f"Leaderboard - Level {level_num} (Top {len(leaderboard_data)})"
            current_level_filter = f"Level {level_num}"
        else:
            leaderboard_data = svc.get_overall_leaderboard()
            leaderboard_title = f"Overall Leaderboard (Top {len(leaderboard_data)})"

        return render_template(
            "leaderboard.html",
            title=leaderboard_title,
            scores_data=leaderboard_data,
            available_levels=available_levels,
            current_level_filter=current_level_filter,
        )

    except Exception as e:
        logger.error(f"Error loading leaderboard view: {e}", exc_info=True)
        flash("An error occurred while loading the leaderboard.", "danger")
        return redirect(url_for("views.index"))


@bp.route("/game")
@login_required
def game():
    return render_template("game.html", title="How to Play")

