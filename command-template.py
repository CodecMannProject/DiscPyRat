from discord.ext import commands

# Command metadata
COMMAND_NAME = "template"
DESCRIPTION = "General template for new commands"
CATEGORY = "utilities" # change this to reflect the command category, change to "mandatory" for core commands
ORDER = 2 # change this to reflect new order in help command

class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def template(self, ctx):
        """Do something useful"""

async def setup(bot):
    await bot.add_cog(Template(bot))