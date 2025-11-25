#!/usr/bin/env python3
"""
UX-MIRROR Command Line Interface
================================

Modern CLI for the UX testing framework.
"""
import argparse
import sys
import asyncio
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

# Try to import from src package (proper package structure)
try:
    from src.ux_tester.utils import load_config, validate_config, setup_logging
except ImportError:
    # Fallback: try direct import
try:
    from ux_tester.utils import load_config, validate_config, setup_logging
except ImportError:
    # Fallback for development
    def load_config(config_path="config.env"):
        """Fallback config loader"""
        config = {
            'response_time_threshold': 500,
            'ui_change_threshold': 0.05,
            'screenshot_quality': 85,
            'openai_api_key': '',
            'anthropic_api_key': '',
            'content_validation_enabled': True
        }
        
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'RESPONSE_TIME_THRESHOLD':
                            config['response_time_threshold'] = int(value) if value else 500
                        elif key == 'UI_CHANGE_THRESHOLD':
                            config['ui_change_threshold'] = float(value) if value else 0.05
                        elif key == 'SCREENSHOT_QUALITY':
                            config['screenshot_quality'] = int(value) if value else 85
                        elif key == 'OPENAI_API_KEY':
                            config['openai_api_key'] = value
                        elif key == 'ANTHROPIC_API_KEY':
                            config['anthropic_api_key'] = value
        except FileNotFoundError:
            print("No config.env found, using defaults")
            
        return config
    
    def validate_config(config):
        """Fallback config validator"""
        return config
    
    def setup_logging(level):
        """Fallback logging setup"""
        import logging
        logging.basicConfig(level=getattr(logging, level))


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='UX-MIRROR Testing Framework - Unified UX Intelligence',
        epilog='Use "ux-tester <command> --help" for more info on specific commands.'
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.env',
        help='Path to configuration file (default: config.env)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='WARNING',
        help='Set logging level (default: WARNING)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command (legacy support)
    test_parser = subparsers.add_parser('test', help='Run UX tests (legacy mode)')
    test_parser.add_argument('--before', action='store_true', help='Capture before screenshot')
    test_parser.add_argument('--after', action='store_true', help='Capture after screenshot')
    test_parser.add_argument('--expect', type=str, help='Expected content description')
    test_parser.add_argument('--analyze', action='store_true', help='Analyze screenshots')

    
    
    # Game testing command
    game_parser = subparsers.add_parser('game', help='Game UX testing with 3:1 feedback cycles')
    game_parser.add_argument('--iterations', type=int, default=12, 
                            help='Total number of testing iterations (default: 12)')
    game_parser.add_argument('--feedback-ratio', type=int, default=3,
                            help='User feedback every N iterations (default: 3)')
    game_parser.add_argument('--config', default='game_ux_config.json',
                            help='Game testing configuration file')
    game_parser.add_argument('--display-screenshots', action='store_true', default=True,
                            help='Display screenshots with analysis overlays')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    # List command (legacy support)
    list_parser = subparsers.add_parser('list', help='List captured screenshots')
    
    # Clean command (legacy support)
    clean_parser = subparsers.add_parser('clean', help='Clean old screenshots')
    clean_parser.add_argument('--keep', type=int, default=20, help='Number of screenshots to keep')
    
    return parser


def handle_test_command(args, config):
    """Handle test-related commands (legacy mode)."""
    print("🔄 Running in legacy mode...")
    
    if args.before:
        cmd = ['python', 'simple_ux_tester.py', 'capture', '--before']
        if args.expect:
            cmd.extend(['--expect', args.expect])
        subprocess.run(cmd)
    elif args.after:
        cmd = ['python', 'simple_ux_tester.py', 'capture', '--after']
        if args.expect:
            cmd.extend(['--expect', args.expect])
        subprocess.run(cmd)
    elif args.analyze:
        subprocess.run(['python', 'simple_ux_tester.py', 'analyze'])
    else:
        print("Use --before, --after, or --analyze with the test command")




def handle_config_command(args, config):
    """Handle configuration commands."""
    if args.show:
        print("⚙️  Current Configuration:")
        print("=" * 50)
        for key, value in config.items():
            # Hide API keys for security
            if 'api_key' in key and value:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"{key}: {display_value}")
    elif args.validate:
        validated = validate_config(config)
        print("✅ Configuration validation complete.")
        print("Any issues have been logged.")
    else:
        print("Use --show or --validate with the config command")


