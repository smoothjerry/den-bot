import logging
import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from ai import ClaudeHandler
    from db import Database
    from points import PointsRepository
    from bot import create_bot
    from temporal import TemporalConfig

    # Initialize dependencies
    chatbot = ClaudeHandler(os.getenv("ANTHROPIC_API_KEY"))
    db = Database(os.getenv("DATABASE_URL"))
    points_repo = PointsRepository(db)

    # Temporal is opt-in: only wire it up if TEMPORAL_ADDRESS is set. The actual
    # connection happens asynchronously inside the bot's setup_hook so it lives
    # on the Discord event loop.
    temporal_config = TemporalConfig.from_env() if os.getenv("TEMPORAL_ADDRESS") else None

    # Create and run the bot
    bot = create_bot(chatbot, points_repo, db, temporal_config=temporal_config)
    bot.run(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    main()
