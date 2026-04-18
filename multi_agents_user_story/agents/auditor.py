"""
Agente 3 — Auditoria

Responsável por avaliar a qualidade final da User Story e da
análise acumulada pelos agentes anteriores.

Funções:
- Revisar backlog, riscos e requisitos ocultos
- Aplicar critérios de qualidade
- Atribuir score
- Gerar relatório final consolidado

Tools:
- audit_reqs(): audita consistência dos artefatos
- score_quality(): atribui score de qualidade
- search_qdrant(): busca memória de longo prazo

Saída esperada:
- Score de qualidade
- Inconsistências encontradas
- Sugestões de melhoria
- Relatório final
"""
import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.auditor_tools import audit_reqs, score_quality
from tools.qdrant_memory import save_to_qdrant, search_qdrant


TOOLS_DECLARATION = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="audit_reqs",
                description=(
                    "Audita a consistência entre User Story, backlog, "
                    "requisitos ocultos, edge cases e riscos. Identifica "
                    "inconsistências, lacunas e redundâncias."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_story": types.Schema(
                            type=types.Type.STRING,
                            description="Texto da User Story"
                        ),
                        "audit_context": types.Schema(
                            type=types.Type.STRING,
                            description="Resumo dos artefatos a auditar"
                        )
                    },
                    required=["user_story", "audit_context"]
                )
            ),
            types.FunctionDeclaration(
                name="score_quality",
                description=(
                    "Atribui score de qualidade (clareza, completude, "
                    "testabilidade, consistência) e gera sugestões de melhoria."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_story": types.Schema(
                            type=types.Type.STRING,
                            description="Texto da User Story"
                        ),
                        "audit_summary": types.Schema(
                            type=types.Type.STRING,
                            description="Resumo da auditoria realizada"
                        )
                    },
                    required=["user_story", "audit_summary"]
                )
            ),
            types.FunctionDeclaration(
                name="search_qdrant",
                description=(
                    "Busca na memória de longo prazo por auditorias "
                    "anteriores e padrões de qualidade."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="Texto de busca semântica"
                        )
                    },
                    required=["query"]
                )
            ),
            types.FunctionDeclaration(
                name="save_to_qdrant",
                description=(
                    "Salva o relatório final da auditoria no Qdrant."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "agent_name": types.Schema(
                            type=types.Type.STRING,
                            description="Nome do agente"
                        ),
                        "content": types.Schema(
                            type=types.Type.STRING,
                            description="Conteúdo a ser salvo"
                        )
                    },
                    required=["agent_name", "content"]
                )
            ),
        ]
    )
]

TOOL_MAP = {
    "audit_reqs": lambda **kwargs: _run_audit(**kwargs),
    "score_quality": lambda **kwargs: score_quality(**kwargs),
    "search_qdrant": lambda **kwargs: search_qdrant(**kwargs),
    "save_to_qdrant": lambda **kwargs: save_to_qdrant(**kwargs),
}

# Contexto compartilhado para a tool audit_reqs
_audit_context_data = {}


def _run_audit(user_story: str, audit_context: str = "") -> dict:
    """Wrapper que usa o contexto armazenado para chamar audit_reqs."""
    return audit_reqs(
        user_story=user_story,
        backlog=_audit_context_data.get("backlog", []),
        hidden_requirements=_audit_context_data.get("hidden_requirements", []),
        edge_cases=_audit_context_data.get("edge_cases", []),
        risks=_audit_context_data.get("risks", []),
    )


SYSTEM_PROMPT = """Você é o Agente Auditor, o terceiro e último agente do pipeline.

Você recebe os outputs dos Agentes 1 (Scrum Master) e 2 (Requisitos Ocultos)
via messages[] (short-term memory).

Seu papel é avaliar a qualidade final e gerar o relatório consolidado.

## Fluxo obrigatório:

1. CONSULTAR MEMÓRIA: Use search_qdrant() para buscar auditorias anteriores.

2. AUDITAR: Use audit_reqs() para verificar consistência entre todos os artefatos.

3. PONTUAR: Use score_quality() para atribuir scores de qualidade.

4. SALVAR: Use save_to_qdrant() para persistir o relatório final.

5. GERAR RELATÓRIO: Produza o JSON final consolidado.

## Formato da saída final (JSON):

{
    "quality_score": {
        "clarity": 8,
        "completeness": 7,
        "testability": 8,
        "consistency": 7,
        "overall": 7.5
    },
    "audit_findings": [
        {"finding": "descrição", "severity": "alta|média|baixa"}
    ],
    "consistency_issues": ["descrição de inconsistência"],
    "suggestions": ["sugestão de melhoria"],
    "missing_acceptance_criteria": ["critério ausente"],
    "final_recommendation": "recomendação final em 2-3 frases",
    "agent": "auditor"
}

IMPORTANTE:
- Use TODAS as tools no fluxo
- Seja rigoroso e objetivo nos scores
- Scores de 1 a 10
- Identifique inconsistências reais, não invente problemas"""


class AuditorAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")

        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            tools=TOOLS_DECLARATION,
            temperature=0.2
        )

    def run(self, scrum_master_output: dict,
            hidden_req_output: dict) -> dict:
        """
        Executa o agente Auditor.

        Args:
            scrum_master_output: Output do Agente 1
            hidden_req_output: Output do Agente 2
            Ambos passados via messages[] (short-term memory)

        Returns:
            dict com relatório final, scores e sugestões
        """
        global _audit_context_data

        print(f"\n{'='*60}")
        print("📝 AGENTE 3 — AUDITORIA")
        print(f"{'='*60}\n")

        # Extrai dados dos agentes anteriores
        us = scrum_master_output.get("user_story_summary", "")
        backlog = scrum_master_output.get("backlog", [])
        raw_sm = scrum_master_output.get("raw_response", "")
        h_reqs = hidden_req_output.get("hidden_requirements", [])
        edges = hidden_req_output.get("edge_cases", [])
        risks = hidden_req_output.get("risks", [])
        deps = hidden_req_output.get("dependencies", [])
        raw_hr = hidden_req_output.get("raw_response", "")

        # Armazena contexto para a tool audit_reqs
        _audit_context_data = {
            "backlog": backlog,
            "hidden_requirements": h_reqs,
            "edge_cases": edges,
            "risks": risks,
        }

        # Monta contexto (short-term memory via messages[])
        context = f"User Story: {us}\n\n"

        if backlog:
            context += "BACKLOG (Agente 1):\n"
            for t in backlog[:10]:
                task = t.get("task", str(t))
                prio = t.get("priority", "?")
                context += f"- [{prio}] {task}\n"
        elif raw_sm:
            context += f"Análise do Scrum Master:\n{raw_sm[:2000]}\n"

        context += "\nREQUISITOS OCULTOS (Agente 2):\n"
        if h_reqs:
            for r in h_reqs[:8]:
                req = r.get("requirement", str(r))
                context += f"- {req}\n"
        elif raw_hr:
            context += f"{raw_hr[:2000]}\n"

        if edges:
            context += "\nEDGE CASES:\n"
            for e in edges[:8]:
                sc = e.get("scenario", str(e))
                context += f"- {sc}\n"

        if risks:
            context += "\nRISCOS:\n"
            for r in risks[:8]:
                risk = r.get("risk", str(r))
                context += f"- {risk}\n"

        user_input = (
            f"Audite a seguinte análise completa recebida dos Agentes 1 e 2.\n\n"
            f"{context}\n\n"
            f"Siga o fluxo: consultar memória → auditar consistência → "
            f"pontuar qualidade → salvar memória → gerar relatório JSON."
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
        ]

        max_iterations = 25
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=self.config,
                )
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
                    wait = int(match.group(1)) + 5 if match else 40
                    print(f"⏳ Rate limit. Aguardando {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"❌ Erro: {error_msg}")
                    return {"status": "error", "message": error_msg}

            if (not response.candidates
                    or not response.candidates[0].content
                    or not response.candidates[0].content.parts):
                print("⚠️  Resposta vazia, tentando novamente...")
                time.sleep(5)
                continue

            parts = response.candidates[0].content.parts
            has_function_call = False

            for part in parts:
                if hasattr(part, 'function_call') and part.function_call:
                    has_function_call = True
                    fc = part.function_call
                    fn_name = fc.name
                    args = dict(fc.args) if fc.args else {}

                    print(f"🔧 Tool: {fn_name}")
                    if fn_name == "audit_reqs":
                        print(f"   Auditando consistência dos artefatos...")
                    elif fn_name == "score_quality":
                        print(f"   Calculando score de qualidade...")
                    elif fn_name == "search_qdrant":
                        print(f"   Buscando memória: {args.get('query', '')}")
                    elif fn_name == "save_to_qdrant":
                        print(f"   Salvando relatório no Qdrant...")

                    try:
                        result = TOOL_MAP[fn_name](**args)
                    except Exception as e:
                        result = {"status": "error", "message": str(e)}

                    print(f"   ✅ Concluído\n")

                    contents.append(response.candidates[0].content)
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=fn_name,
                                        response={"result": result}
                                    )
                                )
                            ]
                        )
                    )
                    break

            if has_function_call:
                continue

            for part in parts:
                if hasattr(part, 'text') and part.text:
                    text = part.text.strip()
                    clean = text
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    if clean.startswith("```"):
                        clean = clean[3:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    clean = clean.strip()

                    try:
                        result = json.loads(clean)
                        print("📊 Relatório final gerado com sucesso\n")
                        return result
                    except json.JSONDecodeError:
                        return {
                            "quality_score": {},
                            "audit_findings": [],
                            "suggestions": [],
                            "raw_response": text,
                            "agent": "auditor"
                        }
            break

        return {"status": "error", "message": "Max iterations reached"}
