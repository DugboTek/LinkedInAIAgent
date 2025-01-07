from crewai import Agent, Task, Crew
from textwrap import dedent
import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_agents(self) -> tuple[Agent, Agent, Agent]:
        """Create and return the specialized agents for content creation."""
        content_strategist = Agent(
            role='Content Strategist',
            goal='Develop engaging LinkedIn content strategies',
            backstory=dedent("""
                Expert in social media strategy with deep understanding of 
                LinkedIn's professional audience and content performance metrics.
                Specialized in B2B content and thought leadership.
            """),
            allow_delegation=False,
            verbose=True
        )

        content_writer = Agent(
            role='Content Writer',
            goal='Create compelling LinkedIn posts',
            backstory=dedent("""
                Professional copywriter with expertise in creating viral LinkedIn 
                content. Skilled in storytelling, building engagement, and 
                crafting hooks that capture attention.
            """),
            allow_delegation=False,
            verbose=True
        )

        content_cleaner = Agent(
            role='Content Cleaner',
            goal='Format and clean content for LinkedIn',
            backstory=dedent("""
                Expert in LinkedIn content formatting and presentation.
                Ensures content is properly formatted without markdown artifacts
                and follows LinkedIn best practices.
            """),
            allow_delegation=False,
            verbose=True
        )

        return content_strategist, content_writer, content_cleaner

    def create_tasks(
        self, 
        content_strategist: Agent, 
        content_writer: Agent, 
        content_cleaner: Agent, 
        topic: str,
        additional_context: Optional[Dict] = None
    ) -> List[Task]:
        """Create tasks for content generation with optional context."""
        strategy_task = Task(
            description=f"""
                Create a content strategy for a LinkedIn post about {topic}.
                Focus on making it engaging and professional.
                Consider the target audience and key messages.
            """,
            expected_output="A content strategy for the LinkedIn post",
            agent=content_strategist
        )

        writing_task = Task(
            description=f"""
                Write an engaging LinkedIn post about {topic}.
                Make it professional, engaging, and include:
                - An attention-grabbing opening
                - Key points or insights
                - A call to action
                - 3-5 relevant hashtags at the end
                Keep it concise and use appropriate emojis sparingly.
                Format with proper line breaks for readability.
            """,
            expected_output="A complete LinkedIn post with hashtags",
            agent=content_writer
        )

        cleaning_task = Task(
            description=f"""
                Clean and format the LinkedIn post for proper display.
                
                Rules:
                1. Remove all markdown formatting (**, ##, etc.)
                2. Keep emojis but use them sparingly
                3. Maintain proper line breaks
                4. Ensure hashtags are properly formatted (no 'hashtag#' prefix)
                5. Remove any section headers like "Relevant Hashtags:"
                6. Make sure the text flows naturally
                7. Keep the post professional and clean
                
                The final output should be ready to post directly to LinkedIn
                without any formatting artifacts or unnecessary labels.
            """,
            expected_output="A clean, properly formatted LinkedIn post",
            agent=content_cleaner
        )

        return [strategy_task, writing_task, cleaning_task]

    def generate_content(
        self, 
        topic: str, 
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate LinkedIn content for the given topic.
        
        Args:
            topic: The main topic for the post
            additional_context: Optional dictionary with additional context
            
        Returns:
            Dict containing the generated content and metadata
        """
        try:
            self.logger.info(f"Starting content generation for topic: {topic}")
            
            content_strategist, content_writer, content_cleaner = self.create_agents()
            
            tasks = self.create_tasks(
                content_strategist, 
                content_writer, 
                content_cleaner, 
                topic,
                additional_context
            )
            
            crew = Crew(
                agents=[content_strategist, content_writer, content_cleaner],
                tasks=tasks,
                verbose=True
            )
            
            result = crew.kickoff()
            
            self.logger.info("Content generation completed successfully")
            
            # Add metadata to the result
            return {
                "content": result,
                "generated_at": datetime.now().isoformat(),
                "topic": topic,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            } 