from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = Path(__file__).parent
pdf_path = str(SCRIPT_DIR / "CSI_HiveWire_Crowdfunding_Guide-2015-1.pdf")
pdf_search_tool = PDFSearchTool(pdf=pdf_path)

@CrewBase
class PdfRag():
	"""Crowdfunding Campaign Generator Crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def market_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['market_researcher'],
			tools=[pdf_search_tool],
			verbose=True
		)

	@agent
	def campaign_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['campaign_strategist'],
			tools=[pdf_search_tool],
			verbose=True
		)

	@agent
	def content_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['content_creator'],
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def strategy_task(self) -> Task:
		return Task(
			config=self.tasks_config['strategy_task'],
		)

	@task
	def content_task(self) -> Task:
		return Task(
			config=self.tasks_config['content_task'],
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)
