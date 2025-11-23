#!/usr/bin/env python3
"""
Universal Active Monitoring Examples

Demonstrates monitoring different application types:
- Web applications
- Windows executables
- Games (with FPS/stutter detection)
- Mobile applications
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integration.universal_active_monitor import (
    UniversalActiveMonitor,
    ApplicationType,
    ProblemDetected,
    PerformanceMetrics
)


def print_problem(problem: ProblemDetected):
    """Print detected problems"""
    print(f"\n⚠️  [{problem.severity.upper()}] {problem.category}: {problem.description}")
    if problem.performance_metrics:
        metrics = problem.performance_metrics
        if metrics.fps:
            print(f"   FPS: {metrics.fps:.1f}")
        if metrics.frame_time_ms:
            print(f"   Frame Time: {metrics.frame_time_ms:.2f}ms")


def print_performance(metrics: PerformanceMetrics):
    """Print performance updates"""
    if metrics.fps:
        status = "✅" if metrics.fps >= 55 else "⚠️" if metrics.fps >= 30 else "❌"
        print(f"{status} FPS: {metrics.fps:.1f}", end="\r")
        if metrics.hitch_detected:
            print(f"\n🚨 HITCH DETECTED! Frame time: {metrics.frame_time_ms:.1f}ms")


async def monitor_web_app():
    """Example: Monitor a web application"""
    print("=" * 60)
    print("Web Application Monitoring")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    monitor = UniversalActiveMonitor(api_key, ApplicationType.WEB)
    monitor.on_problem_detected = print_problem
    
    try:
        await monitor.start_monitoring("https://example.com", headless=False)
        print("Monitoring web app... Press Ctrl+C to stop")
        
        while monitor.monitoring:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await monitor.stop_monitoring()
        print_summary(monitor)


async def monitor_windows_app():
    """Example: Monitor a Windows executable"""
    print("=" * 60)
    print("Windows Application Monitoring")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    monitor = UniversalActiveMonitor(api_key, ApplicationType.WINDOWS_EXE)
    monitor.on_problem_detected = print_problem
    monitor.on_performance_update = print_performance
    
    # Configure for desktop app
    monitor.target_fps = 60.0
    monitor.stutter_threshold_ms = 20.0  # 50fps minimum
    
    try:
        process_name = input("Enter process name (e.g., 'notepad.exe'): ").strip()
        if not process_name:
            process_name = "notepad.exe"
        
        await monitor.start_monitoring(process_name)
        print("Monitoring Windows app... Press Ctrl+C to stop")
        
        while monitor.monitoring:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await monitor.stop_monitoring()
        print_summary(monitor)


async def monitor_game():
    """Example: Monitor a game with FPS/stutter detection"""
    print("=" * 60)
    print("Game Monitoring - FPS & Stutter Detection")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    monitor = UniversalActiveMonitor(api_key, ApplicationType.GAME)
    monitor.on_problem_detected = print_problem
    monitor.on_performance_update = print_performance
    
    # Configure for game (60fps target, strict thresholds)
    monitor.target_fps = 60.0
    monitor.stutter_threshold_ms = 16.67  # 60fps = 16.67ms per frame
    monitor.hitch_threshold_ms = 50.0  # 3+ frames = hitch
    monitor.fps_drop_threshold = 0.1  # 10% drop = problem
    
    try:
        game_name = input("Enter game name or process: ").strip()
        if not game_name:
            game_name = "game.exe"
        
        await monitor.start_monitoring(
            game_name,
            width=1920,
            height=1080
        )
        
        print("Monitoring game performance...")
        print("Watching for:")
        print("  • FPS drops")
        print("  • Stuttering (frame time spikes)")
        print("  • Hitches (severe frame time spikes)")
        print("  • Input lag")
        print("\nPress Ctrl+C to stop\n")
        
        while monitor.monitoring:
            await asyncio.sleep(1)
            
            # Print periodic stats
            summary = monitor.get_summary()
            if summary.get('fps_stats'):
                fps_stats = summary['fps_stats']
                print(f"\n📊 FPS: {fps_stats.get('current', 0):.1f} | "
                      f"Avg: {fps_stats.get('average', 0):.1f} | "
                      f"Min: {fps_stats.get('min', 0):.1f} | "
                      f"Max: {fps_stats.get('max', 0):.1f}", end="\r")
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        await monitor.stop_monitoring()
        print_summary(monitor)


def print_summary(monitor: UniversalActiveMonitor):
    """Print monitoring session summary"""
    summary = monitor.get_summary()
    
    print("\n" + "=" * 60)
    print("📊 Monitoring Session Summary")
    print("=" * 60)
    print(f"Application Type: {summary['app_type']}")
    print(f"Problems Detected: {summary['total_problems']}")
    
    if summary.get('problems_by_severity'):
        print("\nBy Severity:")
        for severity, count in summary['problems_by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")
    
    if summary.get('problems_by_category'):
        print("\nBy Category:")
        for category, count in summary['problems_by_category'].items():
            if count > 0:
                print(f"  {category}: {count}")
    
    if summary.get('performance'):
        perf = summary['performance']
        print("\nPerformance Metrics:")
        if perf.get('fps'):
            print(f"  FPS: {perf['fps']:.1f}")
        if perf.get('frame_time_ms'):
            print(f"  Frame Time: {perf['frame_time_ms']:.2f}ms")
        if perf.get('stutter_count'):
            print(f"  Stutters: {perf['stutter_count']}")
        if perf.get('hitch_detected'):
            print(f"  Hitches: {'Yes' if perf['hitch_detected'] else 'No'}")
    
    if summary.get('fps_stats'):
        fps_stats = summary['fps_stats']
        print("\nFPS Statistics:")
        print(f"  Current: {fps_stats.get('current', 0):.1f}")
        print(f"  Average: {fps_stats.get('average', 0):.1f}")
        print(f"  Min: {fps_stats.get('min', 0):.1f}")
        print(f"  Max: {fps_stats.get('max', 0):.1f}")
    
    print("=" * 60)


async def main():
    """Main menu"""
    print("=" * 60)
    print("Universal Active Monitoring - UX-Mirror")
    print("=" * 60)
    print("\nSelect application type to monitor:")
    print("1. Web Application")
    print("2. Windows Executable")
    print("3. Game (FPS/Stutter Detection)")
    print("4. Mobile Application (coming soon)")
    print("\n0. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        await monitor_web_app()
    elif choice == "2":
        await monitor_windows_app()
    elif choice == "3":
        await monitor_game()
    elif choice == "4":
        print("Mobile monitoring coming soon!")
    else:
        print("Exiting...")


if __name__ == "__main__":
    asyncio.run(main())

