from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
import anthropic
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

load_dotenv()

# =========================================================
# CONFIG
# =========================================================

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"
engine = create_engine(DB_URL)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = "claude-sonnet-4-6"

QDRANT_COLLECTION = "kb_chunks"
qdrant = QdrantClient(host="localhost", port=6333, check_compatibility=False)

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
embed_model = SentenceTransformer(EMBED_MODEL_NAME)


# =========================================================
# SHARED HELPERS
# =========================================================

def call_claude_json(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> dict:
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        temperature=0.1,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    response_text = "\n".join(text_parts).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(response_text[start:end + 1])
        raise ValueError(f"Resposta não veio em JSON válido: {response_text}")


def embed(text: str) -> list[float]:
    return embed_model.encode(text).tolist()


# =========================================================
# TOOL 1: GET CONVERSATION
# =========================================================

def get_ticket_conversation(ticket_id: int) -> dict:
    query = text("""
        SELECT speaker, message, timestamp, ticket_status
        FROM conversations
        WHERE ticket_id = :ticket_id
        ORDER BY timestamp
    """)

    with engine.begin() as conn:
        rows = conn.execute(query, {"ticket_id": ticket_id}).mappings().all()

    if not rows:
        return {
            "ticket_id": ticket_id,
            "found": False,
            "conversation_text": ""
        }

    conversation_text = "\n".join(
        f"{row['speaker']}: {row['message']}"
        for row in rows
    )

    return {
        "ticket_id": ticket_id,
        "found": True,
        "conversation_text": conversation_text
    }


# =========================================================
# TOOL 2: CLASSIFICATION
# =========================================================

def classify_category_prompt(conversation_text: str) -> dict:
    system_prompt = """
Você é um classificador de tickets de suporte.
Responda apenas em JSON válido.
"""

    user_prompt = f"""
Classifique a conversa em apenas uma das categorias abaixo:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com:
- categoria

Conversa:
{conversation_text}
"""

    try:
        result = call_claude_json(system_prompt, user_prompt)

        categoria = result.get("categoria", "outros")
        valid = ["acesso", "pagamento", "entrega", "cancelamento", "conta", "outros"]
        if categoria not in valid:
            categoria = "outros"

        return {
            "categoria": categoria,
            "metodo": "llm_claude"
        }

    except Exception as e:
        print("Erro classify_category_prompt:", e)
        return {
            "categoria": "outros",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 3: ANALYZE WITHOUT HISTORY
# =========================================================

def analyze_without_history(message: str) -> dict:
    system_prompt = """
Você é um analista de suporte ao cliente.
Responda apenas em JSON válido.
"""

    user_prompt = f"""
Analise apenas a mensagem abaixo, SEM considerar histórico anterior.

Sua tarefa é:
1. Identificar a categoria do problema
2. Resumir o problema
3. Sugerir a primeira ação
4. Explicitar que não há histórico

Categorias possíveis:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com:
- categoria
- resumo
- acao_inicial
- observacao

Mensagem:
{message}
"""

    try:
        result = call_claude_json(system_prompt, user_prompt)

        categoria = result.get("categoria", "outros")
        valid = ["acesso", "pagamento", "entrega", "cancelamento", "conta", "outros"]
        if categoria not in valid:
            categoria = "outros"

        return {
            "categoria": categoria,
            "resumo": result.get("resumo", "Não foi possível resumir a mensagem."),
            "acao_inicial": result.get("acao_inicial", "Solicitar mais informações ao cliente."),
            "observacao": result.get("observacao", "Análise sem histórico."),
            "metodo": "llm_sem_historico_claude"
        }

    except Exception as e:
        print("Erro analyze_without_history:", e)

        return {
            "categoria": "outros",
            "resumo": "Não foi possível analisar a mensagem isoladamente.",
            "acao_inicial": "Solicitar mais informações ao cliente.",
            "observacao": "Análise sem histórico (fallback por erro).",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 4: ANALYZE WITH HISTORY
# =========================================================

def analyze_with_history(conversation_text: str, latest_message: str) -> dict:
    system_prompt = """
Você é um analista de suporte ao cliente.
Responda apenas em JSON válido.
"""

    user_prompt = f"""
Analise o caso usando o histórico abaixo e a mensagem mais recente do cliente.

Sua tarefa é:
1. Identificar a categoria do problema
2. Resumir o caso considerando o histórico
3. Sugerir a próxima ação
4. Dizer se o histórico ajudou na análise

Categorias possíveis:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com:
- categoria
- resumo
- proxima_acao
- observacao

Histórico:
{conversation_text}

Mensagem mais recente:
{latest_message}
"""

    try:
        result = call_claude_json(system_prompt, user_prompt)

        categoria = result.get("categoria", "outros")
        valid = ["acesso", "pagamento", "entrega", "cancelamento", "conta", "outros"]
        if categoria not in valid:
            categoria = "outros"

        return {
            "categoria": categoria,
            "resumo": result.get("resumo", "Não foi possível resumir o caso com histórico."),
            "proxima_acao": result.get("proxima_acao", "Validar contexto anterior e solicitar confirmação ao cliente."),
            "observacao": result.get("observacao", "Análise com histórico."),
            "metodo": "llm_com_historico_claude"
        }

    except Exception as e:
        print("Erro analyze_with_history:", e)

        return {
            "categoria": "outros",
            "resumo": "Não foi possível analisar com histórico.",
            "proxima_acao": "Solicitar mais informações ao cliente.",
            "observacao": "Análise com histórico (fallback por erro).",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 5: FOLLOW-UP
# =========================================================

def detect_followup(conversation_text: str) -> dict:
    lines = [line.strip() for line in conversation_text.split("\n") if line.strip()]

    if not lines:
        return {
            "precisa_followup": False,
            "motivo": "sem mensagens",
            "ultima_mensagem_foi_do_atendente": False
        }

    last_line = lines[-1].lower()
    ultima_mensagem_foi_do_atendente = last_line.startswith("atendente:")

    return {
        "precisa_followup": ultima_mensagem_foi_do_atendente,
        "motivo": (
            "última mensagem foi do atendente"
            if ultima_mensagem_foi_do_atendente
            else "última mensagem foi do cliente"
        ),
        "ultima_mensagem_foi_do_atendente": ultima_mensagem_foi_do_atendente
    }


# =========================================================
# TOOL 6: KB SEARCH
# =========================================================

def route_kb_name(categoria: str) -> str | None:
    mapping = {
        "acesso": "support_kb",
        "pagamento": "support_kb",
        "entrega": "support_kb",
        "cancelamento": "policy_kb",
        "conta": "product_faq",
    }
    return mapping.get(categoria)


def search_kb(query: str, kb_name: str | None = None, limit: int = 3, min_score: float = 0.12) -> list[dict]:
    query_vector = embed(query)

    query_filter = None
    if kb_name:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="kb_name",
                    match=MatchValue(value=kb_name),
                )
            ]
        )

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
    ).points

    hits = []
    for r in results:
        if r.score < min_score:
            continue

        payload = r.payload or {}
        hits.append({
            "kb_name": payload.get("kb_name"),
            "title": payload.get("title"),
            "chunk_order": payload.get("chunk_order"),
            "content": payload.get("content"),
            "metadata": payload.get("metadata", {}),
            "score": float(r.score),
        })

    return hits


