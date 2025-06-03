import os
import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, HTTPException, Header, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from agents.task_organizer import TaskOrganizer, TaskStatus
import asyncio
from datetime import datetime
import aiohttp
from pydantic import BaseModel
import webbrowser
import threading

class SubAgent(BaseModel):
    id: str
    name: str
    status: str
    current_task: str
    progress: float
    last_activity: datetime

class TaskNode(BaseModel):
    id: str
    title: str
    status: str
    progress: float
    subtasks: List['TaskNode'] = []
    assigned_agent: Optional[str] = None
    estimated_time: Optional[str] = None
    priority: str = "medium"

class TaskState(BaseModel):
    issue_number: int
    status: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    pr_number: Optional[int]
    labels: List[str]
    assignees: List[str]
    task_tree: Optional[TaskNode] = None
    repository: str = ""

class GitHubIntegration:
    def __init__(self, webhook_secret: str, github_token: str):
        self.webhook_secret = webhook_secret
        self.github = Github(github_token)
        self.task_organizer = TaskOrganizer()
        self.app = FastAPI(title="GitHub Task Organizer")
        self.active_tasks: Dict[int, TaskState] = {}
        self.websocket_connections: List[WebSocket] = []
        self.subagents: Dict[str, SubAgent] = {}
        self.setup_routes()
        self._init_subagents()
    
    def _init_subagents(self):
        """Initialize some example subagents."""
        self.subagents = {
            "code_analyzer": SubAgent(
                id="code_analyzer",
                name="Code Analyzer",
                status="active",
                current_task="Analyzing authentication patterns",
                progress=0.75,
                last_activity=datetime.now()
            ),
            "test_generator": SubAgent(
                id="test_generator",
                name="Test Generator",
                status="idle",
                current_task="Waiting for code analysis",
                progress=0.0,
                last_activity=datetime.now()
            ),
            "security_checker": SubAgent(
                id="security_checker",
                name="Security Checker",
                status="active",
                current_task="Scanning for vulnerabilities",
                progress=0.45,
                last_activity=datetime.now()
            )
        }
    
    def setup_routes(self):
        # Webhook endpoint
        @self.app.post("/webhook")
        async def handle_webhook(
            request: Request,
            x_github_event: str = Header(None),
            x_hub_signature: str = Header(None)
        ):
            payload = await request.body()
            if not self._verify_signature(payload, x_hub_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            event_data = await request.json()
            
            # Enhanced event handling
            if x_github_event == "issues":
                await self._handle_issue_event(event_data)
            elif x_github_event == "pull_request":
                await self._handle_pull_request_event(event_data)
            elif x_github_event == "push":
                await self._handle_push_event(event_data)
            elif x_github_event == "issue_comment":
                await self._handle_comment_event(event_data)
            elif x_github_event == "label":
                await self._handle_label_event(event_data)
            
            # Broadcast update to all connected clients
            await self._broadcast_update()
            return {"status": "success"}
        
        # Enhanced Dashboard
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            return """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Task Organizer Dashboard</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        * { box-sizing: border-box; margin: 0; padding: 0; }
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: #333;
                            min-height: 100vh;
                        }
                        .container { 
                            max-width: 1200px; 
                            margin: 0 auto; 
                            padding: 20px; 
                        }
                        .header {
                            background: white;
                            border-radius: 10px;
                            padding: 20px;
                            margin-bottom: 20px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        }
                        .dashboard-grid {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 20px;
                        }
                        @media (max-width: 768px) {
                            .dashboard-grid { grid-template-columns: 1fr; }
                        }
                        .panel {
                            background: white;
                            border-radius: 10px;
                            padding: 20px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        }
                        .panel h2 {
                            color: #5a67d8;
                            margin-bottom: 15px;
                            font-size: 1.5rem;
                        }
                        .task-tree {
                            font-family: monospace;
                            background: #f7fafc;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #5a67d8;
                        }
                        .tree-node {
                            margin: 5px 0;
                            padding: 8px;
                            background: white;
                            border-radius: 4px;
                            border-left: 3px solid #e2e8f0;
                            transition: all 0.2s;
                        }
                        .tree-node:hover {
                            border-left-color: #5a67d8;
                            transform: translateX(5px);
                        }
                        .tree-node.status-pending { border-left-color: #f6ad55; }
                        .tree-node.status-in_progress { border-left-color: #4299e1; }
                        .tree-node.status-completed { border-left-color: #48bb78; }
                        .subtask {
                            margin-left: 20px;
                            font-size: 0.9em;
                            opacity: 0.8;
                        }
                        .progress-bar {
                            width: 100%;
                            height: 6px;
                            background: #e2e8f0;
                            border-radius: 3px;
                            overflow: hidden;
                            margin: 5px 0;
                        }
                        .progress-fill {
                            height: 100%;
                            background: linear-gradient(90deg, #48bb78, #38a169);
                            transition: width 0.3s ease;
                        }
                        .agent-card {
                            background: #f7fafc;
                            border-radius: 8px;
                            padding: 12px;
                            margin: 8px 0;
                            border-left: 4px solid #e2e8f0;
                        }
                        .agent-card.active { border-left-color: #48bb78; }
                        .agent-card.idle { border-left-color: #a0aec0; }
                        .agent-status {
                            display: inline-block;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 0.8em;
                            font-weight: bold;
                        }
                        .status-active { background: #c6f6d5; color: #22543d; }
                        .status-idle { background: #e2e8f0; color: #4a5568; }
                        .actions {
                            margin-top: 15px;
                            display: flex;
                            gap: 10px;
                            flex-wrap: wrap;
                        }
                        button {
                            padding: 8px 16px;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-weight: 500;
                            transition: all 0.2s;
                        }
                        .btn-approve {
                            background: #48bb78;
                            color: white;
                        }
                        .btn-approve:hover {
                            background: #38a169;
                            transform: translateY(-1px);
                        }
                        .btn-changes {
                            background: #f56565;
                            color: white;
                        }
                        .btn-changes:hover {
                            background: #e53e3e;
                            transform: translateY(-1px);
                        }
                        .status-indicator {
                            display: inline-block;
                            width: 10px;
                            height: 10px;
                            border-radius: 50%;
                            margin-right: 8px;
                        }
                        .indicator-pending { background: #f6ad55; }
                        .indicator-in_progress { background: #4299e1; }
                        .indicator-completed { background: #48bb78; }
                        .indicator-approved { background: #9f7aea; }
                    </style>
                    <script>
                        const ws = new WebSocket('ws://' + window.location.host + '/ws');
                        
                        ws.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            updateDashboard(data);
                        };
                        
                        function updateDashboard(data) {
                            updateTasks(data.tasks || []);
                            updateAgents(data.agents || {});
                        }
                        
                        function updateTasks(tasks) {
                            const tasksDiv = document.getElementById('tasks');
                            tasksDiv.innerHTML = '';
                            
                            tasks.forEach(task => {
                                const taskElement = document.createElement('div');
                                taskElement.className = 'panel';
                                taskElement.innerHTML = `
                                    <h3>
                                        <span class="status-indicator indicator-${task.status}"></span>
                                        ${task.title}
                                    </h3>
                                    <p><strong>Status:</strong> ${task.status}</p>
                                    <p><strong>PR:</strong> ${task.pr_number || 'None'}</p>
                                    <p><strong>Labels:</strong> ${task.labels.join(', ')}</p>
                                    ${renderTaskTree(task.task_tree)}
                                    <div class="actions">
                                        <button class="btn-approve" onclick="approveTask(${task.issue_number})">
                                            ✓ Approve
                                        </button>
                                        <button class="btn-changes" onclick="requestChanges(${task.issue_number})">
                                            ✗ Request Changes
                                        </button>
                                    </div>
                                `;
                                tasksDiv.appendChild(taskElement);
                            });
                        }
                        
                        function renderTaskTree(tree) {
                            if (!tree) return '<p>No task breakdown available</p>';
                            
                            function renderNode(node, level = 0) {
                                const indent = '  '.repeat(level);
                                const progress = node.progress || 0;
                                let html = `
                                    <div class="tree-node status-${node.status}" style="margin-left: ${level * 20}px">
                                        <div>${node.title}</div>
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${progress * 100}%"></div>
                                        </div>
                                        <small>Progress: ${Math.round(progress * 100)}% | Priority: ${node.priority}</small>
                                    </div>
                                `;
                                
                                if (node.subtasks && node.subtasks.length > 0) {
                                    node.subtasks.forEach(subtask => {
                                        html += renderNode(subtask, level + 1);
                                    });
                                }
                                
                                return html;
                            }
                            
                            return '<div class="task-tree">' + renderNode(tree) + '</div>';
                        }
                        
                        function updateAgents(agents) {
                            const agentsDiv = document.getElementById('agents');
                            agentsDiv.innerHTML = '';
                            
                            Object.values(agents).forEach(agent => {
                                const agentElement = document.createElement('div');
                                agentElement.className = `agent-card ${agent.status}`;
                                agentElement.innerHTML = `
                                    <h4>${agent.name} <span class="agent-status status-${agent.status}">${agent.status}</span></h4>
                                    <p><strong>Current Task:</strong> ${agent.current_task}</p>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${agent.progress * 100}%"></div>
                                    </div>
                                    <small>Progress: ${Math.round(agent.progress * 100)}% | Last activity: ${new Date(agent.last_activity).toLocaleTimeString()}</small>
                                `;
                                agentsDiv.appendChild(agentElement);
                            });
                        }
                        
                        async function approveTask(issueNumber) {
                            await fetch('/approve/' + issueNumber, { method: 'POST' });
                        }
                        
                        async function requestChanges(issueNumber) {
                            await fetch('/request-changes/' + issueNumber, { method: 'POST' });
                        }
                        
                        // Auto-refresh every 30 seconds
                        setInterval(() => {
                            fetch('/api/status').then(r => r.json()).then(updateDashboard);
                        }, 30000);
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🤖 Task Organizer Dashboard</h1>
                            <p>Real-time monitoring of tasks and AI agents</p>
                        </div>
                        
                        <div class="dashboard-grid">
                            <div class="panel">
                                <h2>📋 Active Tasks</h2>
                                <div id="tasks"></div>
                            </div>
                            
                            <div class="panel">
                                <h2>🤖 AI Agents</h2>
                                <div id="agents"></div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_connections.append(websocket)
            # Send initial data
            await websocket.send_json({
                "tasks": [task.dict() for task in self.active_tasks.values()],
                "agents": {k: v.dict() for k, v in self.subagents.items()}
            })
            try:
                while True:
                    await websocket.receive_text()
            except:
                self.websocket_connections.remove(websocket)
        
        @self.app.get("/api/status")
        async def get_status():
            return {
                "tasks": [task.dict() for task in self.active_tasks.values()],
                "agents": {k: v.dict() for k, v in self.subagents.items()}
            }
        
        # Task management endpoints
        @self.app.post("/approve/{issue_number}")
        async def approve_task(issue_number: int):
            if issue_number in self.active_tasks:
                task = self.active_tasks[issue_number]
                task.status = TaskStatus.APPROVED.value
                await self._broadcast_update()
                return {"status": "success"}
            return {"status": "error", "message": "Task not found"}
        
        @self.app.post("/request-changes/{issue_number}")
        async def request_changes(issue_number: int):
            if issue_number in self.active_tasks:
                task = self.active_tasks[issue_number]
                task.status = TaskStatus.IN_PROGRESS.value
                await self._broadcast_update()
                return {"status": "success"}
            return {"status": "error", "message": "Task not found"}
    
    async def _broadcast_update(self):
        """Broadcast task updates to all connected clients."""
        data = {
            "tasks": [task.dict() for task in self.active_tasks.values()],
            "agents": {k: v.dict() for k, v in self.subagents.items()}
        }
        for connection in self.websocket_connections:
            try:
                await connection.send_json(data)
            except:
                self.websocket_connections.remove(connection)
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify the GitHub webhook signature."""
        if not signature:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha1
        ).hexdigest()
        
        return hmac.compare_digest(f"sha1={expected_signature}", signature)
    
    async def _handle_comment_event(self, event_data: Dict[str, Any]):
        """Handle issue comment events."""
        action = event_data.get("action")
        comment = event_data.get("comment", {})
        issue = event_data.get("issue", {})
        
        if action == "created" and issue.get("number") in self.active_tasks:
            task = self.active_tasks[issue.get("number")]
            # Process comment for task updates
            comment_body = comment.get("body", "")
            if "!approve" in comment_body.lower():
                await self.approve_task(issue.get("number"))
            elif "!changes" in comment_body.lower():
                await self.request_changes(issue.get("number"))
    
    async def _handle_label_event(self, event_data: Dict[str, Any]):
        """Handle label events."""
        action = event_data.get("action")
        label = event_data.get("label", {})
        issue = event_data.get("issue", {})
        
        if action == "added" and issue.get("number") in self.active_tasks:
            task = self.active_tasks[issue.get("number")]
            task.labels.append(label.get("name"))
            await self._broadcast_update()
    
    async def _handle_issue_event(self, event_data: Dict[str, Any]):
        """Handle GitHub issue events."""
        action = event_data.get("action")
        issue = event_data.get("issue", {})
        
        if action == "opened":
            # Process new issue as a task
            task_description = issue.get("body", "")
            context = {
                "issue_number": issue.get("number"),
                "repository": event_data.get("repository", {}).get("full_name"),
                "labels": [label.get("name") for label in issue.get("labels", [])]
            }
            
            # Process the task
            result = await self.task_organizer.process_task(task_description, context)
            
            # Create a branch and PR for the task
            repo = self.github.get_repo(context["repository"])
            branch_name = f"feature/issue-{issue.get('number')}"
            
            # Create branch from main
            main_branch = repo.get_branch("main")
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=main_branch.commit.sha
            )
            
            # Create PR
            pr = await self.task_organizer.create_pull_request(result, branch_name)
            created_pr = repo.create_pull(
                title=pr["title"],
                body=pr["description"],
                head=branch_name,
                base="main"
            )
            
            # Store task state
            self.active_tasks[issue.get("number")] = TaskState(
                issue_number=issue.get("number"),
                status=TaskStatus.PENDING.value,
                title=issue.get("title"),
                description=issue.get("body"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                pr_number=created_pr.number,
                labels=context["labels"],
                assignees=[assignee.get("login") for assignee in issue.get("assignees", [])]
            )
            
            await self._broadcast_update()
    
    async def _handle_pull_request_event(self, event_data: Dict[str, Any]):
        """Handle GitHub pull request events."""
        action = event_data.get("action")
        pr = event_data.get("pull_request", {})
        
        if action == "reviewed":
            review_state = event_data.get("review", {}).get("state")
            issue_number = int(pr.get("title", "").split("-")[-1])
            
            if issue_number in self.active_tasks:
                task = self.active_tasks[issue_number]
                if review_state == "approved":
                    task.status = TaskStatus.APPROVED.value
                elif review_state == "changes_requested":
                    task.status = TaskStatus.IN_PROGRESS.value
                
                task.updated_at = datetime.now()
                await self._broadcast_update()
    
    async def _handle_push_event(self, event_data: Dict[str, Any]):
        """Handle GitHub push events."""
        # Monitor for changes that might affect existing tasks
        commits = event_data.get("commits", [])
        for commit in commits:
            # Check if commit message references any issues
            message = commit.get("message", "")
            if "#" in message:
                # Extract issue numbers and update related tasks
                pass
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI application."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 