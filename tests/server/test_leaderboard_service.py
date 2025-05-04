# tests/server/test_leaderboard_service.py # Corrected path comment
import pytest
from server.app import create_app # Adjust import
from server.extensions import db
from server.models import User, Score
from server.leaderboard_service import (
    get_leaderboard_by_level,
    get_overall_leaderboard,
    get_distinct_levels,
    TOP_N_PLAYERS # Import constant if needed
)
# --- MODIFIED IMPORT ---
from datetime import datetime, timedelta, UTC # Import UTC

# --- Fixture for Test App Context and Database ---
@pytest.fixture(scope='function')
def leaderboard_db():
    """Fixture to create app context and db, pre-populated for leaderboard tests."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(config_override=test_config)

    with app.app_context():
        db.create_all()

        # --- Create Test Users ---
        user1 = User(username="player1"); user1.set_password("p")
        user2 = User(username="player2"); user2.set_password("p")
        user3 = User(username="player3"); user3.set_password("p")
        user4 = User(username="player4_no_scores"); user4.set_password("p")
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit() # Commit users to get IDs

        # --- Create Test Scores ---
        # Player 1: Good scores, multiple levels, different times
        # Player 2: High scores, tie-breaking needed
        # Player 3: Lower scores
        # --- USE RECOMMENDED METHOD FOR UTC TIME ---
        now = datetime.now(UTC) # Use timezone-aware UTC time

        scores = [
            # Level 1 Scores
            Score(user_id=user1.id, score_value=100, level=1, timestamp=now - timedelta(hours=3)), # P1 L1 Best
            Score(user_id=user1.id, score_value=90, level=1, timestamp=now - timedelta(hours=4)),
            Score(user_id=user2.id, score_value=110, level=1, timestamp=now - timedelta(hours=1)), # P2 L1 Best (Later)
            Score(user_id=user3.id, score_value=80, level=1, timestamp=now - timedelta(hours=2)),  # P3 L1 Best

            # Level 2 Scores
            Score(user_id=user1.id, score_value=200, level=2, timestamp=now - timedelta(minutes=30)), # P1 L2 Best
            Score(user_id=user2.id, score_value=200, level=2, timestamp=now - timedelta(minutes=60)), # P2 L2 Best (Tie score, earlier time)
            Score(user_id=user3.id, score_value=150, level=2, timestamp=now - timedelta(minutes=90)), # P3 L2 Best

            # Level 3 Scores (Only Player 1)
            Score(user_id=user1.id, score_value=500, level=3, timestamp=now - timedelta(days=1)), # P1 L3 Best
        ]
        db.session.add_all(scores)
        db.session.commit()

        yield db # Provide only the db object

        db.session.remove()
        db.drop_all()

# --- Test get_distinct_levels ---
def test_get_distinct_levels(leaderboard_db):
    """Test retrieving distinct levels with scores."""
    levels = get_distinct_levels()
    assert levels == [1, 2, 3] # Should be sorted

# --- Test get_leaderboard_by_level ---
def test_get_leaderboard_level_1(leaderboard_db):
    """Test leaderboard for Level 1 (P2 > P1 > P3)."""
    leaderboard = get_leaderboard_by_level(1)
    assert len(leaderboard) == 3
    # Rank 1: Player 2 (Score 110)
    assert leaderboard[0]['rank'] == 1
    assert leaderboard[0]['username'] == "player2"
    assert leaderboard[0]['score'] == 110
    # Rank 2: Player 1 (Score 100)
    assert leaderboard[1]['rank'] == 2
    assert leaderboard[1]['username'] == "player1"
    assert leaderboard[1]['score'] == 100
    # Rank 3: Player 3 (Score 80)
    assert leaderboard[2]['rank'] == 3
    assert leaderboard[2]['username'] == "player3"
    assert leaderboard[2]['score'] == 80

def test_get_leaderboard_level_2_tiebreak(leaderboard_db):
    """Test leaderboard for Level 2 (P2 > P1 due to earlier timestamp on tie)."""
    leaderboard = get_leaderboard_by_level(2)
    assert len(leaderboard) == 3
    # Rank 1: Player 2 (Score 200, earlier timestamp)
    assert leaderboard[0]['rank'] == 1
    assert leaderboard[0]['username'] == "player2"
    assert leaderboard[0]['score'] == 200
    # Rank 2: Player 1 (Score 200, later timestamp)
    assert leaderboard[1]['rank'] == 2
    assert leaderboard[1]['username'] == "player1"
    assert leaderboard[1]['score'] == 200
    # Rank 3: Player 3 (Score 150)
    assert leaderboard[2]['rank'] == 3
    assert leaderboard[2]['username'] == "player3"
    assert leaderboard[2]['score'] == 150

def test_get_leaderboard_level_3_single_player(leaderboard_db):
    """Test leaderboard for Level 3 (only Player 1)."""
    leaderboard = get_leaderboard_by_level(3)
    assert len(leaderboard) == 1
    assert leaderboard[0]['rank'] == 1
    assert leaderboard[0]['username'] == "player1"
    assert leaderboard[0]['score'] == 500

def test_get_leaderboard_level_no_scores(leaderboard_db):
    """Test leaderboard for a level with no scores."""
    leaderboard = get_leaderboard_by_level(99)
    assert len(leaderboard) == 0

def test_get_leaderboard_limit(leaderboard_db):
    """Test that the leaderboard respects TOP_N_PLAYERS limit (implicitly tested if > TOP_N)."""
    # Add more users/scores if TOP_N_PLAYERS is small to test the limit
    # For now, assume TOP_N_PLAYERS >= 3
    leaderboard = get_leaderboard_by_level(1)
    assert len(leaderboard) <= TOP_N_PLAYERS


# --- Test get_overall_leaderboard ---
def test_get_overall_leaderboard_ranking(leaderboard_db):
    """Test overall leaderboard ranking based on sum of best scores."""
    # Expected Totals:
    # P1: 100 (L1) + 200 (L2) + 500 (L3) = 800
    # P2: 110 (L1) + 200 (L2) = 310
    # P3: 80  (L1) + 150 (L2) = 230
    # Expected Order: P1 > P2 > P3
    leaderboard = get_overall_leaderboard()
    assert len(leaderboard) == 3 # Only users with scores
    # Rank 1: Player 1
    assert leaderboard[0]['rank'] == 1
    assert leaderboard[0]['username'] == "player1"
    assert leaderboard[0]['score'] == 800
    # Rank 2: Player 2
    assert leaderboard[1]['rank'] == 2
    assert leaderboard[1]['username'] == "player2"
    assert leaderboard[1]['score'] == 310
    # Rank 3: Player 3
    assert leaderboard[2]['rank'] == 3
    assert leaderboard[2]['username'] == "player3"
    assert leaderboard[2]['score'] == 230

def test_get_overall_leaderboard_tiebreak(leaderboard_db):
    """Test overall leaderboard tie-breaking (requires adding scores)."""
    # Add scores to create a tie in total score
    user1 = User.query.filter_by(username="player1").first()
    user2 = User.query.filter_by(username="player2").first()
    # --- USE RECOMMENDED METHOD FOR UTC TIME ---
    now = datetime.now(UTC) # Use timezone-aware UTC time

    # Make P2's total score also 800, but ensure their contributing best scores
    # have an *earlier* timestamp overall than P1's earliest contributing best score.
    # P1's earliest best score timestamp is from Level 3 (now - 1 day)
    # Add a high score for P2 on a new level with an even earlier timestamp
    db.session.add(Score(user_id=user2.id, score_value=490, level=4, timestamp=now - timedelta(days=2))) # 310 + 490 = 800
    db.session.commit()

    # Expected Order: P2 > P1 (same total score 800, but P2's earliest best score timestamp is earlier)
    leaderboard = get_overall_leaderboard()
    # Need to re-query distinct levels if adding a new level affects the test
    levels = get_distinct_levels()
    assert 4 in levels # Verify level 4 was added for the tiebreak score

    assert len(leaderboard) == 3 # Still only 3 players with scores contributing to overall
    assert leaderboard[0]['rank'] == 1
    assert leaderboard[0]['username'] == "player2"
    assert leaderboard[0]['score'] == 800
    assert leaderboard[1]['rank'] == 2
    assert leaderboard[1]['username'] == "player1"
    assert leaderboard[1]['score'] == 800
    assert leaderboard[2]['rank'] == 3 # P3 remains 3rd
    assert leaderboard[2]['username'] == "player3"
    assert leaderboard[2]['score'] == 230

