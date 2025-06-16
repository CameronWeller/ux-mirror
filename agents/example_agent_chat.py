#!/usr/bin/env python3
"""
Example script to interact with Anthropic agents from this chat
This allows you to communicate with specialized agents for the UX Mirror project
"""

import os
import sys
from typing import Optional

# Simple agent interaction without external dependencies
class SimpleAgent:
    """Simple agent for direct interaction"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.prompts = {
            "system_architect": """You are the System Architect Agent for the UX Mirror project.
Your personality: methodical optimizer, detail-oriented, performance-focused, integration specialist.
Focus on: Vulkan-HIP interop, GPU optimization, system design, performance bottlenecks.""",
            
            "ux_intelligence": """You are the UX Intelligence Agent for the UX Mirror project.
Your personality: user empathy analyzer, behavior-focused, adaptive learning, feedback-oriented.
Focus on: user patterns, metrics analysis, heatmap generation, UX optimization suggestions.""",
            
            "integration": """You are the Integration Specialist Agent for the UX Mirror project.
Your personality: bridge builder, communication-focused, debugging expert, system connectivity.
Focus on: testing frameworks, CI/CD, agent communication, error handling.""",
            
            "code_review": """You are the Code Review Agent for the UX Mirror project.
Your personality: quality guardian, best practices enforcer, security-conscious, performance-aware.
Focus on: code quality, security vulnerabilities, performance issues, documentation.""",
            
            "documentation": """You are the Documentation Agent for the UX Mirror project.
Your personality: clarity seeker, user-focused writer, example provider, knowledge organizer.
Focus on: API documentation, tutorials, architecture diagrams, user guides."""
        }
        
        self.system_prompt = self.prompts.get(agent_type, self.prompts["system_architect"])
    
    def get_prompt(self, user_message: str) -> str:
        """Generate a complete prompt for the agent"""
        return f"""
{self.system_prompt}

Current project context:
- UX Mirror: GPU-accelerated UX intelligence system
- Technologies: Vulkan 1.3, HIP/CUDA, C++20
- Goal: Autonomous interface optimization through real-time analysis

User request:
{user_message}

Please provide a detailed response focusing on your area of expertise.
"""

def main():
    """Interactive agent chat"""
    print("🤖 UX Mirror Agent Interaction System")
    print("=====================================\n")
    
    # Select agent type
    print("Available agents:")
    print("1. system_architect - System design and GPU optimization")
    print("2. ux_intelligence - User experience analysis")
    print("3. integration - Testing and CI/CD")
    print("4. code_review - Code quality and security")
    print("5. documentation - Technical writing\n")
    
    agent_choice = input("Select agent (1-5): ").strip()
    agent_map = {
        "1": "system_architect",
        "2": "ux_intelligence", 
        "3": "integration",
        "4": "code_review",
        "5": "documentation"
    }
    
    agent_type = agent_map.get(agent_choice, "system_architect")
    agent = SimpleAgent(agent_type)
    
    print(f"\n✅ Connected to {agent_type.replace('_', ' ').title()} Agent")
    print("Type 'exit' to quit, 'switch' to change agents\n")
    
    while True:
        user_input = input("\nYour question: ").strip()
        
        if user_input.lower() == 'exit':
            print("\n👋 Goodbye!")
            break
        elif user_input.lower() == 'switch':
            # Restart to select new agent
            main()
            break
        elif user_input:
            # Generate prompt
            full_prompt = agent.get_prompt(user_input)
            
            print("\n" + "="*50)
            print("AGENT PROMPT (Copy this to Claude):")
            print("="*50)
            print(full_prompt)
            print("="*50)
            print("\nCopy the above prompt and paste it into your Claude chat for agent response.")
            print("The agent will respond with expertise in their specialized area.")

if __name__ == "__main__":
    # Example usage for quick tasks
    if len(sys.argv) > 2:
        agent_type = sys.argv[1]
        question = " ".join(sys.argv[2:])
        agent = SimpleAgent(agent_type)
        print(agent.get_prompt(question))
    else:
        main()

# Quick usage examples:
# python example_agent_chat.py system_architect "How should I implement the Vulkan-HIP shared memory?"
# python example_agent_chat.py ux_intelligence "What metrics should we track for user interactions?"
# python example_agent_chat.py integration "How do we set up CI/CD for GPU testing?" 