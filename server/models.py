# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/models.py
from .extensions import db, login_manager, bcrypt
from flask_login import UserMixin
import datetime

@login_manager.user_loader
def load_user(user_id):
    """Callback used by Flask-Login to reload the user object from the user ID stored in the session."""
    try:
        return db.session.get(User, int(user_id)) # Use db.session.get for primary key lookup
    except (TypeError, ValueError):
        return None

class User(UserMixin, db.Model):
    """User model for authentication and relationship to scores."""
    __tablename__ = 'users' # Optional: Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Define the one-to-many relationship with Score
    # cascade="all, delete-orphan": ensures scores are deleted if the user is deleted
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
    __tablename__ = 'scores' # Optional: Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    score_value = db.Column(db.Integer, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    level_reached = db.Column(db.Integer, nullable=True) # Optional
    # Define the foreign key relationship back to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Score {self.score_value} by User ID {self.user_id} at {self.timestamp}>'