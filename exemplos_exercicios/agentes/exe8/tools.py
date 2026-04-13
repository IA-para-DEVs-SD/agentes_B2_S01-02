import os
import json
import re
from collections import Counter

import pandas as pd
from dotenv import load_dotenv
from exa_py import Exa

from db import get_engine

load_dotenv()

engine = get_engine()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVOS_DIR = os.path.join(BASE_DIR, "arquivos")


# --- Parte 1: Identificar tópicos frequentes ---

KEYWORD_MAP = {
    "login": ["login", "logar", "acessar", "senha", "conta", "acesso"],
    "pagamento": ["pagamento", "cartão", "compra", "recusado", "pagar"],
    "lentidão": ["lento", "lentidão", "demora", "carregar", "demorado"],
    "travamento": ["trava", "travando", "congela", "fechando", "fecha", "erro"],
    "entrega": ["entrega", "atrasou", "atrasada", "transportadora", "chegou"],
    "cancelamento": ["cancelar", "cancelamento", "cancelada", "assinatura"],
}


def get_top_topics() -> dict:
    """Analisa feedbacks e conversations para encontrar os tópicos mais frequentes."""
    feedbacks_df = pd.read_sql("SELECT feedback_text FROM feedbacks", engine)
    conversations_df = pd.read_sql("SELECT message FROM conversations WHERE speaker = 'client'", engine)

    all_texts = (
        feedbacks_df["feedback_text"].dropna().tolist()
        + conversations_df["message"].dropna().tolist()
    )

    topic_counter = Counter()

    for text in all_texts:
        text_lower = text.lower()
        matched_topics = set()
        for topic, keywords in KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    matched_topics.add(topic)
                    break
        for topic in matched_topics:
            topic_counter[topic] += 1

    top = topic_counter.most_common(6)

    return {
        "topics": [{"topic": t, "count": c} for t, c in top],
        "total_texts_analyzed": len(all_texts),
    }


# --- Parte 2: Busca externa com Exa ---

def search_external_articles(topic: str, num_results: int = 3) -> dict:
    """Busca artigos externos sobre um tópico usando Exa AI."""
    exa_key = os.getenv("EXA_API_KEY")
    if not exa_key:
        return {"topic": topic, "error": "EXA_API_KEY não definida", "articles": []}

    exa = Exa(exa_key)

    query = f"customer support {topic} troubleshooting guide"

    try:
        response = exa.search_and_contents(query, num_results=num_results, text=True)
    except Exception as e:
        return {"topic": topic, "error": str(e), "articles": []}

    articles = []
    for item in response.results:
        articles.append({
            "title": item.title or "",
            "url": item.url or "",
            "text": (item.text[:500] if item.text else ""),
        })

    return {"topic": topic, "articles": articles}


# --- Parte 3: Salvar artigos como .txt ---

def save_articles_to_files(topic: str, articles: list) -> dict:
    """Salva os artigos de um tópico como arquivos .txt na pasta exe8/arquivos."""
    os.makedirs(ARQUIVOS_DIR, exist_ok=True)

    # Gemini pode passar MapComposite objects, converter para dicts
    articles_list = [dict(a) for a in articles]

    saved_files = []
    topic_clean = re.sub(r"[^\w]", "_", topic.lower())

    for i, article in enumerate(articles_list, 1):
        filename = f"{topic_clean}_{i}.txt"
        filepath = os.path.join(ARQUIVOS_DIR, filename)

        content = (
            f"Tópico: {topic}\n"
            f"Título: {article.get('title', '')}\n"
            f"URL: {article.get('url', '')}\n"
            f"{'=' * 60}\n"
            f"{article.get('text', '')}\n"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        saved_files.append(filename)

    return {"topic": topic, "files_saved": saved_files, "directory": ARQUIVOS_DIR}


TOOL_MAP = {
    "get_top_topics": get_top_topics,
    "search_external_articles": search_external_articles,
    "save_articles_to_files": save_articles_to_files,
}
