Gemini Coding Standards

This project uses shared conventions for structure and readability. When writing or refactoring code as Codex, follow these orders (mirroring CLAUDE.md) and keep changes minimal and well‑scoped.

Event‑Driven Standard Order
1) Module docstring (what this file does)
2) Imports (dependencies)
3) Constants & Global Setup
4) Asset & Resource Loading (if applicable)
5) Helper Functions (module‑level utilities)
6) Type Definitions / Protocols (if used)
7) Class & Object Definitions
8) Event Handler Functions (callbacks)
9) Event Listeners / Bindings (wiring)
10) Main Event Loop (while loop / orchestration)

Procedural Standard Order
1) Module docstring
2) Imports (dependencies)
3) Constants
4) Helper Functions
5) Orchestration Functions (core logic)
6) Main Function (entry point)
7) if __name__ == "__main__" block

OOP Standard Order
1) Module docstring
2) Imports (dependencies)
3) Type Definitions (TypeVars, Protocols)
4) Constants
5) Exceptions
6) Abstract Base Classes (interfaces)
7) Data Classes
8) Helper Functions
9) Concrete Classes (base → subclasses)
10) Factory Functions
11) Public API Functions
12) Main (if script)

General Guidelines
- Prefer small, focused modules; avoid unrelated changes in a single patch.
- Keep event loops structured as: handle events → update → draw → flip.
- Use AAA pattern for tests. Favor dependency injection for assets and I/O.
- Use absolute or relative imports consistently within a package; prefer relative for intra‑package.
- Log succinctly; avoid noisy prints in tight loops.
