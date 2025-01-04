import os
import psycopg2

import discord

import attachments
from chatgpt import ChatGPTHandler

# Setup database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Setup bot
intents = discord.Intents.default()
intents.message_content = True

# Set up OpenAI API
openai_key = os.getenv("OPENAI_KEY")
chatbot = ChatGPTHandler(openai_key)

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        try:
            await self.tree.sync()  # Sync slash commands with Discord
            print(f"Logged in as {self.user} and synced commands!")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

bot = MyBot()

@bot.tree.command(name="updatepoints", description="Add or subtract points for a user.")
async def update_points(interaction: discord.Interaction, member: discord.Member, points: int):
    user_id = member.id
    username = str(member)  # Full username (e.g., Username#1234)
    display_name = member.display_name  # User's display name in the server

    try:
        cursor.execute('SELECT points FROM points WHERE user_id = %s', (user_id,))
        result = cursor.fetchone()

        if result:
            new_points = result[0] + points
            cursor.execute('UPDATE points SET points = %s, display_name = %s WHERE user_id = %s', 
                           (new_points, display_name, user_id))
        else:
            new_points = points
            cursor.execute('INSERT INTO points (user_id, username, display_name, points) VALUES (%s, %s, %s, %s)', 
                           (user_id, username, display_name, new_points))

        conn.commit()  # Commit changes after successful update
        action = "Added" if points > 0 else "Subtracted"
        await interaction.response.send_message(f"{action} {abs(points)} points to {member.mention}. Total: {new_points} points.")
    except Exception as e:
        conn.rollback()  # Roll back in case of an error
        await interaction.response.send_message(f"An error occurred while updating points: {e}")

@bot.tree.command(name="leaderboard", description="View the leaderboard of den points.")
async def leaderboard(interaction: discord.Interaction):
    try:
        cursor.execute('SELECT user_id, points FROM points ORDER BY points DESC')
        rows = cursor.fetchall()

        if not rows:
            await interaction.response.send_message("No points have been awarded yet!")
            return

        leaderboard = "\n".join([f"<@{row[0]}>: {row[1]} points" for row in rows])
        await interaction.response.send_message(f"**Den Points Leaderboard:**\n{leaderboard}")
    except Exception as e:
        conn.rollback()  # Roll back in case of an error
        await interaction.response.send_message(f"An error occurred while fetching the leaderboard: {e}")

@bot.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()
        image_data = attachments.format_attachment_data(message)

        # Call the OpenAI API using the new method
        try:
            bot_reply = await chatbot.generate_response(user_input, image_data)
            await message.channel.send(bot_reply)
        except Exception as e:
            await message.channel.send(f"Error: {e}")

# Token
TOKEN = os.getenv("BOT_TOKEN")

bot.run(TOKEN)
