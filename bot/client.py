import discord

from discord_utils import format_attachment_data, format_message_coversation
from bot.commands import register_points_commands

REPLY_LIMIT = 5


class MyBot(discord.Client):
    def __init__(self, chatbot, points_repo):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.chatbot = chatbot

        register_points_commands(self, points_repo)

    async def on_ready(self):
        try:
            await self.tree.sync()
            print(f"Logged in as {self.user} and synced commands!")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Check if the bot is mentioned
        if self.user in message.mentions:
            user_input = message.content.replace(f"<@{self.user.id}>", "").strip()
            image_data = format_attachment_data(message)
            conversation_context, is_thread, reply_count = await format_message_coversation(message)

            try:
                bot_reply = await self.chatbot.generate_response(user_input, conversation_context, image_data)

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


def create_bot(chatbot, points_repo):
    return MyBot(chatbot, points_repo)
