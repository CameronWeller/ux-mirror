import os
from dotenv import load_dotenv
from agents.github_integration import GitHubIntegration

def main():
    # Load environment variables
    load_dotenv()
    
    # Get required environment variables
    webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not webhook_secret or not github_token:
        raise ValueError(
            "Missing required environment variables. "
            "Please set GITHUB_WEBHOOK_SECRET and GITHUB_TOKEN in your .env file."
        )
    
    # Initialize and run the GitHub integration
    github_agent = GitHubIntegration(
        webhook_secret=webhook_secret,
        github_token=github_token
    )
    
    print("Starting GitHub Task Organizer agent...")
    print("Listening for GitHub webhook events on http://localhost:8000/webhook")
    github_agent.run()

if __name__ == "__main__":
    main() 