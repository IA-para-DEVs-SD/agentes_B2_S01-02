
import json
from typing import Any, Dict, List
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS_AGENT_2 = [
    {
        "name": "find_hidden_requirements",
        "description": (
            "Identifica requisitos implícitos não descritos explicitamente "
            "na user story ou backlog."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_story": {"type": "string"},
                "backlog": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["user_story", "backlog"]
        }
    },
    {
        "name": "find_edge_cases",
        "description": (
            "Identifica cenários de borda, falhas, dados ausentes, timeouts, "
            "duplicidades e outros casos excepcionais."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_story": {"type": "string"},
                "backlog": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["user_story", "backlog"]
        }
    },
    {
        "name": "map_dependencies",
        "description": (
            "Mapeia dependências técnicas, integrações, serviços, dados e times "
            "necessários para implementar a solução."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "backlog": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["backlog"]
        }
    }
]

def find_edge_cases(user_story: str):
    return [
        "Usuário sem dados",
        "Sistema sem recursos disponíveis",
        "Erro na API externa"
    ]

def search_qdrant(query: str):
    return ["Caso parecido 1", "Caso parecido 2"]

def analyze_risks(tasks: list):
    return ["Dependência de dados", "Escalabilidade"]

def agent_2_hidden_requirements(agent_1_output: dict):
    story = agent_1_output["user_story"]
    tasks = agent_1_output["tasks"]

    similar_cases = search_qdrant(story)
    edge_cases = find_edge_cases(story)
    risks = analyze_risks(tasks)

    return {
        "similar_cases": similar_cases,
        "edge_cases": edge_cases,
        "risks": risks,
        "gaps": ["Critério de sucesso não definido"]
    }

