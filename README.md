# PlaneWar - Multiplayer Arcade Shooter Game 🎮

A complete multiplayer plane war game with server-side functionality for score tracking, user management, and leaderboards. Built with Pygame for the client and Flask for the server.

## 🏗️ Project Structure

```
PlaneWar_Sever/
├── game/                  # Pygame client
│   ├── main.py           # Main game entry point
│   ├── player.py         # Player sprite & logic
│   ├── enemy.py          # Enemy AI & behavior
│   ├── bullet.py         # Bullet physics
│   ├── powerup.py        # Power-up items
│   ├── background.py     # Scrolling background
│   ├── ui.py             # User interface screens
│   ├── network_client.py # Server communication
│   ├── settings.py       # Game configuration
│   ├── utils.py          # Utility functions
│   ├── levels/           # Level configurations
│   └── media/            # Game assets (images, sounds, fonts)
├── server/               # Flask server
│   ├── app.py            # Application factory
│   ├── api.py            # REST API endpoints
│   ├── auth.py           # Authentication routes
│   ├── models.py         # Database models
│   ├── views.py          # Web page routes
│   ├── templates/        # HTML templates
│   └── static/           # CSS styles
├── migrations/           # Database migrations
├── tests/                # Comprehensive test suite
└── pyproject.toml        # Poetry configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Poetry (Python package manager)

### Installation

1. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Clone and setup the project**:
```bash
git clone <repository-url>
cd PlaneWar_Sever
poetry install
```

3. **Configure environment** (`.env` file is already included):
```bash
# The .env file contains:
FLASK_APP=server.app
FLASK_ENV=development
DATABASE_URL=sqlite:///server/database.db
SECRET_KEY=garkEv-wocgor-wahko5
```

4. **Initialize database**:
```bash
poetry run flask db upgrade
```

## 🎮 Running the Game

### Option 1: Run Game Only (Recommended for testing)
```bash
poetry run python -m game.main
```

### Option 2: Full Server + Game Experience
```bash
# Terminal 1 - Start the Flask server
poetry run flask run --host=0.0.0.0 --port=8000

# Terminal 2 - Start the game client
poetry run python -m game.main
```

### Option 3: Using Poetry Scripts
```bash
# For the game client
poetry run run-planewar-game

# For the server
poetry run run-planewar-server
```

## 🎯 Game Features

### Core Gameplay
- **4 Progressive Levels** with increasing difficulty
- **Multiple Enemy Types** (Enemy1-4 + Boss enemies)
- **Power-up System** (Shield, Double Shot, Bomb)
- **Boss Battles** with unique mechanics
- **Score Tracking** per level

### Multiplayer Features
- **User Authentication** (Login/Register)
- **Global Leaderboards** with rankings
- **Score Submission** to server
- **Progress Tracking** across sessions

### Technical Features
- **Responsive Controls** (Keyboard + Mouse)
- **Sound Effects & Background Music**
- **Smooth Animations** and particle effects
- **Network Integration** for online features

## 🛠️ Development

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/game/     # Game client tests
poetry run pytest tests/server/   # Server tests
```

### Code Quality
```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .

# Type checking (if using mypy)
poetry run mypy .
```

### Database Management
```bash
# Create new migration
poetry run flask db migrate -m "Description"

# Apply migrations
poetry run flask db upgrade

# Reset database
poetry run flask db downgrade base
poetry run flask db upgrade
```

## 🌐 Server Features

### Web Interface
- **Leaderboard Viewing**: `http://localhost:8000/leaderboard`
- **User Registration**: `http://localhost:8000/auth/register`
- **User Login**: `http://localhost:8000/auth/login`

### API Endpoints
- `POST /api/login` - User authentication
- `POST /api/submit_score` - Score submission
- `POST /api/logout` - User logout
- `GET /api/leaderboard` - Leaderboard data

## 🎮 Game Controls

### Keyboard Controls
- **WASD** or **Arrow Keys**: Move player
- **Spacebar**: Shoot
- **B**: Use bomb (if available)
- **ESC**: Pause/Quit

### Mouse Controls
- **Left Click**: Shoot
- **Mouse Movement**: Aim (in some modes)

## 🐛 Troubleshooting

### Common Issues

**HTTP 503 Service Unavailable**
- Ensure server is running on port 8000
- Check if proxy settings are interfering
- Restart both server and game client

**Database Errors**
```bash
# Reset database
poetry run flask db downgrade base
poetry run flask db upgrade
```

**Port Conflicts**
- Server runs on port 8000 by default
- If port 5000 is used, macOS Control Center may interfere
- Change port in `game/settings.py` if needed

**Game Won't Start**
```bash
# Check dependencies
poetry install

# Verify Python version
python --version  # Should be 3.10+
```

### Debug Mode
```bash
# Run server in debug mode
FLASK_ENV=development poetry run flask run --debug

# Run game with verbose logging
poetry run python -m game.main --debug
```

## 📊 Project Statistics

- **Total Files**: 97 files
- **Python Files**: 35+ files
- **Game Assets**: 20+ media files
- **Test Coverage**: Comprehensive test suite
- **Database**: SQLite with migrations
- **Dependencies**: Managed by Poetry

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🎯 Roadmap

- [ ] Additional game levels
- [ ] More enemy types
- [ ] Enhanced power-ups
- [ ] Multiplayer real-time gameplay
- [ ] Mobile client support
- [ ] Cloud deployment

---

**Enjoy playing PlaneWar!** 🚀✈️ 