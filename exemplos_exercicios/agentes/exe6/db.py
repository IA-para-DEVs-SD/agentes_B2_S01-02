"""
Módulo de acesso ao banco de dados para internal notes
"""
from sqlalchemy import create_engine, text
from datetime import datetime

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"


def get_engine():
    return create_engine(DB_URL)


def save_internal_note(ticket_id: int, note_text: str, note_status: str, blocked_reason: str = None):
    """
    Salva uma internal note no banco de dados
    
    Args:
        ticket_id: ID do ticket
        note_text: Texto da nota (original ou sanitizado)
        note_status: Status da nota ('saved', 'sanitized_and_saved', 'blocked')
        blocked_reason: Motivo do bloqueio (se aplicável)
    """
    engine = get_engine()
    
    query = text("""
        INSERT INTO internal_notes (ticket_id, note_text, note_status, blocked_reason, created_at)
        VALUES (:ticket_id, :note_text, :note_status, :blocked_reason, :created_at)
        RETURNING id
    """)
    
    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "ticket_id": ticket_id,
                "note_text": note_text,
                "note_status": note_status,
                "blocked_reason": blocked_reason,
                "created_at": datetime.now()
            }
        )
        note_id = result.fetchone()[0]
    
    return note_id


def get_all_notes():
    """
    Retorna todas as internal notes do banco
    """
    engine = get_engine()
    
    query = text("""
        SELECT id, ticket_id, note_text, note_status, blocked_reason, created_at
        FROM internal_notes
        ORDER BY created_at DESC
    """)
    
    with engine.begin() as conn:
        rows = conn.execute(query).mappings().all()
    
    return [dict(row) for row in rows]


def get_notes_by_status(status: str):
    """
    Retorna internal notes filtradas por status
    """
    engine = get_engine()
    
    query = text("""
        SELECT id, ticket_id, note_text, note_status, blocked_reason, created_at
        FROM internal_notes
        WHERE note_status = :status
        ORDER BY created_at DESC
    """)
    
    with engine.begin() as conn:
        rows = conn.execute(query, {"status": status}).mappings().all()
    
    return [dict(row) for row in rows]
