# Docker Cheat Sheet

A practical reference for the Docker commands you'll actually use while working on Denjamin. The main [README](README.md) has the quickstart — this doc fills in the day-to-day operations.

All commands assume you're running them from the repo root.

## Services at a glance

Defined in [docker-compose.yml](docker-compose.yml):

| Service             | Profile     | Port(s)            | Purpose                                 |
|---------------------|-------------|--------------------|-----------------------------------------|
| `db`                | *(default)* | `5432`             | App Postgres — bot data, points         |
| `bot`               | `bot`       | —                  | The Discord bot process                 |
| `temporal-postgres` | `temporal`  | —                  | Dedicated Postgres for Temporal         |
| `temporal`          | `temporal`  | `7233`             | Temporal server (auto-setup, dev only)  |
| `temporal-ui`       | `temporal`  | `8080`             | Temporal Web UI                         |
| `temporal-worker`   | `temporal`  | —                  | Worker process (same image as `bot`)    |

Services without a profile start by default. Profiled services only start when you pass `--profile <name>` (or `COMPOSE_PROFILES=<name>`).

## Common workflows

### Just Postgres (bot runs locally via `uv run denjamin`)

```bash
docker compose up -d                  # start db in background
docker compose ps                     # verify it's healthy
docker compose logs -f db             # tail logs
docker compose down                   # stop (keeps data)
```

### Full bot in a container

```bash
docker compose --profile bot up       # attached; Ctrl-C to stop
docker compose --profile bot up -d    # detached
docker compose --profile bot logs -f  # tail all profile services
```

### Full Temporal stack

```bash
docker compose --profile temporal up -d
open http://localhost:8080            # Temporal Web UI
docker compose --profile temporal down
```

### Everything at once (bot + temporal)

```bash
docker compose --profile bot --profile temporal up -d
```

### Temporal infra only (no worker — useful when iterating on workflow code from a REPL or running the worker locally)

```bash
docker compose up -d temporal temporal-ui temporal-postgres
```

## Rebuilding after code or dependency changes

The `bot` and `temporal-worker` services share one image built from the [Dockerfile](Dockerfile). Anything that changes `pyproject.toml`, `uv.lock`, or application code means a rebuild.

```bash
docker compose build                        # rebuild all buildable services
docker compose build bot                    # rebuild just one
docker compose --profile bot up --build     # rebuild then start
docker compose build --no-cache bot         # force full rebuild (slow; for dep-resolution weirdness)
```

## Inspecting running services

```bash
docker compose ps                     # running services + health
docker compose logs -f <service>      # tail one service
docker compose logs --tail=200 bot    # last 200 lines, no follow
docker compose top                    # processes inside each container
docker compose config                 # render the effective merged config
```

## Running commands inside containers

```bash
# Open a shell in the bot container (must be running)
docker compose exec bot bash

# Run a one-off command in a fresh bot container (no need for it to be up)
docker compose run --rm bot python -c "import denjamin; print('ok')"

# Run the test suite inside the image
docker compose run --rm bot pytest
```

## Accessing Postgres

```bash
# psql into the app DB
docker compose exec db psql -U denbot -d denbot

# One-off query
docker compose exec db psql -U denbot -d denbot -c "select count(*) from points;"

# Dump / restore
docker compose exec db pg_dump -U denbot denbot > denbot.sql
cat denbot.sql | docker compose exec -T db psql -U denbot -d denbot

# Re-apply schema.sql (only runs automatically on *empty* volume)
docker compose exec -T db psql -U denbot -d denbot < db/schema.sql
```

Temporal's Postgres is the same deal with different creds:

```bash
docker compose exec temporal-postgres psql -U temporal -d temporal
```

## Volumes and data

Two named volumes hold persistent state: `pgdata` (app) and `temporal-pgdata` (Temporal).

```bash
docker volume ls | grep den-bot             # list project volumes
docker compose down                         # stop containers, KEEP volumes
docker compose down -v                      # stop and WIPE all volumes (destructive)
docker volume rm den-bot_pgdata             # wipe just the app DB (destructive)
```

Note: `db/schema.sql` is only applied by the Postgres image on an *empty* data directory. If you change the schema, either apply the diff manually via `psql` or wipe `pgdata` to trigger a fresh init.

## Restarting and stopping

```bash
docker compose restart bot            # restart one service
docker compose stop                   # stop everything, keep containers
docker compose start                  # start stopped containers back up
docker compose kill bot               # SIGKILL (when stop grace period isn't cutting it)
```

The `bot` and `temporal-worker` services set `stop_grace_period: 10s` — they'll get SIGTERM, have 10s to clean up, then SIGKILL.

## Troubleshooting

**"port is already allocated"** — something else is using 5432, 7233, or 8080. Find it with `lsof -i :5432` and stop it, or stop the other stack: `docker compose down`.

**Temporal worker crashing at startup** — the worker retries connecting for ~2 minutes and is set to `restart: unless-stopped`. If it's still failing after that, check `docker compose logs temporal` — the auto-setup image sometimes takes a while on the first boot while it provisions the schema.

**Bot container can't reach the DB** — inside the compose network, use `db` as the host, not `localhost`. Your `.env` `DATABASE_URL` should be `postgresql://denbot:denbot@db:5432/denbot` when running the bot as a container (vs. `@localhost:5432` when running it on the host).

**Same for Temporal** — inside the network it's `temporal:7233`; from the host it's `localhost:7233`. The compose file already overrides `TEMPORAL_ADDRESS=temporal:7233` for the worker service so you don't have to juggle this in `.env`.

**Stale image after a dep change** — run `docker compose build bot` (or `--build` on `up`). `up` alone does not rebuild.

**Disk filling up** — prune unused images/containers/volumes:

```bash
docker system df                      # see what's using space
docker system prune                   # remove dangling images + stopped containers
docker system prune --volumes         # also prune unused volumes (careful)
```

## `docker compose` vs `docker-compose`

This doc uses the v2 `docker compose` (space) form that ships with modern Docker Desktop. If you're on an older install that only has `docker-compose` (hyphenated), the commands here work identically with the hyphen.
