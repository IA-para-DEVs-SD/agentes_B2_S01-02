# Agente 01 - Scrum Master
# Responsável por quebrar histórias de usuário em tarefas técnicas

import json
import os
import sys

# Garante que imports relativos funcionem
sys.path.append(os.path.dirname(__file__))

from openai import OpenAI
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, USER_TEMPLATE
from tools import TOOLS, handle_tool_call

# Carrega variáveis de ambiente (.env na raiz de exemplos_exercicios)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

client = OpenAI()

MAX_TOOL_ROUNDS = 5  # limite de ciclos de tool calling


class ScrumAgent:
    """Agente Scrum Master com suporte a tool calling."""

    def __init__(self, model: str = "gpt-4.1"):
        self.model = model

    def run(self, user_story: str) -> dict:
        """
        Executa o agente para uma user story.

        Retorna o JSON estruturado com backlog, critérios de aceitação, etc.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(user_story=user_story)},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = client.responses.create(
                model=self.model,
                input=messages,
                tools=TOOLS,
            )

            # Se não há tool calls, temos a resposta final
            if not response.output:
                break

            # Verifica se há function calls na saída
            tool_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:
                # Resposta final (texto)
                break

            # Processa cada tool call
            messages.extend(response.output)
            for tc in tool_calls:
                args = json.loads(tc.arguments)
                result = handle_tool_call(tc.name, args)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tc.call_id,
                    "output": result,
                })

        # Extrai texto final
        output_text = response.output_text
        # Tenta parsear como JSON
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            return {"raw_output": output_text}


# ── Execução direta ───────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime

    agent = ScrumAgent()

    user_story = """
    Precisamos de um dashboard para acompanhar os alunos no ambiente virtual
    de aprendizagem. O acompanhamento deve focar no acesso, notas e progresso
    por curso.
    """

    print("🚀 Executando Agente Scrum Master...\n")
    result = agent.run(user_story)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Salva relatório em output/
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"scrum_backlog_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Relatório salvo em: {output_path}")

    # Marker para o healthcheck do docker-compose
    with open(os.path.join(output_dir, ".scrum_done"), "w") as f:
        f.write("ok")
