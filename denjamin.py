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
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="updatepoints")
async def update_points(ctx, member: discord.Member, points: int):
    user_id = member.id
    username = str(member)
    cursor.execute('SELECT points FROM points WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        new_points = result[0] + points
        cursor.execute('UPDATE points SET points = ? WHERE user_id = ?', (new_points, user_id))
    else:
        new_points = points
        cursor.execute('INSERT INTO points (user_id, username, points) VALUES (?, ?, ?)', 
                       (user_id, username, new_points))

    conn.commit()
    action = "Added" if points > 0 else "Subtracted"
    await ctx.send(f"{action} {abs(points)} points to {member.mention}. Total: {new_points} points.")

@bot.command(name="listpoints")
async def list_points(ctx):
    cursor.execute('SELECT username, points FROM points ORDER BY points DESC')
    rows = cursor.fetchall()

    if not rows:
        await ctx.send("No points have been awarded yet!")
        return

    leaderboard = "\n".join([f"{row[0]}: {row[1]} points" for row in rows])
    await ctx.send(f"**Den Points Leaderboard:**\n{leaderboard}")

# Token
TOKEN = "your_bot_token_here"

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
