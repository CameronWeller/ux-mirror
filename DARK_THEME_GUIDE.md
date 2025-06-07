# 🌙 UX-MIRROR Dark Theme Guide

## Overview
UX-MIRROR now features a comprehensive dark mode interface inspired by modern development tools like VS Code. The dark theme provides a professional, eye-friendly experience for extended UX analysis sessions.

## 🎨 Design Philosophy

### **Visual Hierarchy**
- **Primary Background**: Deep charcoal (#1e1e1e) - main application background
- **Secondary Background**: Slightly lighter (#252526) - panels and cards
- **Tertiary Background**: Medium gray (#2d2d30) - input fields and content areas
- **Accent Colors**: Bright blue (#4fc3f7) - highlights and interactive elements

### **Color Psychology**
- **Dark backgrounds** reduce eye strain during long sessions
- **High contrast text** ensures excellent readability
- **Color-coded messages** provide instant visual feedback
- **Subtle borders** define sections without being distracting

## 🎯 Color Scheme

### **Background Colors**
```python
BG_PRIMARY = "#1e1e1e"      # Main background (VS Code dark)
BG_SECONDARY = "#252526"    # Secondary background  
BG_TERTIARY = "#2d2d30"     # Card/panel backgrounds
BG_HOVER = "#37373d"        # Hover states
BG_SELECTED = "#094771"     # Selected items
```

### **Text Colors**
```python
TEXT_PRIMARY = "#cccccc"    # Primary text
TEXT_SECONDARY = "#9d9d9d"  # Secondary text
TEXT_MUTED = "#6a6a6a"      # Muted text
TEXT_ACCENT = "#4fc3f7"     # Accent text (links, highlights)
TEXT_SUCCESS = "#4caf50"    # Success messages (✅)
TEXT_WARNING = "#ff9800"    # Warning messages (⚠️)
TEXT_ERROR = "#f44336"      # Error messages (❌)
```

### **UI Element Colors**
```python
BORDER = "#3c3c3c"          # Borders
BUTTON_BG = "#0e639c"       # Button background
BUTTON_HOVER = "#1177bb"    # Button hover
INPUT_BG = "#3c3c3c"        # Input backgrounds
INPUT_FOCUS = "#007acc"     # Input focus border
```

## 🧩 Component Styling

### **Labels & Text**
- **DarkTitle.TLabel**: Large, bold headers
- **DarkSubtitle.TLabel**: Medium secondary text
- **DarkMuted.TLabel**: Small, muted text
- **DarkSuccess/Warning/Error.TLabel**: Color-coded status messages

### **Interactive Elements**
- **Dark.TButton**: Primary action buttons with hover effects
- **Dark.TEntry**: Text input fields with focus highlighting
- **Dark.TCombobox**: Dropdown selections
- **Dark.TCheckbutton/TRadiobutton**: Form controls

### **Data Display**
- **Dark.Treeview**: Data tables with alternating row colors
- **Dark.TNotebook**: Tabbed interfaces
- **Dark.TProgressbar**: Progress indicators
- **DarkTheme.create_text_widget()**: Log areas and text displays

## 🚀 Usage Examples

### **Basic Window Setup**
```python
import tkinter as tk
from tkinter import ttk
from ui.dark_theme import DarkTheme

# Create window
root = tk.Tk()
root.title("My Dark App")

# Apply dark theme
style = DarkTheme.configure_root(root)

# Create styled components
main_frame = ttk.Frame(root, style="Dark.TFrame")
title_label = ttk.Label(main_frame, text="Title", style="DarkTitle.TLabel")
button = ttk.Button(main_frame, text="Action", style="Dark.TButton")
```

### **Color-Coded Log Messages**
```python
# In your application
def log_message(self, message: str):
    # Determine message type
    if "✅" in message:
        color = DarkTheme.get_message_color('success')
    elif "⚠️" in message:
        color = DarkTheme.get_message_color('warning')
    elif "❌" in message:
        color = DarkTheme.get_message_color('error')
    else:
        color = DarkTheme.get_message_color('default')
    
    # Apply color to text widget
    self.text_widget.tag_config("current_msg", foreground=color)
```

### **Custom Text Widgets**
```python
# Create dark-themed text widget
log_area = DarkTheme.create_text_widget(parent, height=10, wrap=tk.WORD)

# Create dark-themed listbox
app_list = DarkTheme.create_listbox(parent, height=8)

# Create dark-themed scrollbar
scrollbar = DarkTheme.create_scrollbar(parent, orient=tk.VERTICAL)
```

## 🎛️ Available Styles

### **Frame Styles**
- `Dark.TFrame` - Standard dark frame
- `DarkCard.TFrame` - Card-style frame with border

### **Label Styles**
- `Dark.TLabel` - Standard text
- `DarkTitle.TLabel` - Large bold headers
- `DarkSubtitle.TLabel` - Medium secondary text
- `DarkMuted.TLabel` - Small muted text
- `DarkSuccess.TLabel` - Green success text
- `DarkWarning.TLabel` - Orange warning text
- `DarkError.TLabel` - Red error text

### **Input Styles**
- `Dark.TButton` - Primary buttons
- `Dark.TEntry` - Text input fields
- `Dark.TCombobox` - Dropdown selections
- `Dark.TCheckbutton` - Checkboxes
- `Dark.TRadiobutton` - Radio buttons

### **Container Styles**
- `Dark.TNotebook` - Tabbed interfaces
- `Dark.TLabelframe` - Grouped sections
- `Dark.Treeview` - Data tables
- `Dark.TProgressbar` - Progress indicators
- `Dark.Vertical.TScrollbar` - Scrollbars

## 🔧 Customization

### **Extending the Theme**
```python
# Add custom styles
style = DarkTheme.configure_root(root)

# Custom button style
style.configure("Custom.TButton",
               background="#ff6b6b",  # Custom red
               foreground=DarkTheme.TEXT_PRIMARY)

# Custom label style  
style.configure("CustomTitle.TLabel",
               background=DarkTheme.BG_PRIMARY,
               foreground="#ffd93d",  # Custom yellow
               font=('Arial', 16, 'bold'))
```

### **Message Color Customization**
```python
# Override message colors
custom_colors = {
    'success': '#00ff88',    # Bright green
    'warning': '#ffaa00',    # Bright orange
    'error': '#ff4444',      # Bright red
    'info': '#44aaff',       # Bright blue
    'default': '#ffffff'     # White
}

# Use in your application
color = custom_colors.get(message_type, custom_colors['default'])
```

## 🧪 Testing & Demo

### **Run Theme Demo**
```bash
# Test all dark theme components
python test_dark_theme.py
```

### **Launch Dark Mode UX-MIRROR**
```bash
# Experience the full dark theme
python ux_mirror_launcher.py
```

## 🎨 Design Benefits

### **User Experience**
- **Reduced Eye Strain**: Dark backgrounds are easier on the eyes
- **Professional Appearance**: Modern, sleek interface design
- **Better Focus**: Dark UI keeps attention on content
- **Consistent Branding**: Unified visual language throughout

### **Technical Benefits**
- **Modular Design**: Easy to customize and extend
- **Performance**: Efficient styling with minimal overhead
- **Accessibility**: High contrast ratios for readability
- **Maintainability**: Centralized color management

## 🔄 Migration from Light Theme

### **Automatic Conversion**
The dark theme is applied automatically when you:
1. Import `DarkTheme` from `ui.dark_theme`
2. Call `DarkTheme.configure_root(root)`
3. Use dark theme styles on components

### **No Breaking Changes**
- Existing functionality remains unchanged
- All features work identically in dark mode
- Settings and configurations are preserved

## 🎯 Best Practices

### **Consistent Styling**
- Always use theme styles instead of manual colors
- Apply styles to all ttk components
- Use helper methods for custom widgets

### **Color Usage**
- Use semantic colors (success, warning, error)
- Maintain sufficient contrast ratios
- Test readability in different lighting conditions

### **Component Guidelines**
- Group related elements with `TLabelframe`
- Use appropriate text hierarchy (Title > Subtitle > Body)
- Provide visual feedback for interactive elements

---

**🌙 The dark theme transforms UX-MIRROR into a modern, professional tool that's comfortable to use during extended analysis sessions while maintaining all the powerful functionality you expect.** 