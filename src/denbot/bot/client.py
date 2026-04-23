import logging
from typing import TYPE_CHECKING, Any

import discord

from denbot.ai.claude import ClaudeHandler
from denbot.db.connection import Database
from denbot.discord import format_attachment_data, format_message_coversation
from denbot.points import register_points_commands
from denbot.points.repository import PointsRepository
from denbot.temporal.config import TemporalConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

REPLY_LIMIT = 5


class MyBot(discord.Client):
    def __init__(
        self,
        chatbot: ClaudeHandler,
        points_repo: PointsRepository,
        db: Database,
        temporal_config: TemporalConfig | None = None,
    ) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.chatbot = chatbot
        self.db = db
        self.temporal_config = temporal_config
        # Populated lazily in setup_hook(); None means Temporal is disabled
        # or the initial connection failed.
        self.temporal_client: Any = None

        register_points_commands(self, points_repo)

    async def setup_hook(self) -> None:
        logger.info("Bot starting up, verifying database connectivity...")
        try:
            with self.db.connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
            logger.info("Database connectivity verified.")
        except Exception:
            logger.exception("Database connectivity check failed during startup")

        if self.temporal_config is not None:
            # Import lazily so the bot doesn't require the temporal package
            # at import time if the feature is off.
            from denbot.temporal.client import get_client

            try:
                self.temporal_client = await get_client(self.temporal_config)
                logger.info(
                    "Temporal client connected address=%s namespace=%s",
                    self.temporal_config.address,
                    self.temporal_config.namespace,
                )
            except Exception:
                logger.exception(
                    "Failed to connect Temporal client; bot will continue without it"
                )
        else:
            logger.info("Temporal disabled (no TEMPORAL_ADDRESS configured).")

    async def on_ready(self) -> None:
        try:
            await self.tree.sync()
            logger.info("Logged in as %s and synced commands!", self.user)
        except Exception as e:
            logger.error("Failed to sync commands: %s", e)

    async def close(self) -> None:
        logger.info("Shutdown initiated, cleaning up resources...")
        try:
            self.db.close()
            logger.info("Database pool closed.")
        except Exception:
            logger.exception("Error closing database pool")
        await super().close()
        logger.info("Discord client closed.")

    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Check if the bot is mentioned
        if self.user in message.mentions:
            user_input = message.content.replace(f"<@{self.user.id}>", "").strip()
            image_data = format_attachment_data(message)
            (
                conversation_context,
                is_thread,
                reply_count,
            ) = await format_message_coversation(message)

            try:
                bot_reply = await self.chatbot.generate_response(
                    user_input, conversation_context, image_data
                )

                # Check if the message is already part of a thread
                if is_thread:
                    await message.channel.send(bot_reply)
                else:
                    if reply_count > REPLY_LIMIT:
                        thread = await message.create_thread(
                            name=f"Conversation with {message.author.display_name}"
                        )
                        await thread.send(bot_reply)
                    else:
                        await message.reply(bot_reply)

            except Exception as e:
                await message.channel.send(f"Error: {e}")


def create_bot(
    chatbot: ClaudeHandler,
    points_repo: PointsRepository,
    db: Database,
    temporal_config: TemporalConfig | None = None,
) -> MyBot:
    return MyBot(chatbot, points_repo, db, temporal_config=temporal_config)
