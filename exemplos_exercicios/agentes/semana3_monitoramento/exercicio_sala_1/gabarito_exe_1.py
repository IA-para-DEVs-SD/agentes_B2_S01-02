"""
✅ GABARITO — Agente de Análise de Texto com Monitoramento
----------------------------------------------------------
Exercício básico: Langfuse v4 + MLflow local

Instalação:

Setup:
    1. Suba o MLflow: docker compose up -d
    2. Crie conta no Langfuse: https://cloud.langfuse.com
    3. Preencha o .env com as chaves
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

# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
langfuse = get_client()  # lê LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY do .env automaticamente

mlflow.set_tracking_uri("http://localhost:5001")

MODEL = "claude-opus-4-5"
MAX_ITERATIONS = 10


# ---------------------------------------------------------------------------
# Definição das ferramentas
# Dica: o "description" é o mais importante — é o que o modelo lê para
# decidir QUANDO usar a ferramenta. Seja claro e específico.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "word_counter",
        "description": "Conta palavras, caracteres e frases de um texto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a ser analisado."}
            },
            "required": ["text"],
        },
    },
    {
        "name": "language_detector",
        "description": "Detecta o idioma de um texto. Retorna o nome do idioma em português.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto para detectar o idioma."}
            },
            "required": ["text"],
        },
    },
    # BÔNUS: ferramenta de resumo
    {
        "name": "summarizer",
        "description": "Resume um texto em uma única frase objetiva.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a ser resumido."}
            },
            "required": ["text"],
        },
    },
]


# ---------------------------------------------------------------------------
# Implementação das ferramentas
# Dica: cada ferramenta recebe um dict com os parâmetros definidos no schema
# e deve retornar sempre uma string.
# ---------------------------------------------------------------------------
@observe()  # @observe() cria um span no Langfuse automaticamente
def run_tool(tool_name: str, tool_input: dict) -> str:

    if tool_name == "word_counter":
        text = tool_input["text"]
        words = len(text.split())
        chars = len(text)
        # Conta frases por pontuação final
        sentences = sum(text.count(p) for p in [".", "!", "?"])
        result = {"palavras": words, "caracteres": chars, "frases": max(sentences, 1)}
        return json.dumps(result, ensure_ascii=False)

    elif tool_name == "language_detector":
        #time.sleep(2) -- usado para simular latencia
        text = tool_input["text"].lower()
        # Detecção simples por palavras-chave (suficiente para o exercício)
        # Em produção, use uma biblioteca como langdetect
        portuguese_markers = ["o", "a", "os", "as", "de", "da", "do", "em", "que", "é", "está"]
        english_markers = ["the", "is", "are", "of", "in", "and", "to", "a", "that"]
        spanish_markers = ["el", "la", "los", "las", "de", "en", "que", "es", "está"]

        words = text.split()
        pt_score = sum(1 for w in words if w in portuguese_markers)
        en_score = sum(1 for w in words if w in english_markers)
        es_score = sum(1 for w in words if w in spanish_markers)

        scores = {"português": pt_score, "inglês": en_score, "espanhol": es_score}
        detected = max(scores, key=scores.get)

        return json.dumps({"idioma": detected, "confiança": "baixa (detecção simples)"}, ensure_ascii=False)

    elif tool_name == "summarizer":
        # Resumo simples: pega as primeiras palavras
        # Em produção, chamaria outro LLM ou usaria uma biblioteca
        text = tool_input["text"]
        words = text.split()
        summary = " ".join(words[:15]) + ("..." if len(words) > 15 else "")
        return json.dumps({"resumo": summary}, ensure_ascii=False)

    return f"Ferramenta '{tool_name}' não encontrada."


# ---------------------------------------------------------------------------
# Chamada ao LLM
# Dica: separar em função própria facilita o rastreamento no Langfuse —
# cada chamada ao LLM vira um span separado com seus tokens.
# ---------------------------------------------------------------------------
@observe()
def call_llm(messages: list) -> anthropic.types.Message:
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )


# ---------------------------------------------------------------------------
# Loop principal do agente
# Dica: o @observe() na função principal cria a trace raiz.
# Todas as funções @observe() chamadas dentro dela viram spans filhos.
# ---------------------------------------------------------------------------
@observe()
def run_agent(user_message: str, session_id: str | None = None) -> str:
    # Propaga session_id e metadados para todos os spans filhos
    with propagate_attributes(session_id=session_id, metadata={"model": MODEL}):

        # MLflow: registra o experimento
        mlflow.set_experiment("agente-analise-texto")
        with mlflow.start_run(run_name=f"agent-{int(time.time())}"):
            mlflow.log_param("model", MODEL)
            mlflow.log_param("pergunta", user_message[:200])

            messages = [{"role": "user", "content": user_message}]
            total_input_tokens = 0
            total_output_tokens = 0
            tools_used = []
            iterations = 0
            start_time = time.time()
            final_text = ""

            # Loop agentico: continua até o modelo parar de chamar ferramentas
            while iterations < MAX_ITERATIONS:
                iterations += 1
                response = call_llm(messages)

                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

                # Modelo terminou — sem mais ferramentas
                if response.stop_reason == "end_turn":
                    final_text = next(
                        (b.text for b in response.content if b.type == "text"), ""
                    )
                    break

                # Modelo quer usar ferramentas
                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type != "tool_use":
                            continue

                        tools_used.append(block.name)
                        result = run_tool(block.name, block.input)

                        # Retorna o resultado da ferramenta para o modelo
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                    messages.append({"role": "user", "content": tool_results})

            # Registra métricas no MLflow
            elapsed = time.time() - start_time
            mlflow.log_metric("input_tokens", total_input_tokens)
            mlflow.log_metric("output_tokens", total_output_tokens)
            mlflow.log_metric("total_tokens", total_input_tokens + total_output_tokens)
            mlflow.log_metric("tool_calls", len(tools_used))
            mlflow.log_metric("iterations", iterations)
            mlflow.log_metric("latency_seconds", round(elapsed, 2))

    langfuse.flush()
    return final_text


# ---------------------------------------------------------------------------
# BÔNUS: LLM-as-a-Judge
# Avalia se o agente respondeu no mesmo idioma da pergunta
# ---------------------------------------------------------------------------
def judge_language(user_message: str, agent_response: str) -> dict:
    prompt = f"""Você é um avaliador de agentes de IA.

