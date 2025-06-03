#!/usr/bin/env python3
"""Create a test UI screenshot for demo purposes"""

from PIL import Image, ImageDraw, ImageFont

# Create a simple UI mockup
img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(img)

# Draw header
draw.rectangle([0, 0, 800, 80], fill='#007bff')
draw.text((20, 25), "Sample Website", fill='white', font=None)

# Draw navigation buttons
nav_items = ["Home", "About", "Services", "Contact"]
x_pos = 500
for item in nav_items:
    draw.rectangle([x_pos, 20, x_pos + 60, 60], fill='#0056b3')
    draw.text((x_pos + 10, 30), item, fill='white', font=None)
    x_pos += 70

# Draw main content area
draw.rectangle([50, 120, 750, 450], outline='#dee2e6', width=2)
draw.text((70, 140), "Welcome to Our Website", fill='#212529', font=None)
draw.text((70, 180), "This is a sample page for UX analysis demonstration.", fill='#6c757d', font=None)

# Draw a small button (intentionally small for usability issue detection)
draw.rectangle([70, 250, 110, 280], fill='#28a745')
draw.text((75, 260), "Click", fill='white', font=None)

# Draw an image placeholder (without alt text for accessibility issue)
draw.rectangle([400, 250, 600, 400], fill='#e9ecef')
draw.text((450, 320), "Image", fill='#6c757d', font=None)

# Draw footer with low contrast text
draw.rectangle([0, 500, 800, 600], fill='#f8f9fa')
draw.text((20, 530), "© 2024 Sample Company - All rights reserved", fill='#e9ecef', font=None)

# Save the image
img.save('test_ui_screenshot.png')
print("Created test_ui_screenshot.png") 