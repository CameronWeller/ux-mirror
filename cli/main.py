#!/usr/bin/env python3
"""
UX-MIRROR Command Line Interface
================================

Modern CLI for the UX testing framework.
"""
import argparse
import sys
from pathlib import Path

# Add src to path for imports during development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ux_tester.utils import load_config, validate_config, setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='UX-MIRROR Testing Framework',
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
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run UX tests')
    test_parser.add_argument('--before', action='store_true', help='Capture before screenshot')
    test_parser.add_argument('--after', action='store_true', help='Capture after screenshot')
    test_parser.add_argument('--expect', type=str, help='Expected content description')
    test_parser.add_argument('--analyze', action='store_true', help='Analyze screenshots')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List captured screenshots')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean old screenshots')
    clean_parser.add_argument('--keep', type=int, default=20, help='Number of screenshots to keep')
    
    return parser


def handle_test_command(args, config):
    """Handle test-related commands."""
    # For now, delegate to the original simple_ux_tester.py
    # This will be refactored to use the new modular system
    import subprocess
    
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
        print("Current Configuration:")
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
        print("Configuration validation complete.")
        print("Any issues have been logged.")
    else:
        print("Use --show or --validate with the config command")


def handle_list_command(args, config):
    """Handle list command."""
    import subprocess
    subprocess.run(['python', 'simple_ux_tester.py', 'list'])


def handle_clean_command(args, config):
    """Handle clean command."""
    import subprocess
    subprocess.run(['python', 'simple_ux_tester.py', 'clean', '--keep', str(args.keep)])


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Load and validate configuration
    config = load_config(args.config)
    config = validate_config(config)
    
    # Handle commands
    if args.command == 'test':
        handle_test_command(args, config)
    elif args.command == 'config':
        handle_config_command(args, config)
    elif args.command == 'list':
        handle_list_command(args, config)
    elif args.command == 'clean':
        handle_clean_command(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 