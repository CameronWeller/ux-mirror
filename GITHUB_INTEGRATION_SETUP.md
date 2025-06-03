# 🔗 UX-Mirror GitHub Integration Setup

This guide will help you set up the complete UX-Mirror GitHub integration, enabling automated visual analysis on pull requests and seamless workflow integration.

## 🎯 Overview

The UX-Mirror GitHub integration provides:

- **Automated PR Analysis**: Triggers visual analysis when PRs are created/updated
- **AI-Powered Feedback**: Posts detailed UX analysis results as PR comments
- **Issue Creation**: Automatically creates GitHub issues for critical UX problems
- **GitHub Actions**: Runs analysis in CI/CD pipeline
- **Webhook Integration**: Real-time analysis via webhook events
- **Dashboard**: Visual dashboard for monitoring analyses

## 📋 Prerequisites

1. **GitHub Repository** with admin access
2. **Anthropic API Key** for visual analysis
3. **Python 3.11+** environment
4. **Domain/Server** for webhook endpoint (optional)

## 🚀 Quick Setup

### 1. Environment Configuration

Create a `.env` file in your repository root:

```bash
# Copy the template
cp env_template.txt .env

# Edit with your credentials
nano .env
```

Required environment variables:

```env
# GitHub API Configuration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-your_api_key_here
```

### 2. GitHub Token Setup

1. Go to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Create a new token with these permissions:
   - `repo` (Full repository access)
   - `issues` (Read and write issues)
   - `pull_requests` (Read and write pull requests)
3. Copy the token to your `.env` file

### 3. Repository Secrets (for GitHub Actions)

Add these secrets to your repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these repository secrets:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `GITHUB_TOKEN`: Already available by default

### 4. Enable GitHub Actions

The workflow is automatically enabled when you push the `.github/workflows/ux-analysis.yml` file. It will:

- ✅ Trigger on PR creation/updates with screenshots
- ✅ Analyze visual changes automatically
- ✅ Post results as PR comments
- ✅ Create issues for critical problems

## 🛠️ Advanced Setup

### Webhook Integration (Optional)

For real-time analysis, set up a webhook endpoint:

1. **Deploy webhook server**:
   ```bash
   python ux_mirror_github_integration.py
   ```

2. **Configure GitHub webhook**:
   - Go to **Repository Settings → Webhooks**
   - Add webhook URL: `https://your-domain.com/webhook`
   - Secret: Use your `GITHUB_WEBHOOK_SECRET`
   - Events: `Pull requests`, `Issues`, `Push`

3. **Test webhook**:
   - Create a test PR with screenshots
   - Check webhook delivery in GitHub settings

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install python-dotenv fastapi uvicorn PyGithub anthropic
   ```

2. **Run local webhook server**:
   ```bash
   python ux_mirror_github_integration.py
   ```

3. **Test with ngrok** (for local testing):
   ```bash
   ngrok http 8000
   # Use the ngrok URL for webhook endpoint
   ```

## 📊 Usage Guide

### Automatic Analysis

The integration automatically triggers when:

1. **PR is created** with screenshot files
2. **PR is updated** with new screenshots
3. **Screenshots are added** to `game_screenshots/` directory

### Manual Triggers

1. **GitHub Actions UI**:
   - Go to **Actions → UX-Mirror Analysis**
   - Click "Run workflow"
   - Optionally specify PR number

2. **API Endpoint**:
   ```bash
   curl -X POST https://your-webhook-url/api/trigger-analysis/owner/repo/123
   ```

3. **Issue Labels**:
   - Create issue with `ux-analysis` label
   - Mention PR number in issue body

### Screenshot Requirements

For analysis to trigger, include screenshots with these naming patterns:

- `screenshot_*.png`
- `capture_*.jpg`
- `ui_*.png`
- Files in `game_screenshots/` directory
- Any file with "screenshot", "capture", or "ui" in the name

## 📈 Monitoring & Dashboards

### UX-Mirror Dashboard

Access at: `http://localhost:8501` (when running Streamlit dashboard)

