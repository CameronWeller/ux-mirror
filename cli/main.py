#!/usr/bin/env python3
"""
UX-MIRROR Command Line Interface
================================

Modern CLI for the UX testing framework with multi-agent support.
"""
import argparse
import sys
import asyncio
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

# Add src to path for imports during development
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

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
        description='UX-MIRROR Testing Framework - Multi-Agent UX Intelligence',
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

    # Agent management commands
    agent_parser = subparsers.add_parser('agent', help='Agent management')
    agent_subparsers = agent_parser.add_subparsers(dest='agent_action', help='Agent actions')
    
    # Start agents
    start_parser = agent_subparsers.add_parser('start', help='Start agents')
    start_parser.add_argument('agent_type', choices=['orchestrator', 'visual', 'metrics', 'all'], 
                             help='Type of agent to start')
    start_parser.add_argument('--host', default='localhost', help='Host to bind/connect to')
    start_parser.add_argument('--port', type=int, default=8765, help='Port to use')
    start_parser.add_argument('--auto-monitor', action='store_true', 
                             help='Start with automatic monitoring enabled')
    start_parser.add_argument('--gpu', action='store_true', help='Enable GPU acceleration')
    
    # Stop agents
    stop_parser = agent_subparsers.add_parser('stop', help='Stop agents')
    stop_parser.add_argument('agent_type', choices=['orchestrator', 'visual', 'metrics', 'all'], 
                            help='Type of agent to stop')
    
    # Agent status
    status_parser = agent_subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('--orchestrator-host', default='localhost', 
                              help='Orchestrator host')
    status_parser.add_argument('--orchestrator-port', type=int, default=8765, 
                              help='Orchestrator port')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time monitoring')
    monitor_subparsers = monitor_parser.add_subparsers(dest='monitor_action', help='Monitor actions')
    
    # Start monitoring
    start_monitor_parser = monitor_subparsers.add_parser('start', help='Start real-time monitoring')
    start_monitor_parser.add_argument('--interval', type=float, default=5.0, 
                                     help='Monitoring interval in seconds')
    start_monitor_parser.add_argument('--targets', nargs='+', 
                                     help='Specific targets to monitor')
    start_monitor_parser.add_argument('--orchestrator-host', default='localhost')
    start_monitor_parser.add_argument('--orchestrator-port', type=int, default=8765)
    
    # Stop monitoring
    stop_monitor_parser = monitor_subparsers.add_parser('stop', help='Stop real-time monitoring')
    stop_monitor_parser.add_argument('--orchestrator-host', default='localhost')
    stop_monitor_parser.add_argument('--orchestrator-port', type=int, default=8765)
    
    # Show monitoring status
    monitor_status_parser = monitor_subparsers.add_parser('status', help='Show monitoring status')
    monitor_status_parser.add_argument('--orchestrator-host', default='localhost')
    monitor_status_parser.add_argument('--orchestrator-port', type=int, default=8765)
    
    # Insights command
    insights_parser = subparsers.add_parser('insights', help='View UX insights')
    insights_parser.add_argument('--limit', type=int, default=20, 
                                help='Number of recent insights to show')
    insights_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'],
                                help='Filter by severity level')
    insights_parser.add_argument('--type', choices=['performance', 'usability', 'accessibility', 'engagement'],
                                help='Filter by insight type')
    insights_parser.add_argument('--orchestrator-host', default='localhost')
    insights_parser.add_argument('--orchestrator-port', type=int, default=8765)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    dashboard_parser.add_argument('--port', type=int, default=3000, help='Dashboard port')
    dashboard_parser.add_argument('--orchestrator-host', default='localhost')
    dashboard_parser.add_argument('--orchestrator-port', type=int, default=8765)
    
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


def handle_agent_command(args, config):
    """Handle agent management commands."""
    if args.agent_action == 'start':
        handle_start_agent(args, config)
    elif args.agent_action == 'stop':
        handle_stop_agent(args, config)
    elif args.agent_action == 'status':
        handle_agent_status(args, config)
    else:
        print("Use 'start', 'stop', or 'status' with the agent command")


