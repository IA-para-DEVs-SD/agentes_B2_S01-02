"""
Agente 1 — Scrum Master

Responsável por interpretar a User Story e transformá-la em itens acionáveis.

Funções:
- Analisar a User Story
- Buscar referências externas (search_exa)
- Quebrar em tarefas menores (break_tasks)
- Priorizar backlog inicial (prioritize)
- Salvar resultado no Qdrant (long-term memory)

Saída esperada:
- Backlog inicial com tarefas priorizadas
- Resumo para o próximo agente (short-term memory via messages[])
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.exa_search import search_exa
from tools.task_breaker import break_tasks
from tools.prioritizer import prioritize
from tools.qdrant_memory import save_to_qdrant, search_qdrant


# ============================================================
# Declaração das tools para o Gemini (function calling)
# ============================================================
TOOLS_DECLARATION = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_exa",
                description=(
                    "Busca referências externas, boas práticas e padrões "
                    "relacionados ao tema da User Story usando a API Exa."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="Texto de busca sobre o tema"
                        )
                    },
                    required=["query"]
                )
            ),
            types.FunctionDeclaration(
                name="break_tasks",
                description=(
                    "Quebra uma User Story em tarefas técnicas menores e "
                    "acionáveis, incluindo backend, frontend, testes e infra."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_story": types.Schema(
                            type=types.Type.STRING,
                            description="Texto da User Story"
                        ),
                        "acceptance_criteria": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Lista de critérios de aceitação"
                        )
                    },
                    required=["user_story"]
                )
            ),
            types.FunctionDeclaration(
                name="prioritize",
                description=(
                    "Prioriza as tarefas do backlog baseado em valor de "
                    "negócio, risco técnico e dependências."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "tasks": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "id": types.Schema(type=types.Type.INTEGER),
                                    "task": types.Schema(type=types.Type.STRING),
                                    "type": types.Schema(type=types.Type.STRING),
                                    "effort": types.Schema(type=types.Type.STRING),
                                },
                            ),
                            description="Lista de tarefas a priorizar"
                        ),
                        "user_story": types.Schema(
                            type=types.Type.STRING,
                            description="User Story original para contexto"
                        )
                    },
                    required=["tasks", "user_story"]
                )
            ),
            types.FunctionDeclaration(
                name="save_to_qdrant",
                description=(
                    "Salva o resultado da análise no Qdrant como memória "
                    "de longo prazo para consulta futura."
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
            types.FunctionDeclaration(
                name="search_qdrant",
                description=(
                    "Busca no Qdrant por análises anteriores similares "
                    "para usar como referência."
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
        ]
    )
]

# Mapa de tools
TOOL_MAP = {
    "search_exa": lambda **kwargs: search_exa(**kwargs),
    "break_tasks": lambda **kwargs: break_tasks(**kwargs),
    "prioritize": lambda **kwargs: prioritize(**kwargs),
    "save_to_qdrant": lambda **kwargs: save_to_qdrant(**kwargs),
    "search_qdrant": lambda **kwargs: search_qdrant(**kwargs),
}

# System prompt
SYSTEM_PROMPT = """Você é o Agente Scrum Master, o primeiro agente de um pipeline multi-agente.

Seu papel é receber uma User Story com critérios de aceitação e produzir um backlog técnico priorizado.

## Fluxo obrigatório de trabalho:

1. BUSCAR REFERÊNCIAS: Use search_exa() para buscar boas práticas e padrões relacionados ao tema da User Story.

2. CONSULTAR MEMÓRIA: Use search_qdrant() para verificar se há análises anteriores similares que possam servir de referência.

3. QUEBRAR EM TAREFAS: Use break_tasks() para decompor a User Story em tarefas técnicas menores e acionáveis.

4. PRIORIZAR: Use prioritize() para ordenar as tarefas por prioridade (Alta, Média, Baixa).

5. SALVAR MEMÓRIA: Use save_to_qdrant() para persistir o resultado da análise como memória de longo prazo.

6. GERAR RESUMO: Produza um resumo estruturado que será passado ao próximo agente.

## Formato da saída final (JSON):

{
    "user_story_summary": "resumo curto da User Story",
    "backlog": [
        {"task": "descrição", "priority": "Alta|Média|Baixa", "type": "backend|frontend|infra|test", "effort": "P|M|G"}
    ],
    "external_references": ["referência 1", "referência 2"],
    "observations": "observações importantes para o próximo agente",
    "agent": "scrum_master"
}

IMPORTANTE:
- Use TODAS as tools disponíveis no fluxo
- Seja técnico e específico nas tarefas
- A saída final deve ser JSON válido
- O resumo será passado ao Agente 2 (Requisitos Ocultos) via messages[]"""


class ScrumMasterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")

        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            tools=TOOLS_DECLARATION,
            temperature=0.2
        )

    def run(self, user_story: str, acceptance_criteria: list = None) -> dict:
        """
        Executa o agente Scrum Master.

        Args:
            user_story: Texto da User Story
            acceptance_criteria: Lista de critérios de aceitação

        Returns:
            dict com backlog priorizado e resumo
        """
        print(f"\n{'='*60}")
        print("📋 AGENTE 1 — SCRUM MASTER")
        print(f"{'='*60}\n")

        # Monta o prompt do usuário
        criteria_text = ""
        if acceptance_criteria:
            criteria_text = "\nCritérios de aceitação:\n"
            criteria_text += "\n".join(f"- {c}" for c in acceptance_criteria)

        user_input = (
            f"Analise a seguinte User Story e gere o backlog priorizado.\n\n"
            f"User Story: {user_story}{criteria_text}\n\n"
            f"Siga o fluxo obrigatório: buscar referências → consultar memória "
            f"→ quebrar em tarefas → priorizar → salvar memória → gerar resumo."
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
        ]

        # Loop de tool calling
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
                    import re
                    match = re.search(r"retry in (\d+)", error_msg, re.IGNORECASE)
                    wait = int(match.group(1)) + 5 if match else 40
                    print(f"⏳ Rate limit atingido. Aguardando {wait}s...")
                    import time
                    time.sleep(wait)
                    continue
                else:
                    print(f"❌ Erro: {error_msg}")
                    return {"status": "error", "message": error_msg}

            # Verifica as partes da resposta
            if (not response.candidates
                    or not response.candidates[0].content
                    or not response.candidates[0].content.parts):
                print("⚠️  Resposta vazia do Gemini, tentando novamente...")
                import time
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
                    elif fn_name == "break_tasks":
                        print(f"   Quebrando User Story em tarefas...")
                    elif fn_name == "prioritize":
                        print(f"   Priorizando {len(args.get('tasks', []))} tarefas...")
                    elif fn_name == "save_to_qdrant":
                        print(f"   Salvando no Qdrant...")
                    elif fn_name == "search_qdrant":
                        print(f"   Buscando memória: {args.get('query', '')}")

                    # Executa a tool
                    try:
                        result = TOOL_MAP[fn_name](**args)
                    except Exception as e:
                        result = {"status": "error", "message": str(e)}

                    print(f"   ✅ Concluído\n")

                    # Adiciona ao histórico
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
                    break  # Processa uma tool por vez

            if has_function_call:
                continue

            # Sem function call = resposta final
            for part in parts:
                if hasattr(part, 'text') and part.text:
                    text = part.text.strip()

                    # Tenta parsear como JSON
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
                            "user_story_summary": user_story,
                            "backlog": [],
                            "raw_response": text,
                            "agent": "scrum_master"
                        }

            break

        return {"status": "error", "message": "Max iterations reached"}
