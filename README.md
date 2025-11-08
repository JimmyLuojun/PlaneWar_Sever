# PlaneWar — Multiplayer Arcade Shooter 🎮

Networked plane shooter with a Flask server (auth, scores, leaderboards) and a Pygame client. The codebase follows a layered structure with clear separation between presentation, application, data, and infrastructure.

## 🏗️ Project Structure

```
PlaneWar_Server/
├── src/
│   └── plane_war_server/       # App package (Flask server + game client)
│       ├── main.py             # Flask app factory + dev entry
│       ├── config.py           # Environment-driven configuration
│       ├── infrastructure/
│       │   └── extensions.py
│       ├── data/
│       │   ├── models.py
│       │   ├── repositories.py
│       │   └── progress_store.py
│       ├── application/
│       │   └── services/
│       │       ├── auth_service.py
│       │       ├── leaderboard_service.py
│       │       └── progress_service.py
│       ├── presentation/
│       │   └── routes/
│       │       ├── api.py
│       │       ├── auth.py
│       │       └── views.py
│       ├── templates/          # Jinja templates
│       ├── static/             # CSS/JS/assets
│       └── game/               # Pygame client
│           ├── main.py         # Game entry point
│           ├── assets.py, loop.py, states.py, ...
│           ├── levels/         # Level configs (JSON)
│           └── media/          # Images, sounds, fonts
├── migrations/              # Database migrations (Alembic)
│   ├── versions/            # Migration scripts
│   └── alembic.ini          # Alembic configuration
├── tests/                   # Test suite (unit + integration)
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
- Poetry

### Installation

1. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Clone and setup the project**:
```bash
git clone <repository-url>
cd PlaneWar_Server
poetry install
```

3. **Configure environment** (`.env` or copy from `.env.example`):
```bash
# Minimal required
FLASK_APP=plane_war_server:create_app
FLASK_ENV=development
SECRET_KEY=change-me-in-prod   # Use a strong random value in production

# Optional database URL (defaults to a local SQLite file)
# DATABASE_URL=sqlite:///database.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/planewar
```

4. **Initialize database**:
```bash
poetry run flask db upgrade
```

## 🎮 Running the Game

### Option 1: Run Game Only (recommended for testing)
```bash
poetry run python -m plane_war_server.game.main
```

### Option 2: Full Server + Game Experience
```bash
# Terminal 1 - Start the Flask server
poetry run flask run --host=0.0.0.0 --port=8000

# Terminal 2 - Start the game client
poetry run python -m plane_war_server.game.main
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
- **6 Progressive Levels** with increasing difficulty
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
- See `CLAUDE-STANDARD.md` for the coding guide followed in this repo.

### Game Architecture (Event-Driven Pattern)
- **assets.py** - Centralized resource loader for all game assets (images, sounds, fonts, level data)
- **loop.py** - Main game loop orchestrator handling event processing and state transitions
- **states.py** - State machine managing application flow (Login → Start Menu → Gameplay → End Screen)
- **progress.py** - Persistent player progression system tracking unlocked levels and scores
- **explosion.py** - Particle effect system for visual feedback

### Server Architecture (Layered)
- **presentation/** - Blueprints and HTTP handlers (api, auth, views)
- **application/** - Use-case services (auth, leaderboard, progress)
- **data/** - ORM models, repositories, progress store
- **infrastructure/** - Flask extensions and wiring

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
poetry run pytest

# Run specific test file
poetry run pytest tests/game/test_player.py -v
```

### Code Quality
```bash
# Lint code
poetry run ruff check .

# Format code (if using ruff format)
poetry run ruff format .
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
- `GET /api/progress` - Get max unlocked level (auth required)
- `POST /api/progress` - Set max unlocked level (auth required)

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
poetry run python -m plane_war_server.game.main --debug
```

## ⚙️ Configuration

Environment variables consumed by the server (see `.env.example`):
- `FLASK_APP` — should be `plane_war_server:create_app`
- `FLASK_ENV` — one of `development`, `production`, `testing`
- `SECRET_KEY` — required in production
- `DATABASE_URL` — SQLAlchemy URL (optional; defaults to SQLite file)

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
