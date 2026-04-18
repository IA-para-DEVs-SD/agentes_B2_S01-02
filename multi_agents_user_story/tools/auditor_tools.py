"""
Tools de auditoria para o Agente 3.
Avalia qualidade, consistência e atribui score à análise completa.
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


def audit_reqs(user_story: str, backlog: list, hidden_requirements: list,
               edge_cases: list, risks: list) -> dict:
    """
    Audita a consistência entre a User Story, backlog, requisitos
    ocultos, edge cases e riscos identificados.

    Returns:
        dict com inconsistências, lacunas e achados da auditoria
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY não configurada"}

    client = genai.Client(api_key=api_key)

    prompt = f"""Você é um auditor de qualidade de requisitos de software.

Audite a consistência e completude dos seguintes artefatos:

User Story: {user_story}

Backlog:
{json.dumps(backlog[:15], ensure_ascii=False, indent=2) if backlog else "Não disponível em formato estruturado"}

Requisitos Ocultos:
{json.dumps(hidden_requirements[:10], ensure_ascii=False, indent=2) if hidden_requirements else "[]"}

Edge Cases:
{json.dumps(edge_cases[:10], ensure_ascii=False, indent=2) if edge_cases else "[]"}

Riscos:
{json.dumps(risks[:10], ensure_ascii=False, indent=2) if risks else "[]"}

Retorne APENAS um JSON válido:
{{
    "audit_findings": [
        {{
            "finding": "descrição do achado",
            "severity": "alta|média|baixa",
            "category": "inconsistência|lacuna|redundância|ambiguidade"
        }}
    ],
    "coverage_analysis": {{
        "criteria_covered": true,
        "security_addressed": true,
        "performance_addressed": true,
        "error_handling_addressed": true,
        "accessibility_addressed": false,
        "notes": "observações sobre cobertura"
    }},
    "consistency_issues": [
        "descrição de inconsistência encontrada"
    ]
}}

Seja rigoroso e objetivo."""

    config = types.GenerateContentConfig(temperature=0.2)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt, config=config
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
            wait = int(match.group(1)) + 5 if match else 40
            print(f"      ⏳ Rate limit em audit_reqs. Aguardando {wait}s...")
            time.sleep(wait)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt, config=config
            )
        else:
            return {"status": "error", "message": error_msg}

    text = response.text.strip()
    for prefix in ["```json", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        result["status"] = "success"
        return result
    except json.JSONDecodeError:
        return {"status": "success", "audit_findings": [], "raw_response": text}


def score_quality(user_story: str, audit_summary: str) -> dict:
    """
    Atribui score de qualidade e gera sugestões de melhoria.

    Returns:
        dict com scores e sugestões
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY não configurada"}

    client = genai.Client(api_key=api_key)

    prompt = f"""Você é um auditor de qualidade de requisitos de software.

Com base na User Story e no resumo da auditoria, atribua scores e gere sugestões.

User Story: {user_story}

Resumo da auditoria:
{audit_summary}

Retorne APENAS um JSON válido:
{{
    "quality_score": {{
        "clarity": 8,
        "completeness": 7,
        "testability": 8,
        "consistency": 7,
        "overall": 7.5
    }},
    "suggestions": [
        "sugestão concreta de melhoria 1",
        "sugestão concreta de melhoria 2"
    ],
    "rewritten_story": "versão melhorada da User Story (opcional)",
    "missing_acceptance_criteria": [
        "critério de aceitação que deveria existir"
    ]
}}

Scores de 1 a 10. Seja justo e objetivo."""

    config = types.GenerateContentConfig(temperature=0.2)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt, config=config
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
            wait = int(match.group(1)) + 5 if match else 40
            print(f"      ⏳ Rate limit em score_quality. Aguardando {wait}s...")
            time.sleep(wait)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt, config=config
            )
        else:
            return {"status": "error", "message": error_msg}

    text = response.text.strip()
    for prefix in ["```json", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        result["status"] = "success"
        return result
    except json.JSONDecodeError:
        return {"status": "success", "quality_score": {}, "raw_response": text}
