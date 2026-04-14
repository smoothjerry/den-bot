import os

from dotenv import load_dotenv
load_dotenv()

from ai import ClaudeHandler
from db import Database
from points import PointsRepository
from bot import create_bot

# Initialize dependencies
chatbot = ClaudeHandler(os.getenv("ANTHROPIC_API_KEY"))
db = Database(os.getenv("DATABASE_URL"))
points_repo = PointsRepository(db)

# Create and run the bot
bot = create_bot(chatbot, points_repo)
bot.run(os.getenv("BOT_TOKEN"))
