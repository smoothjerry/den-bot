# Denjamin

This is a discord bot that will help you and your friends increase your denliness! Denjamin brings AI-powered chat (via Claude) and a points/leaderboard system to your server. Mention him in a channel and he'll respond with his unique personality — he supports text, images, and threaded conversations.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
- PostgreSQL (local install or via Docker)
- A Discord bot token ([Developer Portal](https://discord.com/developers/applications))
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/smoothjerry/den-bot.git
   cd den-bot
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

   This creates a `.venv/` and installs the exact versions pinned in `uv.lock`. Add `--group dev` if you plan to run tests or use dev tools like `ipython`.

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in your `BOT_TOKEN`, `DATABASE_URL`, and `ANTHROPIC_API_KEY`.

4. **Start PostgreSQL and create a database**

   ```bash
   createdb denbot
   ```

5. **Run the schema**

   ```bash
   psql -d denbot -f db/schema.sql
   ```

6. **Run the bot**

   ```bash
   uv run denjamin
   ```

   The bot connects outbound to Discord's websocket gateway — no port forwarding or tunnels needed.

## Docker

Instead of installing PostgreSQL locally, you can run Postgres (and optionally the bot itself) in Docker. See [DOCKER.md](DOCKER.md) for the full command reference — it covers lifecycle, rebuilds, volumes, psql access, and troubleshooting.

Quickstart — start Postgres in the background and run the bot on your host:

```bash
docker compose up -d
```

Then set `DATABASE_URL=postgresql://denbot:denbot@localhost:5432/denbot` in your `.env`.

## Temporal (workflow orchestration)

Denjamin ships with an opt-in Temporal stack for durable workflow execution, gated behind a `temporal` compose profile. See [DOCKER.md](DOCKER.md) for how to bring it up; the rest of this section is config and production notes.

**Enable the Temporal client in the bot** by setting `TEMPORAL_ADDRESS` in your `.env`:

```
TEMPORAL_ADDRESS=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=denjamin-main
```

Leave `TEMPORAL_ADDRESS` blank to disable Temporal entirely — the bot will run as before.

**Run the worker locally** (instead of in a container):

```bash
uv run temporal-worker
```

The worker and the Discord bot ship from the **same Docker image**; only the entrypoint differs. Scale workers horizontally in production by running more `temporal-worker` containers — Temporal distributes task-queue work across them automatically.

### Production notes (self-hosted)

The `temporalio/auto-setup` image we use for dev is explicitly not recommended by Temporal for production. For a productionized self-hosted deployment (e.g., on a Raspberry Pi 4/5 or similar single-node host):

- Replace `auto-setup` with separate `frontend`, `history`, `matching`, and `internal-frontend` services using the `temporalio/server` image, and run `temporalio/admin-tools` once as a schema-setup job.
- Keep Temporal's Postgres isolated from the application's Postgres (this repo's compose already does).
- Set `TEMPORAL_TLS_CERT_PATH` / `TEMPORAL_TLS_KEY_PATH` and mount mTLS certs if the worker/client traverse an untrusted network; plaintext gRPC is fine when everything runs on the same private bridge network.
- Expected resource baseline: ~700MB–1GB RAM idle for the Temporal services + their Postgres. A Pi 4 with 4GB+ or Pi 5 is recommended; Pi Zero will not work.
- All `temporalio/*` images publish `linux/arm64` variants, so ARM hosts are supported.

## Creating a Discord Test Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**
2. Navigate to the **Bot** section
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**
4. Copy the bot token and add it to your `.env` file
5. Go to **OAuth2 → URL Generator**:
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Read Message History`
6. Open the generated URL to invite the bot to a test Discord server

## Running Tests

```bash
uv run pytest
```

Tests use mocked Discord, database, and Anthropic connections — no real services needed. If you haven't installed dev deps yet, run `uv sync --group dev` first.
