import os
import dotenv
import discord
from discord.ext import commands

# Setup environment variables
dotenv.load_dotenv()
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
for filename in os.listdir(os.path.join(os.path.dirname(__file__), "commands")):
    if filename.endswith(".py") and not filename.startswith("__"):
        bot.load_extension(f"commands.{filename[:-3]}")

bot.run(TOKEN)