Features:
- Real-time iteration tracking
- Visual analysis history
- Issue detection metrics
- Screenshot distribution

### GitHub Integration Dashboard

Access at: `http://your-webhook-url/` (when webhook server is running)

Features:
- Analysis status monitoring
- Webhook endpoint information
- Recent analysis results
- Integration health checks

### GitHub Actions

Monitor in **Actions** tab:
- Workflow run history
- Analysis artifacts
- Execution logs
- Performance metrics

## 🔍 Analysis Results

### PR Comments

Automated comments include:

- **Analysis Summary**: Screenshots count, quality score
- **Issues Found**: Categorized problems with severity
- **Recommendations**: Specific improvement suggestions
- **Visual Quality Score**: Overall UX rating

### GitHub Issues

Critical problems automatically create issues with:

- **Problem Description**: Detailed issue explanation
- **Severity Level**: Priority classification
- **Recommendations**: Specific fix suggestions
- **Context**: Link to source PR and analysis

### Analysis Files

Generated artifacts:

- `temporal_analysis_*.json`: Full AI analysis results
- `analysis_summary.md`: Human-readable summary
- `analysis_output.txt`: Execution logs

## 🛡️ Security Considerations

### Webhook Security

- ✅ Signature verification using HMAC-SHA1
- ✅ Environment variable for webhook secret
- ✅ HTTPS enforcement recommended

### Token Permissions

Use minimal required permissions:
- **Read**: Repository contents, issues, PRs
- **Write**: Issues, PR comments
- **No Admin**: Avoid repository admin permissions

### API Key Protection

- ✅ Store in GitHub Secrets (not repository files)
- ✅ Use environment variables
- ✅ Rotate keys periodically

## 🚨 Troubleshooting

### Common Issues

1. **No analysis triggered**:
   - Check screenshot file naming
   - Verify webhook endpoint accessibility
   - Check GitHub Actions permissions

2. **Authentication errors**:
   - Verify GitHub token permissions
   - Check token expiration
   - Confirm repository access

3. **Analysis failures**:
   - Check Anthropic API key validity
   - Verify screenshot file formats
   - Review analysis logs

### Debug Commands

```bash
# Test GitHub token
python -c "from github import Github; print(Github('your_token').get_user().login)"

# Test Anthropic API
python -c "import anthropic; print(anthropic.Anthropic(api_key='your_key').messages.create(model='claude-3-sonnet-20240229', max_tokens=10, messages=[{'role': 'user', 'content': 'test'}]))"

# Check webhook endpoint
curl -X GET http://localhost:8000/

# Test analysis manually
python agents/temporal_screenshot_analyzer.py
```

### Logs and Monitoring

- **GitHub Actions**: Check workflow run logs
- **Webhook Server**: Monitor console output
- **Analysis Results**: Review generated JSON files

## 🔄 Continuous Improvement

### Feedback Loop

1. **Monitor Results**: Track analysis accuracy
2. **Refine Prompts**: Improve AI analysis quality
3. **Update Thresholds**: Adjust issue detection sensitivity
4. **Enhance Workflows**: Add new analysis types

### Customization

The integration is designed to be extensible:

- **Analysis Types**: Add custom visual analysis methods
- **Issue Templates**: Customize issue creation logic
- **Notification**: Add Slack/email notifications
- **Metrics**: Integrate with monitoring systems

## 📞 Support

For issues and questions:

1. **Check Logs**: Review GitHub Actions and webhook logs
2. **Documentation**: Reference this guide and code comments
3. **Issues**: Create GitHub issues for bugs/features
4. **Discussions**: Use GitHub Discussions for questions

---

**🎯 UX-Mirror GitHub Integration** - Bridging the gap between development and user experience through automated visual analysis. 