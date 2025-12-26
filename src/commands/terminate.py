from discord.ext import commands

# Command metadata
COMMAND_NAME = "terminate"
CATEGORY = "mandatory"
ORDER = 0

class Terminate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def terminate(self, ctx):
        """Terminate the bot (owner only)"""
        await ctx.send("Terminating bot...")
        await self.bot.close()

def setup(bot):
    bot.add_cog(Terminate(bot))
