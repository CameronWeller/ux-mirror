#!/usr/bin/env python3
"""
UX-MIRROR Core System Startup
=============================

Starts the core UX-MIRROR system with:
1. Simple Orchestrator (lightweight coordinator)
2. Visual Analysis Agent (screenshot analysis)
3. Metrics Intelligence Agent (user behavior tracking)
4. Autonomous Implementation Agent (code generation)

This demonstrates the primary functionality without complex orchestration.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import subprocess
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UXMirrorCoreSystem:
    """Manages the core UX-MIRROR system startup"""
    
    def __init__(self):
        self.processes = []
        self.agents_dir = Path("agents")
        
        # Check if agents exist
        self.required_agents = [
            "simple_orchestrator.py",
            "visual_analysis.py", 
            "metrics_intelligence.py",
            "autonomous_implementation.py"
        ]
    
    def check_requirements(self):
        """Check if all required agents exist"""
        missing_agents = []
        for agent in self.required_agents:
            agent_path = self.agents_dir / agent
            if not agent_path.exists():
                missing_agents.append(agent)
        
        if missing_agents:
            logger.error(f"Missing required agents: {missing_agents}")
            return False
        
        logger.info("All required agents found")
        return True
    
    async def start_system(self):
        """Start the core UX-MIRROR system"""
        if not self.check_requirements():
            logger.error("Cannot start system - missing requirements")
            return
        
        logger.info("Starting UX-MIRROR Core System...")
        
        try:
            # Start the simple orchestrator first
            logger.info("Starting Simple Orchestrator...")
            orchestrator_process = subprocess.Popen([
                sys.executable, str(self.agents_dir / "simple_orchestrator.py")
            ])
            self.processes.append(("simple_orchestrator", orchestrator_process))
            
            # Wait a moment for orchestrator to start
            await asyncio.sleep(2)
            
            # Start the core agents
            agents = [
                ("visual_analysis", "visual_analysis.py"),
                ("metrics_intelligence", "metrics_intelligence.py"), 
                ("autonomous_implementation", "autonomous_implementation.py")
            ]
            
            for agent_name, agent_file in agents:
                logger.info(f"Starting {agent_name}...")
                process = subprocess.Popen([
                    sys.executable, str(self.agents_dir / agent_file)
                ])
                self.processes.append((agent_name, process))
                
                # Stagger startup to avoid connection issues
                await asyncio.sleep(1)
            
            logger.info("All agents started successfully!")
            logger.info("UX-MIRROR Core System is now running")
            
            # Monitor the system
            await self.monitor_system()
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        except Exception as e:
            logger.error(f"Error starting system: {e}")
        finally:
            await self.shutdown_system()
    
    async def monitor_system(self):
        """Monitor the running system"""
        logger.info("Monitoring system... Press Ctrl+C to stop")
        
        try:
            while True:
                # Check if all processes are still running
                running_agents = []
                failed_agents = []
                
                for agent_name, process in self.processes:
                    if process.poll() is None:
                        running_agents.append(agent_name)
                    else:
                        failed_agents.append(agent_name)
                
                if failed_agents:
                    logger.warning(f"Failed agents detected: {failed_agents}")
                
                if running_agents:
                    logger.info(f"System status - Running agents: {', '.join(running_agents)}")
                else:
                    logger.error("No agents running!")
                    break
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
    
    async def shutdown_system(self):
        """Gracefully shutdown all agents"""
        logger.info("Shutting down UX-MIRROR Core System...")
        
        for agent_name, process in self.processes:
            try:
                logger.info(f"Stopping {agent_name}...")
                process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {agent_name}...")
                    process.kill()
                    
            except Exception as e:
                logger.error(f"Error stopping {agent_name}: {e}")
        
        self.processes.clear()
        logger.info("System shutdown complete")

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                        UX-MIRROR CORE SYSTEM                    ║
║                   Self-Programming UX Intelligence              ║
║                                                                  ║
║  • Visual Analysis Agent: Screenshot & UI analysis              ║
║  • Metrics Intelligence Agent: User behavior tracking           ║
║  • Autonomous Implementation Agent: Code generation             ║
║  • Simple Orchestrator: Lightweight coordination                ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main entry point"""
    print_banner()
    
    system = UXMirrorCoreSystem()
    
    try:
        asyncio.run(system.start_system())
    except KeyboardInterrupt:
        logger.info("Startup interrupted")
    except Exception as e:
        logger.error(f"System error: {e}")

if __name__ == "__main__":
    main() 