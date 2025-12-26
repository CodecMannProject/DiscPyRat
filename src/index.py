import os
import sys
import dotenv
import discord
from discord.ext import commands

# Setup environment variables
# Handle both development and packaged executable scenarios
if hasattr(sys, 'frozen'):
    # When running as compiled exe
    base_path = os.path.dirname(sys.executable)
    env_path = os.path.join(base_path, '.env')
else:
    # When running as script
    env_path = os.path.join(os.path.dirname(__file__), '.env')

dotenv.load_dotenv(env_path)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Setup intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Load all cogs from the commands folder
commands_path = os.path.join(os.path.dirname(__file__), "commands")
if os.path.exists(commands_path):
    for filename in os.listdir(commands_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                bot.load_extension(f"commands.{filename[:-3]}")
                print(f"Loaded command: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load command {filename[:-3]}: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)