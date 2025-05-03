"""
Authentication routes
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from .models import User
from .extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required.')
            return jsonify({'error': 'Missing fields'}), 400

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return jsonify({'error': 'Username taken'}), 400

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return jsonify({'error': 'Email taken'}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return jsonify({'message': 'Registration successful'}), 201
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': 'Login successful'}), 200
            return redirect(url_for('views.index'))

        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid username or password')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index')) 