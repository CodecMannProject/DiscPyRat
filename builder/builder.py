import os
import json
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys

# Paths
builder_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(builder_dir, '..', 'src'))
commands_dir = os.path.join(src_dir, 'commands')
settings_file = os.path.join(builder_dir, 'build_settings.json')

# Get list of .py files (excluding __init__.py)
command_files = [
    f for f in os.listdir(commands_dir)
    if f.endswith('.py') and f != '__init__.py'
]

# Load settings from JSON if exists
def load_settings():
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'commands': {cmd: True for cmd in [os.path.splitext(f)[0] for f in command_files]},
        'discord_bot_token': 'your_discord_bot_token_here',
        'discord_server_id': 'your_discord_server_id_here',
        'discord_alerts_channel_id': 'your_discord_channel_id_here',
        'icon': 'default.ico'
    }

def save_settings():
    settings = {
        'commands': {cmd: command_vars[cmd].get() for cmd in command_vars},
        'discord_bot_token': token_entry.get(),
        'discord_server_id': server_id_entry.get(),
        'discord_alerts_channel_id': alerts_channel_entry.get(),
        'icon': icon_entry.get()
    }
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

def select_icon_file():
    file_path = filedialog.askopenfilename(
        title="Select Icon File",
        filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
    )
    if file_path:
        icon_entry.delete(0, tk.END)
        icon_entry.insert(0, file_path)

def build_exe():
    # Validate inputs
    token = token_entry.get().strip()
    server_id = server_id_entry.get().strip()
    alerts_channel = alerts_channel_entry.get().strip()
    icon = icon_entry.get().strip()
    
    # Resolve icon path relative to builder directory if just a filename
    if icon and not os.path.isabs(icon):
        icon = os.path.join(builder_dir, icon)
    
    if not token or token == 'your_discord_bot_token_here':
        messagebox.showerror("Error", "Please enter a valid Discord Bot Token")
        return
    
    enabled = [cmd for cmd, var in command_vars.items() if var.get()]
    if not enabled:
        messagebox.showwarning("Warning", "Please select at least one command")
        return
    
    # Save settings
    save_settings()
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix='discpy_build_')
        temp_src = os.path.join(temp_dir, 'src')
        temp_commands = os.path.join(temp_src, 'commands')
        os.makedirs(temp_commands)
        
        # Copy index.py to temp
        shutil.copy(os.path.join(src_dir, 'index.py'), os.path.join(temp_src, 'index.py'))
        
        # Copy selected commands to temp
        for cmd in enabled:
            cmd_file = f"{cmd}.py"
            src_file = os.path.join(commands_dir, cmd_file)
            dest_file = os.path.join(temp_commands, cmd_file)
            shutil.copy(src_file, dest_file)
        
        # Create __init__.py in commands folder
        with open(os.path.join(temp_commands, '__init__.py'), 'w') as f:
            f.write('')
        
        # Create __init__.py in src folder
        with open(os.path.join(temp_src, '__init__.py'), 'w') as f:
            f.write('')
        
        # Create .env file in temp src
        env_content = f'''DISCORD_BOT_TOKEN="{token}"
DISCORD_SERVER_ID="{server_id}"
DISCORD_ALERTS_CHANNEL_ID="{alerts_channel}"
'''
        with open(os.path.join(temp_src, '.env'), 'w') as f:
            f.write(env_content)
        
        # Create a wrapper script that will be the entry point
        wrapper_content = '''import os
import sys

# Add the temp src to path
sys.path.insert(0, os.path.dirname(__file__))

# Run the bot
from index import bot, TOKEN
bot.run(TOKEN)
'''
        wrapper_file = os.path.join(temp_dir, 'main.py')
        with open(wrapper_file, 'w') as f:
            f.write(wrapper_content)
        
        # Build exe using PyInstaller
        output_dir = os.path.join(builder_dir, 'dist')
        
        # Check if PyInstaller is available
        try:
            import PyInstaller
        except ImportError:
            messagebox.showerror("Error", "PyInstaller not found. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        # Build command
        build_cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--noconsole',
            '--name', 'DiscPy',
            '--distpath', output_dir,
            '--add-data', f'{temp_src}{os.pathsep}src',
        ]
        
        # Add icon if specified
        if icon and os.path.exists(icon):
            build_cmd.extend(['--icon', icon])
        
        build_cmd.append(wrapper_file)
        
        messagebox.showinfo("Build", f"Building exe from {wrapper_file}...\nThis may take a moment.")
        
        # Run PyInstaller
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            messagebox.showerror("Build Error", f"PyInstaller failed:\n{result.stderr}")
        else:
            exe_path = os.path.join(output_dir, 'DiscPy.exe')
            messagebox.showinfo("Success", f"Build complete!\nExecutable: {exe_path}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Build failed: {str(e)}")
    
    finally:
        # Clean up temp folder
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# GUI setup
root = tk.Tk()
root.title("DiscPy Builder")
root.geometry("500x700")

# Main frame
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Commands section
ttk.Label(main_frame, text="Commands:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(0, 5))
commands_frame = ttk.LabelFrame(main_frame, text="Select Commands to Include", padding=5)
commands_frame.pack(fill=tk.BOTH, expand=True, pady=5)

# Store checkbutton variables
command_vars = {}
settings = load_settings()

for cmd_file in command_files:
    cmd_name = os.path.splitext(cmd_file)[0]
    var = tk.BooleanVar(value=settings['commands'].get(cmd_name, True))
    chk = ttk.Checkbutton(commands_frame, text=cmd_name, variable=var)
    chk.pack(anchor='w')
    command_vars[cmd_name] = var

# Environment variables section
env_frame = ttk.LabelFrame(main_frame, text="Discord Bot Configuration", padding=10)
env_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Token
ttk.Label(env_frame, text="Discord Bot Token:").pack(anchor='w')
token_entry = ttk.Entry(env_frame, width=50, show='*')
token_entry.insert(0, settings.get('discord_bot_token', 'your_discord_bot_token_here'))
token_entry.pack(anchor='w', pady=(0, 10))

# Server ID
ttk.Label(env_frame, text="Discord Server ID:").pack(anchor='w')
server_id_entry = ttk.Entry(env_frame, width=50)
server_id_entry.insert(0, settings.get('discord_server_id', 'your_discord_server_id_here'))
server_id_entry.pack(anchor='w', pady=(0, 10))

# Alerts Channel ID
ttk.Label(env_frame, text="Alerts Channel ID:").pack(anchor='w')
alerts_channel_entry = ttk.Entry(env_frame, width=50)
alerts_channel_entry.insert(0, settings.get('discord_alerts_channel_id', 'your_discord_channel_id_here'))
alerts_channel_entry.pack(anchor='w', pady=(0, 10))

# Icon path
ttk.Label(env_frame, text="Icon File (optional):").pack(anchor='w')
icon_frame = ttk.Frame(env_frame)
icon_frame.pack(anchor='w', pady=(0, 10), fill=tk.X)
icon_entry = ttk.Entry(icon_frame, width=35)
icon_entry.insert(0, settings.get('icon', 'default.ico'))
icon_entry.pack(side=tk.LEFT, padx=(0, 5))
ttk.Button(icon_frame, text="Browse", command=select_icon_file).pack(side=tk.LEFT)

# Buttons frame
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

ttk.Button(button_frame, text="Save Settings", command=save_settings).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Build EXE", command=build_exe).pack(side=tk.LEFT, padx=5)

root.mainloop()