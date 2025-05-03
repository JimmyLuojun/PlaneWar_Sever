# PlaneWar Server

A multiplayer plane war game with server-side functionality for score tracking and user management.

## Project Structure

The project is divided into two main components:

1. **Game Client** (`game/`): A Pygame-based client that handles the game logic and rendering
2. **Server** (`server/`): A Flask-based server that handles user authentication, score tracking, and leaderboards

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=server.app
FLASK_ENV=development
DATABASE_URL=sqlite:///game.db
SECRET_KEY=your-secret-key
```

4. Initialize the database:
```bash
poetry run flask db init
poetry run flask db migrate
poetry run flask db upgrade
```

## Running the Application

1. Start the server:
```bash
poetry run flask run
```

2. Run the game client:
```bash
poetry run python game/main.py
```

## Features

- User authentication (login/register)
- Score tracking and leaderboards
- Multiplayer capabilities
- Power-ups and different enemy types
- Multiple levels with increasing difficulty

## Development

- Use `poetry shell` to activate the virtual environment
- Run tests with `poetry run pytest`
- Format code with `poetry run black .`
- Check code style with `poetry run flake8` 