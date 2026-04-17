import json
from typing import Any, Dict, List
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS_AGENT_3 = [
    {
        "name": "audit_solution_consistency",
        "description": (
            "Audita a consistência entre user story, backlog, requisitos ocultos, "
            "edge cases e dependências."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_story": {"type": "string"},
                "backlog": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "hidden_requirements": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "edge_cases": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "dependencies": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": [
                "user_story",
                "backlog",
                "hidden_requirements",
                "edge_cases",
                "dependencies"
            ]
        }
    },
    {
        "name": "score_solution_quality",
        "description": (
            "Atribui score de qualidade para a solução com base em cobertura, "
            "clareza, riscos, dependências e prontidão para implementação."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "audit_summary": {"type": "string"}
            },
            "required": ["audit_summary"]
        }
    },
    {
        "name": "generate_improvement_suggestions",
        "description": (
            "Gera sugestões práticas para melhorar a qualidade e reduzir riscos "
            "antes da implementação."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "audit_summary": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["audit_summary", "score"]
        }
    }
]