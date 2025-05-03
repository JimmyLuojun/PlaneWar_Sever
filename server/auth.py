# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from .models import User  # Import User model
from .extensions import db, bcrypt # Import db and bcrypt from extensions

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('views.leaderboard')) # Redirect if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2') # Password confirmation field

        # Basic Validation
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != password2:
            error = 'Passwords do not match.'
        elif User.query.filter_by(username=username).first() is not None:
             error = f"User '{username}' is already registered."

        if error is None:
            # Create new user and hash password
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger') # Display error message

    # If GET request or validation fails, show the form
    return render_template('auth/register.html', title='Register')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('views.leaderboard')) # Redirect if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on' # Checkbox value

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        # Log the user in using Flask-Login
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to the page the user was trying to access, or the leaderboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('views.leaderboard') # Default redirect
        return redirect(next_page)

    # If GET request, show the form
    return render_template('auth/login.html', title='Log In')

@bp.route('/logout')
@login_required # User must be logged in to log out
def logout():
    """Handles user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login')) # Redirect to login page after logout