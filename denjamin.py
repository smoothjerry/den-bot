import os

from ai import ChatGPTHandler
from db import PointsRepository
from bot import create_bot

# Initialize dependencies
chatbot = ChatGPTHandler(os.getenv("OPENAI_KEY"))
points_repo = PointsRepository(os.getenv("DATABASE_URL"))

# Create and run the bot
bot = create_bot(chatbot, points_repo)
bot.run(os.getenv("BOT_TOKEN"))
