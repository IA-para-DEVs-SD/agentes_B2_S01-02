"""
✅ GABARITO — Exercício 2: Benchmark de Modelos
------------------------------------------------
Compara claude-haiku vs claude-opus em custo, velocidade e qualidade.
Judge obrigatório: avalia precisão técnica das respostas.

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
EXPERIMENTO_NOME = "benchmark-modelos-suporte"

VARIACOES = [
    {"model": "claude-haiku-4-5"},
    {"model": "claude-opus-4-5"},
    # BÔNUS: adicione outros vendors aqui
    # {"model": "gpt-4o"},
]

SYSTEM_PROMPT = "Você é um especialista em suporte técnico de APIs. Responda de forma clara e precisa."

PERGUNTAS = [
    "Como faço para resetar minha senha via API?",
    "Qual a diferença entre autenticação OAuth e API Key?",
    "Minha requisição está retornando erro 429, o que significa?",
]


# ---------------------------------------------------------------------------
# Chamada ao LLM parametrizada por modelo
# ---------------------------------------------------------------------------
def call_llm(messages: list, model: str) -> anthropic.types.Message:
    return client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )


# ---------------------------------------------------------------------------
# Agente simples
# ---------------------------------------------------------------------------
def run_agent(user_message: str, config: dict, session_id: str | None = None) -> dict:
    model = config["model"]
    messages = [{"role": "user", "content": user_message}]
    start_time = time.time()

    with propagate_attributes(session_id=session_id, metadata={"model": model}):
        response = call_llm(messages, model)

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
# LLM-as-a-Judge — avalia precisão técnica (obrigatório)
# Dica: usa haiku para o judge — mais barato e rápido
# ---------------------------------------------------------------------------
def judge_precisao_tecnica(pergunta: str, resposta: str) -> dict:
    prompt = f"""Você é um engenheiro sênior avaliando respostas de suporte técnico.

Pergunta: "{pergunta}"
Resposta: "{resposta}"

A resposta é tecnicamente correta e útil para um desenvolvedor?
- Score 1.0: correta, clara e completa
- Score 0.5: parcialmente correta ou incompleta
- Score 0.0: incorreta ou confusa

Responda APENAS com JSON válido, sem texto adicional, sem markdown:
{{"score": 0.0, "justificativa": "..."}}"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ⚠️  Judge retornou formato inesperado: {raw}")
        return {"score": 0.5, "justificativa": "Erro ao parsear resposta do judge."}


# ---------------------------------------------------------------------------
# Runner do experimento
# ---------------------------------------------------------------------------
def rodar_experimento():
    mlflow.set_experiment(EXPERIMENTO_NOME)

    print(f"\n🧪 Experimento: {EXPERIMENTO_NOME}")
    print(f"   {len(VARIACOES)} modelos x {len(PERGUNTAS)} perguntas\n")

    resultados_finais = []

    for variacao in VARIACOES:
        model = variacao["model"]
        run_name = model.replace("/", "-")

        print(f"\n{'='*60}")
        print(f"🤖 Modelo: {model}")
        print(f"{'='*60}")

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("model", model)
            mlflow.log_param("system_prompt", SYSTEM_PROMPT)

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

                print(f"  Resposta: {resultado['resposta'][:120]}...")

                avaliacao = judge_precisao_tecnica(pergunta, resultado["resposta"])
                print(f"  Judge: {avaliacao['score']} | {avaliacao['justificativa']}")

                total_tokens += resultado["total_tokens"]
                total_latency += resultado["latency_seconds"]
                total_judge_score += avaliacao["score"]

                mlflow.log_metric("tokens_por_pergunta", resultado["total_tokens"], step=j)
                mlflow.log_metric("latencia_por_pergunta", resultado["latency_seconds"], step=j)
                mlflow.log_metric("judge_por_pergunta", avaliacao["score"], step=j)

            n = len(PERGUNTAS)
            tokens_medio = total_tokens / n
            latencia_media = total_latency / n
            judge_medio = total_judge_score / n

            mlflow.log_metric("tokens_medio", tokens_medio)
            mlflow.log_metric("latencia_media", latencia_media)
            mlflow.log_metric("judge_score_medio", judge_medio)

            resultados_finais.append({
                "model": model,
                "tokens_medio": round(tokens_medio),
                "latencia_media": round(latencia_media, 2),
                "judge_score_medio": round(judge_medio, 2),
            })

    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"{'Modelo':<25} {'Tokens':>8} {'Latência':>10} {'Judge':>8}")
    print(f"{'-'*55}")
    for r in resultados_finais:
        print(f"{r['model']:<25} {r['tokens_medio']:>8} {r['latencia_media']:>9}s {r['judge_score_medio']:>8}")

    # Recomendação baseada em relação qualidade/custo
    melhor = max(resultados_finais, key=lambda x: x["judge_score_medio"] / x["tokens_medio"] * 1000)
    print(f"\n🏆 Recomendação: {melhor['model']}")
    print(f"   Melhor relação qualidade/custo")

    langfuse.flush()
    print(f"\n✅ Veja os resultados em http://localhost:5001")
    print(f"💡 Selecione os runs e clique em 'Compare' para ver os gráficos!")


if __name__ == "__main__":
    rodar_experimento()