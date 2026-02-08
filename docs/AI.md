# Repository Guidelines

## AI Usage Guidelines
- AI tools are implementation assistants; humans own architecture and product decisions.
- Follow existing domain models, interfaces, and file layout.
- Use strict typing (mypy) and add focused unit tests for new logic.
- Avoid introducing new dependencies unless explicitly requested.
- Treat `docs/tasks/*` (scope, acceptance criteria) and `docs/decisions/*` (trade-offs) as sources of truth.
- Implement changes according to the relevant task’s acceptance criteria.

## Canonical Development Commands (Makefile)
- Install dependencies: `make install` (or `uv sync`)
- Run full checks: `make check` (lint + typecheck + tests)
- Auto-format code: `make fmt`
- Single steps: `make test`, `make lint`, `make typecheck`

## Python Environment Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
make install
make check
```

## Project Structure (Quick)
•	src/arblens/ — core package (src layout); main areas: cli/, domain/, exchanges/, analytics/, pipeline/, storage/.
•	tests/ — unit and integration tests.
•	docs/ — tasks (docs/tasks/*) and architectural decisions (docs/decisions/*).