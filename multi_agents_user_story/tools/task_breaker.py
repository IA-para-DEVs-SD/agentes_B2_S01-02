"""
Tool para quebrar User Stories em tarefas técnicas menores.
Usa o LLM para decompor a história em itens acionáveis.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def break_tasks(user_story: str, acceptance_criteria: list = None) -> dict:
    """
    Quebra uma User Story em tarefas técnicas menores.

    Args:
        user_story: Texto da User Story
        acceptance_criteria: Lista de critérios de aceitação

    Returns:
        dict com lista de tarefas técnicas
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY não configurada"}

    client = genai.Client(api_key=api_key)

    criteria_text = ""
    if acceptance_criteria:
        criteria_text = "\n".join(f"- {c}" for c in acceptance_criteria)
        criteria_text = f"\n\nCritérios de aceitação:\n{criteria_text}"

    prompt = f"""Analise a seguinte User Story e quebre em tarefas técnicas detalhadas.

User Story: {user_story}{criteria_text}

Retorne APENAS um JSON válido no seguinte formato:
{{
    "tasks": [
        {{
            "id": 1,
            "task": "descrição da tarefa",
            "type": "backend|frontend|infra|test|docs",
            "effort": "P|M|G",
            "dependencies": []
        }}
    ]
}}

Regras:
- Cada tarefa deve ser acionável e específica
- Inclua tarefas de backend, frontend, testes e infraestrutura
- Estime esforço como P (pequeno), M (médio) ou G (grande)
- Identifique dependências entre tarefas (lista de IDs)
- Seja técnico e prático"""

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
            print(f"      ⏳ Rate limit em break_tasks. Aguardando {wait}s...")
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
            "tasks": [],
            "raw_response": text
        }
