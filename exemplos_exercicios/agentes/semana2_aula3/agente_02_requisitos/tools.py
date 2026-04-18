# Tools para o Agente de Requisitos
# - find_edges: identifica dependências entre componentes/requisitos

import json


# ── Tool definitions (OpenAI Responses API format) ─────────────────────────

TOOLS = [
    {
        "type": "function",
        "name": "find_edges",
        "description": (
            "Analisa uma lista de tarefas ou requisitos e retorna um mapa "
            "de dependências entre componentes do sistema."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tasks_json": {
                    "type": "string",
                    "description": "JSON stringificado com a lista de tarefas/requisitos a analisar.",
                },
            },
            "required": ["tasks_json"],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────

def find_edges(tasks_json: str) -> str:
    """
    Analisa tarefas e retorna dependências entre componentes.
    Em produção poderia usar grafos ou outro modelo para inferir relações.
    """
    try:
        tasks = json.loads(tasks_json)
    except json.JSONDecodeError:
        tasks = []

    # Monta mapa de dependências a partir das tasks
    dependency_map = {}
    for task in tasks:
        task_id = task.get("id", "unknown")
        deps = task.get("dependencies", [])
        if deps:
            dependency_map[task_id] = deps

    # Adiciona dependências de componentes típicos de um dashboard educacional
    component_edges = {
        "frontend_dashboard": ["api_metricas", "autenticacao"],
        "api_metricas": ["banco_dados", "cache"],
        "banco_dados": ["etl_dados_ava"],
        "etl_dados_ava": ["fonte_dados_lms"],
        "filtros_segmentacao": ["api_metricas", "frontend_dashboard"],
    }

    return json.dumps(
        {"task_dependencies": dependency_map, "component_dependencies": component_edges},
        ensure_ascii=False,
    )


# ── Dispatcher ─────────────────────────────────────────────────────────────

TOOL_MAP = {
    "find_edges": find_edges,
}


def handle_tool_call(name: str, arguments: dict) -> str:
    """Executa a tool pelo nome e retorna o resultado como string."""
    fn = TOOL_MAP.get(name)
    if fn is None:
        return json.dumps({"error": f"Tool '{name}' não encontrada."})
    return fn(**arguments)
