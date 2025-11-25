#!/usr/bin/env python3
"""
Game UX Testing Session Controller

Manages game-focused UX testing sessions with:
- 3:1 feedback cycle (user feedback every 3 iterations)
- Screenshot capture and display
- Real-time game metrics analysis
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass

from agents.visual_analysis_agent import VisualAnalysisAgent, VisualAnalysisResult
from agents.core_orchestrator import CoreOrchestrator
from core.screenshot_analyzer import ScreenshotAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualAnalysisResult:
    """Result of visual analysis"""
    timestamp: datetime
    change_score: float
    quality_score: float
    ui_elements_detected: int
    response_time: Optional[float]
    attention_areas: List[Tuple[int, int, int, int]]  # Bounding boxes (x, y, w, h)
    accessibility_issues: List[str]
    performance_impact: str
    recommendations: List[str]

@dataclass
class GameTestingSession:
    """Game testing session configuration and state"""
    session_id: str
    total_iterations: int
    feedback_ratio: int  # Every N iterations for user feedback
    current_iteration: int = 0
    feedback_sessions: List[Dict] = None
    screenshots_dir: str = "game_screenshots"
    
    def __post_init__(self):
        if self.feedback_sessions is None:
            self.feedback_sessions = []
        # Create screenshots directory
        Path(self.screenshots_dir).mkdir(exist_ok=True)

class GameUXTestingController:
    """
    Main controller for game UX testing sessions with screenshot display
    and 3:1 feedback cycles
    """
    
    def __init__(self, config_path: str = "game_ux_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.session: Optional[GameTestingSession] = None
        
        # Analysis components
        self.screenshot_analyzer = ScreenshotAnalyzer()
        self.visual_agent: Optional[VisualAnalysisAgent] = None
        self.orchestrator: Optional[CoreOrchestrator] = None
        
        # Session state
        self.running = False
        self.iteration_results: List[VisualAnalysisResult] = []
        self.user_feedback_history: List[Dict] = []
        
        # Screenshot display
        self.current_screenshot: Optional[np.ndarray] = None
        self.display_size = (800, 600)  # For screenshot display
        
        logger.info("Game UX Testing Controller initialized")
    
    def _load_config(self) -> Dict:
        """Load game testing configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {self.config_path} not found")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default game testing configuration"""
        return {
            "game_ux_testing": {
                "session_config": {
                    "feedback_ratio": "3:1",
                    "session_duration": 60,
                    "analysis_intervals": [15, 30, 45, 60]
                },
                "game_specific_metrics": {
                    "ui_responsiveness": {"target_fps": 60},
                    "visual_clarity": {"text_readability_threshold": 0.8},
                    "accessibility": {"colorblind_compatibility": True}
                }
            }
        }
    
    async def start_game_testing_session(self, 
                                       total_iterations: int = 12, 
                                       feedback_ratio: int = 3) -> str:
        """
        Start a new game testing session
        
        Args:
            total_iterations: Total number of analysis iterations
            feedback_ratio: User feedback every N iterations (3:1 means every 3 iterations)
        
        Returns:
            Session ID
        """
        session_id = f"game_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.session = GameTestingSession(
            session_id=session_id,
            total_iterations=total_iterations,
            feedback_ratio=feedback_ratio
        )
        
        # Initialize agents
        await self._initialize_agents()
        
        logger.info(f"Started game testing session: {session_id}")
        logger.info(f"Configuration: {total_iterations} iterations with feedback every {feedback_ratio} cycles")
        
        return session_id
    
    async def _initialize_agents(self):
        """Initialize visual analysis and orchestrator agents"""
        try:
            # Start orchestrator
            self.orchestrator = CoreOrchestrator()
            orchestrator_task = asyncio.create_task(self.orchestrator.start())
            
            # Give orchestrator time to start
            await asyncio.sleep(2)
            
            # Start visual analysis agent
            self.visual_agent = VisualAnalysisAgent()
            visual_task = asyncio.create_task(self.visual_agent.start())
            
            # Give agents time to connect
            await asyncio.sleep(3)
            
            logger.info("Game testing agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            # Fall back to local screenshot analysis
            logger.info("Falling back to local screenshot analysis")
    
    async def run_testing_session(self):
        """Run the complete game testing session with 3:1 feedback cycles"""
        if not self.session:
            raise ValueError("No active session. Call start_game_testing_session() first.")
        
        self.running = True
        logger.info(f"Running game testing session: {self.session.session_id}")
        
        try:
            while (self.session.current_iteration < self.session.total_iterations 
                   and self.running):
                
                # Run analysis iteration
                await self._run_iteration()
                
                # Check if it's time for user feedback
                if (self.session.current_iteration % self.session.feedback_ratio == 0 
                    and self.session.current_iteration > 0):
                    await self._conduct_user_feedback_session()
                
                # Brief pause between iterations
                await asyncio.sleep(2)
            
            # Final session summary
            await self._generate_session_summary()
            
        except KeyboardInterrupt:
            logger.info("Testing session interrupted by user")
        except Exception as e:
            logger.error(f"Error during testing session: {e}")
        finally:
            self.running = False
            await self._cleanup_session()
    
    async def _run_iteration(self):
        """Run a single testing iteration"""
        self.session.current_iteration += 1
        iteration_num = self.session.current_iteration
        
        logger.info(f"Running iteration {iteration_num}/{self.session.total_iterations}")
        
        # Capture screenshot
        screenshot_path = await self._capture_screenshot(iteration_num)
        
        # Analyze screenshot
        if self.visual_agent and self.visual_agent.running:
            # Use visual agent for analysis
            result = await self.visual_agent._analyze_specific_screenshot(screenshot_path)
        else:
            # Use local screenshot analyzer
            result = await self._analyze_screenshot_locally(screenshot_path)
        
        # Display screenshot with analysis results
        await self._display_screenshot_with_analysis(screenshot_path, result)
        
        # Store results
        self.iteration_results.append(result)
        
        # Log iteration summary
        logger.info(f"Iteration {iteration_num} completed:")
        logger.info(f"  - Quality Score: {result.quality_score:.2f}")
        logger.info(f"  - UI Elements Detected: {result.ui_elements_detected}")
        logger.info(f"  - Change Score: {result.change_score:.2f}")
        
        if result.accessibility_issues:
            logger.warning(f"  - Accessibility Issues: {len(result.accessibility_issues)}")
    
    async def _capture_screenshot(self, iteration_num: int) -> str:
        """Capture screenshot and save it"""
        try:
            # Use the screenshot analyzer to take screenshot
            image_path = await self.screenshot_analyzer.capture_screenshot()
            
            # Copy to session-specific location
            session_screenshot_path = (
                Path(self.session.screenshots_dir) / 
                f"{self.session.session_id}_iter_{iteration_num:03d}.png"
            )
            
            # Copy the file
            import shutil
            shutil.copy2(image_path, session_screenshot_path)
            
            logger.info(f"Screenshot saved: {session_screenshot_path}")
            return str(session_screenshot_path)
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    async def _analyze_screenshot_locally(self, screenshot_path: str) -> VisualAnalysisResult:
        """Analyze screenshot using local methods when agents are unavailable"""
        if not screenshot_path or not Path(screenshot_path).exists():
            # Return dummy result
            return VisualAnalysisResult(
                timestamp=datetime.now(),
                change_score=0.0,
                quality_score=0.5,
                ui_elements_detected=0,
                response_time=None,
                attention_areas=[],
                accessibility_issues=[],
                performance_impact="unknown",
                recommendations=["Agent connection required for detailed analysis"]
            )
        
        # Use screenshot analyzer for basic analysis
        result = await self.screenshot_analyzer.analyze_image(screenshot_path)
        
        # Convert to VisualAnalysisResult format
        return VisualAnalysisResult(
            timestamp=datetime.now(),
            change_score=result.get('change_score', 0.0),
            quality_score=result.get('quality_score', 0.5),
            ui_elements_detected=len(result.get('ui_elements', [])),
            response_time=result.get('analysis_time'),
            attention_areas=[(elem.get('x', 0), elem.get('y', 0), 
                            elem.get('width', 100), elem.get('height', 50)) 
                           for elem in result.get('ui_elements', [])],
            accessibility_issues=result.get('accessibility_issues', []),
            performance_impact=result.get('performance_assessment', 'good'),
            recommendations=result.get('recommendations', [])
        )
    
    async def _display_screenshot_with_analysis(self, screenshot_path: str, 
                                              analysis_result: VisualAnalysisResult):
        """Display screenshot with visual analysis overlay"""
        if not screenshot_path or not Path(screenshot_path).exists():
            logger.warning("No screenshot to display")
            return
        
        try:
            # Load screenshot
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Could not load screenshot: {screenshot_path}")
                return
            
            # Convert BGR to RGB for matplotlib
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Display original screenshot
            ax1.imshow(image_rgb)
            ax1.set_title(f"Game Screenshot - Iteration {self.session.current_iteration}")
            ax1.axis('off')
            
            # Add UI element detection overlays
            for i, (x, y, w, h) in enumerate(analysis_result.attention_areas):
                rect = patches.Rectangle((x, y), w, h, linewidth=2, 
                                       edgecolor='red', facecolor='none', alpha=0.7)
                ax1.add_patch(rect)
                ax1.text(x, y-5, f'UI-{i+1}', color='red', fontweight='bold')
            
            # Display analysis metrics
            ax2.axis('off')
            metrics_text = f"""
GAME UX ANALYSIS - Iteration {self.session.current_iteration}
═══════════════════════════════════════════════

📊 QUALITY METRICS:
   Visual Quality: {analysis_result.quality_score:.1%}
   UI Elements: {analysis_result.ui_elements_detected}
   Change Score: {analysis_result.change_score:.1%}

🎮 GAMING FOCUS AREAS:
   • UI Responsiveness: {'✓' if analysis_result.quality_score > 0.7 else '⚠'}
   • Visual Clarity: {'✓' if analysis_result.quality_score > 0.6 else '⚠'}
   • Element Detection: {'✓' if analysis_result.ui_elements_detected > 0 else '⚠'}

♿ ACCESSIBILITY:
   Issues Found: {len(analysis_result.accessibility_issues)}
   {chr(10).join([f"   • {issue}" for issue in analysis_result.accessibility_issues[:3]])}

⚡ PERFORMANCE:
   Impact: {analysis_result.performance_impact.title()}
   Response Time: {analysis_result.response_time:.3f}s if analysis_result.response_time else 'N/A'

💡 RECOMMENDATIONS:
   {chr(10).join([f"   • {rec}" for rec in analysis_result.recommendations[:4]])}

📅 Next Feedback Session: 
   {'In ' + str(self.session.feedback_ratio - (self.session.current_iteration % self.session.feedback_ratio)) + ' iterations' if (self.session.current_iteration % self.session.feedback_ratio) != 0 else 'NOW'}
            """
            
            ax2.text(0.05, 0.95, metrics_text, transform=ax2.transAxes, 
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
            
            plt.tight_layout()
            
            # Save analysis visualization
            viz_path = (Path(self.session.screenshots_dir) / 
                       f"{self.session.session_id}_analysis_{self.session.current_iteration:03d}.png")
            plt.savefig(viz_path, dpi=100, bbox_inches='tight')
            
            # Show the plot
            plt.show(block=False)
            plt.pause(0.1)  # Brief pause to ensure display
            
            logger.info(f"Screenshot analysis visualization saved: {viz_path}")
            
        except Exception as e:
            logger.error(f"Failed to display screenshot analysis: {e}")
    
    async def _conduct_user_feedback_session(self):
        """Conduct user feedback session every N iterations"""
        feedback_session_num = self.session.current_iteration // self.session.feedback_ratio
        
        logger.info(f"🎯 USER FEEDBACK SESSION #{feedback_session_num}")
        logger.info(f"   Completed {self.session.current_iteration} iterations")
        
        # Display recent results summary
        recent_results = self.iteration_results[-self.session.feedback_ratio:]
        avg_quality = sum(r.quality_score for r in recent_results) / len(recent_results)
        total_ui_elements = sum(r.ui_elements_detected for r in recent_results)
        
        print(f"\n{'='*60}")
        print(f"🎮 GAME UX FEEDBACK SESSION #{feedback_session_num}")
        print(f"{'='*60}")
        print(f"📊 Last {self.session.feedback_ratio} iterations summary:")
        print(f"   • Average Quality Score: {avg_quality:.1%}")
        print(f"   • Total UI Elements Detected: {total_ui_elements}")
        print(f"   • Iterations Completed: {self.session.current_iteration}/{self.session.total_iterations}")
        
        # Collect user feedback
        feedback = await self._collect_user_feedback()
        
        # Store feedback
        feedback_entry = {
            "session_number": feedback_session_num,
            "iteration_range": f"{self.session.current_iteration - self.session.feedback_ratio + 1}-{self.session.current_iteration}",
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "metrics_summary": {
                "avg_quality": avg_quality,
                "total_ui_elements": total_ui_elements
            }
        }
        
        self.user_feedback_history.append(feedback_entry)
        self.session.feedback_sessions.append(feedback_entry)
        
        logger.info(f"User feedback session #{feedback_session_num} completed")
    
    async def _collect_user_feedback(self) -> Dict:
        """Collect user feedback interactively"""
        print(f"\n🎯 Please provide your feedback on the game UX:")
        print(f"   (Press Enter to skip any question)\n")
        
        # Check for any manual feedback from monitoring window
        manual_feedback = self._load_manual_feedback()
        if manual_feedback:
            print(f"📋 Found {len(manual_feedback)} manual feedback entries:")
            for i, feedback in enumerate(manual_feedback[-3:], 1):  # Show last 3
                timestamp = feedback.get('timestamp', 'Unknown time')
                message = feedback.get('message', 'No message')
                print(f"   {i}. [{timestamp[:19]}] {message}")
            print()
        
        feedback = {}
        
        # Game-specific feedback questions
        questions = [
            ("ui_responsiveness", "How responsive does the UI feel? (1-5, 5=very responsive): "),
            ("visual_clarity", "How clear and readable are the game elements? (1-5, 5=very clear): "),
            ("navigation_ease", "How easy is it to navigate the game interface? (1-5, 5=very easy): "),
            ("accessibility", "Any accessibility concerns? (text): "),
            ("overall_experience", "Overall game UX impression? (text): "),
            ("specific_issues", "Any specific issues noticed? (text): "),
            ("suggestions", "Suggestions for improvement? (text): ")
        ]
        
        for key, question in questions:
            try:
                response = input(question).strip()
                if response:
                    # Try to convert to number if it looks like a rating
                    if key in ["ui_responsiveness", "visual_clarity", "navigation_ease"]:
                        try:
                            feedback[key] = int(response)
                        except ValueError:
                            feedback[key] = response
                    else:
                        feedback[key] = response
            except KeyboardInterrupt:
                print("\nFeedback collection interrupted")
                break
            except Exception as e:
                logger.warning(f"Error collecting feedback for {key}: {e}")
        
        print(f"\n✅ Feedback collected. Continuing with testing...\n")
        
        # Include manual feedback if available
        manual_feedback = self._load_manual_feedback()
        if manual_feedback:
            feedback['manual_feedback_entries'] = len(manual_feedback)
            feedback['recent_manual_feedback'] = [
                {
                    'timestamp': fb.get('timestamp'),
                    'message': fb.get('message'),
                    'quality_score': fb.get('analysis', {}).get('quality_score', 0)
                }
                for fb in manual_feedback[-3:]  # Include last 3 manual entries
            ]
        
        return feedback
    
    def _load_manual_feedback(self) -> List[Dict]:
        """Load manual feedback from monitoring window"""
        try:
            feedback_file = Path("game_screenshots") / "manual_feedback_log.json"
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"Could not load manual feedback: {e}")
            return []
    
    async def _generate_session_summary(self):
        """Generate comprehensive session summary"""
        if not self.session:
            return
        
        logger.info(f"Generating session summary for {self.session.session_id}")
        
        # Calculate overall metrics
        if self.iteration_results:
            avg_quality = sum(r.quality_score for r in self.iteration_results) / len(self.iteration_results)
            total_ui_elements = sum(r.ui_elements_detected for r in self.iteration_results)
            total_accessibility_issues = sum(len(r.accessibility_issues) for r in self.iteration_results)
        else:
            avg_quality = 0.0
            total_ui_elements = 0
            total_accessibility_issues = 0
        
        # Generate summary report
        summary = {
            "session_id": self.session.session_id,
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "total_iterations": self.session.total_iterations,
                "feedback_ratio": self.session.feedback_ratio,
                "feedback_sessions_conducted": len(self.session.feedback_sessions)
            },
            "analysis_results": {
                "iterations_completed": len(self.iteration_results),
                "average_quality_score": avg_quality,
                "total_ui_elements_detected": total_ui_elements,
                "total_accessibility_issues": total_accessibility_issues
            },
            "user_feedback": self.user_feedback_history,
            "key_insights": self._generate_key_insights()
        }
        
        # Save summary to file
        summary_path = Path(self.session.screenshots_dir) / f"{self.session.session_id}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Display summary
        print(f"\n{'='*80}")
        print(f"🎮 GAME UX TESTING SESSION SUMMARY")
        print(f"{'='*80}")
        print(f"Session ID: {self.session.session_id}")
        print(f"Completed: {len(self.iteration_results)}/{self.session.total_iterations} iterations")
        print(f"Feedback Sessions: {len(self.session.feedback_sessions)}")
        print(f"Average Quality Score: {avg_quality:.1%}")
        print(f"UI Elements Detected: {total_ui_elements}")
        print(f"Accessibility Issues: {total_accessibility_issues}")
        print(f"\n📋 Key Insights:")
        for insight in summary["key_insights"]:
            print(f"   • {insight}")
        print(f"\n📁 Session files saved in: {self.session.screenshots_dir}/")
        print(f"   • Screenshots with analysis overlays")
        print(f"   • Session summary: {summary_path.name}")
        print(f"{'='*80}\n")
        
        logger.info(f"Session summary saved: {summary_path}")
    
    def _generate_key_insights(self) -> List[str]:
        """Generate key insights from session data"""
        insights = []
        
        if not self.iteration_results:
            return ["No analysis data available"]
        
        # Quality trend analysis
        quality_scores = [r.quality_score for r in self.iteration_results]
        if len(quality_scores) > 1:
            if quality_scores[-1] > quality_scores[0]:
                insights.append("Visual quality improved over the session")
            elif quality_scores[-1] < quality_scores[0]:
                insights.append("Visual quality declined during session")
            else:
                insights.append("Visual quality remained stable")
        
        # UI element detection consistency
        ui_counts = [r.ui_elements_detected for r in self.iteration_results]
        avg_ui_count = sum(ui_counts) / len(ui_counts)
        if avg_ui_count > 10:
            insights.append("Rich UI with many interactive elements detected")
        elif avg_ui_count < 3:
            insights.append("Minimal UI design with few interactive elements")
        
        # Accessibility analysis
        total_issues = sum(len(r.accessibility_issues) for r in self.iteration_results)
        if total_issues == 0:
            insights.append("No significant accessibility issues detected")
        elif total_issues > 5:
            insights.append(f"Multiple accessibility concerns found ({total_issues} issues)")
        
        # User feedback insights
        if self.user_feedback_history:
            feedback_count = len(self.user_feedback_history)
            insights.append(f"Collected user feedback across {feedback_count} sessions")
            
            # Analyze feedback ratings if available
            ratings = []
            for feedback in self.user_feedback_history:
                for key in ["ui_responsiveness", "visual_clarity", "navigation_ease"]:
                    if key in feedback["feedback"] and isinstance(feedback["feedback"][key], int):
                        ratings.append(feedback["feedback"][key])
            
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                if avg_rating >= 4:
                    insights.append("User feedback indicates positive UX experience")
                elif avg_rating <= 2:
                    insights.append("User feedback indicates UX improvements needed")
                else:
                    insights.append("User feedback indicates mixed UX experience")
        
        return insights if insights else ["Session completed successfully"]
    
    async def _cleanup_session(self):
        """Clean up session resources"""
        if self.visual_agent:
            # Stop visual agent if running
            self.visual_agent.running = False
        
        if self.orchestrator:
            # Stop orchestrator if running
            self.orchestrator.running = False
        
        logger.info("Session cleanup completed")
    
    def stop_session(self):
        """Stop the current testing session"""
        self.running = False
        logger.info("Testing session stop requested")

# Main execution
async def main():
    """Run game UX testing session"""
    controller = GameUXTestingController()
    
    try:
        # Start session with 3:1 feedback ratio
        session_id = await controller.start_game_testing_session(
            total_iterations=12,  # 12 iterations total
            feedback_ratio=3      # User feedback every 3 iterations
        )
        
        print(f"\n🎮 Starting Game UX Testing Session")
        print(f"Session ID: {session_id}")
        print(f"Configuration: 12 iterations with user feedback every 3 cycles")
        print(f"Screenshots will be displayed with analysis overlays")
        print(f"Press Ctrl+C to stop the session early\n")
        
        # Run the testing session
        await controller.run_testing_session()
        
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user")
    except Exception as e:
        logger.error(f"Session error: {e}")
    finally:
        controller.stop_session()

if __name__ == "__main__":
    asyncio.run(main()) 