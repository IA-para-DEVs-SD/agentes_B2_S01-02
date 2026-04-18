# Tools para o Agente Scrum Master
# - break_tasks: quebra histórias em tarefas técnicas
# - exa: busca externa de boas práticas (opcional, requer exa-py)

import json


# ── Tool definitions (OpenAI function calling format) ──────────────────────

TOOLS = [
    {
        "type": "function",
        "name": "break_tasks",
        "description": (
            "Recebe uma user story e retorna uma lista de tarefas técnicas "
            "com prioridade e estimativa de esforço."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_story": {
                    "type": "string",
                    "description": "A user story original para ser quebrada em tarefas.",
                },
                "context": {
                    "type": "string",
                    "description": "Contexto adicional sobre o domínio ou tecnologia.",
                },
            },
            "required": ["user_story"],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────

def break_tasks(user_story: str, context: str = "") -> str:
    """
    Heurística simples que estrutura a user story em tarefas padrão
    de um projeto web/dashboard. Em produção, isso poderia chamar
    outro modelo ou serviço.
    """
    tasks = [
        {
            "id": "T1",
            "title": "Levantamento de requisitos e dados disponíveis",
            "description": "Mapear fontes de dados (LMS/AVA), APIs disponíveis e métricas necessárias.",
            "priority": "alta",
            "effort_estimate": "M",
            "dependencies": [],
        },
        {
            "id": "T2",
            "title": "Modelagem do banco de dados / camada de dados",
            "description": "Definir schema para armazenar acessos, notas e progresso por curso.",
            "priority": "alta",
            "effort_estimate": "M",
            "dependencies": ["T1"],
        },
        {
            "id": "T3",
            "title": "Backend - API de métricas",
            "description": "Criar endpoints REST para fornecer dados agregados ao dashboard.",
            "priority": "alta",
            "effort_estimate": "G",
            "dependencies": ["T2"],
        },
        {
            "id": "T4",
            "title": "Frontend - Layout e componentes do dashboard",
            "description": "Implementar telas com gráficos de acesso, notas e progresso.",
            "priority": "alta",
            "effort_estimate": "G",
            "dependencies": ["T3"],
        },
        {
            "id": "T5",
            "title": "Filtros e segmentação por curso",
            "description": "Permitir filtrar dados por curso, período e aluno.",
            "priority": "média",
            "effort_estimate": "M",
            "dependencies": ["T4"],
        },
        {
            "id": "T6",
            "title": "Testes e validação com stakeholders",
            "description": "Testes de integração, usabilidade e validação com coordenadores.",
            "priority": "média",
            "effort_estimate": "M",
            "dependencies": ["T4", "T5"],
        },
    ]
    return json.dumps(tasks, ensure_ascii=False)


# ── Dispatcher ─────────────────────────────────────────────────────────────

TOOL_MAP = {
    "break_tasks": break_tasks,
}


def handle_tool_call(name: str, arguments: dict) -> str:
    """Executa a tool pelo nome e retorna o resultado como string."""
    fn = TOOL_MAP.get(name)
    if fn is None:
        return json.dumps({"error": f"Tool '{name}' não encontrada."})
    return fn(**arguments)
