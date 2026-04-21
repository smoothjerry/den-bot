FROM python:3.12-slim

# Grab the uv binary from the official image — no pip install, no curl.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install production deps into .venv in a cacheable layer — only
# re-runs when pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Install the project itself so entry-point scripts (denjamin,
# temporal-worker) are available on PATH.
COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

STOPSIGNAL SIGTERM
CMD ["denjamin"]
