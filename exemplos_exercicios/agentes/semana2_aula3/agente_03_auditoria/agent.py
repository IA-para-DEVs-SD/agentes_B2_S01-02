# Agente 03 - Auditor de Qualidade
# Responsável por validar e pontuar a qualidade dos requisitos

import glob
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


class AuditAgent:
    """Agente Auditor de Qualidade com suporte a tool calling."""

    def __init__(self, model: str = "gpt-4.1"):
        self.model = model

    def run(self, scrum_output: dict | str, requirements_output: dict | str) -> dict:
        """
        Recebe os outputs dos Agentes 01 e 02 e produz
        relatório de auditoria com score de qualidade.
        """
        if isinstance(scrum_output, dict):
            scrum_output = json.dumps(scrum_output, ensure_ascii=False, indent=2)
        if isinstance(requirements_output, dict):
            requirements_output = json.dumps(requirements_output, ensure_ascii=False, indent=2)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(
                scrum_output=scrum_output,
                requirements_output=requirements_output,
            )},
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

def _load_latest(pattern: str, label: str) -> dict | None:
    """Busca o JSON mais recente que bate com o pattern em output/."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    files = sorted(glob.glob(os.path.join(output_dir, pattern)))
    if not files:
        return None
    latest = files[-1]
    print(f"📂 Lendo {label}: {os.path.basename(latest)}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Execução direta ────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime

    agent = AuditAgent()

    scrum_output = _load_latest("scrum_backlog_*.json", "output do Agente 01")
    requirements_output = _load_latest("requirements_*.json", "output do Agente 02")

    if scrum_output is None or requirements_output is None:
        missing = []
        if scrum_output is None:
            missing.append("Agente 01 (scrum_backlog_*.json)")
        if requirements_output is None:
            missing.append("Agente 02 (requirements_*.json)")
        print(f"⚠️  Outputs não encontrados: {', '.join(missing)}")
        print("   Execute os agentes anteriores primeiro.")
        sys.exit(1)

    print("✅ Executando Agente Auditor de Qualidade...\n")
    result = agent.run(scrum_output, requirements_output)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Salva relatório
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"audit_report_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Relatório salvo em: {output_path}")