# =========================================================
# TOOL 7: FINAL RESPONSE GENERATION
# =========================================================

def generate_final_answer(
    message: str,
    categoria: str,
    analysis: dict,
    kb_hits: list[dict],
    followup: dict | None = None,
    conversation_text: str | None = None,
) -> dict:
    system_prompt = """
Você é um agente de suporte ao cliente.
Gere uma resposta clara, útil e objetiva.
Responda apenas em JSON válido.
"""

    kb_context = "\n".join(
        [
            f"- [{hit['kb_name']}] {hit['title']} (score={hit['score']:.3f}): {hit['content']}"
            for hit in kb_hits
        ]
    ) or "Nenhum contexto relevante encontrado na base."

    user_prompt = f"""
Monte uma resposta final para o cliente com base nos dados abaixo.

Mensagem atual:
{message}

Categoria:
{categoria}

Análise:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

Follow-up:
{json.dumps(followup, ensure_ascii=False, indent=2) if followup else "Não aplicável"}

Histórico:
{conversation_text if conversation_text else "Não disponível"}

Contexto recuperado da base:
{kb_context}

Responda em JSON com:
- resposta_cliente
- resumo_interno
- confianca
- usou_base_conhecimento

A resposta ao cliente deve:
- ser cordial
- sugerir próximo passo
- não inventar informações
- mencionar limites quando não houver contexto suficiente
"""

    try:
        result = call_claude_json(system_prompt, user_prompt, max_tokens=1200)

        return {
            "resposta_cliente": result.get("resposta_cliente", "Não foi possível gerar resposta ao cliente."),
            "resumo_interno": result.get("resumo_interno", "Sem resumo interno."),
            "confianca": result.get("confianca", "media"),
            "usou_base_conhecimento": result.get("usou_base_conhecimento", bool(kb_hits)),
        }

    except Exception as e:
        print("Erro generate_final_answer:", e)
        return {
            "resposta_cliente": "Entendi seu caso. Vou precisar de mais informações para orientar o próximo passo com segurança.",
            "resumo_interno": "Falha ao gerar resposta final com LLM.",
            "confianca": "baixa",
            "usou_base_conhecimento": bool(kb_hits),
        }


