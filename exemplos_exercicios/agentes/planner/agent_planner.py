from agents import Agent

planner_agent = Agent(
    name="Scrum Planner",
    instructions=(
        "Você é um agente planner. "
        "Receba um backlog e devolva um plano curto, em JSON, com etapas de análise. "
        "Considere pelo menos: tarefas bloqueadas, itens críticos atrasados, bugs e distribuição de trabalho. "
        "Responda apenas com JSON no formato: "
        '{"steps": ["...", "...", "..."]}'
    ),
)
