# requirements.txt
"""
crewai==0.11.0
python-dotenv==1.0.0
openai==1.3.0
"""

# .env
"""
OPENAI_API_KEY=your_openai_api_key_here
"""

# main.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from textwrap import dedent

# Load environment variables
load_dotenv()

class LinkedInPostCreator:
    def __init__(self):
        # No need to pass API key directly as it's loaded from environment
        pass
        
    def create_agents(self):
        # Content Strategist Agent
        content_strategist = Agent(
            role='Content Strategist',
            goal='Develop engaging LinkedIn content strategies',
            backstory=dedent("""
                Expert in social media strategy with deep understanding of 
                LinkedIn's professional audience and content performance metrics.
                Specialized in B2B content and thought leadership.
            """),
            allow_delegation=True,
            verbose=True
        )

        # Content Writer Agent
        content_writer = Agent(
            role='Content Writer',
            goal='Create compelling LinkedIn posts',
            backstory=dedent("""
                Professional copywriter with expertise in creating viral LinkedIn 
                content. Skilled in storytelling, building engagement, and 
                crafting hooks that capture attention.
            """),
            allow_delegation=True,
            verbose=True
        )

        # Content Optimizer Agent
        content_optimizer = Agent(
            role='Content Optimizer',
            goal='Optimize posts for maximum engagement',
            backstory=dedent("""
                Analytics expert specialized in LinkedIn's algorithm and engagement 
                metrics. Focuses on optimizing content for reach and interaction.
            """),
            allow_delegation=True,
            verbose=True
        )

        return content_strategist, content_writer, content_optimizer

    def create_tasks(self, content_strategist, content_writer, content_optimizer, topic):
        # Task 1: Develop Content Strategy
        strategy_task = Task(
            description=f"""
                Develop a content strategy for a LinkedIn post about {topic}.
                Include target audience, key messages, and desired outcomes.
                Consider current LinkedIn trends and best practices.
                
                Output format:
                - Target Audience: [description]
                - Key Messages: [bullet points]
                - Content Angle: [approach]
                - Desired Outcomes: [goals]
            """,
            expected_output="A detailed content strategy document following the specified format",
            agent=content_strategist
        )

        # Task 2: Write Post Content
        writing_task = Task(
            description=f"""
                Create an engaging LinkedIn post about {topic} based on the strategy.
                Include hooks, storytelling elements, and clear call-to-action.
                Follow LinkedIn best practices for formatting and length.
                
                Requirements:
                - Compelling hook in first 2-3 lines
                - Clear value proposition
                - Engaging story or examples
                - Call-to-action
                - Professional tone
                - Appropriate line breaks for readability
            """,
            expected_output="A complete, engaging LinkedIn post following the specified requirements",
            agent=content_writer
        )

        # Task 3: Optimize Content
        optimization_task = Task(
            description=f"""
                Optimize the LinkedIn post for maximum engagement.
                Consider hashtags, timing, and formatting.
                
                Provide:
                1. Final post with optimized formatting
                2. 3-5 relevant hashtags
                3. Best time to post
                4. Additional engagement tips
            """,
            expected_output="An optimized LinkedIn post with hashtags, timing recommendations, and engagement tips",
            agent=content_optimizer
        )

        return [strategy_task, writing_task, optimization_task]

    def generate_post(self, topic):
        # Create agents
        content_strategist, content_writer, content_optimizer = self.create_agents()
        
        # Create tasks
        tasks = self.create_tasks(
            content_strategist, 
            content_writer, 
            content_optimizer, 
            topic
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[content_strategist, content_writer, content_optimizer],
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result

def main():
    # Create the LinkedIn post generator
    creator = LinkedInPostCreator()
    
    # Get topic from user input
    topic = input("Enter the topic for your LinkedIn post: ")
    
    print("\nGenerating LinkedIn post...")
    result = creator.generate_post(topic)
    
    print("\nGenerated LinkedIn Post:")
    print("-" * 50)
    print(result)
    print("-" * 50)

if __name__ == "__main__":
    main()