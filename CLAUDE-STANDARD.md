# CLAUDE-STANDARD.md — Standard Coding Guide for Small-to-Medium Projects

## When to Use This Guide
- ✅ Small to medium projects (500-5,000 lines)
- ✅ Internal tools & services
- ✅ Microservices
- ✅ Libraries & packages
- ✅ API backends (internal use)
- ✅ Projects with 2-10 developers

**For smaller scripts** (< 500 lines), use **CLAUDE-LITE.md**.
**For production applications** (> 5,000 lines), use **CLAUDE-FULL.md**.

---

# TABLE OF CONTENTS

1. [Design & Planning](#phase-1-design--planning)
2. [Coding Standards](#phase-2-coding-standards)
3. [Testing](#phase-3-testing)
4. [Code Review](#phase-4-code-review)
5. [CI/CD & Deployment](#phase-5-cicd--deployment)
6. [Basic Monitoring](#phase-6-basic-monitoring)
7. [Common Patterns & Examples](#common-patterns--examples)
8. [References & Resources](#references--resources)
9. [When to Switch Tiers](#when-to-switch-tiers)
10. [Quick Reference](#quick-reference-checklist)

---

# ═══════════════════════════════════════════════════════════
# PHASE 1: DESIGN & PLANNING
# ═══════════════════════════════════════════════════════════

## Architecture Overview

### Layered Architecture (Recommended)
Use a simplified layered approach:

```
┌─────────────────────────────────┐
│   Presentation Layer            │  Controllers/Routes/CLI
│   (HTTP handlers, CLI)          │
├─────────────────────────────────┤
│   Application Layer             │  Business Logic/Use Cases
│   (Core logic)                  │
├─────────────────────────────────┤
│   Data Layer                    │  Database/External APIs
│   (Persistence, I/O)            │
├─────────────────────────────────┤
│   Infrastructure                │  Config, DI, Bootstrap
│   (Configuration)               │
└─────────────────────────────────┘
```

**Dependency Rule**: Each layer only depends on the layer below it.

### Project Structure Example

```
my-project/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config.py            # Configuration
│       ├── presentation/        # HTTP/CLI layer
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── application/         # Business logic
│       │   ├── __init__.py
│       │   └── services.py
│       └── data/                # Data access
│           ├── __init__.py
│           ├── models.py
│           └── repositories.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── test_services.py
    │   └── test_repositories.py
    └── integration/
        └── test_api.py
```

## Design Documentation (Lightweight)

### README.md (Required)
```markdown
# Project Name

Brief description (2-3 sentences).

## Features
- Feature 1
- Feature 2
- Feature 3

## Quick Start

\```bash
# Install
poetry install

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
poetry run python -m my_project

# Test
poetry run pytest
\```

## Architecture
Brief overview of how the system is structured.
See docs/architecture.md for details (optional).

## API Documentation
Link to API docs or inline examples.

## Development

\```bash
# Install dev dependencies
poetry install

# Run tests
poetry run pytest

# Run linter
poetry run ruff check .

# Run type checker
poetry run basedpyright
\```

## Configuration
List of environment variables and their purpose.

## License
[Your License]
```

### docs/architecture.md (Optional)
```markdown
# Architecture

## Overview
High-level description of the system.

## Components
- **Component A**: What it does
- **Component B**: What it does

## Data Flow
How data moves through the system.

## Key Design Decisions
Why we chose X over Y.
```

### Design Checklist
- [ ] README.md exists with setup instructions
- [ ] Project structure follows layered architecture
- [ ] .env.example with all required config
- [ ] API endpoints documented (if applicable)
- [ ] Database schema documented (if applicable)

---

# ═══════════════════════════════════════════════════════════
# PHASE 2: CODING STANDARDS
# ═══════════════════════════════════════════════════════════

## File Organization (Universal Order)

Every Python module should follow this order:

```python
"""Module docstring: What this module does."""

# 1. Imports (grouped: stdlib, third-party, local)
import sys
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import select

from my_project.data.models import User
from my_project.config import settings

# 2. Type definitions
from typing import Protocol

class UserRepository(Protocol):
    """Interface for user data access."""
    def get(self, user_id: int) -> User | None: ...

# 3. Constants
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30

# 4. Exceptions
class UserNotFoundError(Exception):
    """Raised when user doesn't exist."""

# 5. Data classes / Models
from dataclasses import dataclass

@dataclass
class UserDTO:
    id: int
    email: str

# 6. Helper functions
def _validate_email(email: str) -> bool:
    """Private helper to validate email format."""
    return "@" in email

# 7. Core logic (classes, main functions)
class UserService:
    """Handles user business logic."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user(self, user_id: int) -> UserDTO:
        user = self.repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return UserDTO(id=user.id, email=user.email)

# 8. Public API / exports
__all__ = ["UserService", "UserDTO", "UserNotFoundError"]
```

## Layer Responsibilities

### Presentation Layer (HTTP/CLI)
**Purpose**: Handle external input/output

```python
# presentation/routes.py
from fastapi import APIRouter, HTTPException
from my_project.application.services import UserService

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: int, user_service: UserService):
    """
    Thin controller:
    1. Validate input (FastAPI does this)
    2. Call service
    3. Format response
    4. Handle errors
    """
    try:
        user = user_service.get_user(user_id)
        return {"id": user.id, "email": user.email}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
```

**Rules**:
- ✅ Validate input
- ✅ Call application layer
- ✅ Format response
- ❌ NO business logic
- ❌ NO direct database access

### Application Layer (Business Logic)
**Purpose**: Implement use cases and business rules

```python
# application/services.py
from my_project.data.repositories import UserRepository

class UserService:
    """User business logic."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user(self, user_id: int) -> UserDTO:
        """Get user by ID."""
        if user_id <= 0:
            raise ValueError("User ID must be positive")

        user = self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        return UserDTO(id=user.id, email=user.email)
```

**Rules**:
- ✅ Business logic goes here
- ✅ Orchestrate multiple operations
- ✅ Depend on interfaces (protocols)
- ❌ NO framework imports (FastAPI, Flask, etc.)
- ❌ NO direct database/ORM code

### Data Layer (Persistence)
**Purpose**: Handle data storage and retrieval

```python
# data/repositories.py
from sqlalchemy.orm import Session
from my_project.data.models import User

class SqlUserRepository:
    """SQL implementation of user repository."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> User | None:
        """Fetch user from database."""
        return self.session.get(User, user_id)

    def save(self, user: User) -> None:
        """Persist user to database."""
        self.session.add(user)
        self.session.commit()
```

**Rules**:
- ✅ Database/API access here
- ✅ Framework code allowed (SQLAlchemy, requests, etc.)
- ✅ Map errors to domain errors
- ❌ NO business logic

## Code Quality Standards

### Type Hints (Required)
```python
# ✅ Good: All signatures have type hints
def process_user(user_id: int, active: bool = True) -> UserDTO | None:
    """Process a user."""
    pass

# ❌ Bad: No type hints
def process_user(user_id, active=True):
    pass
```

### Docstrings (Required for Public APIs)
```python
# ✅ Good: Clear docstring with Google style
def calculate_discount(price: float, user_type: str) -> float:
    """
    Calculate discount based on user type.

    Args:
        price: Original price in dollars
        user_type: One of 'regular', 'premium', 'vip'

    Returns:
        Final price after discount

    Raises:
        ValueError: If user_type is invalid
    """
    pass

# ❌ Bad: No docstring for public function
def calculate_discount(price: float, user_type: str) -> float:
    return price * 0.9
```

### Naming Conventions
- **Modules/Packages**: `lowercase_with_underscores`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Error Handling
```python
# ✅ Good: Specific exceptions, clear messages
class InvalidEmailError(ValueError):
    """Email format is invalid."""

def validate_email(email: str) -> None:
    if "@" not in email:
        raise InvalidEmailError(f"Invalid email: {email}")

# ❌ Bad: Generic exceptions, no context
def validate_email(email: str) -> None:
    if "@" not in email:
        raise Exception("Bad email")
```

## Dependencies & Configuration

### pyproject.toml Structure
```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "Brief description"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "my_project", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
sqlalchemy = "^2.0.0"
pydantic-settings = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
basedpyright = "^1.18.0"
httpx = "^0.25.0"  # For testing FastAPI

[tool.poetry.scripts]
my-project = "my_project.main:main"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "standard"
reportMissingTypeStubs = false
reportUnknownMemberType = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Configuration Management
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration."""

    # App settings
    app_name: str = "My Project"
    debug: bool = False

    # Database
    database_url: str

    # API Keys
    api_key: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
```

### .env.example
```bash
# Application
APP_NAME="My Project"
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb

# External APIs
API_KEY=your-api-key-here
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 3: TESTING
# ═══════════════════════════════════════════════════════════

## Testing Strategy

### Test Coverage Goals
- **Overall**: Minimum 80% coverage
- **Business Logic**: 90%+ coverage
- **Data Layer**: 80%+ coverage
- **Presentation**: 70%+ (don't duplicate business logic tests)

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_services.py     # Business logic tests
│   └── test_repositories.py # Data access tests (mocked)
└── integration/
    ├── test_api.py          # API endpoint tests
    └── test_database.py     # Real database tests
```

## Unit Tests

### Testing Business Logic (Application Layer)
```python
# tests/unit/test_services.py
import pytest
from my_project.application.services import UserService, UserNotFoundError
from my_project.data.repositories import UserRepository

class MockUserRepository:
    """Mock repository for testing."""

    def __init__(self):
        self.users = {}

    def get(self, user_id: int):
        return self.users.get(user_id)

    def save(self, user):
        self.users[user.id] = user

def test_get_user_success():
    # Arrange
    repo = MockUserRepository()
    repo.users[1] = User(id=1, email="test@example.com")
    service = UserService(repo)

    # Act
    user = service.get_user(1)

    # Assert
    assert user.id == 1
    assert user.email == "test@example.com"

def test_get_user_not_found():
    # Arrange
    repo = MockUserRepository()
    service = UserService(repo)

    # Act & Assert
    with pytest.raises(UserNotFoundError):
        service.get_user(999)

def test_get_user_invalid_id():
    # Arrange
    repo = MockUserRepository()
    service = UserService(repo)

    # Act & Assert
    with pytest.raises(ValueError, match="must be positive"):
        service.get_user(-1)
```

### Testing Data Layer
```python
# tests/unit/test_repositories.py
import pytest
from unittest.mock import Mock, MagicMock
from my_project.data.repositories import SqlUserRepository
from my_project.data.models import User

def test_get_user_from_database():
    # Arrange
    mock_session = Mock()
    mock_session.get.return_value = User(id=1, email="test@example.com")
    repo = SqlUserRepository(mock_session)

    # Act
    user = repo.get(1)

    # Assert
    assert user.id == 1
    mock_session.get.assert_called_once_with(User, 1)

def test_save_user_commits():
    # Arrange
    mock_session = Mock()
    repo = SqlUserRepository(mock_session)
    user = User(id=1, email="test@example.com")

    # Act
    repo.save(user)

    # Assert
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
```

## Integration Tests

### Testing API Endpoints
```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from my_project.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_user_endpoint_success(client):
    # Act
    response = client.get("/users/1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data

def test_get_user_endpoint_not_found(client):
    # Act
    response = client.get("/users/999")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

### Testing with Real Database (Optional)
```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from my_project.data.models import Base, User
from my_project.data.repositories import SqlUserRepository

@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

def test_repository_with_real_db(db_session):
    # Arrange
    repo = SqlUserRepository(db_session)
    user = User(id=1, email="test@example.com")

    # Act
    repo.save(user)
    retrieved = repo.get(1)

    # Assert
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
```

## Fixtures (conftest.py)
```python
# tests/conftest.py
import pytest
from my_project.data.repositories import UserRepository

@pytest.fixture
def mock_user_repo():
    """Shared mock repository fixture."""
    class MockRepo:
        def __init__(self):
            self.users = {}

        def get(self, user_id: int):
            return self.users.get(user_id)

        def save(self, user):
            self.users[user.id] = user

    return MockRepo()
```

## Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_services.py

# Run tests matching pattern
poetry run pytest -k "test_user"

# Run with verbose output
poetry run pytest -v

# Run and stop on first failure
poetry run pytest -x
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 4: CODE REVIEW
# ═══════════════════════════════════════════════════════════

## Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Description
Brief summary of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring
- [ ] Documentation
- [ ] Other (specify):

## Changes Made
- Change 1
- Change 2

## Testing
How was this tested?
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Coverage not decreased
- [ ] Documentation updated (if needed)
```

## Code Review Checklist

### For Reviewers

**Functionality**:
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

**Code Quality**:
- [ ] Follows file organization order
- [ ] Naming is clear and consistent
- [ ] No code duplication
- [ ] Functions are small and focused
- [ ] Type hints present

**Testing**:
- [ ] Tests added for new functionality
- [ ] Tests cover happy path and error cases
- [ ] Coverage meets minimum 80%
- [ ] Tests are clear and maintainable

**Architecture**:
- [ ] Respects layer boundaries
- [ ] No upward dependencies
- [ ] Proper separation of concerns

**Security** (if applicable):
- [ ] No secrets in code
- [ ] Input validation present
- [ ] No SQL injection risks
- [ ] Authentication/authorization checked

**Documentation**:
- [ ] Public functions have docstrings
- [ ] Complex logic has comments
- [ ] README updated (if needed)

## Review Guidelines

### PR Size
- **Small** (< 200 lines): Fast review (< 1 hour)
- **Medium** (200-500 lines): Standard review (< 1 day)
- **Large** (> 500 lines): Should be split into smaller PRs

### Approval Requirements
- **Standard PRs**: 1 approval
- **Breaking changes**: 2 approvals

### Feedback Format
```markdown
# Blocking (must fix before merge)
- Issue that breaks functionality
- Security vulnerability
- Major architecture violation

# Suggestions (nice to have)
- Minor improvements
- Style preferences
- Performance optimizations

# Questions
- Clarification requests
- Alternative approaches
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 5: CI/CD & DEPLOYMENT
# ═══════════════════════════════════════════════════════════

## CI Pipeline (GitHub Actions)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: poetry install

    - name: Run linter
      run: poetry run ruff check .

    - name: Run type checker
      run: poetry run basedpyright

    - name: Run tests
      run: poetry run pytest --cov=src --cov-report=xml

    - name: Check coverage
      run: poetry run coverage report --fail-under=80

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Deployment

### Docker Support (Optional but Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (without dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY src/ ./src/

# Run the application
CMD ["python", "-m", "my_project"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Simple Deployment Script

Create `scripts/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Deploying to $ENV environment..."

# Pull latest code
git pull origin main

# Install dependencies
poetry install --no-dev

# Run database migrations (if using Alembic)
poetry run alembic upgrade head

# Restart service (adjust for your setup)
sudo systemctl restart my-project

echo "Deployment complete!"
```

### Environment-Specific Configs

```bash
# .env.development
DEBUG=true
DATABASE_URL=sqlite:///dev.db

# .env.production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/mydb
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 6: BASIC MONITORING
# ═══════════════════════════════════════════════════════════

## Logging

### Basic Logging Setup
```python
# config.py
import logging
import sys

def setup_logging(debug: bool = False):
    """Configure application logging."""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

# Usage in main.py
from my_project.config import setup_logging, settings

setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)
```

### Logging in Code
```python
import logging

logger = logging.getLogger(__name__)

def process_user(user_id: int):
    logger.info(f"Processing user {user_id}")

    try:
        # Process
        logger.debug(f"User {user_id} data: {data}")
        logger.info(f"User {user_id} processed successfully")
    except Exception as e:
        logger.error(f"Failed to process user {user_id}: {e}")
        raise
```

## Health Checks

### Simple Health Endpoint
```python
# presentation/routes.py
@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

@router.get("/health/db")
def database_health_check(db: Session):
    """Check database connection."""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

## Basic Metrics (Optional)

### Simple Request Tracking
```python
# middleware/metrics.py
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Log request duration and status."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s"
    )

    return response

# Add to FastAPI app
app.middleware("http")(log_requests)
```

---

# ═══════════════════════════════════════════════════════════
# QUICK REFERENCE CHECKLIST
# ═══════════════════════════════════════════════════════════

## Project Setup
- [ ] Initialize with Poetry (`poetry init`)
- [ ] Create project structure (src/, tests/)
- [ ] Add pyproject.toml with dependencies
- [ ] Create .env.example
- [ ] Write README.md with setup instructions
- [ ] Set up Git repository
- [ ] Add .gitignore

## Before Coding
- [ ] Review architecture design
- [ ] Understand layer responsibilities
- [ ] Plan which layers are affected
- [ ] Write test scenarios

## During Coding
- [ ] Follow file organization order
- [ ] Add type hints to all functions
- [ ] Add docstrings to public APIs
- [ ] Write tests alongside code
- [ ] Keep functions small (< 50 lines)
- [ ] Respect layer boundaries

## Before Committing
- [ ] Run linter (`poetry run ruff check .`)
- [ ] Run type checker (`poetry run basedpyright`)
- [ ] Run tests (`poetry run pytest`)
- [ ] Check coverage (>= 80%)
- [ ] Review your own code
- [ ] Update documentation

## Before Creating PR
- [ ] All tests pass
- [ ] Coverage meets threshold
- [ ] No linter errors
- [ ] README updated (if needed)
- [ ] Write clear PR description
- [ ] Self-review completed

## Before Deploying
- [ ] PR approved and merged
- [ ] CI pipeline green
- [ ] Test in staging (if available)
- [ ] Database migrations tested
- [ ] Environment variables configured

---

# ═══════════════════════════════════════════════════════════
# COMMON PATTERNS & EXAMPLES
# ═══════════════════════════════════════════════════════════

## Dependency Injection Pattern

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from my_project.data.database import get_db
from my_project.data.repositories import SqlUserRepository
from my_project.application.services import UserService

app = FastAPI()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService."""
    repo = SqlUserRepository(db)
    return UserService(repo)

@app.get("/users/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_user(user_id)
```

## Database Setup (SQLAlchemy)

```python
# data/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from my_project.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## CLI Entry Point

```python
# main.py
import sys
import argparse
from my_project.config import setup_logging

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="My Project")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    try:
        # Your application logic
        return 0
    except Exception as e:
        logger.error(f"Application failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

# ═══════════════════════════════════════════════════════════
# REFERENCES & RESOURCES
# ═══════════════════════════════════════════════════════════

## Internal Documentation

### Detailed Architecture Specification
- **layered-order.md**: Complete architectural reference
  - Location: `docs/architecture/layered-order.md`
  - Defines: 5-layer architecture, universal file order, ports/error mapping
  - Testing strategy by layer

### How to Use layered-order.md in Your Project

**Step 1: Create docs folder**
```bash
mkdir -p docs/architecture
```

**Step 2: Symlink the master specification**
```bash
ln -sf "/Users/junluo/Documents/Obsidian_Vault/05.Tools/Prompts/Coding Prompts/layered-order.md" \
       ./docs/architecture/layered-order.md
```

**Step 3: Verify**
```bash
ls -la docs/architecture/layered-order.md
```

Now AI agents (Claude, Codex, Gemini) can automatically read the detailed architecture specs!

### Other Project Documentation
- **API specifications**: `docs/api/` (OpenAPI/Swagger files)
- **README.md**: Setup, quick start, development guide
- **CHANGELOG.md**: Version history (Keep-a-Changelog format)

## External Resources

### Architecture & Design Patterns
- **Clean Architecture** by Robert C. Martin
  - Layered architecture principles
  - Dependency inversion
  - https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

- **Domain-Driven Design** by Eric Evans
  - Bounded contexts
  - Entities vs Value Objects
  - https://www.domainlanguage.com/ddd/

### Python Best Practices
- **PEP 8**: Python Style Guide
  - https://peps.python.org/pep-0008/

- **Type Hints Guide** (PEP 484)
  - https://peps.python.org/pep-0484/

- **basedpyright**: Modern type checker
  - Faster and more accurate than mypy
  - Better IDE integration
  - https://github.com/DetachHead/basedpyright

### Testing
- **Pytest Documentation**
  - https://docs.pytest.org/

- **Test Pyramid** concept
  - Unit tests (most) → Integration tests (some) → E2E tests (few)

### CI/CD & DevOps
- **GitHub Actions Documentation**
  - https://docs.github.com/en/actions

- **Docker Best Practices**
  - https://docs.docker.com/develop/dev-best-practices/

### Poetry (Dependency Management)
- **Poetry Documentation**
  - https://python-poetry.org/docs/

---

# ═══════════════════════════════════════════════════════════
# WHEN TO SWITCH TIERS
# ═══════════════════════════════════════════════════════════

## Downgrade to CLAUDE-LITE.md

Consider downgrading if your project:

- [ ] < 500 lines of code
- [ ] Single file or simple script
- [ ] Used only by you (not a team)
- [ ] Doesn't need CI/CD
- [ ] Minimal testing is sufficient

**CLAUDE-LITE.md** is perfect for:
- Quick utilities and tools
- One-off scripts
- Prototypes
- Learning projects

## Upgrade to CLAUDE-FULL.md

Consider upgrading when your project meets ANY of these:

- [ ] > 5,000 lines of code
- [ ] Customer-facing production application
- [ ] Handles sensitive/regulated data (PII, PCI, HIPAA)
- [ ] Requires 99.9%+ uptime SLA
- [ ] Team size > 10 developers
- [ ] Multiple services/microservices
- [ ] Needs advanced monitoring (Prometheus, Grafana)
- [ ] Requires incident response procedures
- [ ] Needs compliance (SOC2, ISO)

**CLAUDE-FULL.md** gives you:
- All 7 phases (Design → Code → Test → Review → Deploy → Monitor → Operate)
- Architecture Decision Records (ADRs)
- Feature specifications before coding
- Advanced security scanning (OWASP Top 10)
- Comprehensive monitoring & alerting
- Incident response runbooks
- Blue-green/canary deployments
- Database migration procedures
- Full enterprise standards

---

# SUMMARY

For standard projects (500-5,000 lines):

✅ **Use**:
- Layered architecture
- Poetry for dependency management
- 80%+ test coverage
- Basic CI/CD pipeline
- Code reviews with PR template
- Simple logging and health checks

❌ **Skip** (compared to FULL):
- Architecture Decision Records
- Comprehensive monitoring/alerting
- Detailed runbooks
- Advanced security scanning
- Multiple deployment environments
- Incident response procedures

**Balance**: Professional standards without enterprise overhead. 🎯