def handle_start_agent(args, config):
    """Start specified agents."""
    print(f"🚀 Starting {args.agent_type} agent(s)...")
    
    if args.agent_type == 'orchestrator' or args.agent_type == 'all':
        start_orchestrator(args)
    
    if args.agent_type == 'visual' or args.agent_type == 'all':
        start_visual_agent(args)
    
    if args.agent_type == 'metrics' or args.agent_type == 'all':
        start_metrics_agent(args)


def start_orchestrator(args):
    """Start the core orchestrator."""
    cmd = ['python', 'agents/core_orchestrator.py', 
           '--host', args.host, '--port', str(args.port)]
    
    if args.auto_monitor:
        cmd.append('--auto-insights')
    
    print(f"Starting Core Orchestrator on {args.host}:{args.port}")
    subprocess.Popen(cmd)


def start_visual_agent(args):
    """Start the visual analysis agent."""
    cmd = ['python', 'agents/visual_analysis_agent.py',
           '--orchestrator-host', args.host, 
           '--orchestrator-port', str(args.port)]
    
    if args.auto_monitor:
        cmd.extend(['--auto-monitor', '--monitor-interval', '5.0'])
    
    print(f"Starting Visual Analysis Agent (connecting to {args.host}:{args.port})")
    subprocess.Popen(cmd)


def start_metrics_agent(args):
    """Start the metrics intelligence agent."""
    cmd = ['python', 'agents/metrics_intelligence.py',
           '--orchestrator-host', args.host,
           '--orchestrator-port', str(args.port)]
    
    print(f"Starting Metrics Intelligence Agent (connecting to {args.host}:{args.port})")
    subprocess.Popen(cmd)


def handle_stop_agent(args, config):
    """Stop specified agents."""
    print(f"🛑 Stopping {args.agent_type} agent(s)...")
    
    # Use secure subprocess.run instead of vulnerable os.system
    import subprocess
    import signal
    
    def safe_pkill(process_name):
        """Safely kill processes by name using subprocess."""
        try:
            result = subprocess.run(
                ['pkill', '-f', process_name], 
                check=False, 
                timeout=30,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Successfully stopped processes matching: {process_name}")
            elif result.returncode == 1:
                print(f"⚠️  No processes found matching: {process_name}")
            else:
                print(f"❌ Error stopping processes: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout while stopping processes matching: {process_name}")
        except FileNotFoundError:
            print("❌ 'pkill' command not found. Unable to stop processes.")
        except Exception as e:
            print(f"❌ Unexpected error stopping processes: {e}")
    
    if args.agent_type == 'all':
        safe_pkill('core_orchestrator.py')
        safe_pkill('visual_analysis_agent.py')
        safe_pkill('metrics_intelligence.py')
    elif args.agent_type == 'orchestrator':
        safe_pkill('core_orchestrator.py')
    elif args.agent_type == 'visual':
        safe_pkill('visual_analysis_agent.py')
    elif args.agent_type == 'metrics':
        safe_pkill('metrics_intelligence.py')


def handle_agent_status(args, config):
    """Show agent status via orchestrator API."""
    try:
        # For demonstration, we'll create a simple status check
        # In production, this would query the orchestrator's REST API
        print("📊 Agent Status:")
        print("=" * 50)
        print("Core Orchestrator: ❓ (checking...)")
        print("Visual Analysis Agent: ❓ (checking...)")
        print("Metrics Intelligence Agent: ❓ (checking...)")
        print()
        print("💡 Use 'ux-tester monitor status' for detailed real-time status")
        
    except Exception as e:
        print(f"❌ Error checking agent status: {e}")


def handle_monitor_command(args, config):
    """Handle monitoring commands."""
    if args.monitor_action == 'start':
        handle_start_monitoring(args, config)
    elif args.monitor_action == 'stop':
        handle_stop_monitoring(args, config)
    elif args.monitor_action == 'status':
        handle_monitor_status(args, config)
    else:
        print("Use 'start', 'stop', or 'status' with the monitor command")


def handle_start_monitoring(args, config):
    """Start real-time monitoring."""
    print("🔍 Starting real-time monitoring...")
    print(f"   Interval: {args.interval}s")
    if args.targets:
        print(f"   Targets: {', '.join(args.targets)}")
    print(f"   Orchestrator: {args.orchestrator_host}:{args.orchestrator_port}")
    
    # In production, this would send a command to the orchestrator
    print("✅ Monitoring started (simulated)")
    print("💡 Use 'ux-tester insights' to view collected insights")


def handle_stop_monitoring(args, config):
    """Stop real-time monitoring."""
    print("⏹️  Stopping real-time monitoring...")
    print("✅ Monitoring stopped (simulated)")


def handle_monitor_status(args, config):
    """Show monitoring status."""
    print("📈 Monitoring Status:")
    print("=" * 50)
    print("🔍 Real-time monitoring: ⚪ Inactive")
    print("🎯 Monitoring targets: None")
    print("📊 Insights generated: 0")
    print("🏥 System health: 🟢 Good")
    print()
    print("💡 Use 'ux-tester monitor start' to begin monitoring")


def handle_insights_command(args, config):
    """Handle insights viewing."""
    print(f"🧠 Recent UX Insights (limit: {args.limit}):")
    print("=" * 60)
    
    # Mock insights for demonstration
    insights = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "usability",
            "severity": "medium",
            "description": "Low contrast detected in button elements",
            "recommendations": ["Increase contrast ratio", "Review color scheme"]
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "performance",
            "severity": "high",
            "description": "Response time exceeded threshold (750ms)",
            "recommendations": ["Optimize resource loading", "Review database queries"]
        }
    ]
    
    for i, insight in enumerate(insights, 1):
        severity_icons = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🟠',
            'critical': '🔴'
        }
        
        icon = severity_icons.get(insight['severity'], '⚪')
        print(f"{i}. {icon} [{insight['type'].upper()}] {insight['description']}")
        print(f"   Severity: {insight['severity']}")
        print(f"   Recommendations: {', '.join(insight['recommendations'])}")
        print()
    
    print("💡 Use 'ux-tester agent start all' to begin collecting real insights")


