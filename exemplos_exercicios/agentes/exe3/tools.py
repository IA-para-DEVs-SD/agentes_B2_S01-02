import os
import json
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5455")
DB_URL = f"postgresql+psycopg2://admin:admin123@{DB_HOST}:{DB_PORT}/suporte_ai"
engine = create_engine(DB_URL)

# Armazena os resultados das análises individuais
analyzed_feedbacks = []


def get_all_feedbacks() -> dict:
    """Lê todos os feedbacks da tabela feedbacks no banco."""
    query = text("""
        SELECT feedback_id, feedback_text, created_at, channel
        FROM feedbacks
        ORDER BY feedback_id
    """)

    with engine.begin() as conn:
        rows = conn.execute(query).mappings().all()

    feedbacks = [
        {
            "feedback_id": row["feedback_id"],
            "feedback_text": row["feedback_text"],
            "created_at": str(row["created_at"]),
            "channel": row["channel"],
        }
        for row in rows
    ]

    return {"total": len(feedbacks), "feedbacks": feedbacks}


def classify_feedback(feedback_id: int, feedback_text: str, categoria: str, sentimento: str, resumo: str) -> dict:
    """Salva a classificação de um feedback individual na lista de resultados."""
    result = {
        "feedback_id": feedback_id,
        "feedback_text": feedback_text,
        "categoria": categoria,
        "sentimento": sentimento,
        "resumo": resumo,
    }
    analyzed_feedbacks.append(result)
    return {"status": "ok", "feedback_id": feedback_id, "saved": True}


def generate_report(principais_pontos: list[str]) -> dict:
    """Gera o relatório consolidado a partir dos feedbacks já analisados."""
    total = len(analyzed_feedbacks)

    categorias = {}
    sentimentos = {}

    for fb in analyzed_feedbacks:
        cat = fb["categoria"]
        sent = fb["sentimento"]
        categorias[cat] = categorias.get(cat, 0) + 1
        sentimentos[sent] = sentimentos.get(sent, 0) + 1

    report = {
        "total_feedbacks": total,
        "categorias": categorias,
        "sentimentos": sentimentos,
        "principais_pontos": principais_pontos,
    }

    return report


def save_results_to_file(report_json: str, feedbacks_json: str) -> dict:
    """Salva o relatório e os feedbacks analisados em arquivos JSON locais."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    report_path = os.path.join(base_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_json)

    feedbacks_path = os.path.join(base_dir, "feedbacks_analyzed.json")
    with open(feedbacks_path, "w", encoding="utf-8") as f:
        f.write(feedbacks_json)

    return {
        "status": "ok",
        "files_saved": [report_path, feedbacks_path],
    }


TOOL_MAP = {
    "get_all_feedbacks": get_all_feedbacks,
    "classify_feedback": classify_feedback,
    "generate_report": generate_report,
    "save_results_to_file": save_results_to_file,
}
