import logging
import os

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from ai import ClaudeHandler
from db import Database
from points import PointsRepository
from bot import create_bot

# Initialize dependencies
chatbot = ClaudeHandler(os.getenv("ANTHROPIC_API_KEY"))
db = Database(os.getenv("DATABASE_URL"))
points_repo = PointsRepository(db)

# Create and run the bot
bot = create_bot(chatbot, points_repo, db)
bot.run(os.getenv("BOT_TOKEN"))
