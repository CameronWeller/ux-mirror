#!/usr/bin/env python3
"""
Test script for UX-MIRROR Dark Theme
Demonstrates the dark mode styling and components
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ui.dark_theme import DarkTheme

def create_demo_window():
    """Create a demo window showing dark theme components"""
    root = tk.Tk()
    root.title("🌙 UX-MIRROR Dark Theme Demo")
    root.geometry("700x500")
    
    # Apply dark theme
    style = DarkTheme.configure_root(root)
    
    # Main container
    main_frame = ttk.Frame(root, style="Dark.TFrame", padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="🌙 Dark Theme Components", 
                           style="DarkTitle.TLabel")
    title_label.pack(anchor=tk.W, pady=(0, 20))
    
    # Create notebook for different component demos
    notebook = ttk.Notebook(main_frame, style="Dark.TNotebook")
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Basic Components Tab
    basic_frame = ttk.Frame(notebook, style="Dark.TFrame")
    notebook.add(basic_frame, text="Basic Components")
    create_basic_components_demo(basic_frame)
    
    # Input Components Tab
    input_frame = ttk.Frame(notebook, style="Dark.TFrame")
    notebook.add(input_frame, text="Input Components")
    create_input_components_demo(input_frame)
    
    # Data Components Tab
    data_frame = ttk.Frame(notebook, style="Dark.TFrame")
    notebook.add(data_frame, text="Data Components")
    create_data_components_demo(data_frame)
    
    return root

def create_basic_components_demo(parent):
    """Demo basic components"""
    container = ttk.Frame(parent, style="Dark.TFrame", padding="20")
    container.pack(fill=tk.BOTH, expand=True)
    
    # Labels
    ttk.Label(container, text="Label Styles:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    
    ttk.Label(container, text="Primary text label", style="Dark.TLabel").pack(anchor=tk.W)
    ttk.Label(container, text="Secondary text label", style="DarkSubtitle.TLabel").pack(anchor=tk.W)
    ttk.Label(container, text="Muted text label", style="DarkMuted.TLabel").pack(anchor=tk.W)
    ttk.Label(container, text="Success message", style="DarkSuccess.TLabel").pack(anchor=tk.W)
    ttk.Label(container, text="Warning message", style="DarkWarning.TLabel").pack(anchor=tk.W)
    ttk.Label(container, text="Error message", style="DarkError.TLabel").pack(anchor=tk.W)
    
    # Buttons
    ttk.Label(container, text="Buttons:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(20, 10))
    
    button_frame = ttk.Frame(container, style="Dark.TFrame")
    button_frame.pack(anchor=tk.W, pady=(0, 20))
    
    ttk.Button(button_frame, text="Primary Button", style="Dark.TButton").pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="Disabled Button", style="Dark.TButton", state='disabled').pack(side=tk.LEFT)
    
    # Progress bar
    ttk.Label(container, text="Progress Bar:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    progress = ttk.Progressbar(container, style="Dark.Horizontal.TProgressbar", length=300, mode='determinate')
    progress.pack(anchor=tk.W)
    progress['value'] = 65

def create_input_components_demo(parent):
    """Demo input components"""
    container = ttk.Frame(parent, style="Dark.TFrame", padding="20")
    container.pack(fill=tk.BOTH, expand=True)
    
    # Entry
    ttk.Label(container, text="Text Entry:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    entry = ttk.Entry(container, style="Dark.TEntry", width=40)
    entry.pack(anchor=tk.W, pady=(0, 20))
    entry.insert(0, "Sample text input")
    
    # Combobox
    ttk.Label(container, text="Combobox:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    combo = ttk.Combobox(container, style="Dark.TCombobox", width=37)
    combo['values'] = ('Option 1', 'Option 2', 'Option 3')
    combo.pack(anchor=tk.W, pady=(0, 20))
    combo.set('Option 1')
    
    # Checkbuttons and Radiobuttons
    ttk.Label(container, text="Checkboxes & Radio Buttons:", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    
    check_frame = ttk.Frame(container, style="Dark.TFrame")
    check_frame.pack(anchor=tk.W, pady=(0, 10))
    
    var1 = tk.BooleanVar(value=True)
    var2 = tk.BooleanVar(value=False)
    ttk.Checkbutton(check_frame, text="Enabled option", variable=var1, style="Dark.TCheckbutton").pack(anchor=tk.W)
    ttk.Checkbutton(check_frame, text="Disabled option", variable=var2, style="Dark.TCheckbutton").pack(anchor=tk.W)
    
    radio_frame = ttk.Frame(container, style="Dark.TFrame")
    radio_frame.pack(anchor=tk.W, pady=(10, 0))
    
    radio_var = tk.StringVar(value="option1")
    ttk.Radiobutton(radio_frame, text="Radio Option 1", variable=radio_var, value="option1", style="Dark.TRadiobutton").pack(anchor=tk.W)
    ttk.Radiobutton(radio_frame, text="Radio Option 2", variable=radio_var, value="option2", style="Dark.TRadiobutton").pack(anchor=tk.W)

def create_data_components_demo(parent):
    """Demo data display components"""
    container = ttk.Frame(parent, style="Dark.TFrame", padding="20")
    container.pack(fill=tk.BOTH, expand=True)
    
    # Treeview
    ttk.Label(container, text="Treeview (Data Table):", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
    
    tree_frame = ttk.Frame(container, style="Dark.TFrame")
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('name', 'type', 'value')
    tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=6, style="Dark.Treeview")
    
    tree.heading('#0', text='Item')
    tree.heading('name', text='Name')
    tree.heading('type', text='Type')
    tree.heading('value', text='Value')
    
    tree.column('#0', width=100)
    tree.column('name', width=150)
    tree.column('type', width=100)
    tree.column('value', width=100)
    
    # Add sample data
    tree.insert('', 'end', text='Component 1', values=('Button', 'UI Element', 'Active'))
    tree.insert('', 'end', text='Component 2', values=('Label', 'Text', 'Visible'))
    tree.insert('', 'end', text='Component 3', values=('Entry', 'Input', 'Focused'))
    
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview, style="Dark.Vertical.TScrollbar")
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Text widget
    ttk.Label(container, text="Text Widget (Log Area):", style="DarkTitle.TLabel").pack(anchor=tk.W, pady=(20, 10))
    
    text_widget = DarkTheme.create_text_widget(container, height=8, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Add sample log messages with colors
    sample_messages = [
        ("✅ Success message - operation completed", "success"),
        ("⚠️ Warning message - check configuration", "warning"),
        ("❌ Error message - operation failed", "error"),
        ("🔄 Info message - processing data", "info"),
        ("Regular log message without special formatting", "default")
    ]
    
    text_widget.configure(state='normal')
    for message, msg_type in sample_messages:
        color = DarkTheme.get_message_color(msg_type)
        start_index = text_widget.index(tk.END)
        text_widget.insert(tk.END, f"{message}\n")
        end_index = text_widget.index(tk.END)
        text_widget.tag_add(f"msg_{msg_type}", start_index, end_index)
        text_widget.tag_config(f"msg_{msg_type}", foreground=color)
    text_widget.configure(state='disabled')

def main():
    """Run the dark theme demo"""
    print("🌙 Starting UX-MIRROR Dark Theme Demo...")
    
    root = create_demo_window()
    
    print("✅ Dark theme demo window created")
    print("🎨 Features demonstrated:")
    print("   • VS Code-inspired dark color scheme")
    print("   • Styled buttons, labels, and inputs")
    print("   • Dark treeview and text widgets")
    print("   • Color-coded log messages")
    print("   • Professional notebook tabs")
    
    root.mainloop()

if __name__ == "__main__":
    main() 