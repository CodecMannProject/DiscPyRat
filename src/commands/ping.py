from discord.ext import commands

# Command metadata
COMMAND_NAME = "ping"
CATEGORY = "utilities"
ORDER = 1

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        await ctx.send("Pong!")

def setup(bot):
    bot.add_cog(Ping(bot))