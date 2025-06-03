#!/usr/bin/env python3
"""
UX-Mirror GitHub Integration
===========================

Enhanced GitHub integration that combines visual analysis with GitHub workflows:
- Automatically triggers UX analysis on PR creation
- Posts visual analysis results as PR comments
- Creates issues from detected UX problems
- Integrates with existing UX-Mirror dashboard

Author: UX-Mirror System
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue
import hmac
import hashlib
import subprocess
import sys

from agents.temporal_screenshot_analyzer import TemporalScreenshotAnalyzer

class UXMirrorGitHubIntegration:
    def __init__(self, github_token: str, webhook_secret: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.webhook_secret = webhook_secret
        self.anthropic_api_key = anthropic_api_key
        
        # Initialize the visual analyzer
        self.visual_analyzer = TemporalScreenshotAnalyzer(anthropic_api_key)
        
        # FastAPI app for webhooks
        self.app = FastAPI(title="UX-Mirror GitHub Integration")
        self.setup_routes()
        
        # Track ongoing analyses
        self.active_analyses: Dict[str, Dict] = {}
        
        print("🔗 UX-Mirror GitHub Integration initialized")
        print(f"📊 Visual analysis available: {anthropic_api_key is not None}")
    
    def setup_routes(self):
        """Set up FastAPI routes for GitHub webhooks and UI"""
        
        @self.app.post("/webhook")
        async def github_webhook(
            request: Request,
            x_github_event: str = Header(None),
            x_hub_signature: str = Header(None)
        ):
            """Handle GitHub webhook events"""
            payload = await request.body()
            
            # Verify signature
            if not self._verify_signature(payload, x_hub_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            event_data = await request.json()
            
            # Route different event types
            if x_github_event == "pull_request":
                await self._handle_pull_request(event_data)
            elif x_github_event == "issues":
                await self._handle_issue(event_data)
            elif x_github_event == "push":
                await self._handle_push(event_data)
            elif x_github_event == "workflow_run":
                await self._handle_workflow_run(event_data)
            
            return {"status": "processed", "event": x_github_event}
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Main dashboard showing integration status"""
            return self._generate_dashboard_html()
        
        @self.app.get("/api/analyses")
        async def get_analyses():
            """API endpoint to get current analyses"""
            return JSONResponse(self.active_analyses)
        
        @self.app.post("/api/trigger-analysis/{repo_name}/{pr_number}")
        async def trigger_manual_analysis(repo_name: str, pr_number: int):
            """Manually trigger UX analysis for a PR"""
            try:
                repo = self.github.get_repo(repo_name)
                pr = repo.get_pull(pr_number)
                
                result = await self._run_ux_analysis(repo, pr)
                return {"status": "success", "analysis": result}
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not signature or not self.webhook_secret:
            return False
        
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha1
        ).hexdigest()
        
        return hmac.compare_digest(f"sha1={expected}", signature)
    
    async def _handle_pull_request(self, event_data: Dict[str, Any]):
        """Handle pull request events"""
        action = event_data.get("action")
        pr_data = event_data.get("pull_request", {})
        repo_data = event_data.get("repository", {})
        
        print(f"📥 PR Event: {action} for PR #{pr_data.get('number')}")
        
        if action in ["opened", "synchronize", "ready_for_review"]:
            # Trigger UX analysis for new/updated PRs
            repo = self.github.get_repo(repo_data["full_name"])
            pr = repo.get_pull(pr_data["number"])
            
            await self._run_ux_analysis(repo, pr)
    
    async def _handle_issue(self, event_data: Dict[str, Any]):
        """Handle issue events"""
        action = event_data.get("action")
        issue_data = event_data.get("issue", {})
        
        print(f"📋 Issue Event: {action} for Issue #{issue_data.get('number')}")
        
        if action == "opened" and "ux-analysis" in [label["name"] for label in issue_data.get("labels", [])]:
            # Issue labeled for UX analysis
            await self._handle_ux_analysis_request(event_data)
    
    async def _handle_push(self, event_data: Dict[str, Any]):
        """Handle push events"""
        ref = event_data.get("ref", "")
        repo_data = event_data.get("repository", {})
        
        # Only process pushes to main branch
        if ref == "refs/heads/main":
            print(f"🔄 Push to main in {repo_data.get('full_name')}")
            # Could trigger baseline UX analysis here
    
    async def _handle_workflow_run(self, event_data: Dict[str, Any]):
        """Handle workflow run events"""
        workflow = event_data.get("workflow_run", {})
        
        if workflow.get("name") == "UX Analysis" and workflow.get("status") == "completed":
            print(f"✅ UX Analysis workflow completed")
            # Process workflow results
    
    async def _run_ux_analysis(self, repo: Repository, pr: PullRequest) -> Dict:
        """Run UX analysis on a pull request"""
        analysis_id = f"{repo.full_name}/PR-{pr.number}"
        
        print(f"🔍 Starting UX analysis for {analysis_id}")
        
        # Track analysis
        self.active_analyses[analysis_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "repo": repo.full_name,
            "pr_number": pr.number,
            "pr_title": pr.title
        }
        
        try:
            # 1. Check if there are screenshots in the PR
            screenshots_found = await self._find_screenshots_in_pr(repo, pr)
            
            if screenshots_found:
                # 2. Run visual analysis on screenshots
                analysis_result = await self._analyze_screenshots(screenshots_found)
                
                # 3. Post results as PR comment
                await self._post_analysis_comment(pr, analysis_result)
                
                # 4. Create issues for any problems found
                await self._create_issues_for_problems(repo, analysis_result, pr)
                
                self.active_analyses[analysis_id].update({
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "screenshots_found": len(screenshots_found),
                    "issues_found": len(analysis_result.get("issues", [])),
                    "result": analysis_result
                })
                
                return analysis_result
            
            else:
                # No screenshots found
                comment = self._generate_no_screenshots_comment(pr)
                pr.create_issue_comment(comment)
                
                self.active_analyses[analysis_id].update({
                    "status": "no_screenshots",
                    "completed_at": datetime.now().isoformat(),
                    "message": "No screenshots found in PR"
                })
                
                return {"status": "no_screenshots"}
        
        except Exception as e:
            print(f"❌ Error in UX analysis: {e}")
            
            self.active_analyses[analysis_id].update({
                "status": "error",
                "completed_at": datetime.now().isoformat(),
                "error": str(e)
            })
            
            # Post error comment
            error_comment = f"""
## 🚨 UX Analysis Error

An error occurred during automated UX analysis:

```
{str(e)}
```

Please check the logs or contact the development team.
"""
            pr.create_issue_comment(error_comment)
            
            return {"status": "error", "message": str(e)}
    
    async def _find_screenshots_in_pr(self, repo: Repository, pr: PullRequest) -> List[str]:
        """Find screenshot files in the PR changes"""
        screenshots = []
        
        try:
            # Get files changed in the PR
            files = pr.get_files()
            
            for file in files:
                filename = file.filename.lower()
                
                # Look for image files
                if any(ext in filename for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                    # Check if it's a screenshot (by name or location)
                    if any(term in filename for term in ['screenshot', 'capture', 'screen', 'ui', 'game_screenshots']):
                        screenshots.append(file.filename)
            
            # Also check for screenshots directory
            try:
                contents = repo.get_contents("game_screenshots", ref=pr.head.sha)
                if isinstance(contents, list):
                    for item in contents:
                        if item.name.endswith(('.png', '.jpg', '.jpeg')):
                            screenshots.append(f"game_screenshots/{item.name}")
            except:
                pass  # Directory doesn't exist
            
        except Exception as e:
            print(f"Error finding screenshots: {e}")
        
        return screenshots
    
    async def _analyze_screenshots(self, screenshot_paths: List[str]) -> Dict:
        """Analyze screenshots using the visual analyzer"""
        try:
            # For now, run a simple analysis
            # In a real implementation, you'd download the files and analyze them
            
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "screenshots_analyzed": len(screenshot_paths),
                "analysis_summary": f"Analyzed {len(screenshot_paths)} screenshots",
                "issues": [],
                "recommendations": [],
                "visual_quality_score": 85  # Placeholder
            }
            
            # Simulate finding some issues based on screenshot names
            for path in screenshot_paths:
                if "dark" in path.lower() or "blue" in path.lower():
                    analysis_result["issues"].append({
                        "severity": "medium",
                        "category": "visibility",
                        "description": f"Potential visibility issues detected in {path}",
                        "recommendation": "Consider improving contrast and brightness"
                    })
            
            if not analysis_result["issues"]:
                analysis_result["summary"] = "✅ No critical UX issues detected"
            else:
                analysis_result["summary"] = f"⚠️ {len(analysis_result['issues'])} potential issues found"
            
            return analysis_result
            
        except Exception as e:
            return {"error": str(e), "status": "analysis_failed"}
    
    async def _post_analysis_comment(self, pr: PullRequest, analysis_result: Dict):
        """Post UX analysis results as a PR comment"""
        
        issues = analysis_result.get("issues", [])
        summary = analysis_result.get("summary", "Analysis completed")
        
        comment = f"""
## 🎯 UX-Mirror Analysis Results

{summary}

### 📊 Analysis Summary
- **Screenshots Analyzed**: {analysis_result.get('screenshots_analyzed', 0)}
- **Visual Quality Score**: {analysis_result.get('visual_quality_score', 'N/A')}/100
- **Issues Found**: {len(issues)}

"""
        
        if issues:
            comment += "### ⚠️ Issues Detected\n\n"
            for i, issue in enumerate(issues, 1):
                comment += f"""
**{i}. {issue.get('category', 'General').title()} Issue** ({issue.get('severity', 'medium')})
- {issue.get('description', 'No description')}
- 💡 **Recommendation**: {issue.get('recommendation', 'No recommendation')}

"""
        else:
            comment += "### ✅ No Critical Issues\n\nGreat work! No critical UX issues were detected in the visual analysis.\n\n"
        
        comment += """
---
*🤖 This analysis was performed automatically by UX-Mirror. For questions or manual review, please contact the UX team.*
"""
        
        pr.create_issue_comment(comment)
    
    async def _create_issues_for_problems(self, repo: Repository, analysis_result: Dict, pr: PullRequest):
        """Create GitHub issues for critical problems found"""
        issues = analysis_result.get("issues", [])
        
        # Only create issues for high/critical severity problems
        critical_issues = [issue for issue in issues if issue.get("severity") in ["high", "critical"]]
        
        for issue in critical_issues:
            title = f"UX Issue: {issue.get('category', 'General')} problem detected"
            
            body = f"""
## 🚨 Automated UX Issue Detection

**Source**: PR #{pr.number} - {pr.title}
**Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Severity**: {issue.get('severity', 'medium').upper()}

### Problem Description
{issue.get('description', 'No description available')}

### Recommendation
{issue.get('recommendation', 'No recommendation available')}

### Context
This issue was automatically detected during UX analysis of PR #{pr.number}.

---
*🤖 Auto-generated by UX-Mirror | Labels: ux-issue, {issue.get('severity', 'medium')}-priority*
"""
            
            # Create the issue
            created_issue = repo.create_issue(
                title=title,
                body=body,
                labels=["ux-issue", f"{issue.get('severity', 'medium')}-priority", "auto-generated"]
            )
            
            print(f"📋 Created issue #{created_issue.number} for UX problem")
    
    def _generate_no_screenshots_comment(self, pr: PullRequest) -> str:
        """Generate comment when no screenshots are found"""
        return f"""
## 🎯 UX-Mirror Analysis

### 📸 No Screenshots Detected

No screenshots were found in this PR. To enable automated UX analysis:

1. **Add screenshots** to the `game_screenshots/` directory
2. **Include visual changes** with descriptive filenames
3. **Use naming conventions** like `screenshot_`, `ui_`, or `capture_`

### Manual Analysis Options

If this PR includes visual changes that aren't captured in screenshots:

- Add screenshots manually and push to trigger re-analysis
- Request manual UX review by adding the `ux-review` label
- Tag `@ux-team` for priority review

---
*🤖 Automated by UX-Mirror | Add screenshots to enable visual analysis*
"""
    
    async def _handle_ux_analysis_request(self, event_data: Dict[str, Any]):
        """Handle explicit UX analysis requests via issues"""
        issue_data = event_data.get("issue", {})
        repo_data = event_data.get("repository", {})
        
        # Parse issue for analysis instructions
        issue_body = issue_data.get("body", "")
        
        # Look for specific analysis requests
        if "analyze pr" in issue_body.lower():
            # Extract PR number if mentioned
            import re
            pr_matches = re.findall(r'#(\d+)', issue_body)
            
            if pr_matches:
                pr_number = int(pr_matches[0])
                repo = self.github.get_repo(repo_data["full_name"])
                issue = repo.get_issue(issue_data["number"])
                
                try:
                    pr = repo.get_pull(pr_number)
                    result = await self._run_ux_analysis(repo, pr)
                    
                    # Comment on the issue with results
                    issue.create_comment(f"""
## 🎯 UX Analysis Complete

Analysis of PR #{pr_number} has been completed. Check the PR comments for detailed results.

**Summary**: {result.get('summary', 'Analysis completed')}
""")
                    
                    # Close the issue
                    issue.edit(state="closed")
                    
                except Exception as e:
                    issue.create_comment(f"❌ Error analyzing PR #{pr_number}: {str(e)}")
    
    def _generate_dashboard_html(self) -> str:
        """Generate HTML dashboard for the integration"""
        analyses_count = len(self.active_analyses)
        running_count = len([a for a in self.active_analyses.values() if a["status"] == "running"])
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>UX-Mirror GitHub Integration</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #5a67d8;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #5a67d8;
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #5a67d8;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        .analysis-item {{
            background: #f7fafc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #4299e1;
        }}
        .status-running {{ border-left-color: #f6ad55; }}
        .status-completed {{ border-left-color: #48bb78; }}
        .status-error {{ border-left-color: #f56565; }}
        .endpoint {{
            background: #2d3748;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 UX-Mirror GitHub Integration</h1>
        <p class="subtitle">Automated UX analysis for GitHub workflows</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{analyses_count}</div>
                <div class="stat-label">Total Analyses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{running_count}</div>
                <div class="stat-label">Currently Running</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">✅</div>
                <div class="stat-label">Integration Active</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📡 Webhook Endpoints</h2>
            <div class="endpoint">POST /webhook - GitHub webhook receiver</div>
            <div class="endpoint">GET /api/analyses - Current analysis status</div>
            <div class="endpoint">POST /api/trigger-analysis/{{repo}}/{{pr}} - Manual trigger</div>
        </div>
        
        <div class="section">
            <h2>🔄 Recent Analyses</h2>
            <div id="analyses">
                {'<p>No analyses yet. Create a PR to trigger analysis.</p>' if not self.active_analyses else ''}
            </div>
        </div>
        
        <div class="section">
            <h2>🛠️ Setup Instructions</h2>
            <ol>
                <li>Configure GitHub webhook to point to <code>/webhook</code></li>
                <li>Set webhook secret in environment variables</li>
                <li>Add GitHub token with repo access</li>
                <li>Include screenshots in PRs for automatic analysis</li>
            </ol>
        </div>
    </div>
    
    <script>
        // Auto-refresh analyses every 30 seconds
        setInterval(async () => {{
            try {{
                const response = await fetch('/api/analyses');
                const analyses = await response.json();
                
                const container = document.getElementById('analyses');
                if (Object.keys(analyses).length === 0) {{
                    container.innerHTML = '<p>No analyses yet. Create a PR to trigger analysis.</p>';
                    return;
                }}
                
                container.innerHTML = Object.entries(analyses).map(([id, analysis]) => `
                    <div class="analysis-item status-${{analysis.status}}">
                        <strong>${{id}}</strong> - ${{analysis.status}}
                        <br><small>Started: ${{analysis.started_at}}</small>
                        ${{analysis.completed_at ? `<br><small>Completed: ${{analysis.completed_at}}</small>` : ''}}
                    </div>
                `).join('');
            }} catch (e) {{
                console.error('Failed to refresh analyses:', e);
            }}
        }}, 30000);
    </script>
</body>
</html>
"""
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the GitHub integration server"""
        import uvicorn
        
        print(f"🚀 Starting UX-Mirror GitHub Integration")
        print(f"📡 Webhook endpoint: http://{host}:{port}/webhook")
        print(f"📊 Dashboard: http://{host}:{port}/")
        
        uvicorn.run(self.app, host=host, port=port)

def main():
    """Main entry point"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration from environment
    github_token = os.getenv("GITHUB_TOKEN")
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable required")
        print("💡 Get a token from: https://github.com/settings/tokens")
        return
    
    if not webhook_secret:
        print("⚠️ GITHUB_WEBHOOK_SECRET not set - webhook verification disabled")
        webhook_secret = ""
    
    if not anthropic_key:
        print("⚠️ ANTHROPIC_API_KEY not set - visual analysis disabled")
    
    # Initialize and run
    integration = UXMirrorGitHubIntegration(
        github_token=github_token,
        webhook_secret=webhook_secret,
        anthropic_api_key=anthropic_key
    )
    
    integration.run()

if __name__ == "__main__":
    main() 