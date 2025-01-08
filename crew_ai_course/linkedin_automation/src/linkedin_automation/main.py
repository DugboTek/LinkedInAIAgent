#!/usr/bin/env python
import sys
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from crew import LinkedinAutomation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    print("Starting LinkedIn Automation...")
    try:
        LinkedinAutomation().crew().kickoff()
        print("LinkedIn Automation completed successfully!")
    except Exception as e:
        print(f"Error during execution: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        LinkedinAutomation().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LinkedinAutomation().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    try:
        LinkedinAutomation().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

run()
