"""
Experimento: compara temperaturas do agente
--------------------------------------------
Fácil de adaptar para comparar modelos, prompts, max_tokens, etc.

Instalação:
    pip install anthropic langfuse mlflow python-dotenv
"""

import os
import json
import time
from datetime import datetime
import anthropic
import mlflow
from langfuse import observe, get_client, propagate_attributes
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
langfuse = get_client()

mlflow.set_tracking_uri("http://localhost:5001")

# ---------------------------------------------------------------------------
# ✏️ CONFIGURE O EXPERIMENTO AQUI
# Troque os valores abaixo para comparar outras variáveis
# ---------------------------------------------------------------------------
EXPERIMENTO_NOME = "comparacao-temperatura"

VARIACOES = [
    {"temperature": 0.0},
    {"temperature": 0.5},
    {"temperature": 1.0},
]

# Perguntas usadas em TODAS as variações (para comparação justa)
PERGUNTAS = [
    "Crie uma metáfora criativa para explicar o que é inteligência artificial.",
    "Resuma em uma frase: 'O céu é azul porque as moléculas do ar dispersam mais a luz azul do que as outras cores.'",
]

# ---------------------------------------------------------------------------
# Ferramentas
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "word_counter",
        "description": "Conta palavras, caracteres e frases de um texto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            },
            "required": ["text"],
        },
    },
]

def run_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "word_counter":
        text = tool_input["text"]
        words = len(text.split())
        chars = len(text)
        sentences = sum(text.count(p) for p in [".", "!", "?"])
        return json.dumps({"palavras": words, "caracteres": chars, "frases": max(sentences, 1)})
    return f"Ferramenta '{tool_name}' não encontrada."


# ---------------------------------------------------------------------------
# Agente parametrizado
# Recebe config como argumento — fácil de variar
# ---------------------------------------------------------------------------
def run_agent(user_message: str, config: dict, session_id: str | None = None) -> dict:
    """
    Roda o agente com a config fornecida.
    Retorna um dict com a resposta e as métricas coletadas.
    """
    model = config.get("model", "claude-haiku-4-5")
    temperature = config.get("temperature", 1.0)
    max_tokens = config.get("max_tokens", 1024)

    messages = [{"role": "user", "content": user_message}]
    total_input_tokens = 0
    total_output_tokens = 0
    tools_used = []
    iterations = 0
    start_time = time.time()
    final_text = ""

    with propagate_attributes(session_id=session_id, metadata={"model": model, "temperature": temperature}):
        while iterations < 10:
            iterations += 1

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=TOOLS,
                messages=messages,
            )

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
                    tools_used.append(block.name)
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
                messages.append({"role": "user", "content": tool_results})

    elapsed = time.time() - start_time

    return {
        "resposta": final_text,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "tool_calls": len(tools_used),
        "iterations": iterations,
        "latency_seconds": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Runner do experimento
# ---------------------------------------------------------------------------
def rodar_experimento():
    mlflow.set_experiment(EXPERIMENTO_NOME)

    print(f"\n🧪 Experimento: {EXPERIMENTO_NOME}")
    print(f"   {len(VARIACOES)} variações x {len(PERGUNTAS)} perguntas\n")

    for variacao in VARIACOES:
        # Nome do run descreve a variação
        run_name = "_".join(f"{k}={v}" for k, v in variacao.items())

        print(f"\n{'='*60}")
        print(f"🔧 Variação: {variacao}")
        print(f"{'='*60}")

        # Config completa = defaults + variação atual
        config = {
            "model": "claude-haiku-4-5",
            "temperature": 1.0,
            "max_tokens": 1024,
            **variacao,  # sobrescreve com a variação atual
        }

        with mlflow.start_run(run_name=run_name):
            # Loga a config completa como params
            for k, v in config.items():
                mlflow.log_param(k, v)

            # Acumula métricas de todas as perguntas
            metricas_totais = {
                "total_tokens": 0,
                "latency_seconds": 0,
                "tool_calls": 0,
            }

            for i, pergunta in enumerate(PERGUNTAS, 1):
                print(f"\n  Pergunta {i}: {pergunta[:60]}...")

                resultado = run_agent(
                    pergunta,
                    config=config,
                    session_id=f"{run_name}-q{i}",
                )

                print(f"  Resposta: {resultado['resposta'][:100]}...")
                print(f"  Tokens: {resultado['total_tokens']} | Latência: {resultado['latency_seconds']}s")

                metricas_totais["total_tokens"] += resultado["total_tokens"]
                metricas_totais["latency_seconds"] += resultado["latency_seconds"]
                metricas_totais["tool_calls"] += resultado["tool_calls"]

                # Loga métricas por pergunta (com step = índice da pergunta)
                mlflow.log_metric("tokens_por_pergunta", resultado["total_tokens"], step=i)
                mlflow.log_metric("latencia_por_pergunta", resultado["latency_seconds"], step=i)

            # Loga médias da variação
            n = len(PERGUNTAS)
            mlflow.log_metric("tokens_medio", metricas_totais["total_tokens"] / n)
            mlflow.log_metric("latencia_media", metricas_totais["latency_seconds"] / n)
            mlflow.log_metric("tool_calls_total", metricas_totais["tool_calls"])

    langfuse.flush()
    print(f"\n✅ Experimento concluído! Veja os resultados em http://localhost:5001")


if __name__ == "__main__":
    rodar_experimento()