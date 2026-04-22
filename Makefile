.PHONY: all check lint format fix test

all: check test

check:
	uv run ruff check src tests
	uv run ruff format --check src tests

lint:
	uv run ruff check src tests

fix:
	uv run ruff check --fix src tests

format:
	uv run ruff format src tests

test:
	uv run pytest
