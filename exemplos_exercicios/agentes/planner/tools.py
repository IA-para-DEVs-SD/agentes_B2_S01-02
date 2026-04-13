import json
import psycopg2
from agents import function_tool

@function_tool
def load_backlog() -> str:
    """Carrega o backlog do Postgres e retorna JSON."""
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="suporte_ai",
        user="admin",
        password="admin123",
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT titulo, responsavel, status, prioridade,
               story_points, dias_em_aberto, bugs_relacionados, sprint
        FROM backlog
    """)
    rows = cur.fetchall()
    conn.close()

    cols = [
        "titulo", "responsavel", "status", "prioridade",
        "story_points", "dias_em_aberto", "bugs_relacionados", "sprint"
    ]

    data = [dict(zip(cols, row)) for row in rows]
    return json.dumps(data, ensure_ascii=False)