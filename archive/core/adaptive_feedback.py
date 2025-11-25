#!/usr/bin/env python3
"""
Adaptive Feedback Engine for UX-MIRROR

Replaces rigid 3:1 feedback ratios with intelligent, confidence-based user engagement.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class AnalysisConfidence(Enum):
    """Analysis confidence levels"""
    VERY_LOW = "very_low"      # < 0.3
    LOW = "low"                # 0.3 - 0.5
    MODERATE = "moderate"      # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.85
    VERY_HIGH = "very_high"    # > 0.85

class UserEngagementAction(Enum):
    """Actions for user engagement"""
    CONTINUE_ANALYSIS = "continue_analysis"
    REQUEST_INPUT = "request_input"
    IMMEDIATE_ATTENTION = "immediate_attention"
    READY_FOR_REVIEW = "ready_for_review"
    SESSION_COMPLETE = "session_complete"

@dataclass
class AnalysisIteration:
    """Single analysis iteration data"""
    iteration_number: int
    timestamp: datetime
    quality_score: float
    ui_elements_detected: int
    accessibility_issues: List[str]
    recommendations: List[str]
    response_time: float
    change_score: float = 0.0
    confidence_factors: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionState:
    """Current session analysis state"""
    session_id: str
    iterations: List[AnalysisIteration] = field(default_factory=list)
    current_confidence: float = 0.0
    confidence_trend: List[float] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    user_feedback_history: List[Dict] = field(default_factory=list)
    last_user_engagement: Optional[datetime] = None
    session_start: datetime = field(default_factory=datetime.now)

class AdaptiveFeedbackEngine:
    """
    Intelligent feedback engine that adapts to analysis confidence and context
    """
    
    def __init__(self):
        # Confidence thresholds
        self.confidence_thresholds = {
            'ready_for_review': 0.85,
            'high_confidence': 0.7,
            'moderate_confidence': 0.5,
            'low_confidence': 0.3,
            'critical_threshold': 0.2
        }
        
        # Iteration limits
        self.max_iterations = 15
        self.min_iterations = 3
        self.max_time_without_user = timedelta(minutes=30)
        
        # Confidence calculation weights
        self.confidence_weights = {
            'consistency': 0.3,      # How consistent are results across iterations
            'completeness': 0.25,    # How complete is the analysis
            'validation': 0.2,       # How well validated are the findings
            'stability': 0.15,       # How stable are the metrics
            'coverage': 0.1          # How much of the UI is covered
        }
        
        # Session tracking
        self.active_sessions: Dict[str, SessionState] = {}
        
        logger.info("Adaptive Feedback Engine initialized")
    
    def start_session(self, session_id: str, context: Dict[str, Any] = None) -> SessionState:
        """
        Start a new adaptive analysis session
        
        Args:
            session_id: Unique session identifier
            context: Additional context about the session
            
        Returns:
            SessionState object
        """
        session = SessionState(
            session_id=session_id,
            session_start=datetime.now()
        )
        
        if context:
            session.metadata = context
            
        self.active_sessions[session_id] = session
        
        logger.info(f"Started adaptive session: {session_id}")
        return session
    
    def add_iteration(self, session_id: str, iteration_data: Dict[str, Any]) -> AnalysisIteration:
        """
        Add analysis iteration data to session
        
        Args:
            session_id: Session identifier
            iteration_data: Analysis results from this iteration
            
        Returns:
            AnalysisIteration object
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        iteration_num = len(session.iterations) + 1
        
        # Create iteration object
        iteration = AnalysisIteration(
            iteration_number=iteration_num,
            timestamp=datetime.now(),
            quality_score=iteration_data.get('quality_score', 0.0),
            ui_elements_detected=iteration_data.get('ui_elements_detected', 0),
            accessibility_issues=iteration_data.get('accessibility_issues', []),
            recommendations=iteration_data.get('recommendations', []),
            response_time=iteration_data.get('response_time', 0.0),
            change_score=iteration_data.get('change_score', 0.0),
            metadata=iteration_data.get('metadata', {})
        )
        
        # Calculate confidence factors
        iteration.confidence_factors = self._calculate_confidence_factors(session, iteration)
        
        # Add to session
        session.iterations.append(iteration)
        
        # Update session confidence
        session.current_confidence = self._calculate_session_confidence(session)
        session.confidence_trend.append(session.current_confidence)
        
        # Update critical issues
        self._update_critical_issues(session, iteration)
        
        logger.debug(f"Added iteration {iteration_num} to session {session_id}, confidence: {session.current_confidence:.3f}")
        
        return iteration
    
    def determine_action(self, session_id: str) -> Tuple[UserEngagementAction, Dict[str, Any]]:
        """
        Determine what action to take based on current session state
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (action, context_data)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Get current state
        confidence = session.current_confidence
        iterations = len(session.iterations)
        time_since_start = datetime.now() - session.session_start
        
        context = {
            'confidence': confidence,
            'iterations': iterations,
            'session_duration': time_since_start.total_seconds(),
            'confidence_level': self._get_confidence_level(confidence),
            'critical_issues_count': len(session.critical_issues)
        }
        
        # Decision logic
        
        # 1. Critical issues require immediate attention
        if session.critical_issues:
            return UserEngagementAction.IMMEDIATE_ATTENTION, context
        
        # 2. Very high confidence - ready for review
        if confidence >= self.confidence_thresholds['ready_for_review']:
            return UserEngagementAction.READY_FOR_REVIEW, context
        
        # 3. Hit max iterations
        if iterations >= self.max_iterations:
            return UserEngagementAction.SESSION_COMPLETE, context
        
        # 4. Low confidence after reasonable attempts
        if (confidence < self.confidence_thresholds['low_confidence'] and 
            iterations >= self.min_iterations):
            
            # Check if we haven't engaged user recently
            if (not session.last_user_engagement or 
                datetime.now() - session.last_user_engagement > timedelta(minutes=10)):
                return UserEngagementAction.REQUEST_INPUT, context
        
        # 5. Continue analysis
        return UserEngagementAction.CONTINUE_ANALYSIS, context
    
    def add_user_feedback(self, session_id: str, feedback: Dict[str, Any]) -> None:
        """
        Add user feedback to session
        
        Args:
            session_id: Session identifier
            feedback: User feedback data
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        feedback_entry = {
            'timestamp': datetime.now(),
            'iteration_at_feedback': len(session.iterations),
            'confidence_at_feedback': session.current_confidence,
            'feedback': feedback
        }
        
        session.user_feedback_history.append(feedback_entry)
        session.last_user_engagement = datetime.now()
        
        # Boost confidence if user feedback is positive
        self._apply_feedback_boost(session, feedback)
        
        logger.info(f"Added user feedback to session {session_id}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive session summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary dictionary
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Calculate summary metrics
        if session.iterations:
            avg_quality = np.mean([i.quality_score for i in session.iterations])
            total_ui_elements = sum(i.ui_elements_detected for i in session.iterations)
            total_issues = sum(len(i.accessibility_issues) for i in session.iterations)
            avg_response_time = np.mean([i.response_time for i in session.iterations if i.response_time > 0])
        else:
            avg_quality = 0.0
            total_ui_elements = 0
            total_issues = 0
            avg_response_time = 0.0
        
        summary = {
            'session_id': session_id,
            'duration': (datetime.now() - session.session_start).total_seconds(),
            'iterations_completed': len(session.iterations),
            'final_confidence': session.current_confidence,
            'confidence_level': self._get_confidence_level(session.current_confidence),
            'metrics': {
                'avg_quality_score': avg_quality,
                'total_ui_elements': total_ui_elements,
                'total_accessibility_issues': total_issues,
                'avg_response_time': avg_response_time
            },
            'user_feedback_sessions': len(session.user_feedback_history),
            'critical_issues': session.critical_issues,
            'confidence_trend': session.confidence_trend
        }
        
        return summary
    
    def _calculate_confidence_factors(self, session: SessionState, iteration: AnalysisIteration) -> Dict[str, float]:
        """Calculate confidence factors for an iteration"""
        factors = {}
        
        # Consistency: How consistent are quality scores
        if len(session.iterations) > 0:
            recent_scores = [i.quality_score for i in session.iterations[-3:]]  # Last 3
            recent_scores.append(iteration.quality_score)
            consistency = 1.0 - np.std(recent_scores) if len(recent_scores) > 1 else 1.0
            factors['consistency'] = min(1.0, max(0.0, consistency))
        else:
            factors['consistency'] = 0.5  # Neutral for first iteration
        
        # Completeness: Based on quality score and elements detected
        completeness = (iteration.quality_score * 0.7 + 
                       min(1.0, iteration.ui_elements_detected / 10) * 0.3)
        factors['completeness'] = min(1.0, max(0.0, completeness))
        
        # Validation: Based on response time and change detection
        if iteration.response_time > 0:
            response_factor = min(1.0, 1.0 / max(0.1, iteration.response_time / 1000))  # Faster is better
        else:
            response_factor = 0.5
        
        change_factor = min(1.0, iteration.change_score * 2)  # More change = better validation
        validation = (response_factor + change_factor) / 2
        factors['validation'] = min(1.0, max(0.0, validation))
        
        # Stability: How stable are the metrics over time
        if len(session.iterations) >= 2:
            element_counts = [i.ui_elements_detected for i in session.iterations[-2:]]
            element_counts.append(iteration.ui_elements_detected)
            stability = 1.0 - (np.std(element_counts) / max(1, np.mean(element_counts)))
            factors['stability'] = min(1.0, max(0.0, stability))
        else:
            factors['stability'] = 0.5
        
        # Coverage: Based on UI elements and recommendations
        coverage = min(1.0, (iteration.ui_elements_detected / 5 + len(iteration.recommendations) / 3) / 2)
        factors['coverage'] = min(1.0, max(0.0, coverage))
        
        return factors
    
    def _calculate_session_confidence(self, session: SessionState) -> float:
        """Calculate overall session confidence"""
        if not session.iterations:
            return 0.0
        
        latest_iteration = session.iterations[-1]
        factors = latest_iteration.confidence_factors
        
        # Weighted sum of confidence factors
        confidence = sum(factors.get(factor, 0.0) * weight 
                        for factor, weight in self.confidence_weights.items())
        
        # Apply trend bonus/penalty
        if len(session.confidence_trend) >= 3:
            recent_trend = session.confidence_trend[-3:]
            if all(recent_trend[i] <= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                confidence *= 1.1  # Bonus for improving trend
            elif all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                confidence *= 0.9  # Penalty for declining trend
        
        return min(1.0, max(0.0, confidence))
    
    def _update_critical_issues(self, session: SessionState, iteration: AnalysisIteration):
        """Update critical issues list"""
        # Critical quality threshold
        if iteration.quality_score < 0.3:
            issue = f"Very low quality score: {iteration.quality_score:.2f}"
            if issue not in session.critical_issues:
                session.critical_issues.append(issue)
        
        # High number of accessibility issues
        if len(iteration.accessibility_issues) > 5:
            issue = f"High accessibility issue count: {len(iteration.accessibility_issues)}"
            if issue not in session.critical_issues:
                session.critical_issues.append(issue)
        
        # No UI elements detected
        if iteration.ui_elements_detected == 0:
            issue = "No UI elements detected"
            if issue not in session.critical_issues:
                session.critical_issues.append(issue)
    
    def _is_confidence_declining(self, session: SessionState) -> bool:
        """Check if confidence is declining over recent iterations"""
        if len(session.confidence_trend) < 3:
            return False
        
        recent_trend = session.confidence_trend[-3:]
        return all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1))
    
    def _get_confidence_level(self, confidence: float) -> AnalysisConfidence:
        """Convert confidence score to level"""
        if confidence >= 0.85:
            return AnalysisConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return AnalysisConfidence.HIGH
        elif confidence >= 0.5:
            return AnalysisConfidence.MODERATE
        elif confidence >= 0.3:
            return AnalysisConfidence.LOW
        else:
            return AnalysisConfidence.VERY_LOW
    
    def _apply_feedback_boost(self, session: SessionState, feedback: Dict[str, Any]):
        """Apply confidence boost based on user feedback"""
        boost = 0.0
        
        # Positive ratings boost confidence
        for key in ['ui_responsiveness', 'visual_clarity', 'navigation_ease']:
            if key in feedback and isinstance(feedback[key], (int, float)):
                rating = feedback[key]
                if rating >= 4:
                    boost += 0.05
                elif rating <= 2:
                    boost -= 0.05
        
        # Positive text feedback
        positive_keywords = ['good', 'great', 'excellent', 'clear', 'smooth', 'responsive']
        negative_keywords = ['bad', 'poor', 'confusing', 'slow', 'unclear', 'difficult']
        
        feedback_text = str(feedback.get('overall_experience', '')).lower()
        
        for keyword in positive_keywords:
            if keyword in feedback_text:
                boost += 0.02
        
        for keyword in negative_keywords:
            if keyword in feedback_text:
                boost -= 0.02
        
        # Apply boost
        if boost != 0:
            session.current_confidence = min(1.0, max(0.0, session.current_confidence + boost))
            logger.debug(f"Applied feedback boost: {boost:.3f}, new confidence: {session.current_confidence:.3f}") 