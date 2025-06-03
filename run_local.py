import asyncio
from agents.github_integration import GitHubIntegration, TaskNode, TaskState
from datetime import datetime
import uvicorn
import webbrowser
import threading
import time

def open_browser():
    """Open browser after a short delay to ensure server is running"""
    time.sleep(2)
    webbrowser.open('http://localhost:8001')

def main():
    # Initialize with dummy credentials for local testing
    github_agent = GitHubIntegration(
        webhook_secret="local_test_secret",
        github_token="local_test_token"
    )
    
    # Create rich test task trees
    auth_task_tree = TaskNode(
        id="auth_main",
        title="User Authentication System",
        status="in_progress",
        progress=0.65,
        priority="high",
        subtasks=[
            TaskNode(
                id="auth_backend",
                title="Backend Authentication",
                status="completed",
                progress=1.0,
                priority="high",
                subtasks=[
                    TaskNode(
                        id="auth_jwt",
                        title="JWT Token Implementation",
                        status="completed",
                        progress=1.0,
                        priority="high"
                    ),
                    TaskNode(
                        id="auth_validation",
                        title="User Validation Logic",
                        status="completed",
                        progress=1.0,
                        priority="medium"
                    )
                ]
            ),
            TaskNode(
                id="auth_frontend",
                title="Frontend Integration",
                status="in_progress",
                progress=0.4,
                priority="medium",
                subtasks=[
                    TaskNode(
                        id="auth_login_form",
                        title="Login Form Component",
                        status="completed",
                        progress=1.0,
                        priority="high"
                    ),
                    TaskNode(
                        id="auth_session_mgmt",
                        title="Session Management",
                        status="in_progress",
                        progress=0.3,
                        priority="medium"
                    )
                ]
            ),
            TaskNode(
                id="auth_testing",
                title="Testing & Security",
                status="pending",
                progress=0.0,
                priority="high",
                subtasks=[
                    TaskNode(
                        id="auth_unit_tests",
                        title="Unit Tests",
                        status="pending",
                        progress=0.0,
                        priority="medium"
                    ),
                    TaskNode(
                        id="auth_security_audit",
                        title="Security Audit",
                        status="pending",
                        progress=0.0,
                        priority="high"
                    )
                ]
            )
        ]
    )
    
    ui_task_tree = TaskNode(
        id="ui_main",
        title="Mobile UI Improvements",
        status="in_progress",
        progress=0.3,
        priority="medium",
        subtasks=[
            TaskNode(
                id="ui_responsive",
                title="Responsive Design",
                status="in_progress",
                progress=0.5,
                priority="high"
            ),
            TaskNode(
                id="ui_accessibility",
                title="Accessibility Features",
                status="pending",
                progress=0.0,
                priority="medium"
            ),
            TaskNode(
                id="ui_performance",
                title="Performance Optimization",
                status="pending",
                progress=0.0,
                priority="low"
            )
        ]
    )
    
    # Create rich test tasks with the task trees
    test_tasks = [
        TaskState(
            issue_number=1,
            status="in_progress",
            title="Implement user authentication",
            description="Add OAuth2 authentication to the application with JWT tokens",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pr_number=101,
            labels=["feature", "security", "high-priority"],
            assignees=["developer1", "security-team"],
            task_tree=auth_task_tree,
            repository="ux-mirror/auth-service"
        ),
        TaskState(
            issue_number=2,
            status="in_progress",
            title="Fix login page layout for mobile",
            description="Adjust responsive design for mobile devices and improve accessibility",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pr_number=102,
            labels=["bug", "ui", "mobile"],
            assignees=["developer2", "ux-team"],
            task_tree=ui_task_tree,
            repository="ux-mirror/frontend"
        ),
        TaskState(
            issue_number=3,
            status="pending",
            title="Database migration for user profiles",
            description="Migrate user profile data to new schema with enhanced security",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pr_number=None,
            labels=["database", "migration", "users"],
            assignees=["database-team"],
            task_tree=TaskNode(
                id="db_migration",
                title="Database Migration",
                status="pending",
                progress=0.0,
                priority="high",
                subtasks=[
                    TaskNode(
                        id="db_backup",
                        title="Create Backup",
                        status="pending",
                        progress=0.0,
                        priority="critical"
                    ),
                    TaskNode(
                        id="db_schema",
                        title="Update Schema",
                        status="pending",
                        progress=0.0,
                        priority="high"
                    ),
                    TaskNode(
                        id="db_data_migration",
                        title="Migrate Data",
                        status="pending",
                        progress=0.0,
                        priority="high"
                    )
                ]
            ),
            repository="ux-mirror/database"
        )
    ]
    
    # Add test tasks to the agent
    for task in test_tasks:
        github_agent.active_tasks[task.issue_number] = task
    
    # Update agent progress
    github_agent.subagents["code_analyzer"].current_task = "Analyzing authentication system complexity"
    github_agent.subagents["code_analyzer"].progress = 0.85
    
    github_agent.subagents["test_generator"].status = "active"
    github_agent.subagents["test_generator"].current_task = "Generating unit tests for auth module"
    github_agent.subagents["test_generator"].progress = 0.25
    
    github_agent.subagents["security_checker"].current_task = "Reviewing JWT implementation security"
    github_agent.subagents["security_checker"].progress = 0.60
    
    print("🚀 Starting local Task Organizer dashboard...")
    print("📊 Dashboard URL: http://localhost:8001")
    print("📋 Loaded 3 test tasks with detailed breakdowns")
    print("🤖 Initialized 3 AI agents with current progress")
    print("🌐 Opening browser in 2 seconds...")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the server on port 8001 to avoid conflicts
    uvicorn.run(github_agent.app, host="127.0.0.1", port=8001)

if __name__ == "__main__":
    main() 