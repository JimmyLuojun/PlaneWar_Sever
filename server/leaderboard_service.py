"""Business logic for calculating and retrieving leaderboard data.

Encapsulates database queries and logic for generating ranked leaderboards.
Provides functions to get top scores overall, top scores per level, and
the distinct levels available, handling tie-breaking logic where necessary.
"""

from sqlalchemy import asc, desc, distinct, func

from .extensions import db
from .models import Score, User


# Constants
TOP_N_PLAYERS = 30


# Core Logic
def get_leaderboard_by_level(level_num):
    """
    Gets the top players for a specific level based on their highest score for that level.
    Tie-breaking is done by the earliest timestamp achieving that highest score.

    Args:
        level_num (int): The level number to get the leaderboard for.

    Returns:
        list: A list of dictionaries, each containing 'rank', 'username', 'score', 'timestamp'.
              Returns empty list if level doesn't exist or has no scores.
    """
    # Subquery to find the highest score for each user ON THIS LEVEL
    subq_max_score = (
        db.session.query(Score.user_id, func.max(Score.score_value).label("max_score"))
        .filter(Score.level == level_num)
        .group_by(Score.user_id)
        .subquery()
    )

    # Find the earliest timestamp associated with that max score for each user ON THIS LEVEL
    subq_earliest_timestamp = (
        db.session.query(
            Score.user_id, func.min(Score.timestamp).label("earliest_timestamp")
        )
        .join(
            subq_max_score,
            db.and_(
                Score.user_id == subq_max_score.c.user_id,
                Score.score_value == subq_max_score.c.max_score,
            ),
        )
        .filter(Score.level == level_num)
        .group_by(Score.user_id)
        .subquery()
    )

    # Main query to get user details and rank them
    results = (
        db.session.query(
            User.username,
            subq_max_score.c.max_score,
            subq_earliest_timestamp.c.earliest_timestamp,
        )
        .select_from(User)
        .join(subq_max_score, User.id == subq_max_score.c.user_id)
        .join(subq_earliest_timestamp, User.id == subq_earliest_timestamp.c.user_id)
        .order_by(
            subq_max_score.c.max_score.desc(),  # Highest score first
            subq_earliest_timestamp.c.earliest_timestamp.asc(),  # Earliest timestamp first for ties
        )
        .limit(TOP_N_PLAYERS)
        .all()
    )

    # Format results with rank
    leaderboard = []
    for i, (username, score, timestamp) in enumerate(results):
        leaderboard.append(
            {
                "rank": i + 1,
                "username": username,
                "score": score,
                "timestamp": timestamp,
            }
        )

    return leaderboard


def get_overall_leaderboard():
    """Gets the top players based on the sum of their highest scores across all levels.

    Tie-breaking uses the timestamp of the user's last submitted score that was
    a personal best for any level (contributing to the sum).

    Returns:
        list: A list of dictionaries, each containing 'rank', 'username', 'total_score', 'timestamp'.
    """
    subq_max_per_level = (
        db.session.query(
            Score.user_id,
            Score.level,
            func.max(Score.score_value).label("max_score_for_level"),
        )
        .group_by(Score.user_id, Score.level)
        .subquery()
    )

    subq_max_score_timestamps = (
        db.session.query(
            Score.user_id,
            Score.level,
            func.min(Score.timestamp).label("earliest_timestamp_for_max"),
        )
        .join(
            subq_max_per_level,
            db.and_(
                Score.user_id == subq_max_per_level.c.user_id,
                Score.level == subq_max_per_level.c.level,
                Score.score_value == subq_max_per_level.c.max_score_for_level,
            ),
        )
        .group_by(Score.user_id, Score.level)
        .subquery()
    )

    subq_overall = (
        db.session.query(
            subq_max_per_level.c.user_id,
            func.sum(subq_max_per_level.c.max_score_for_level).label("total_score"),
            func.min(subq_max_score_timestamps.c.earliest_timestamp_for_max).label(
                "earliest_best_score_timestamp"
            ),
        )
        .select_from(subq_max_per_level)
        .join(
            subq_max_score_timestamps,
            db.and_(
                subq_max_per_level.c.user_id == subq_max_score_timestamps.c.user_id,
                subq_max_per_level.c.level == subq_max_score_timestamps.c.level,
            ),
        )
        .group_by(subq_max_per_level.c.user_id)
        .subquery()
    )

    results = (
        db.session.query(
            User.username,
            subq_overall.c.total_score,
            subq_overall.c.earliest_best_score_timestamp,
        )
        .select_from(User)
        .join(subq_overall, User.id == subq_overall.c.user_id)
        .order_by(
            subq_overall.c.total_score.desc(),
            subq_overall.c.earliest_best_score_timestamp.asc(),
        )
        .limit(TOP_N_PLAYERS)
        .all()
    )

    leaderboard = []
    for i, (username, total_score, timestamp) in enumerate(results):
        leaderboard.append(
            {
                "rank": i + 1,
                "username": username,
                "score": total_score,
                "timestamp": timestamp,
            }
        )

    return leaderboard


def get_distinct_levels():
    """Gets a sorted list of distinct level numbers that have scores."""
    levels = db.session.query(Score.level).distinct().order_by(Score.level.asc()).all()
    return [level[0] for level in levels]
