import os
import json
from sqlalchemy import create_engine, text
from agents import function_tool

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "suporte_ai")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

@function_tool
def get_ticket_conversation(ticket_id: int) -> str:
    """Busca informações de um ticket e retorna a conversa em JSON."""
    print(f"[tool] ticket_id recebido: {ticket_id}")
    print(f"[tool] conectando em: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT ticket_id, speaker, message, timestamp, ticket_status
                    FROM conversations
                    WHERE ticket_id = :ticket_id
                    ORDER BY timestamp
                """),
                {"ticket_id": ticket_id}
            )
            rows = [dict(row._mapping) for row in result.fetchall()]
            print(f"[tool] linhas encontradas: {len(rows)}")

        return json.dumps(rows, ensure_ascii=False, default=str)

    except Exception as e:
        print(f"[tool] erro: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)