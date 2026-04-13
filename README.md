# Denjamin

This is a discord bot that will help you and your friends increase your denliness! Denjamin brings AI-powered chat (via Claude) and a points/leaderboard system to your server. Mention him in a channel and he'll respond with his unique personality — he supports text, images, and threaded conversations.

## Prerequisites

- Python 3.x
- PostgreSQL (local install or via Docker)
- A Discord bot token ([Developer Portal](https://discord.com/developers/applications))
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/smoothjerry/den-bot.git
   cd den-bot
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in your `BOT_TOKEN`, `DATABASE_URL`, and `ANTHROPIC_API_KEY`.

5. **Start PostgreSQL and create a database**

   ```bash
   createdb denbot
   ```

6. **Run the schema**

   ```bash
   psql -d denbot -f db/schema.sql
   ```

7. **Run the bot**

   ```bash
   python denjamin.py
   ```

   The bot connects outbound to Discord's websocket gateway — no port forwarding or tunnels needed.

## Docker

Instead of installing PostgreSQL locally, you can use Docker:

**Start Postgres for local dev** (bot runs on your machine):

```bash
docker-compose up -d
```

This starts Postgres on `localhost:5432` and auto-creates the `points` table. Set your `DATABASE_URL` to `postgresql://denbot:denbot@localhost:5432/denbot`.

**Run everything in containers** (Postgres + bot):

```bash
docker-compose --profile bot up
```

**Tear down and remove data:**

```bash
docker-compose down -v
```

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
pytest
```

Tests use mocked Discord, database, and Anthropic connections — no real services needed.
