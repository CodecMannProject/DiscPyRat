from discord.ext import commands
import discord
import importlib.util
import os

# Command metadata
COMMAND_NAME = "help"
CATEGORY = "mandatory"
ORDER = 1

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_command_metadata(self):
        """Extract metadata from all loaded command modules"""
        commands_path = os.path.join(os.path.dirname(__file__))
        metadata = {}
        
        for filename in os.listdir(commands_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    # Try to import the module to get metadata
                    spec = importlib.util.spec_from_file_location(
                        module_name, 
                        os.path.join(commands_path, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'COMMAND_NAME') and hasattr(module, 'CATEGORY') and hasattr(module, 'ORDER'):
                        cmd_name = module.COMMAND_NAME
                        metadata[cmd_name] = {
                            'category': module.CATEGORY,
                            'order': module.ORDER,
                            'description': None
                        }
                except:
                    pass
        
        return metadata

    @commands.command()
    async def help(self, ctx, command=None):
        """Show available commands or help for a specific command"""
        if command:
            # Get help for a specific command
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send(f"Command `{command}` not found.")
                return
            
            embed = discord.Embed(title=f"Help: ${command}", color=discord.Color.blue())
            embed.add_field(name="Description", value=cmd.help or "No description provided", inline=False)
            embed.add_field(name="Usage", value=f"${command}", inline=False)
            await ctx.send(embed=embed)
        else:
            # List all commands organized by category
            embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
            
            metadata = self.get_command_metadata()
            categories = {}
            
            # Organize commands by category
            for cmd in self.bot.commands:
                if not cmd.hidden:
                    cmd_name = cmd.name
                    if cmd_name in metadata:
                        category = metadata[cmd_name]['category']
                        order = metadata[cmd_name]['order']
                    else:
                        category = 'other'
                        order = 999
                    
                    if category not in categories:
                        categories[category] = []
                    categories[category].append((order, cmd_name, cmd.help or 'No description'))
            
            # Sort categories and commands by order
            category_order = {'mandatory': 0, 'utilities': 1, 'admin': 2, 'other': 999}
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: category_order.get(x[0], 999)
            )
            
            for category, cmds in sorted_categories:
                # Sort commands within category by order
                sorted_cmds = sorted(cmds, key=lambda x: x[0])
                cmd_text = "\n".join([f"**${cmd_name}** - {desc}" for _, cmd_name, desc in sorted_cmds])
                embed.add_field(name=category.capitalize(), value=cmd_text, inline=False)
            
            embed.set_footer(text="Use $help <command> for more info on a specific command")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