Pergunta do usuário: "{user_message}"
Resposta do agente: "{agent_response[:300]}"

Avalie se o agente respondeu NO MESMO IDIOMA da pergunta.

- Score 1.0: respondeu no idioma correto
- Score 0.0: respondeu em idioma diferente

Responda APENAS com JSON (sem mais nada):
{{"score": 0.0, "justificativa": "..."}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.content[0].text)


@observe()
def run_agent_with_judge(user_message: str, session_id: str | None = None) -> str:
    """Versão do agente com avaliação automática de idioma."""
    with propagate_attributes(session_id=session_id, metadata={"model": MODEL}):

        final_text = run_agent(user_message, session_id=session_id)

        # Avalia a resposta
        print(f"\n🔍 Avaliando idioma da resposta...")
        evaluation = judge_language(user_message, final_text)
        score = evaluation["score"]
        justificativa = evaluation["justificativa"]
        print(f"   Score: {score} | {justificativa}")

        # Envia score para o Langfuse
        trace_id = langfuse.get_current_trace_id()
        if trace_id:
            langfuse.create_score(
                trace_id=trace_id,
                name="language_consistency",
                value=score,
                comment=justificativa,
            )

    langfuse.flush()
    return final_text


# ---------------------------------------------------------------------------
# Casos de teste do exercício
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    perguntas = [
        #"Quantas palavras tem o texto: 'O céu é azul e o sol brilha forte hoje'?",
        "Em qual idioma está escrito: 'The quick brown fox jumps over the lazy dog'?",
        #"Analise o seguinte texto: 'Inteligência artificial está transformando o mundo.'",
    ]

    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{'='*60}")
        print(f"Pergunta {i}: {pergunta}")
        print("="*60)

        # Troca run_agent por run_agent_with_judge para o bônus
        resposta = run_agent(pergunta, session_id=f"exercicio-session-{i}")
        print(f"\nResposta:\n{resposta}")