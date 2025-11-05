# PlaneWar - Multiplayer Arcade Shooter Game 🎮

A complete multiplayer plane war game with server-side functionality for score tracking, user management, and leaderboards. Built with Pygame for the client and Flask for the server.

**Recently Refactored**: The project has been restructured following modern software engineering practices with event-driven architecture, comprehensive test coverage (18 test modules), and modular design patterns.

## 🏗️ Project Structure

```
PlaneWar_Sever/
├── game/                     # Pygame client
│   ├── main.py              # Main game entry point
│   ├── assets.py            # Asset loading and resource caching
│   ├── loop.py              # Event-driven game loop orchestration
│   ├── states.py            # Application state machine (login, start, running, end)
│   ├── progress.py          # Player progression tracking and level unlocking
│   ├── player.py            # Player sprite & logic
│   ├── enemy.py             # Enemy AI & behavior
│   ├── bullet.py            # Bullet physics
│   ├── powerup.py           # Power-up items
│   ├── explosion.py         # Explosion visual effects
│   ├── background.py        # Scrolling background
│   ├── ui.py                # User interface screens
│   ├── network_client.py    # Server communication
│   ├── settings.py          # Game configuration
│   ├── utils.py             # Utility functions
│   ├── levels/              # Level configurations (JSON files)
│   │   ├── level_1.json
│   │   ├── level_2.json
│   │   ├── level_3.json
│   │   └── level_4.json
│   └── media/               # Game assets
│       ├── images/          # Sprites and backgrounds
│       ├── sounds/          # Sound effects and music
│       └── fonts/           # Game fonts
├── server/                  # Flask server
│   ├── app.py               # Application factory
│   ├── config.py            # Configuration management (Dev, Prod, Test)
│   ├── extensions.py        # Flask extensions initialization
│   ├── api.py               # REST API endpoints
│   ├── auth.py              # Authentication routes
│   ├── models.py            # Database models (User, Score)
│   ├── views.py             # Web page routes
│   ├── leaderboard_service.py  # Leaderboard business logic
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── game.html
│   │   ├── leaderboard.html
│   │   └── auth/
│   │       ├── login.html
│   │       └── register.html
│   └── static/              # CSS styles
│       └── style.css
├── migrations/              # Database migrations (Alembic)
│   ├── versions/            # Migration scripts
│   └── alembic.ini          # Alembic configuration
├── tests/                   # Comprehensive test suite (18 modules)
│   ├── game/                # Game client tests (12 modules)
│   │   ├── test_assets.py
│   │   ├── test_background.py
│   │   ├── test_bullet.py
│   │   ├── test_enemy.py
│   │   ├── test_explosion.py
│   │   ├── test_network_client.py
│   │   ├── test_player.py
│   │   ├── test_powerup.py
│   │   ├── test_progress.py
│   │   ├── test_ui.py
│   │   ├── test_utils.py
│   │   └── conftest.py
│   └── server/              # Server tests (6 modules)
│       ├── test_api.py
│       ├── test_auth.py
│       ├── test_leaderboard_service.py
│       ├── test_models.py
│       ├── test_views.py
│       └── conftest.py
├── .env                     # Environment variables
├── pyproject.toml           # Poetry configuration
└── poetry.lock              # Dependency lock file
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

## 🏛️ Architecture

The project follows modern software engineering practices with clear separation of concerns:

### Architecture Docs
- See `AGENTS.md` for agent-facing coding rules that Codex follows.
- See `docs/architecture/layered-order.md` for the full Refined Layered Order spec and file order.

### Game Architecture (Event-Driven Pattern)
- **assets.py** - Centralized resource loader for all game assets (images, sounds, fonts, level data)
- **loop.py** - Main game loop orchestrator handling event processing and state transitions
- **states.py** - State machine managing application flow (Login → Start Menu → Gameplay → End Screen)
- **progress.py** - Persistent player progression system tracking unlocked levels and scores
- **explosion.py** - Particle effect system for visual feedback

### Server Architecture (MVC Pattern)
- **config.py** - Environment-based configuration (Development, Production, Testing)
- **extensions.py** - Centralized Flask extension initialization (SQLAlchemy, Migrate, Login, Bcrypt)
- **leaderboard_service.py** - Business logic layer separating data access from API routes
- **models.py** - SQLAlchemy ORM models (User, Score)
- **api.py** - RESTful API endpoints for game client communication
- **auth.py** - User authentication and session management
- **views.py** - Web page routes for leaderboard viewing

### Testing Strategy
All tests follow the **AAA (Arrange-Act-Assert)** pattern:
- **Unit Tests**: Individual component testing (sprites, bullets, power-ups)
- **Integration Tests**: API endpoints, database operations, authentication flows
- **Mocking**: Network requests and database interactions for isolated testing

## 🛠️ Development

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/game/     # Game client tests (12 modules)
poetry run pytest tests/server/   # Server tests (6 modules)

# Run with coverage report
poetry run pytest --cov=game --cov=server

# Run specific test file
poetry run pytest tests/game/test_player.py -v
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

- **Total Files**: 80+ files (excluding cache/build files)
- **Python Modules**: 47+ files
  - Game modules: 16 files
  - Server modules: 9 files
  - Test modules: 18 files
- **Game Assets**: 30+ media files
  - Images: 10 sprite/background files
  - Sounds: 10+ audio files
  - Fonts: Game typography assets
- **Test Coverage**: Comprehensive test suite with 18 test modules
  - Game tests: 12 modules (AAA pattern)
  - Server tests: 6 modules (AAA pattern)
- **Database**: SQLite with Alembic migrations (2 versions)
- **Dependencies**: Managed by Poetry
- **Architecture**: Event-driven game loop, MVC server pattern

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

### Completed ✅
- [x] Code refactoring with event-driven architecture
- [x] Comprehensive test suite (18 modules, AAA pattern)
- [x] Modular asset loading system
- [x] State machine for game flow
- [x] Player progression tracking
- [x] Leaderboard service layer

### Planned 🚀
- [ ] Additional game levels (Level 7+)
- [ ] More enemy types and attack patterns
- [ ] Enhanced power-ups (speed boost, invincibility)
- [ ] Achievement system
- [ ] Multiplayer real-time gameplay (WebSocket)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Heroku)
- [ ] Mobile client support

---

**Enjoy playing PlaneWar!** 🚀✈️ 
