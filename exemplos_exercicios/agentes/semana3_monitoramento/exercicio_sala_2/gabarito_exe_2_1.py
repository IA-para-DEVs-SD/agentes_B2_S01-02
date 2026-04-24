"""
✅ GABARITO — Exercício 1: Engenharia de Prompts
-------------------------------------------------
Compara 3 system prompts e mede tokens, latência e qualidade.

Instalação:
    pip install anthropic langfuse mlflow python-dotenv
"""

import os
import json
import time
import anthropic
import mlflow
from langfuse import get_client, propagate_attributes
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
langfuse = get_client()
mlflow.set_tracking_uri("http://localhost:5001")

# ---------------------------------------------------------------------------
# ✏️ CONFIGURAÇÃO DO EXPERIMENTO
# ---------------------------------------------------------------------------
EXPERIMENTO_NOME = "comparacao-prompts-ecommerce"
MODEL = "claude-haiku-4-5"

VARIACOES = [
    {"system_prompt": "Você é um atendente de e-commerce. Responda de forma objetiva."},
    {"system_prompt": "Você é um atendente de e-commerce simpático. Use linguagem informal e emojis."},
    {"system_prompt": "Você é um especialista em e-commerce. Dê respostas detalhadas com exemplos práticos."},
]

PERGUNTAS = [
    "Meu pedido não chegou, o que eu faço?",
    "Vocês aceitam devolução?",
    "Como rastreio minha entrega?",
]


# ---------------------------------------------------------------------------
# Chamada ao LLM com system prompt parametrizado
# ---------------------------------------------------------------------------
def call_llm(messages: list, system_prompt: str) -> anthropic.types.Message:
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )


# ---------------------------------------------------------------------------
# Agente simples (sem ferramentas — foco é no prompt)
# ---------------------------------------------------------------------------
def run_agent(user_message: str, config: dict, session_id: str | None = None) -> dict:
    system_prompt = config["system_prompt"]
    messages = [{"role": "user", "content": user_message}]
    start_time = time.time()

    with propagate_attributes(session_id=session_id, metadata={"model": MODEL}):
        response = call_llm(messages, system_prompt)

    final_text = response.content[0].text
    elapsed = time.time() - start_time

    return {
        "resposta": final_text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "latency_seconds": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# BÔNUS: LLM-as-a-Judge — avalia satisfação do cliente
# ---------------------------------------------------------------------------
def judge_satisfacao(pergunta: str, resposta: str) -> dict:
    prompt = f"""Você é um avaliador de atendimento ao cliente.

Pergunta do cliente: "{pergunta}"
Resposta do atendente: "{resposta}"

O cliente ficaria satisfeito com essa resposta?
- Score 1.0: resposta clara, resolutiva e amigável
- Score 0.5: resposta correta mas incompleta ou fria
- Score 0.0: resposta confusa, incorreta ou inadequada

Responda APENAS com JSON válido, sem texto adicional, sem markdown:
{{"score": 0.0, "justificativa": "..."}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    try:
        # Remove blocos ```json ``` se o modelo incluir
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback seguro se o modelo não seguir o formato
        print(f"  ⚠️  Judge retornou formato inesperado: {raw}")
        return {"score": 0.5, "justificativa": "Erro ao parsear resposta do judge."}


# ---------------------------------------------------------------------------
# Runner do experimento
# ---------------------------------------------------------------------------
def rodar_experimento():
    mlflow.set_experiment(EXPERIMENTO_NOME)

    print(f"\n🧪 Experimento: {EXPERIMENTO_NOME}")
    print(f"   {len(VARIACOES)} variações x {len(PERGUNTAS)} perguntas\n")

    for i, variacao in enumerate(VARIACOES, 1):
        run_name = f"prompt-v{i}"
        print(f"\n{'='*60}")
        print(f"🔧 Variação {i}: {variacao['system_prompt'][:60]}...")
        print(f"{'='*60}")

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("model", MODEL)
            mlflow.log_param("system_prompt", variacao["system_prompt"])

            total_tokens = 0
            total_latency = 0
            total_judge_score = 0

            for j, pergunta in enumerate(PERGUNTAS, 1):
                print(f"\n  Pergunta {j}: {pergunta}")

                resultado = run_agent(
                    pergunta,
                    config=variacao,
                    session_id=f"{run_name}-q{j}",
                )

                print(f"  Resposta: {resultado['resposta'][:100]}...")

                # BÔNUS: avalia com judge
                avaliacao = judge_satisfacao(pergunta, resultado["resposta"])
                print(f"  Judge score: {avaliacao['score']} | {avaliacao['justificativa']}")

                total_tokens += resultado["total_tokens"]
                total_latency += resultado["latency_seconds"]
                total_judge_score += avaliacao["score"]

                mlflow.log_metric("tokens_por_pergunta", resultado["total_tokens"], step=j)
                mlflow.log_metric("latencia_por_pergunta", resultado["latency_seconds"], step=j)
                mlflow.log_metric("judge_por_pergunta", avaliacao["score"], step=j)

            n = len(PERGUNTAS)
            mlflow.log_metric("tokens_medio", total_tokens / n)
            mlflow.log_metric("latencia_media", total_latency / n)
            mlflow.log_metric("judge_score_medio", total_judge_score / n)

    langfuse.flush()
    print(f"\n✅ Experimento concluído! Veja os resultados em http://localhost:5001")
    print(f"💡 Selecione os 3 runs e clique em 'Compare' para ver os gráficos!")


if __name__ == "__main__":
    rodar_experimento()