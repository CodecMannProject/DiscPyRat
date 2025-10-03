import os
import tkinter as tk
from tkinter import ttk

# Path to the commands directory
commands_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'commands'))

# Get list of .py files (excluding __init__.py)
command_files = [
    f for f in os.listdir(commands_dir)
    if f.endswith('.py') and f != '__init__.py'
]

# GUI setup
root = tk.Tk()
root.title("Enable/Disable Commands")

# Store checkbutton variables
command_vars = {}

def print_selected():
    enabled = [cmd for cmd, var in command_vars.items() if var.get()]
    print("Enabled commands:", enabled)

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Commands:").pack(anchor='w')

for cmd_file in command_files:
    cmd_name = os.path.splitext(cmd_file)[0]
    var = tk.BooleanVar(value=True)
    chk = ttk.Checkbutton(frame, text=cmd_name, variable=var)
    chk.pack(anchor='w')
    command_vars[cmd_name] = var

ttk.Button(frame, text="Build", command=print_selected).pack(pady=10)

root.mainloop()