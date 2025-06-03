import asyncio
import logging
from agents.task_organizer import TaskOrganizer, TaskStatus

async def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the task organizer with custom retry settings
        organizer = TaskOrganizer(max_retries=3, retry_delay=1.0)
        
        # Example 1: Process a single task with validation
        task_description = "Implement a new feature for user authentication in the application"
        context = {
            "project_type": "web application",
            "team_size": 3,
            "deadline": "2 weeks",
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
        }
        
        logger.info("Processing single task...")
        result = await organizer.process_task(task_description, context)
        
        logger.info("\nTask Analysis:")
        logger.info(result["raw_response"])
        
        # Create a pull request for the task
        branch_name = f"feature/user-auth-{result['timestamp'].split('T')[0]}"
        pr = await organizer.create_pull_request(result, branch_name)
        
        logger.info(f"\nCreated Pull Request:")
        logger.info(f"Title: {pr['title']}")
        logger.info(f"Status: {pr['status']}")
        logger.info(f"Branch: {pr['branch']}")
        
        # Example 2: Get recommendations for multiple tasks
        current_tasks = [
            "Set up development environment",
            "Implement user authentication",
            "Create database schema",
            "Write API documentation",
            "Set up CI/CD pipeline"
        ]
        
        logger.info("\nGetting task recommendations...")
        recommendations = await organizer.get_task_recommendations(current_tasks)
        logger.info("\nTask Recommendations:")
        logger.info(recommendations["recommendations"])
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 