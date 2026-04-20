
import os
import json
from typing import Any, Dict, List
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS = [
    {
        "name": "search_web_best_practices",
        "description": (
            "Busca boas práticas, padrões de arquitetura, riscos comuns e "
            "referências externas relacionadas à user story."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "context": {"type": "string"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "break_story_into_tasks",
        "description": (
            "Quebra uma user story em tarefas técnicas objetivas, com título, "
            "descrição e critério de aceite."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_story": {"type": "string"}
            },
            "required": ["user_story"]
        }
    },
    {
        "name": "prioritize_backlog",
        "description": (
            "Prioriza o backlog com base em impacto, urgência, dependências e risco."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["tasks"]
        }
    }
]


def search_web_best_practices(topic: str, context: str = "") -> Dict[str, Any]:
    # mock inicial; depois você pode trocar por Exa, Tavily, SerpAPI etc.
    return {
        "topic": topic,
        "references": [
            f"Best practice encontrada para: {topic}",
            "Considerar autenticação, observabilidade e tratamento de erros",
            "Evitar acoplamento entre UI e regras de negócio"
        ],
        "context_used": context
    }


def break_story_into_tasks(user_story: str) -> Dict[str, Any]:
    return {
        "tasks": [
            {
                "title": "Mapear requisitos funcionais",
                "description": "Extrair objetivo, atores, entradas e saídas da story",
                "acceptance_criteria": "Requisitos documentados"
            },
            {
                "title": "Definir contrato de API",
                "description": "Especificar payloads, campos obrigatórios e erros",
                "acceptance_criteria": "Contrato definido e revisado"
            },
            {
                "title": "Implementar persistência",
                "description": "Salvar dados processados em banco ou índice vetorial",
                "acceptance_criteria": "Dados persistidos corretamente"
            }
        ]
    }


def prioritize_backlog(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    prioritized = []
    for i, task in enumerate(tasks, start=1):
        item = dict(task)
        item["priority"] = i
        item["reason"] = "Ordem inicial baseada em dependência lógica"
        prioritized.append(item)

    return {"prioritized_backlog": prioritized}


TOOL_FUNCTIONS = {
    "search_web_best_practices": search_web_best_practices,
    "break_story_into_tasks": break_story_into_tasks,
    "prioritize_backlog": prioritize_backlog,
}


def run_agent(user_story: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                "Você é o agente Scrum Master. "
                "Use as tools disponíveis para:\n"
                "1. buscar referências externas\n"
                "2. quebrar a story em tarefas\n"
                "3. priorizar o backlog\n\n"
                f"User story: {user_story}"
            )
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            tools=TOOLS,
            messages=messages
        )

        assistant_content = response.content
        messages.append({
            "role": "assistant",
            "content": assistant_content
        })

        tool_uses = [block for block in assistant_content if block.type == "tool_use"]

        if not tool_uses:
            text_parts = [block.text for block in assistant_content if block.type == "text"]
            return "\n".join(text_parts)

        tool_results = []
        for tool_call in tool_uses:
            tool_name = tool_call.name
            tool_input = tool_call.input

            result = TOOL_FUNCTIONS[tool_name](**tool_input)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

        messages.append({
            "role": "user",
            "content": tool_results
        })


if __name__ == "__main__":
    story = (
        "Como usuária, quero receber recomendações de recursos com base no meu perfil "
        "para encontrar ajuda relevante com mais rapidez."
    )

    final_output = run_agent(story)
    print(final_output)
