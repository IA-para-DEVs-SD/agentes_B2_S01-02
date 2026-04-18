"""
Tool para identificar edge cases e requisitos ocultos em User Stories.
Usa o LLM para encontrar lacunas, dependências e cenários extremos.
"""
import os
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def find_edge_cases(user_story: str, backlog: list = None) -> dict:
    """
    Identifica edge cases, requisitos ocultos e dependências
    não explicitadas na User Story.

    Args:
        user_story: Texto da User Story
        backlog: Backlog gerado pelo Agente 1 (opcional)

    Returns:
        dict com edge cases, requisitos ocultos, riscos e dependências
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY não configurada"}

    client = genai.Client(api_key=api_key)

    backlog_text = ""
    if backlog:
        backlog_text = "\n\nBacklog gerado pelo Scrum Master:\n"
        backlog_text += json.dumps(backlog, ensure_ascii=False, indent=2)

    prompt = f"""Analise a seguinte User Story e identifique tudo que NÃO foi
explicitado mas é necessário para uma boa implementação.

User Story: {user_story}{backlog_text}

Retorne APENAS um JSON válido no seguinte formato:
{{
    "hidden_requirements": [
        {{
            "requirement": "descrição do requisito oculto",
            "category": "segurança|performance|usabilidade|dados|integração|negócio",
            "impact": "alto|médio|baixo",
            "reason": "por que isso é necessário"
        }}
    ],
    "edge_cases": [
        {{
            "scenario": "descrição do cenário extremo",
            "expected_behavior": "como o sistema deveria reagir",
            "risk_level": "alto|médio|baixo"
        }}
    ],
    "dependencies": [
        {{
            "dependency": "descrição da dependência",
            "type": "técnica|funcional|externa|dados",
            "blocking": true
        }}
    ],
    "risks": [
        {{
            "risk": "descrição do risco",
            "category": "implementação|negócio|experiência_usuario|segurança",
            "probability": "alta|média|baixa",
            "mitigation": "sugestão de mitigação"
        }}
    ]
}}

Regras:
- Foque no que NÃO está escrito mas é essencial
- Considere segurança, performance, acessibilidade, edge cases de dados
- Identifique dependências técnicas e funcionais
- Pense em cenários de erro, limites e exceções
- Seja específico e prático"""

    config = types.GenerateContentConfig(temperature=0.3)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
            wait = int(match.group(1)) + 5 if match else 40
            print(f"      ⏳ Rate limit em find_edge_cases. Aguardando {wait}s...")
            time.sleep(wait)
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
            "hidden_requirements": [],
            "edge_cases": [],
            "dependencies": [],
            "risks": [],
            "raw_response": text
        }
