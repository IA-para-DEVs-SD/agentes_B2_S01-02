import json
from sqlalchemy import text as sql_text

from db import get_engine
from guardrails import validate_note

engine = get_engine()


def validate_internal_note(note_text: str) -> dict:
    """Valida uma internal note aplicando guardrails de PII e linguagem negativa."""
    return validate_note(note_text)


def save_internal_note(ticket_id: int, note_text: str, note_status: str, blocked_reason: str = None) -> dict:
    """Salva a internal note no banco com o status da validação."""
    query = sql_text("""
        INSERT INTO internal_notes (ticket_id, note_text, note_status, blocked_reason)
        VALUES (:ticket_id, :note_text, :note_status, :blocked_reason)
        RETURNING id
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {
            "ticket_id": ticket_id,
            "note_text": note_text,
            "note_status": note_status,
            "blocked_reason": blocked_reason,
        })
        note_id = result.scalar()

    return {"note_id": note_id, "status": note_status, "saved": True}


def list_internal_notes(ticket_id: int = None) -> dict:
    """Lista internal notes salvas, opcionalmente filtradas por ticket_id."""
    if ticket_id:
        query = sql_text("SELECT * FROM internal_notes WHERE ticket_id = :tid ORDER BY created_at DESC")
        params = {"tid": ticket_id}
    else:
        query = sql_text("SELECT * FROM internal_notes ORDER BY created_at DESC LIMIT 20")
        params = {}

    with engine.begin() as conn:
        rows = conn.execute(query, params).mappings().all()

    notes = [
        {
            "id": row["id"],
            "ticket_id": row["ticket_id"],
            "note_text": row["note_text"],
            "note_status": row["note_status"],
            "blocked_reason": row["blocked_reason"],
            "created_at": str(row["created_at"]),
        }
        for row in rows
    ]

    return {"total": len(notes), "notes": notes}


TOOL_MAP = {
    "validate_internal_note": validate_internal_note,
    "save_internal_note": save_internal_note,
    "list_internal_notes": list_internal_notes,
}