# =========================================================
# TOOL 8: LOG EXECUTION
# =========================================================

def save_agent_run(agent_name: str, ticket_id: int | None, input_text: str, output_text: dict) -> None:
    query = text("""
        INSERT INTO agent_runs (
            agent_name,
            ticket_id,
            input_text,
            output_text
        )
        VALUES (
            :agent_name,
            :ticket_id,
            :input_text,
            :output_text
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "agent_name": agent_name,
                "ticket_id": ticket_id,
                "input_text": input_text,
                "output_text": json.dumps(output_text, ensure_ascii=False)
            }
        )


# =========================================================
# ORCHESTRATOR
# =========================================================

def analyze_ticket_pipeline(ticket_id: int | None, message: str) -> dict:
    conversation = None
    followup = None
    analysis = None
    categoria = "outros"
    modo = "sem_historico"

    if ticket_id is not None:
        conversation = get_ticket_conversation(ticket_id)

        if conversation["found"] and conversation["conversation_text"]:
            modo = "com_historico"
            followup = detect_followup(conversation["conversation_text"])
            analysis = analyze_with_history(
                conversation_text=conversation["conversation_text"],
                latest_message=message
            )
            categoria = analysis["categoria"]

    if analysis is None:
        analysis = analyze_without_history(message)
        categoria = analysis["categoria"]

    kb_name = route_kb_name(categoria)
    kb_hits = search_kb(
        query=f"{categoria}. {message}",
        kb_name=kb_name,
        limit=3,
        min_score=0.12
    )

    final_answer = generate_final_answer(
        message=message,
        categoria=categoria,
        analysis=analysis,
        kb_hits=kb_hits,
        followup=followup,
        conversation_text=conversation["conversation_text"] if conversation and conversation["found"] else None,
    )

    pipeline_result = {
        "ticket_id": ticket_id,
        "modo": modo,
        "categoria": categoria,
        "kb_escolhida": kb_name,
        "analysis": analysis,
        "followup": followup,
        "kb_hits": kb_hits,
        "final_answer": final_answer,
    }

    save_agent_run(
        agent_name="support_pipeline_claude",
        ticket_id=ticket_id,
        input_text=message,
        output_text=pipeline_result
    )

    return pipeline_result


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    print("\n==============================")
    print("PIPELINE COMPLETO - SEM HISTÓRICO")
    print("==============================\n")

    result_1 = analyze_ticket_pipeline(
        ticket_id=None,
        message="me ajuda? eu estou sem acesso à minha conta, tentei logar, nada funciona"
    )
    print(json.dumps(result_1, indent=2, ensure_ascii=False))

    print("\n==============================")
    print("PIPELINE COMPLETO - COM HISTÓRICO")
    print("==============================\n")

    result_2 = analyze_ticket_pipeline(
        ticket_id=1001,
        message="ainda não consegui resolver meu acesso"
    )
    print(json.dumps(result_2, indent=2, ensure_ascii=False))