# Agente 02 - Analista de Requisitos
# Responsável por identificar requisitos e dependências

import json
import os
import sys

sys.path.append(os.path.dirname(__file__))

from openai import OpenAI
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, USER_TEMPLATE
from tools import TOOLS, handle_tool_call

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

client = OpenAI()

MAX_TOOL_ROUNDS = 5


class RequirementsAgent:
    """Agente Analista de Requisitos com suporte a tool calling."""

    def __init__(self, model: str = "gpt-4.1"):
        self.model = model

    def run(self, scrum_output: dict | str) -> dict:
        """
        Recebe o output do Agente 01 (Scrum Master) e produz
        documento de requisitos funcionais, não-funcionais,
        mapa de dependências e riscos.
        """
        if isinstance(scrum_output, dict):
            scrum_output = json.dumps(scrum_output, ensure_ascii=False, indent=2)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(scrum_output=scrum_output)},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = client.responses.create(
                model=self.model,
                input=messages,
                tools=TOOLS,
            )

            if not response.output:
                break

            tool_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:
                break

            messages.extend(response.output)
            for tc in tool_calls:
                args = json.loads(tc.arguments)
                result = handle_tool_call(tc.name, args)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tc.call_id,
                    "output": result,
                })

        output_text = response.output_text
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            return {"raw_output": output_text}


# ── Helpers ─────────────────────────────────────────────────────────────────

def load_latest_scrum_output() -> dict | None:
    """Busca o JSON mais recente do Agente 01 na pasta output/."""
    import glob

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    pattern = os.path.join(output_dir, "scrum_backlog_*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        return None

    latest = files[-1]
    print(f"📂 Lendo output do Agente 01: {os.path.basename(latest)}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Execução direta ────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime

    agent = RequirementsAgent()

    scrum_output = load_latest_scrum_output()

    if scrum_output is None:
        print("⚠️  Nenhum output do Agente 01 encontrado em output/.")
        print("   Execute o Agente 01 (Scrum Master) primeiro:")
        print("   docker compose up scrum-agent --build")
        sys.exit(1)

    print("📝 Executando Agente Analista de Requisitos...\n")
    result = agent.run(scrum_output)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Salva relatório
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"requirements_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Relatório salvo em: {output_path}")

    # Marker para o healthcheck do docker-compose
    with open(os.path.join(output_dir, ".requirements_done"), "w") as f:
        f.write("ok")
