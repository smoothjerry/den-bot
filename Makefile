.PHONY: all check lint format fix test typecheck

all: check test

check:
	uv run ruff check src tests
	uv run ruff format --check src tests
	uv run mypy

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy

fix:
	uv run ruff check --fix src tests

format:
	uv run ruff format src tests

test:
	uv run pytest
