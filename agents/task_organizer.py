import os
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv
from enum import Enum
import logging
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskOrganizer:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TaskOrganizer')
        
    async def process_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task with retry logic and error handling.
        """
        for attempt in range(self.max_retries):
            try:
                # Prepare the prompt with context
                prompt = self._prepare_prompt(task_description, context)
                
                # Get response from Claude
                response = await self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # Process and validate the response
                result = self._process_response(response.content[0].text)
                validation_result = await self._validate_task_plan(result)
                
                if validation_result["is_valid"]:
                    return result
                else:
                    self.logger.warning(f"Task plan validation failed: {validation_result['issues']}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    
            except Exception as e:
                self.logger.error(f"Error processing task (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception("Failed to process task after maximum retries")
    
    async def create_pull_request(self, task_result: Dict[str, Any], branch_name: str) -> Dict[str, Any]:
        """
        Create a pull request for the proposed changes.
        """
        try:
            # Prepare PR description
            pr_description = self._prepare_pr_description(task_result)
            
            # TODO: Implement actual PR creation using your preferred Git provider
            # This is a placeholder for the PR creation logic
            pr_data = {
                "title": f"Task Implementation: {task_result.get('title', 'Untitled Task')}",
                "description": pr_description,
                "branch": branch_name,
                "status": TaskStatus.PENDING.value
            }
            
            self.logger.info(f"Created pull request for task: {pr_data['title']}")
            return pr_data
            
        except Exception as e:
            self.logger.error(f"Error creating pull request: {str(e)}")
            raise
    
    async def _validate_task_plan(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Self-validate the task plan using Claude.
        """
        validation_prompt = f"""Validate the following task plan for completeness, feasibility, and alignment with best practices:

{task_plan['raw_response']}

Provide validation in the following format:
1. Is the plan valid? (yes/no)
2. List any issues or concerns
3. Suggestions for improvement
"""
        
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": validation_prompt
                    }
                ]
            )
            
            # Parse validation response
            validation_text = response.content[0].text
            is_valid = "yes" in validation_text.lower()
            
            return {
                "is_valid": is_valid,
                "validation_response": validation_text,
                "issues": [] if is_valid else self._extract_issues(validation_text)
            }
            
        except Exception as e:
            self.logger.error(f"Error in task plan validation: {str(e)}")
            return {
                "is_valid": False,
                "validation_response": str(e),
                "issues": ["Validation failed due to technical error"]
            }
    
    def _extract_issues(self, validation_text: str) -> List[str]:
        """Extract issues from validation response."""
        # Simple implementation - can be enhanced with more sophisticated parsing
        lines = validation_text.split('\n')
        issues = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['issue', 'concern', 'problem', 'missing']):
                issues.append(line.strip())
        return issues
    
    def _prepare_pr_description(self, task_result: Dict[str, Any]) -> str:
        """Prepare a detailed PR description from the task result."""
        return f"""# Task Implementation

## Overview
{task_result.get('raw_response', 'No description available')}

## Changes
- Task breakdown: {len(task_result.get('task_breakdown', []))} subtasks
- Priority: {task_result.get('priority', 'Not specified')}
- Timeline: {task_result.get('timeline', 'Not specified')}

## Validation
This implementation has been self-validated for:
- Completeness
- Feasibility
- Best practices alignment

## Additional Notes
Please review the implementation and provide feedback.
"""
    
    def _prepare_prompt(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare a detailed prompt for the AI."""
        prompt = f"""You are a task organization and orientation assistant. Analyze the following task and provide:
1. Task breakdown into subtasks
2. Priority assessment
3. Required resources
4. Potential challenges
5. Recommended approach
6. Timeline estimation
7. Implementation steps
8. Testing strategy
9. Success criteria

Task Description: {task_description}
"""
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        return prompt
    
    def _process_response(self, response_text: str) -> Dict[str, Any]:
        """Process the AI response into a structured format."""
        # Basic structure for the response
        structured_response = {
            "task_breakdown": [],
            "priority": "",
            "resources": [],
            "challenges": [],
            "approach": "",
            "timeline": "",
            "implementation_steps": [],
            "testing_strategy": "",
            "success_criteria": [],
            "raw_response": response_text,
            "timestamp": datetime.now().isoformat()
        }
        
        # TODO: Implement more sophisticated response parsing
        # For now, we'll return the raw response in a structured format
        
        return structured_response
    
    async def get_task_recommendations(self, current_tasks: List[str]) -> Dict[str, Any]:
        """
        Get recommendations for task organization and prioritization.
        """
        for attempt in range(self.max_retries):
            try:
                prompt = f"""Given the following list of tasks, provide:
1. Optimal task ordering
2. Task dependencies
3. Resource allocation suggestions
4. Time management recommendations
5. Risk assessment
6. Success metrics

Tasks:
{chr(10).join(f'- {task}' for task in current_tasks)}
"""
                
                response = await self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                return {
                    "recommendations": response.content[0].text,
                    "raw_response": response.content[0].text,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error getting recommendations (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception("Failed to get recommendations after maximum retries")
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = [] 