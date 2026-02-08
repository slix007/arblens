.PHONY: help install test lint typecheck check fmt cli

help:
	@echo "Common commands:"
	@echo "  make install     Install dependencies and editable package"
	@echo "  make test        Run tests"
	@echo "  make lint        Run ruff linter"
	@echo "  make typecheck   Run mypy"
	@echo "  make check       Run lint + typecheck + tests"
	@echo "  make fmt         Auto-format code"
	@echo "  make cli         Show CLI help"

install:
	uv sync
	uv pip install -e .

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck test

fmt:
	uv run ruff format .

cli:
	uv run python -m arblens.cli.main report --help