#!/usr/bin/env python
import sys
import warnings
from crew import PdfRag

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    print("Welcome to the Crowdfunding Campaign Generator!")
    
    # Gather user inputs
    project_type = input("What type of project are you crowdfunding? (e.g., Art, Technology, Community, etc.) ")
    target_amount = input("What is your funding goal? (e.g., $50,000) ")
    target_audience = input("Who is your target audience? ")
    tone = input("What tone would you like for your campaign? (e.g., professional, friendly, passionate) ")

    inputs = {
        'project_type': project_type,
        'target_amount': target_amount,
        'target_audience': target_audience,
        'tone': tone
    }

    print("\nGenerating your crowdfunding campaign...")
    result = PdfRag().crew().kickoff(inputs=inputs)
    print("\nYour Campaign:")
    print(result)

if __name__ == '__main__':
    run()