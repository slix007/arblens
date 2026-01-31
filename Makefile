.PHONY: help install test lint typecheck check fmt

help:
	@echo "Common commands:"
	@echo "  make install     Install dependencies"
	@echo "  make test        Run tests"
	@echo "  make lint        Run ruff linter"
	@echo "  make typecheck   Run mypy"
	@echo "  make check       Run lint + typecheck + tests"
	@echo "  make fmt         Auto-format code"

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck test

fmt:
	uv run ruff format .
