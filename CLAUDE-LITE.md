# CLAUDE-LITE.md — Lightweight Coding Guide for Small Scripts & Tools

## When to Use This Guide
- ✅ Small utility scripts (< 500 lines)
- ✅ One-off automation tools
- ✅ Data processing scripts
- ✅ CLI utilities
- ✅ Prototypes & experiments

**For larger projects**, use CLAUDE-STANDARD.md or CLAUDE-FULL.md instead.

---

## File Structure (Simple Scripts)

**REQUIRED: Visual Section Markers**

Even for lightweight scripts, you **MUST** use visual section markers to clearly delineate code sections. This improves readability and maintainability.

**Format**: Use three-line section markers with equals signs:
```
# ============================================================================
# Section Name
# ============================================================================
```

**Rules**:
- Replace simple numbered comments (e.g., `# 1. Imports`) with visual markers
- Only include markers for sections that actually exist in your file
- Use clear, descriptive section names
- This is **mandatory**, not optional

### Procedural Scripts (Most Common)
```python
"""
Brief description of what this script does.

Usage:
    python script.py [arguments]

Example:
    python script.py --input data.csv --output result.json
"""

# 1. Imports
import sys
from pathlib import Path
from typing import Optional

# 2. Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# 3. Helper Functions
def validate_input(data: str) -> bool:
    """Validate input data format."""
    return len(data) > 0

def process_data(input_path: Path) -> dict:
    """Process the input file and return results."""
    # Implementation
    pass

# 4. Main Function
def main() -> int:
    """Main entry point."""
    try:
        # Your logic here
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

# 5. Entry Point
if __name__ == "__main__":
    sys.exit(main())
```

### Object-Oriented Scripts (When Needed)
```python
"""Script description."""

# 1. Imports
from dataclasses import dataclass
from typing import Protocol

# 2. Constants
CONFIG_FILE = "config.json"

# 3. Data Classes
@dataclass
class Config:
    input_path: str
    output_path: str

# 4. Main Class
class DataProcessor:
    """Processes data from input to output."""

    def __init__(self, config: Config):
        self.config = config

    def process(self) -> None:
        """Run the processing."""
        pass

# 5. Main Function
def main() -> int:
    config = Config(input_path="data.csv", output_path="result.json")
    processor = DataProcessor(config)
    processor.process()
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Minimal Coding Standards

### Code Quality (Keep It Simple)
```python
# ✅ Good: Clear, simple, type hints
def calculate_total(prices: list[float]) -> float:
    """Calculate sum of all prices."""
    return sum(prices)

# ❌ Bad: No type hints, unclear name
def calc(x):
    return sum(x)
```

### Type Hints (Required)
```python
from typing import Optional

def process(data: str, timeout: int = 30) -> Optional[dict]:
    """Always use type hints for clarity."""
    pass
