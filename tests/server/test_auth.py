"""Tests for the auth blueprint.

This module contains tests for the authentication routes, including
registration, login, and logout functionality.
"""

from flask import url_for

from plane_war_server.data.models import User


def test_register(client, db):
    """Test user registration."""
    # Test GET request
    response = client.get(url_for("auth.register"))
    assert response.status_code == 200

    # Test POST request with valid data
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful! Please log in." in response.data
    assert User.query.filter_by(username="testuser").first() is not None


def test_register_with_existing_user(client, db):
    """Test registration with a username that is already taken."""
    # Create a user to conflict with
    client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
    )

    # Test POST request with existing username
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"User &#39;testuser&#39; is already registered." in response.data

def test_register_with_mismatched_passwords(client, db):
    """Test registration with mismatched passwords."""
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "wrongpassword",
        },
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_login(client, db):
    """Test user login."""
    # Register a user to log in with
    client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
    )

    # Test GET request
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200

    # Test POST request with valid credentials
    response = client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back, testuser!" in response.data


def test_login_with_invalid_username(client, db):
    """Test login with an invalid username."""
    response = client.post(
        url_for("auth.login"),
        data={"username": "wronguser", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_login_with_invalid_password(client, db):
    """Test login with an invalid password."""
    # Register a user to log in with
    client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
    )

    # Test POST request with invalid password
    response = client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_logout(client, db):
    """Test user logout."""
    # Register and log in a user
    client.post(
        url_for("auth.register"),
        data={
            "username": "testuser",
            "password": "password",
            "password2": "password",
        },
    )
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Test logout
    response = client.get(url_for("auth.logout"), follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
