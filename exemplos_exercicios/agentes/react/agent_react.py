from agents import Agent
from tools import get_ticket_conversation

react_agent = Agent(
    name="Support ReAct Agent",
    instructions=(
        "Você é um agente de suporte.\n"
        "Sempre use a tool get_ticket_conversation.\n"
        "Retorne status, última mensagem e próximo passo."
    ),
    tools=[get_ticket_conversation],
)