"""
Parte 3: Enriquecer tópicos com artigos externos
"""
import os
from topic_analyzer import get_top_topics
from external_search import search_external_articles


def enrich_topics_with_external_articles(topics: list[str], articles_per_topic: int = 3) -> dict:
    """
    Para cada tópico, busca artigos externos
    
    Args:
        topics: Lista de tópicos a serem enriquecidos
        articles_per_topic: Número de artigos por tópico
    
    Returns:
        Dicionário com tópicos e seus artigos
    """
    enriched_data = {}
    
    for topic in topics:
        print(f"🔍 Buscando artigos para: {topic}...")
        articles = search_external_articles(topic, num_results=articles_per_topic)
        enriched_data[topic] = articles
    
    return enriched_data


def save_articles_to_files(enriched_data: dict, output_dir: str = "exemplos_exercicios/agentes/exe8/arquivos"):
    """
    Salva os artigos como arquivos .txt
    
    Args:
        enriched_data: Dicionário com tópicos e artigos
        output_dir: Diretório de saída
    """
    # Cria diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    for topic, articles in enriched_data.items():
        if not articles:
            continue
        
        filename = os.path.join(output_dir, f"{topic}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"TÓPICO: {topic.upper()}\n")
            f.write("="*60 + "\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"ARTIGO {i}\n")
                f.write("-"*60 + "\n")
                f.write(f"Título: {article['title']}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"\nConteúdo:\n{article['text']}\n")
                f.write("\n" + "="*60 + "\n\n")
        
        print(f"✅ Salvo: {filename}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔄 ENRIQUECIMENTO DE TÓPICOS")
    print("="*60 + "\n")
    
    # Pega os top 5 tópicos
    top_topics = get_top_topics(limit=5)
    topics_list = [topic for topic, count in top_topics]
    
    print("Tópicos a serem enriquecidos:")
    for i, (topic, count) in enumerate(top_topics, 1):
        print(f"  {i}. {topic} ({count} ocorrências)")
    
    print("\n" + "="*60)
    print("🔍 BUSCANDO ARTIGOS EXTERNOS")
    print("="*60 + "\n")
    
    # Enriquece com artigos externos
    enriched_data = enrich_topics_with_external_articles(topics_list, articles_per_topic=2)
    
    print("\n" + "="*60)
    print("💾 SALVANDO ARTIGOS")
    print("="*60 + "\n")
    
    # Salva em arquivos
    save_articles_to_files(enriched_data)
    
    print("\n" + "="*60)
    print("✅ PROCESSO CONCLUÍDO")
    print("="*60)
    print(f"\nTotal de tópicos processados: {len(enriched_data)}")
    total_articles = sum(len(articles) for articles in enriched_data.values())
    print(f"Total de artigos salvos: {total_articles}")
    print(f"\nArquivos salvos em: exemplos_exercicios/agentes/exe8/arquivos/")
    print("\n")
