from discord.ext import commands
import discord
import os
import sys

# Command metadata
COMMAND_NAME = "help"
DESCRIPTION = "Show available commands or help for a specific command"
CATEGORY = "mandatory"
ORDER = 1

# Store metadata globally to avoid reimporting
_COMMAND_METADATA = {}

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_command_metadata()

    def load_command_metadata(self):
        """Load metadata from all command modules"""
        global _COMMAND_METADATA
        
        # Find commands directory
        commands_path = os.path.dirname(os.path.abspath(__file__))
        
        if not os.path.exists(commands_path):
            return
        
        # Read metadata from each command file
        for filename in os.listdir(commands_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(commands_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Parse metadata from file
                        local_vars = {}
                        exec(content, local_vars)
                        
                        if 'COMMAND_NAME' in local_vars:
                            cmd_name = local_vars['COMMAND_NAME']
                            _COMMAND_METADATA[cmd_name] = {
                                'category': local_vars.get('CATEGORY', 'other'),
                                'order': local_vars.get('ORDER', 999),
                                'description': local_vars.get('DESCRIPTION', 'No description'),
                            }
                except Exception as e:
                    pass

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
            
            categories = {}
            
            # Organize commands by category using stored metadata
            for cmd in self.bot.commands:
                if not cmd.hidden:
                    cmd_name = cmd.name
                    if cmd_name in _COMMAND_METADATA:
                        category = _COMMAND_METADATA[cmd_name]['category']
                        order = _COMMAND_METADATA[cmd_name]['order']
                        description = _COMMAND_METADATA[cmd_name]['description']
                    else:
                        category = 'other'
                        order = 999
                        description = cmd.help or 'No description'
                    
                    if category not in categories:
                        categories[category] = []
                    categories[category].append((order, cmd_name, description))
            
            # Sort categories
            category_order = {'mandatory': 0, 'utilities': 1, 'admin': 2, 'other': 999}
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: category_order.get(x[0], 999)
            )
            
            # Add fields for each category
            for category, cmds in sorted_categories:
                # Sort commands within category by order
                sorted_cmds = sorted(cmds, key=lambda x: x[0])
                cmd_text = "\n".join([f"**${cmd_name}** - {desc}" for _, cmd_name, desc in sorted_cmds])
                embed.add_field(name=category.capitalize(), value=cmd_text, inline=False)
            
            embed.set_footer(text="Use $help <command> for more info on a specific command")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
