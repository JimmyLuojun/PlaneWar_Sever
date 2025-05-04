"""Database models for the PlaneWar server application.

Defines SQLAlchemy ORM models representing database tables, such as `User`
(for player accounts) and `Score` (for storing game scores). Includes column
definitions, relationships between models, and potentially helper methods
(e.g., password hashing).
"""
# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/models.py
from .extensions import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime # Correct import

@login_manager.user_loader
def load_user(user_id):
    """Callback used by Flask-Login to reload the user object from the user ID stored in the session."""
    try:
        # Use db.session.get for efficient primary key lookup
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None

class User(UserMixin, db.Model):
    """User model for authentication and relationship to scores."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationship: One user has many scores.
    scores = db.relationship('Score', backref='player', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Score(db.Model):
    """Score model to store game results."""
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign key relationship back to User table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # Value of the score achieved
    score_value = db.Column(db.Integer, nullable=False, index=True)
    # Level on which the score was achieved (ensure this is correct)
    level = db.Column(db.Integer, nullable=False, index=True) # <<< MAKE SURE THIS LINE IS CORRECT
    # Timestamp when the score was recorded (defaults to UTC now)
    timestamp = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        # Updated repr to include level
        return f'<Score {self.score_value} by UserID {self.user_id} on Level {self.level} at {self.timestamp}>'

