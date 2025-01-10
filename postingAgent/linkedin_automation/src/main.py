import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import schedule
import time
from rich.console import Console
from rich.logging import RichHandler
from typing import Optional, Dict

from content_generator import ContentGenerator
from linkedin_poster import LinkedInPoster

# Set up rich console for better output
console = Console()

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

class LinkedInAutomation:
    def __init__(self, config_dir: str):
        """
        Initialize LinkedIn automation with configuration directory.
        
        Args:
            config_dir: Path to configuration directory containing credentials and .env
        """
        self.config_dir = Path(config_dir)
        self.credentials_path = self.config_dir / "credentials.json"
        self.content_generator = ContentGenerator()
        self.linkedin_poster = LinkedInPoster(str(self.credentials_path))
        # Default test content
        self.test_content = {
            "content": """🤖 Exploring AI Agents: The Future of Automation

Fascinating how AI agents are revolutionizing the way we work! They're like digital assistants on steroids, handling complex tasks with incredible precision.

Key benefits I've discovered:
• Automated decision-making
• 24/7 operation capability
• Scalable task management
• Reduced human error

Have you implemented AI agents in your workflow? Share your experience! 

#ArtificialIntelligence #Automation #FutureOfWork #TechInnovation #AI""",
            "status": "success"
        }

    async def post_content(
        self, 
        topic: str, 
        user_id: str, 
        image_path: Optional[str] = None,
        additional_context: Optional[Dict] = None,
        generate_new_content: bool = True
    ) -> bool:
        """
        Generate and post content to LinkedIn.
        
        Args:
            topic: Topic for the post
            user_id: ID of the user to post as
            image_path: Optional path to image file
            additional_context: Optional additional context for content generation
            generate_new_content: If False, uses default test content instead of generating new content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if generate_new_content:
                console.print(f"[bold blue]Generating content for topic: {topic}[/bold blue]")
                content_result = self.content_generator.generate_content(topic, additional_context)
                
                # Clean the content
                content = str(content_result["content"])
                # Remove any JSON-like formatting
                if content.strip().startswith("{"):
                    try:
                        import json
                        parsed = json.loads(content)
                        if isinstance(parsed, dict):
                            content = parsed.get("post_content", content)
                    except:
                        pass
                
                # Clean up any remaining artifacts
                content = (content
                          .replace('```json', '')
                          .replace('```', '')
                          .replace('"post_content":', '')
                          .replace('"hashtags":', '')
                          .strip())
                
                content_result["content"] = content
            else:
                console.print("[bold yellow]Using test content[/bold yellow]")
                content_result = self.test_content

            if content_result["status"] == "error":
                raise Exception(f"Content generation failed: {content_result['error']}")

            # Login to LinkedIn
            console.print(f"[bold blue]Logging in as user: {user_id}[/bold blue]")
            login_success = await self.linkedin_poster.login(user_id)
            
            if not login_success:
                raise Exception("LinkedIn login failed")

            # Create post
            console.print("[bold blue]Creating LinkedIn post[/bold blue]")
            post_success = await self.linkedin_poster.create_post(
                content_result["content"],
                image_path
            )

            if post_success:
                console.print("[bold green]Post created successfully![/bold green]")
                return True
            else:
                raise Exception("Failed to create post")

        except Exception as e:
            logger.error(f"Error in post_content: {str(e)}")
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            return False

        finally:
            await self.linkedin_poster.close()

def schedule_post(automation: LinkedInAutomation, topic: str, user_id: str, time_str: str):
    """Schedule a post for a specific time."""
    schedule.every().day.at(time_str).do(
        lambda: asyncio.run(automation.post_content(topic, user_id))
    )

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Content Automation")
    parser.add_argument("--topic", required=True, help="Topic for the LinkedIn post")
    parser.add_argument("--user", required=True, help="User ID from credentials to post as")
    parser.add_argument("--image", help="Path to image file to include in post")
    parser.add_argument("--schedule", help="Time to schedule post (HH:MM format)")
    parser.add_argument("--config", default="config", help="Path to config directory")
    parser.add_argument("--test", action="store_true", help="Use test content instead of generating new content")
    
    args = parser.parse_args()
    
    automation = LinkedInAutomation(args.config)

    if args.schedule:
        console.print(f"[bold blue]Scheduling post for {args.schedule}[/bold blue]")
        schedule_post(automation, args.topic, args.user, args.schedule)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        asyncio.run(automation.post_content(
            args.topic, 
            args.user, 
            args.image, 
            generate_new_content=not args.test
        ))

if __name__ == "__main__":
    main() 