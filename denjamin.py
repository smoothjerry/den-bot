import discord
from discord.ext import commands
import os
import psycopg2

# Setup database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS points (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    points INTEGER DEFAULT 0
)
''')
conn.commit()

# Setup bot
intents = discord.Intents.default()
intents.message_content = True  # Ensure this is enabled for text commands.
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
tree = bot.tree 

@bot.event
async def on_ready():
    try:
        await tree.sync()  # Sync slash commands with Discord
        print(f"Logged in as {bot.user} and synced commands!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@tree.command(name="updatepoints", description="Add or subtract points for a user.")
async def update_points(interaction: discord.Interaction, member: discord.Member, points: int):
    user_id = member.id
    username = str(member)  # Full username (e.g., Username#1234)
    display_name = member.display_name  # User's display name in the server

    try:
        cursor.execute('SELECT points FROM points WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            new_points = result[0] + points
            cursor.execute('UPDATE points SET points = ?, display_name = ? WHERE user_id = ?', 
                           (new_points, display_name, user_id))
        else:
            new_points = points
            cursor.execute('INSERT INTO points (user_id, username, display_name, points) VALUES (?, ?, ?, ?)', 
                           (user_id, username, display_name, new_points))

        conn.commit()  # Commit changes after successful update
        action = "Added" if points > 0 else "Subtracted"
        await interaction.response.send_message(f"{action} {abs(points)} points to {member.mention}. Total: {new_points} points.")
    except Exception as e:
        conn.rollback()  # Roll back in case of an error
        await interaction.response.send_message(f"An error occurred while updating points: {e}")

@tree.command(name="listpoints", description="View the leaderboard of den points.")
async def list_points(interaction: discord.Interaction):
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
        await interaction.response.send_message(f"An error occurred: {e}")

# Token
TOKEN = os.getenv("BOT_TOKEN")

# Hosting Instructions
# ======================
# To host the bot, follow these detailed steps:

# 1. Local Testing
#    - Ensure Python is installed on your system.
#    - Install dependencies using: pip install discord.py
#    - Replace "your_bot_token_here" with your actual Discord bot token from the Discord Developer Portal.
#    - Run the bot locally: python bot.py

# 2. Hosting on Heroku
#    - Sign up at https://www.heroku.com/.
#    - Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli.
#    - Initialize a Git repository and push your code to Heroku:
#        1. heroku login
#        2. git init
#        3. heroku create
#        4. git add .
#        5. git commit -m "Initial commit"
#        6. git push heroku master
#    - Set the bot token as a config variable:
#        heroku config:set TOKEN=your_bot_token_here
#    - Use a `Procfile` to specify the command to run the bot:
#        worker: python bot.py

# 3. Hosting on Railway
#    - Sign up at https://railway.app/.
#    - Connect your GitHub repository to Railway.
#    - Add the bot token in the environment variables section under the key "TOKEN".
#    - Deploy the project and monitor logs for successful startup.

# 4. Hosting on Render
#    - Sign up at https://render.com/.
#    - Create a new Web Service, linking your GitHub repository.
#    - Set the environment variable "TOKEN" with your bot token.
#    - Specify "python bot.py" as the start command.

# 5. Database Considerations
#    - For long-term hosting, consider using a hosted database (e.g., PostgreSQL or MongoDB) instead of SQLite for better scalability.
#    - Many platforms like Heroku and Railway provide integrated database solutions.

bot.run(TOKEN)
