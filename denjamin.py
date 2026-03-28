import os

from ai import ClaudeHandler
from db import PointsRepository
from bot import create_bot

# Initialize dependencies
chatbot = ClaudeHandler(os.getenv("ANTHROPIC_API_KEY"))
points_repo = PointsRepository(os.getenv("DATABASE_URL"))

# Create and run the bot
bot = create_bot(chatbot, points_repo)
bot.run(os.getenv("BOT_TOKEN"))
