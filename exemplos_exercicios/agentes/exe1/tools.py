import os
from sqlalchemy import create_engine, text
import json

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"postgresql+psycopg2://admin:admin123@{DB_HOST}:5455/suporte_ai"
engine = create_engine(DB_URL)


def get_ticket_conversation(ticket_id: int) -> str:
    query = text("""
        SELECT speaker, message, timestamp, ticket_status
        FROM conversations
        WHERE ticket_id = :ticket_id
        ORDER BY timestamp
    """)

    with engine.begin() as conn:
        rows = conn.execute(query, {"ticket_id": ticket_id}).mappings().all()

    if not rows:
        return ""

    conversation = "\n".join(
        f"{row['speaker']}: {row['message']}"
        for row in rows
    )

    return conversation


def classify_category(conversation: str) -> dict:
    text_lower = conversation.lower()

    if "login" in text_lower or "senha" in text_lower:
        categoria = "login"
    elif "pagamento" in text_lower or "cartão" in text_lower:
        categoria = "pagamento"
    elif "entrega" in text_lower:
        categoria = "entrega"
    elif "cancelar" in text_lower:
        categoria = "cancelamento"
    else:
        categoria = "outros"

    return {
        "categoria": categoria,
        "metodo": "regra_simples"
    }


def detect_followup(conversation: str) -> dict:
    lines = conversation.strip().split("\n")

    if not lines or conversation == "":
        return {
            "precisa_followup": False,
            "motivo": "sem mensagens"
        }

    last_line = lines[-1].lower()

    if last_line.startswith("atendente"):
        return {
            "precisa_followup": True,
            "motivo": "última mensagem foi do atendente"
        }

    return {
        "precisa_followup": False,
        "motivo": "cliente respondeu por último"
    }


def save_agent_run(agent_name: str, ticket_id: int, input_text: str, output_text: dict) -> None:
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