```

### Error Handling (Simple & Clear)
```python
def main() -> int:
    try:
        result = process_data()
        print(f"Success: {result}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `process_data`, `validate_input`)
- **Classes**: `PascalCase` (e.g., `DataProcessor`, `ConfigLoader`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Variables**: `snake_case` (e.g., `input_path`, `user_count`)

---

## Minimal Testing (Optional but Recommended)

### Quick Test File
```python
# test_script.py
import pytest
from script import validate_input, process_data

def test_validate_input_accepts_valid_data():
    assert validate_input("valid") is True

def test_validate_input_rejects_empty():
    assert validate_input("") is False

def test_process_data_returns_dict():
    result = process_data(Path("test_data.csv"))
    assert isinstance(result, dict)
```

### Run Tests
```bash
# Add pytest as dev dependency
poetry add --group dev pytest

# Run tests
poetry run pytest test_script.py
```

---

## Minimal Documentation

### README.md (Simple Template)
```markdown
# Script Name

One-line description.

## Installation

\```bash
# Install dependencies with Poetry
poetry install

# Or if you don't have Poetry installed yet
pip install poetry
poetry install
\```

## Usage

\```bash
# Run with Poetry
poetry run python script.py --input data.csv --output result.json

# Or activate the virtual environment first
poetry shell
python script.py --input data.csv --output result.json
\```

## Arguments

- `--input`: Path to input file (required)
- `--output`: Path to output file (required)
- `--verbose`: Enable verbose logging (optional)

## Examples

\```bash
# Process CSV file
poetry run python script.py --input data.csv --output result.json

# With verbose logging
poetry run python script.py --input data.csv --output result.json --verbose
\```
```

### Inline Comments (When Needed)
```python
# ✅ Good: Explain WHY, not WHAT
# Use exponential backoff because API rate limits are aggressive
time.sleep(2 ** retry_count)

# ❌ Bad: Explaining obvious WHAT
# Sleep for 2 seconds
time.sleep(2)
```

---

## Quick Checklist (Before You're Done)

### Before Committing
- [ ] Script has module docstring
- [ ] **Visual section markers (`# ============`) used for all sections**
- [ ] Functions have type hints
- [ ] Main logic in `main()` function
- [ ] Has `if __name__ == "__main__":` block
- [ ] Error handling for common failures
- [ ] README.md with usage example
- [ ] pyproject.toml with dependencies listed

### Optional (If Time Permits)
- [ ] Add 2-3 basic tests (happy path + error case)
- [ ] Add command-line argument parsing (argparse)
- [ ] Add logging instead of print statements
- [ ] Add ruff/basedpyright to dev dependencies for code quality

---

## Poetry Project Setup

### Initialize a New Script Project

```bash
# Create project directory
mkdir my-script && cd my-script

# Initialize Poetry project (interactive)
poetry init

# Or use this minimal pyproject.toml template
```

### Minimal pyproject.toml Template

```toml
[tool.poetry]
name = "my-script"
version = "0.1.0"
description = "Brief description of what this script does"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
ruff = "^0.1.0"
basedpyright = "^1.18.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Common Poetry Commands

```bash
# Install dependencies
poetry install

# Add a runtime dependency
poetry add requests

# Add a dev dependency
poetry add --group dev pytest

# Update dependencies
poetry update

# Run script
poetry run python script.py

# Activate virtual environment
poetry shell

# Show installed packages
poetry show

# Export to requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```

---

## Common Patterns

### Command-Line Arguments (argparse)
```python
import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process data files")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    print(f"Processing {args.input} -> {args.output}")
    return 0
```

### Logging (Better than print)
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("Starting process")
    try:
        result = process_data()
        logger.info(f"Success: {result}")
        return 0
    except Exception as e:
        logger.error(f"Failed: {e}")
        return 1
```

### File I/O (Pathlib is better)
```python
from pathlib import Path

def read_file(path: Path) -> str:
    """Read file content safely."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    return path.read_text(encoding="utf-8")

def write_file(path: Path, content: str) -> None:
    """Write content to file safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
```

### Config Files (JSON/YAML)
```python
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    input_path: str
    output_path: str
    timeout: int = 30

def load_config(path: Path) -> Config:
    """Load configuration from JSON file."""
    data = json.loads(path.read_text())
    return Config(**data)

# Usage
config = load_config(Path("config.json"))
```

---

## When to Upgrade

### Upgrade to CLAUDE-STANDARD.md

Upgrade when your script grows and meets ANY of these:

- [ ] 500-5,000 lines of code
- [ ] Used by other people/teams (internal)
- [ ] Multiple modules/files
- [ ] Requires integration tests
- [ ] Needs CI/CD pipeline
- [ ] Part of a microservice architecture
- [ ] Team of 2-10 developers

**CLAUDE-STANDARD.md** gives you:
- Layered architecture
- 80%+ test coverage
- GitHub Actions CI
- Code review process
- Basic logging & monitoring

### Upgrade to CLAUDE-FULL.md

Upgrade when your project meets ANY of these:

- [ ] > 5,000 lines of code
- [ ] Customer-facing production application
- [ ] Handles sensitive/regulated data (PII, PCI, HIPAA)
- [ ] Requires 99.9%+ uptime SLA
- [ ] Team size > 10 developers
- [ ] Multiple services/microservices
- [ ] Needs advanced monitoring (Prometheus, Grafana)
- [ ] Requires incident response procedures

**CLAUDE-FULL.md** gives you:
- All 7 phases (Design → Code → Test → Review → Deploy → Monitor → Operate)
- Architecture Decision Records (ADRs)
- Advanced security & monitoring
- Incident response runbooks
- Blue-green/canary deployments
- Full enterprise standards

---

## Quick Reference: Script Template

### Step 1: Create pyproject.toml

```toml
[tool.poetry]
name = "my-script"
version = "0.1.0"
description = "Brief description"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Step 2: Create your script (e.g., `script.py`)

```python
#!/usr/bin/env python3
"""
[Description of what this script does]

Usage:
    poetry run python script.py [arguments]
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30


def main() -> int:
    """Main entry point."""
    try:
        logger.info("Starting...")
        # Your code here
        logger.info("Done!")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Step 3: Install dependencies and run

```bash
# Install dependencies
poetry install

# Run the script
poetry run python script.py
```

---

## That's It!

For small scripts, **keep it simple**:
1. Use Poetry for dependency management (pyproject.toml)
2. Clear structure (imports → constants → functions → main)
3. Type hints for all functions
4. Basic error handling
5. README.md with installation & usage

Don't overthink it. Write clean code, add basic tests if you have time, and move on. 🚀
