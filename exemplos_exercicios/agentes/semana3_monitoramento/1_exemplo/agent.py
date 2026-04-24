"""
Agente simples com Anthropic SDK + Langfuse v4 (cloud) + MLflow (local)
------------------------------------------------------------------------
Instalação:
    pip install anthropic langfuse mlflow python-dotenv
"""

import os
import json
import time
import anthropic
import mlflow
from langfuse import observe, get_client, propagate_attributes
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
langfuse = get_client()

mlflow.set_tracking_uri("http://localhost:5001")

MODEL = "claude-opus-4-5"
MAX_ITERATIONS = 10


# ---------------------------------------------------------------------------
# Ferramentas disponíveis para o agente
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "calculator",
        "description": "Realiza operações matemáticas básicas: soma, subtração, multiplicação e divisão.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "A operação a ser realizada.",
                },
                "a": {"type": "number", "description": "Primeiro operando."},
                "b": {"type": "number", "description": "Segundo operando."},
            },
            "required": ["operation", "a", "b"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Retorna a data e hora atual.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "text_analyzer",
        "description": "Analisa um texto e retorna estatísticas: número de palavras, caracteres e frases.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a ser analisado."}
            },
            "required": ["text"],
        },
    },
]


# ---------------------------------------------------------------------------
# Implementação das ferramentas
# ---------------------------------------------------------------------------
@observe()
def run_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "calculator":
        a, b = tool_input["a"], tool_input["b"]
        op = tool_input["operation"]
        if op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        elif op == "divide":
            result = a / b if b != 0 else "Erro: divisão por zero"
        return str(result)

    elif tool_name == "get_current_time":
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elif tool_name == "text_analyzer":
        text = tool_input["text"]
        words = len(text.split())
        chars = len(text)
        sentences = text.count(".") + text.count("!") + text.count("?")
        return json.dumps({"palavras": words, "caracteres": chars, "frases": sentences})

    return f"Ferramenta '{tool_name}' não encontrada."


# ---------------------------------------------------------------------------
# Chamada ao LLM
# ---------------------------------------------------------------------------
@observe()
def call_llm(messages: list) -> anthropic.types.Message:
    return client.messages.create(
        model=MODEL,
        max_tokens=4096,
        tools=TOOLS,
        messages=messages,
    )


# ---------------------------------------------------------------------------
# Loop principal do agente
# ---------------------------------------------------------------------------
@observe()
def run_agent(user_message: str, session_id: str | None = None) -> str:
    mlflow.set_experiment("agente-claude")
    with mlflow.start_run(run_name=f"agent-{int(time.time())}"):
        mlflow.log_param("model", MODEL)
        mlflow.log_param("user_message", user_message[:200])
        mlflow.log_param("session_id", session_id or "no-session")

        with propagate_attributes(session_id=session_id, metadata={"model": MODEL}):
            messages = [{"role": "user", "content": user_message}]
            total_input_tokens = 0
            total_output_tokens = 0
            tool_calls_count = 0
            iterations = 0
            start_time = time.time()
            final_text = ""

            try:
                while iterations < MAX_ITERATIONS:
                    iterations += 1

                    response = call_llm(messages)

                    total_input_tokens += response.usage.input_tokens
                    total_output_tokens += response.usage.output_tokens

                    if response.stop_reason == "end_turn":
                        final_text = next(
                            (b.text for b in response.content if b.type == "text"), ""
                        )
                        break

                    if response.stop_reason == "tool_use":
                        messages.append({"role": "assistant", "content": response.content})

                        tool_results = []
                        for block in response.content:
                            if block.type != "tool_use":
                                continue

                            tool_calls_count += 1
                            result = run_tool(block.name, block.input)

                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": result,
                                }
                            )

                        messages.append({"role": "user", "content": tool_results})

                    else:
                        final_text = "Agente encerrou sem resposta textual."
                        break

                else:
                    final_text = "Número máximo de iterações atingido."

            except Exception as e:
                mlflow.log_param("error", str(e))
                raise

            elapsed = time.time() - start_time

            mlflow.log_metric("input_tokens", total_input_tokens)
            mlflow.log_metric("output_tokens", total_output_tokens)
            mlflow.log_metric("total_tokens", total_input_tokens + total_output_tokens)
            mlflow.log_metric("tool_calls", tool_calls_count)
            mlflow.log_metric("iterations", iterations)
            mlflow.log_metric("latency_seconds", elapsed)

        langfuse.flush()
        return final_text


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    perguntas = [
        "Quanto é 1234 multiplicado por 56, dividido por 7? Me mostre o passo a passo.",
        "Que horas são agora? Analise também o seguinte texto: 'Hoje é um belo dia de sol. O céu está azul!'",
    ]

    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{'='*60}")
        print(f"Pergunta {i}: {pergunta}")
        print("="*60)

        resposta = run_agent(pergunta, session_id=f"demo-session-{i}")
        print(f"Resposta:\n{resposta}")