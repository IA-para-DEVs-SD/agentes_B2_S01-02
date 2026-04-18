"""
Parte 1: Identificar temas frequentes em conversas e feedbacks
"""
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import re

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"


def get_engine():
    return create_engine(DB_URL)


def extract_keywords(text: str) -> list[str]:
    """
    Extrai palavras-chave relevantes de um texto
    """
    if not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    
    # Palavras-chave relacionadas a problemas comuns
    keywords_map = {
        "login": ["login", "logar", "senha", "autenticação", "acesso"],
        "pagamento": ["pagamento", "payment", "pagar", "cartão", "compra", "cobrança"],
        "lentidão": ["lento", "lentidão", "demora", "travando", "congela", "performance"],
        "travamento": ["trava", "travando", "crash", "fecha sozinho", "erro"],
        "entrega": ["entrega", "atrasou", "atrasada", "delivery", "envio"],
        "cancelamento": ["cancelar", "cancelamento", "assinatura", "pedido"],
        "atendimento": ["atendimento", "suporte", "atender", "resposta"],
        "interface": ["interface", "layout", "design", "tela", "visual"],
        "bug": ["bug", "erro", "falha", "problema técnico"],
        "elogio": ["gostei", "adorei", "excelente", "ótimo", "bom"]
    }
    
    found_topics = []
    
    for topic, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_topics.append(topic)
                break  # Encontrou um, não precisa verificar os outros
    
    return found_topics


def get_top_topics(limit: int = 10) -> list[tuple[str, int]]:
    """
    Analisa conversations e feedbacks para encontrar os temas mais frequentes
    
    Returns:
        Lista de tuplas (tema, contagem) ordenada por frequência
    """
    engine = get_engine()
    
    # Busca conversas
    conversations_df = pd.read_sql("SELECT message FROM conversations", engine)
    
    # Busca feedbacks
    feedbacks_df = pd.read_sql("SELECT feedback_text FROM feedbacks", engine)
    
    # Extrai tópicos de todas as mensagens
    all_topics = []
    
    for message in conversations_df['message']:
        topics = extract_keywords(message)
        all_topics.extend(topics)
    
    for feedback in feedbacks_df['feedback_text']:
        topics = extract_keywords(feedback)
        all_topics.extend(topics)
    
    # Conta frequência
    topic_counts = Counter(all_topics)
    
    # Retorna os mais frequentes
    return topic_counts.most_common(limit)


def get_topic_examples(topic: str, limit: int = 3) -> list[str]:
    """
    Retorna exemplos de mensagens relacionadas a um tópico
    """
    engine = get_engine()
    
    # Busca conversas
    conversations_df = pd.read_sql("SELECT message FROM conversations", engine)
    feedbacks_df = pd.read_sql("SELECT feedback_text FROM feedbacks", engine)
    
    examples = []
    
    # Busca em conversas
    for message in conversations_df['message']:
        if topic in extract_keywords(message):
            examples.append(message)
            if len(examples) >= limit:
                break
    
    # Se não encontrou suficiente, busca em feedbacks
    if len(examples) < limit:
        for feedback in feedbacks_df['feedback_text']:
            if topic in extract_keywords(feedback):
                examples.append(feedback)
                if len(examples) >= limit:
                    break
    
    return examples[:limit]


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 ANÁLISE DE TÓPICOS FREQUENTES")
    print("="*60 + "\n")
    
    topics = get_top_topics(limit=10)
    
    print(f"Total de tópicos identificados: {len(topics)}\n")
    
    print("Tópicos mais frequentes:")
    for i, (topic, count) in enumerate(topics, 1):
        print(f"{i:2d}. {topic:15s} ({count} ocorrências)")
    
    print("\n" + "="*60)
    print("📝 EXEMPLOS DE MENSAGENS")
    print("="*60 + "\n")
    
    # Mostra exemplos dos 3 primeiros tópicos
    for topic, count in topics[:3]:
        print(f"\n[{topic.upper()}]")
        examples = get_topic_examples(topic, limit=2)
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example[:80]}...")
    
    print("\n" + "="*60 + "\n")
