from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

# =========================
# CONFIG
# =========================
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"
engine = create_engine(DB_URL)


# =========================
# 1. GET CONVERSATION
# =========================
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
        return {"found": False, "conversation_text": ""}

    conversation_text = "\n".join(
        f"{row['speaker']}: {row['message']}"
        for row in rows
    )

    return {"found": True, "conversation_text": conversation_text}


# =========================
# 2. CLASSIFY CATEGORY
# =========================
def classify_category_prompt(conversation_text: str) -> dict:
    prompt = f"""
Classifique a conversa em uma categoria:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda JSON:
{{ "categoria": "..." }}

Conversa:
{conversation_text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    text_resp = response.content[0].text.strip()

    if text_resp.startswith("```"):
        text_resp = text_resp.split("\n", 1)[1].replace("```", "").strip()

    return json.loads(text_resp)


# =========================
# 3. SEARCH KB (RAG SIMPLES)
# =========================
def search_kb_simple(query_text: str, category: str) -> dict:
    sql = """
        SELECT title, content
        FROM knowledge_base
        WHERE category = :category
        AND (
            LOWER(title) LIKE LOWER(:q)
            OR LOWER(content) LIKE LOWER(:q)
        )
        LIMIT 3
    """

    with engine.begin() as conn:
        rows = conn.execute(
            text(sql),
            {"q": f"%{query_text}%", "category": category}
        ).mappings().all()

    return [dict(r) for r in rows]


# =========================
# 4. FINAL AGENT
# =========================
def generate_final_answer(ticket_id: int, new_message: str):
    conversation = get_ticket_conversation(ticket_id)

    if not conversation["found"]:
        return {"erro": "sem histórico"}

    conversation_text = conversation["conversation_text"]

    # categoria
    categoria = classify_category_prompt(conversation_text)["categoria"]

    # busca KB
    kb_docs = search_kb_simple(new_message, categoria)

    kb_context = "\n".join([
        f"- {d['title']}: {d['content']}"
        for d in kb_docs
    ]) if kb_docs else "Nenhum artigo encontrado"

    prompt = f"""
Você é suporte.

Explique:
- problema
- resumo
- use base de conhecimento
- próxima ação

Responda JSON:
{{
 "categoria": "...",
 "resumo": "...",
 "acao": "..."
}}

Histórico:
{conversation_text}

Nova mensagem:
{new_message}

Base de conhecimento:
{kb_context}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    text_resp = response.content[0].text.strip()

    if text_resp.startswith("```"):
        text_resp = text_resp.split("\n", 1)[1].replace("```", "").strip()

    result = json.loads(text_resp)

    result["kb"] = kb_docs
    return result


# =========================
# RUN
# =========================
if __name__ == "__main__":
    result = generate_final_answer(
        ticket_id=1001,
        new_message="Agora apareceu que minha conta está bloqueada"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))