def handle_list_command(args, config):
    """Handle list command (legacy)."""
    print("📁 Listing captured screenshots...")
    subprocess.run(['python', 'simple_ux_tester.py', 'list'])


def handle_clean_command(args, config):
    """Handle clean command (legacy)."""
    print(f"🧹 Cleaning old screenshots (keeping {args.keep})...")
    subprocess.run(['python', 'simple_ux_tester.py', 'clean', '--keep', str(args.keep)])


def handle_game_command(args, config):
    """Handle game UX testing with 3:1 feedback cycles."""
    print("🎮 Starting Game UX Testing Session...")
    print("=" * 60)
    print(f"📋 Configuration:")
    print(f"   • Total iterations: {args.iterations}")
    print(f"   • Feedback ratio: 1 feedback session every {args.feedback_ratio} iterations")
    print(f"   • Config file: {args.config}")
    print(f"   • Screenshot display: {'Yes' if args.display_screenshots else 'No'}")
    print(f"")
    
    # Import and run the game testing controller
    try:
        import asyncio
        import sys
        import os
        
        # Import game testing session
        try:
        from game_testing_session import GameUXTestingController
        except ImportError:
            print("Error: Could not import game_testing_session module")
            return
        
        async def run_game_session():
            controller = GameUXTestingController(config_path=args.config)
            
            try:
                # Start session
                session_id = await controller.start_game_testing_session(
                    total_iterations=args.iterations,
                    feedback_ratio=args.feedback_ratio
                )
                
                print(f"🎯 Session ID: {session_id}")
                print(f"🖼️  Screenshots will be displayed with analysis overlays")
                print(f"💬 You'll be prompted for feedback every {args.feedback_ratio} iterations")
                print(f"🛑 Press Ctrl+C to stop the session early")
                print(f"")
                
                # Run the testing session
                await controller.run_testing_session()
                
            except KeyboardInterrupt:
                print("\n\n🛑 Game testing session interrupted by user")
            except Exception as e:
                print(f"❌ Error during game testing session: {e}")
                import traceback
                traceback.print_exc()
            finally:
                controller.stop_session()
                print("🏁 Game testing session completed")
        
        # Run the async session
        asyncio.run(run_game_session())
        
    except ImportError as e:
        print(f"❌ Error importing game testing modules: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install opencv-python matplotlib pillow numpy")
    except Exception as e:
        print(f"❌ Error starting game testing session: {e}")
        import traceback
        traceback.print_exc()


def handle_analyze_command(args, config):
    """Handle analyze command - analyze a screenshot or running application."""
    print("📊 UX Analysis")
        print("=" * 60)
    print("Use the GUI launcher for interactive analysis:")
    print("  python ux_mirror_launcher.py")
    print()
    print("Or use the simple tester:")
    print("  ux-tester test --before")
    print("  # perform interaction")
    print("  ux-tester test --after")
    print("  ux-tester test --analyze")


def print_welcome():
    """Print welcome message with system info."""
    print("🎯 UX-MIRROR v0.1.0: AI-Powered UX Analysis")
    print("=" * 50)
    print("✨ Simple, focused tool for desktop application UX analysis")
    print()


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Print welcome message
    print_welcome()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Load and validate configuration
    config = load_config(args.config)
    config = validate_config(config)
    
    # Handle commands
    if args.command == 'test':
        handle_test_command(args, config)
    elif args.command == 'game':
        handle_game_command(args, config)
    elif args.command == 'config':
        handle_config_command(args, config)
    elif args.command == 'list':
        handle_list_command(args, config)
    elif args.command == 'clean':
        handle_clean_command(args, config)
    elif args.command == 'analyze':
        handle_analyze_command(args, config)
    else:
        print("🚀 Quick Start Guide:")
        print("=" * 30)
        print("1. GUI Launcher (Recommended):")
        print("   python ux_mirror_launcher.py")
        print()
        print("2. Game UX Testing:")
        print("   ux-tester game --iterations 12 --feedback-ratio 3")
        print()
        print("3. Basic Testing:")
        print("   ux-tester test --before")
        print("   # perform interaction")
        print("   ux-tester test --after")
        print("   ux-tester test --analyze")
        print()
        print("4. Configuration:")
        print("   ux-tester config --show")
        print("   ux-tester config --validate")
        print()
        parser.print_help()


if __name__ == "__main__":
    main() 