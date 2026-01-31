# Repository Guidelines

## Project Structure & Module Organization
- `src/arblens/` holds the core package in a `src/` layout. Key areas: `cli/` for the Typer CLI, `domain/` for models/contracts, `exchanges/` for exchange adapters, and `pipeline/`, `storage/`, `analytics/` for processing modules.
- `tests/` is split into `tests/unit/` and `tests/integration/` (currently empty).
- `docs/` contains decisions and milestones.
- Top-level `main.py` is a convenience entry point; prefer `src/arblens/cli/main.py` for CLI changes.

## Build, Test, and Development Commands
This project uses `uv` with a `src/` layout. Run commands from the repo root.
- `uv sync --dev`: install dev dependencies from `uv.lock`.
- `PYTHONPATH=src uv run python -m arblens.cli.main <command>`: run the CLI without packaging.
- `uv run pytest`: run the test suite.
- `uv run ruff check .`: lint.
- `uv run ruff format .`: format.
- `uv run mypy src`: type-check (strict config).

## Coding Style & Naming Conventions
- Python 3.11+; 4-space indentation.
- Follow Ruff defaults with line length 100 (see `pyproject.toml`).
- Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep public APIs in `src/arblens/__init__.py` or module `__init__.py` files.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`.
- Place unit tests in `tests/unit/` and integration tests in `tests/integration/`.
- Name files `test_*.py` and tests `test_*`.
- No explicit coverage requirement yet; add focused tests for new logic and CLI commands.

## Commit & Pull Request Guidelines
- Current history uses short, sentence-style commit subjects (e.g., "Initial project setup ..."). Keep subjects concise and descriptive.
- PRs should include: a clear description, testing notes (commands + results), and any doc updates in `docs/` when behavior changes.

## Agent-Specific Notes
- The repo uses a `src/` layout; ensure `PYTHONPATH=src` or packaging is configured before running modules with `-m`.
