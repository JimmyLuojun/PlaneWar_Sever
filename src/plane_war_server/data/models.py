"""Database models for the PlaneWar server application.

Defines SQLAlchemy ORM models representing database tables, such as `User`
and `Score`. Includes helper methods for password hashing.
"""

from datetime import datetime

from flask_login import UserMixin

from ..infrastructure.extensions import bcrypt, db, login_manager


TABLE_USERS = "users"
TABLE_SCORES = "scores"


class User(UserMixin, db.Model):
    """User model for authentication and relationship to scores."""

    __tablename__ = TABLE_USERS

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    scores = db.relationship(
        "Score", backref="player", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bool(bcrypt.check_password_hash(self.password_hash, password))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.username}>"


class Score(db.Model):
    """Score model to store game results."""

    __tablename__ = TABLE_SCORES

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    score_value = db.Column(db.Integer, nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Score {self.score_value} by UserID {self.user_id} on Level {self.level} at {self.timestamp}>"


@login_manager.user_loader
def load_user(user_id):  # pragma: no cover - simple integration callback
    """Reload user by ID for Flask-Login."""
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None