def handle_dashboard_command(args, config):
    """Launch web dashboard."""
    print(f"🌐 Launching UX-MIRROR Dashboard on port {args.port}...")
    print(f"   Dashboard URL: http://localhost:{args.port}")
    print(f"   Orchestrator: {args.orchestrator_host}:{args.orchestrator_port}")
    
    # In production, this would start a web server
    print("⚠️  Dashboard not yet implemented")
    print("💡 Use 'ux-tester insights' for text-based insights")


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
        
        # Add the project root to Python path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Also add current working directory
        sys.path.insert(0, os.getcwd())
        
        from game_testing_session import GameUXTestingController
        
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


def print_welcome():
    """Print welcome message with system info."""
    print("🎯 UX-MIRROR: Self-Programming GPU-Driven UX Intelligence System")
    print("=" * 65)
    print("✨ Multi-Agent Architecture for Real-Time UX Analysis")
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
    elif args.command == 'agent':
        handle_agent_command(args, config)
    elif args.command == 'monitor':
        handle_monitor_command(args, config)
    elif args.command == 'insights':
        handle_insights_command(args, config)
    elif args.command == 'dashboard':
        handle_dashboard_command(args, config)
    elif args.command == 'game':
        handle_game_command(args, config)
    elif args.command == 'config':
        handle_config_command(args, config)
    elif args.command == 'list':
        handle_list_command(args, config)
    elif args.command == 'clean':
        handle_clean_command(args, config)
    else:
        print("🚀 Quick Start Guide:")
        print("=" * 30)
        print("1. Game UX Testing (3:1 feedback cycles):")
        print("   ux-tester game --iterations 12 --feedback-ratio 3")
        print()
        print("2. Start the multi-agent system:")
        print("   ux-tester agent start all")
        print()
        print("3. Begin real-time monitoring:")
        print("   ux-tester monitor start")
        print()
        print("4. View UX insights:")
        print("   ux-tester insights")
        print()
        print("5. For legacy testing:")
        print("   ux-tester test --before")
        print("   # perform interaction")
        print("   ux-tester test --after")
        print("   ux-tester test --analyze")
        print()
        parser.print_help()


if __name__ == "__main__":
    main() 