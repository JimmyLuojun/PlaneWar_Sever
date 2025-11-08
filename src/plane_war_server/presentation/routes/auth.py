"""Handles user authentication routes (login, logout, registration)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ...infrastructure.extensions import db
from ...data.models import User
from ...data.repositories import UserRepository
from ...application.services.auth_service import AuthService


bp = Blueprint("auth", __name__)


def _service() -> AuthService:
    return AuthService(UserRepository(db.session))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("views.leaderboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        error = None
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif password != password2:
            error = "Passwords do not match."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"User '{username}' is already registered."

        if error is None:
            # Use service to create the user
            svc = _service()
            user = svc.register(username, password)
            if user is not None:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("auth.login"))
            else:
                error = "Registration failed."

        if error:
            flash(error, "danger")

    return render_template("auth/register.html", title="Register")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.leaderboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        svc = _service()
        user = svc.verify_login(username, password)

        if user is None:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.username}!", "success")

        next_page = request.args.get("next")
        if not next_page:
            next_page = url_for("views.leaderboard")
        return redirect(next_page)

    return render_template("auth/login.html", title="Log In")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

