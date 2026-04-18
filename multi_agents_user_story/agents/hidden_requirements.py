"""
Agente 2 — Requisitos Ocultos

Responsável por identificar o que não foi explicitado na User Story
mas é necessário para boa execução.

Funções:
- Buscar lacunas na User Story
- Identificar dependências
- Levantar edge cases
- Consultar memória vetorial (Qdrant) para contexto anterior
- Salvar nova análise no Qdrant

Tools:
- search_exa(): busca externa de referências
- find_edge_cases(): identifica cenários extremos e requisitos ocultos
- search_qdrant(): busca memória de longo prazo
- save_to_qdrant(): salva resultado na memória

Saída esperada:
- Requisitos implícitos
- Riscos
- Dependências
- Casos de borda
- Resumo para o próximo agente
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

from tools.exa_search import search_exa
from tools.edge_cases import find_edge_cases
from tools.qdrant_memory import save_to_qdrant, search_qdrant


TOOLS_DECLARATION = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_exa",
                description=(
                    "Busca referências externas sobre riscos, edge cases e "
                    "requisitos ocultos comuns para o tema da User Story."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="Texto de busca"
                        )
                    },
                    required=["query"]
                )
            ),
            types.FunctionDeclaration(
                name="find_edge_cases",
                description=(
                    "Analisa a User Story e o backlog para identificar "
                    "edge cases, requisitos ocultos, dependências e riscos "
                    "que não foram explicitados."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_story": types.Schema(
                            type=types.Type.STRING,
                            description="Texto da User Story"
                        )
                    },
                    required=["user_story"]
                )
            ),
            types.FunctionDeclaration(
                name="search_qdrant",
                description=(
                    "Busca na memória de longo prazo por análises anteriores "
                    "similares, riscos já identificados e padrões de edge cases."
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
                    "Salva o resultado da análise de requisitos ocultos "
                    "no Qdrant como memória de longo prazo."
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
    "search_exa": lambda **kwargs: search_exa(**kwargs),
    "find_edge_cases": lambda **kwargs: find_edge_cases(**kwargs),
    "search_qdrant": lambda **kwargs: search_qdrant(**kwargs),
    "save_to_qdrant": lambda **kwargs: save_to_qdrant(**kwargs),
}

SYSTEM_PROMPT = """Você é o Agente de Requisitos Ocultos, o segundo agente de um pipeline multi-agente.

Você recebe o resumo do Agente 1 (Scrum Master) via messages[] (short-term memory) contendo:
- A User Story original
- O backlog priorizado
- Observações do Scrum Master

Seu papel é complementar a análise identificando tudo que NÃO foi explicitado.

## Fluxo obrigatório:

1. BUSCAR REFERÊNCIAS: Use search_exa() para buscar riscos e edge cases comuns para o tema.

2. CONSULTAR MEMÓRIA: Use search_qdrant() para buscar análises anteriores similares no Qdrant.

3. IDENTIFICAR EDGE CASES: Use find_edge_cases() para analisar a User Story e encontrar lacunas.

4. SALVAR MEMÓRIA: Use save_to_qdrant() para persistir sua análise.

5. GERAR RESUMO: Produza um JSON estruturado.

## Formato da saída final (JSON):

{
    "hidden_requirements": [
        {"requirement": "descrição", "category": "segurança|performance|usabilidade|dados", "impact": "alto|médio|baixo"}
    ],
    "edge_cases": [
        {"scenario": "descrição", "expected_behavior": "como reagir", "risk_level": "alto|médio|baixo"}
    ],
    "dependencies": [
        {"dependency": "descrição", "type": "técnica|funcional|externa", "blocking": true}
    ],
    "risks": [
        {"risk": "descrição", "category": "implementação|negócio|experiência_usuario|segurança", "probability": "alta|média|baixa", "mitigation": "sugestão"}
    ],
    "summary_for_next_agent": "resumo consolidado para o Agente 3 (Auditoria)",
    "agent": "hidden_requirements"
}

IMPORTANTE:
- Use TODAS as tools no fluxo
- Foque no que NÃO está escrito mas é essencial
- Considere segurança, performance, acessibilidade, dados
- A saída será passada ao Agente 3 (Auditoria) via messages[]"""


class HiddenRequirementsAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")

        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            tools=TOOLS_DECLARATION,
            temperature=0.2
        )

    def run(self, scrum_master_output: dict) -> dict:
        """
        Executa o agente de Requisitos Ocultos.

        Args:
            scrum_master_output: Output do Agente 1 (Scrum Master)
                passado via messages[] (short-term memory)

        Returns:
            dict com requisitos ocultos, edge cases, riscos e dependências
        """
        print(f"\n{'='*60}")
        print("🔍 AGENTE 2 — REQUISITOS OCULTOS")
        print(f"{'='*60}\n")

        # Monta o contexto a partir do output do Agente 1 (short-term memory)
        us = scrum_master_output.get("user_story_summary", "")
        backlog = scrum_master_output.get("backlog", [])
        observations = scrum_master_output.get("observations", "")
        raw = scrum_master_output.get("raw_response", "")

        context = f"User Story: {us}\n\n"
        if backlog:
            context += "Backlog do Scrum Master:\n"
            context += json.dumps(backlog, ensure_ascii=False, indent=2)
        elif raw:
            context += f"Análise do Scrum Master:\n{raw[:3000]}"
        if observations:
            context += f"\n\nObservações do Scrum Master: {observations}"

        user_input = (
            f"Analise o seguinte contexto recebido do Agente 1 (Scrum Master) "
            f"e identifique requisitos ocultos, edge cases, dependências e riscos.\n\n"
            f"{context}\n\n"
            f"Siga o fluxo obrigatório: buscar referências → consultar memória "
            f"→ identificar edge cases → salvar memória → gerar resumo JSON."
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
                print("⚠️  Resposta vazia do Gemini, tentando novamente...")
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
                    if fn_name == "search_exa":
                        print(f"   Query: {args.get('query', '')}")
                    elif fn_name == "find_edge_cases":
                        print(f"   Analisando edge cases e requisitos ocultos...")
                    elif fn_name == "search_qdrant":
                        print(f"   Buscando memória: {args.get('query', '')}")
                    elif fn_name == "save_to_qdrant":
                        print(f"   Salvando no Qdrant...")

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
                        print("📊 Resultado gerado com sucesso\n")
                        return result
                    except json.JSONDecodeError:
                        return {
                            "hidden_requirements": [],
                            "edge_cases": [],
                            "dependencies": [],
                            "risks": [],
                            "raw_response": text,
                            "agent": "hidden_requirements"
                        }
            break

        return {"status": "error", "message": "Max iterations reached"}
