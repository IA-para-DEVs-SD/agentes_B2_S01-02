"""
Tool para priorizar tarefas do backlog.
Usa o LLM para atribuir prioridades baseado em valor, risco e dependências.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def prioritize(tasks: list, user_story: str) -> dict:
    """
    Prioriza uma lista de tarefas baseado em valor de negócio,
    risco técnico e dependências.

    Args:
        tasks: Lista de tarefas (dicts com task, type, effort, dependencies)
        user_story: User Story original para contexto

    Returns:
        dict com tarefas priorizadas
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY não configurada"}

    client = genai.Client(api_key=api_key)

    tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)

    prompt = f"""Priorize as seguintes tarefas de um backlog Scrum.

User Story: {user_story}

Tarefas:
{tasks_json}

Retorne APENAS um JSON válido no seguinte formato:
{{
    "prioritized_backlog": [
        {{
            "id": 1,
            "task": "descrição",
            "priority": "Alta|Média|Baixa",
            "priority_reason": "justificativa curta",
            "sprint_suggestion": 1
        }}
    ],
    "summary": "resumo da priorização em 2-3 frases"
}}

Critérios de priorização:
- Alta: Essencial para o MVP, bloqueia outras tarefas, alto valor de negócio
- Média: Importante mas não bloqueia, pode ser feita em paralelo
- Baixa: Nice-to-have, melhorias, documentação complementar
- Considere dependências entre tarefas
- Tarefas bloqueantes devem ter prioridade mais alta"""

    config = types.GenerateContentConfig(temperature=0.2)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            import re, time as _time
            match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
            wait = int(match.group(1)) + 5 if match else 40
            print(f"      ⏳ Rate limit em prioritize. Aguardando {wait}s...")
            _time.sleep(wait)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
        else:
            return {"status": "error", "message": error_msg}

    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        result["status"] = "success"
        return result
    except json.JSONDecodeError:
        return {
            "status": "success",
            "prioritized_backlog": [],
            "raw_response": text
        }
