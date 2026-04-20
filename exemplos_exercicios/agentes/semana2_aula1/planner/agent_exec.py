from agents import Agent
from tools import load_backlog

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

executor_agent = Agent(
    name="Executor",
    instructions=(
        "Você é um Scrum Master. Use a tool load_backlog para analisar o backlog. "
        "Identifique riscos, bloqueios e prioridades."
    ),
    tools=[load_backlog],
)