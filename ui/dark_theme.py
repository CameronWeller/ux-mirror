#!/usr/bin/env python3
"""
Dark Theme Configuration for UX-MIRROR
Provides modern dark mode styling for the tkinter interface
"""

import tkinter as tk
from tkinter import ttk

class DarkTheme:
    """Dark theme color scheme and styling"""
    
    # Main colors
    BG_PRIMARY = "#1e1e1e"      # Main background (VS Code dark)
    BG_SECONDARY = "#252526"    # Secondary background
    BG_TERTIARY = "#2d2d30"     # Card/panel backgrounds
    BG_HOVER = "#37373d"        # Hover states
    BG_SELECTED = "#094771"     # Selected items
    
    # Text colors
    TEXT_PRIMARY = "#cccccc"    # Primary text
    TEXT_SECONDARY = "#9d9d9d"  # Secondary text
    TEXT_MUTED = "#6a6a6a"      # Muted text
    TEXT_ACCENT = "#4fc3f7"     # Accent text (links, highlights)
    TEXT_SUCCESS = "#4caf50"    # Success messages
    TEXT_WARNING = "#ff9800"    # Warning messages
    TEXT_ERROR = "#f44336"      # Error messages
    
    # UI Elements
    BORDER = "#3c3c3c"          # Borders
    SCROLLBAR = "#424242"       # Scrollbars
    BUTTON_BG = "#0e639c"       # Button background
    BUTTON_HOVER = "#1177bb"    # Button hover
    BUTTON_ACTIVE = "#0d5185"   # Button active
    
    # Input elements
    INPUT_BG = "#3c3c3c"        # Input backgrounds
    INPUT_BORDER = "#464647"    # Input borders
    INPUT_FOCUS = "#007acc"     # Input focus border
    
    @classmethod
    def configure_root(cls, root):
        """Configure root window with dark theme"""
        root.configure(bg=cls.BG_PRIMARY)
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Main frame style
        style.configure("Dark.TFrame", 
                       background=cls.BG_PRIMARY, 
                       borderwidth=0)
        
        # Secondary frame style  
        style.configure("DarkCard.TFrame", 
                       background=cls.BG_TERTIARY, 
                       borderwidth=1,
                       relief="solid")
        
        # Label styles
        style.configure("Dark.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_PRIMARY,
                       font=('Segoe UI', 9))
        
        style.configure("DarkTitle.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_PRIMARY,
                       font=('Segoe UI', 14, 'bold'))
        
        style.configure("DarkSubtitle.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_SECONDARY,
                       font=('Segoe UI', 10))
        
        style.configure("DarkMuted.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_MUTED,
                       font=('Segoe UI', 9))
        
        style.configure("DarkSuccess.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_SUCCESS,
                       font=('Segoe UI', 9))
        
        style.configure("DarkWarning.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_WARNING,
                       font=('Segoe UI', 9))
        
        style.configure("DarkError.TLabel", 
                       background=cls.BG_PRIMARY, 
                       foreground=cls.TEXT_ERROR,
                       font=('Segoe UI', 9))
        
        # Button styles
        style.configure("Dark.TButton",
                       background=cls.BUTTON_BG,
                       foreground=cls.TEXT_PRIMARY,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map("Dark.TButton",
                 background=[('active', cls.BUTTON_HOVER),
                           ('pressed', cls.BUTTON_ACTIVE)])
        
        # Entry styles
        style.configure("Dark.TEntry",
                       fieldbackground=cls.INPUT_BG,
                       background=cls.INPUT_BG,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.INPUT_BORDER,
                       lightcolor=cls.INPUT_FOCUS,
                       darkcolor=cls.INPUT_FOCUS,
                       borderwidth=1,
                       insertcolor=cls.TEXT_PRIMARY)
        
        style.map("Dark.TEntry",
                 focuscolor=[('!focus', cls.INPUT_BORDER),
                           ('focus', cls.INPUT_FOCUS)])
        
        # Combobox styles
        style.configure("Dark.TCombobox",
                       fieldbackground=cls.INPUT_BG,
                       background=cls.INPUT_BG,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.INPUT_BORDER,
                       lightcolor=cls.INPUT_FOCUS,
                       darkcolor=cls.INPUT_FOCUS,
                       borderwidth=1,
                       arrowcolor=cls.TEXT_PRIMARY)
        
        # Listbox style
        style.configure("Dark.TListbox",
                       background=cls.BG_TERTIARY,
                       foreground=cls.TEXT_PRIMARY,
                       selectbackground=cls.BG_SELECTED,
                       selectforeground=cls.TEXT_PRIMARY,
                       borderwidth=1,
                       relief="solid")
        
        # Notebook styles
        style.configure("Dark.TNotebook",
                       background=cls.BG_PRIMARY,
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        
        style.configure("Dark.TNotebook.Tab",
                       background=cls.BG_SECONDARY,
                       foreground=cls.TEXT_SECONDARY,
                       padding=[15, 8],
                       borderwidth=0,
                       font=('Segoe UI', 9))
        
        style.map("Dark.TNotebook.Tab",
                 background=[('selected', cls.BG_TERTIARY),
                           ('active', cls.BG_HOVER)],
                 foreground=[('selected', cls.TEXT_PRIMARY),
                           ('active', cls.TEXT_PRIMARY)])
        
        # LabelFrame styles
        style.configure("Dark.TLabelframe",
                       background=cls.BG_PRIMARY,
                       bordercolor=cls.BORDER,
                       borderwidth=1,
                       relief="solid")
        
        style.configure("Dark.TLabelframe.Label",
                       background=cls.BG_PRIMARY,
                       foreground=cls.TEXT_ACCENT,
                       font=('Segoe UI', 9, 'bold'))
        
        # Checkbutton styles
        style.configure("Dark.TCheckbutton",
                       background=cls.BG_PRIMARY,
                       foreground=cls.TEXT_PRIMARY,
                       focuscolor='none',
                       borderwidth=0,
                       font=('Segoe UI', 9))
        
        # Radiobutton styles
        style.configure("Dark.TRadiobutton",
                       background=cls.BG_PRIMARY,
                       foreground=cls.TEXT_PRIMARY,
                       focuscolor='none',
                       borderwidth=0,
                       font=('Segoe UI', 9))
        
        # Progressbar styles
        style.configure("Dark.Horizontal.TProgressbar",
                       background=cls.TEXT_ACCENT,
                       troughcolor=cls.BG_SECONDARY,
                       borderwidth=0,
                       lightcolor=cls.TEXT_ACCENT,
                       darkcolor=cls.TEXT_ACCENT)
        
        style.configure("Dark.Vertical.TProgressbar", 
                       background=cls.TEXT_ACCENT,
                       troughcolor=cls.BG_SECONDARY,
                       borderwidth=0,
                       lightcolor=cls.TEXT_ACCENT,
                       darkcolor=cls.TEXT_ACCENT)
        
        # Scrollbar styles
        style.configure("Dark.Vertical.TScrollbar",
                       background=cls.BG_SECONDARY,
                       troughcolor=cls.BG_PRIMARY,
                       bordercolor=cls.BG_SECONDARY,
                       arrowcolor=cls.TEXT_SECONDARY,
                       darkcolor=cls.BG_SECONDARY,
                       lightcolor=cls.BG_SECONDARY)
        
        # Treeview styles
        style.configure("Dark.Treeview",
                       background=cls.BG_TERTIARY,
                       foreground=cls.TEXT_PRIMARY,
                       fieldbackground=cls.BG_TERTIARY,
                       borderwidth=1,
                       relief="solid")
        
        style.configure("Dark.Treeview.Heading",
                       background=cls.BG_SECONDARY,
                       foreground=cls.TEXT_PRIMARY,
                       borderwidth=1,
                       relief="solid",
                       font=('Segoe UI', 9, 'bold'))
        
        style.map("Dark.Treeview",
                 background=[('selected', cls.BG_SELECTED)],
                 foreground=[('selected', cls.TEXT_PRIMARY)])
        
        style.map("Dark.Treeview.Heading",
                 background=[('active', cls.BG_HOVER)])
        
        return style
    
    @classmethod
    def create_text_widget(cls, parent, **kwargs):
        """Create a dark-themed text widget"""
        defaults = {
            'bg': cls.BG_TERTIARY,
            'fg': cls.TEXT_PRIMARY,
            'insertbackground': cls.TEXT_PRIMARY,
            'selectbackground': cls.BG_SELECTED,
            'selectforeground': cls.TEXT_PRIMARY,
            'borderwidth': 1,
            'relief': 'solid',
            'highlightthickness': 1,
            'highlightcolor': cls.INPUT_FOCUS,
            'highlightbackground': cls.BORDER,
            'font': ('Consolas', 9)
        }
        defaults.update(kwargs)
        return tk.Text(parent, **defaults)
    
    @classmethod
    def create_listbox(cls, parent, **kwargs):
        """Create a dark-themed listbox"""
        defaults = {
            'bg': cls.BG_TERTIARY,
            'fg': cls.TEXT_PRIMARY,
            'selectbackground': cls.BG_SELECTED,
            'selectforeground': cls.TEXT_PRIMARY,
            'borderwidth': 1,
            'relief': 'solid',
            'highlightthickness': 1,
            'highlightcolor': cls.INPUT_FOCUS,
            'highlightbackground': cls.BORDER,
            'font': ('Segoe UI', 9)
        }
        defaults.update(kwargs)
        return tk.Listbox(parent, **defaults)
    
    @classmethod
    def create_scrollbar(cls, parent, **kwargs):
        """Create a dark-themed scrollbar"""
        defaults = {
            'bg': cls.BG_SECONDARY,
            'troughcolor': cls.BG_PRIMARY,
            'borderwidth': 0,
            'highlightthickness': 0,
            'activebackground': cls.BG_HOVER,
        }
        defaults.update(kwargs)
        return tk.Scrollbar(parent, **defaults)
    
    @classmethod
    def get_message_color(cls, message_type):
        """Get color for different message types"""
        colors = {
            'success': cls.TEXT_SUCCESS,
            'warning': cls.TEXT_WARNING, 
            'error': cls.TEXT_ERROR,
            'info': cls.TEXT_ACCENT,
            'default': cls.TEXT_PRIMARY
        }
        return colors.get(message_type, colors['default']) 