from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .gmail_utility import authenticate_gmail, create_message, create_draft
from agentops import record_tool

class GmailToolInput(BaseModel):
    """Input schema for GmailTool."""

    body: str = Field(..., description="The body of the email to send.")

@record_tool("This is used for gmail draft emails")
class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = (
        "Clear description for what this tool is useful for, you agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, body: str) -> str:
        try:
        # Implementation goes here
            service = authenticate_gmail()
            sender = "spearschristopher2002@gmail.com"
            to = "spearschristopher2002@gmail.com"
            subject = "Meeting Minutes"
            message_text = body 

            message = create_message(sender, to, subject, message_text)
            draft = create_draft(service, "me", message)




            return f"email sent succesfully! Draft idL {draft['id']}"
        except Exception as e:
            return f"Error sending email: {e}"