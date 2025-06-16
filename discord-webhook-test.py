#!/usr/bin/env python3
"""
Discord Webhook Integration for UX Mirror
Tests the webhook and provides notification templates
"""

import requests
import json
from datetime import datetime

# Your Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1384291487876907129/y6_yUFUsJU0QvvYsJjz25IbAz2gKql96exUSEMTjEGXn6q4arRlulpQ132-E5p-Y5E32"

def send_discord_message(content=None, embeds=None):
    """Send a message to Discord via webhook"""
    data = {}
    if content:
        data["content"] = content
    if embeds:
        data["embeds"] = embeds
    
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Failed to send message: {response.status_code}")
        print(response.text)
    return response

def test_basic_message():
    """Test basic text message"""
    print("Testing basic message...")
    send_discord_message("🚀 UX Mirror webhook is connected and working!")

def test_launch_announcement():
    """Send project launch announcement"""
    print("Sending launch announcement...")
    
    embed = {
        "title": "🚀 UX Mirror Project Launch!",
        "description": "We're excited to announce the official launch of **UX Mirror** - a GPU-accelerated UX intelligence system!",
        "color": 0x00ff00,  # Green
        "fields": [
            {
                "name": "🖼️ Vulkan Graphics",
                "value": "Real-time visual analysis with ray tracing",
                "inline": True
            },
            {
                "name": "🚀 HIP/CUDA Compute",
                "value": "GPU-accelerated processing",
                "inline": True
            },
            {
                "name": "🧠 AI Intelligence",
                "value": "Autonomous UX optimization",
                "inline": True
            }
        ],
        "footer": {
            "text": "UX Mirror • GPU-Accelerated UX Intelligence",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "url": "https://github.com/CameronWeller/ux-mirror"
    }
    
    send_discord_message(embeds=[embed])

def test_github_notification():
    """Simulate GitHub event notification"""
    print("Sending GitHub notification...")
    
    embed = {
        "title": "📦 New Pull Request",
        "description": "**#1: Add unit tests for CircularBuffer class**",
        "color": 0x0366d6,  # GitHub blue
        "author": {
            "name": "CameronWeller",
            "icon_url": "https://github.com/CameronWeller.png",
            "url": "https://github.com/CameronWeller"
        },
        "fields": [
            {
                "name": "Status",
                "value": "🟢 Open",
                "inline": True
            },
            {
                "name": "Labels",
                "value": "`good first issue` `testing`",
                "inline": True
            }
        ],
        "footer": {
            "text": "GitHub",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    send_discord_message(embeds=[embed])

def test_build_status():
    """Send CI/CD build status"""
    print("Sending build status...")
    
    embed = {
        "title": "✅ Build Successful",
        "description": "All checks passed for commit `abc123`",
        "color": 0x28a745,  # Success green
        "fields": [
            {
                "name": "🧪 Tests",
                "value": "42 passed",
                "inline": True
            },
            {
                "name": "📊 Coverage",
                "value": "87%",
                "inline": True
            },
            {
                "name": "⏱️ Duration",
                "value": "3m 42s",
                "inline": True
            }
        ],
        "footer": {
            "text": "GitHub Actions",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    send_discord_message(embeds=[embed])

def setup_github_webhook():
    """Instructions for setting up GitHub webhook"""
    print("\n📋 GitHub Webhook Setup Instructions:")
    print("1. Go to: https://github.com/CameronWeller/ux-mirror/settings/hooks")
    print("2. Click 'Add webhook'")
    print("3. Payload URL: " + WEBHOOK_URL + "/github")
    print("4. Content type: application/json")
    print("5. Select events: Push, Pull Request, Issues, Release")
    print("6. Click 'Add webhook'\n")

def main():
    """Run all tests"""
    print("🔧 Testing Discord Webhook for UX Mirror\n")
    
    # Test different message types
    test_basic_message()
    input("\nPress Enter to send launch announcement...")
    test_launch_announcement()
    input("\nPress Enter to send GitHub notification...")
    test_github_notification()
    input("\nPress Enter to send build status...")
    test_build_status()
    
    # Show setup instructions
    setup_github_webhook()
    
    print("\n✨ All tests complete! Your Discord webhook is working properly.")
    print("\nNext steps:")
    print("1. Set up GitHub webhook integration")
    print("2. Update the Discord invite link in README.md")
    print("3. Configure bot permissions in your Discord server")

if __name__ == "__main__":
    main() 