"""
Parte 4: Script principal - Análise completa e exibição de resultados
"""
from topic_analyzer import get_top_topics, get_topic_examples
from external_search import search_external_articles
from topic_enrichment import enrich_topics_with_external_articles, save_articles_to_files


def display_results(top_topics: list[tuple[str, int]], enriched_data: dict):
    """
    Exibe os resultados de forma organizada
    """
    print("\n" + "="*60)
    print("📊 TÓPICOS MAIS FREQUENTES")
    print("="*60 + "\n")
    
    for i, (topic, count) in enumerate(top_topics, 1):
        print(f"{i:2d}. {topic:15s} ({count} ocorrências)")
    
    print("\n" + "="*60)
    print("📝 EXEMPLOS DE MENSAGENS DOS USUÁRIOS")
    print("="*60)
    
    for topic, count in top_topics[:3]:
        print(f"\n[{topic.upper()}]")
        examples = get_topic_examples(topic, limit=2)
        for i, example in enumerate(examples, 1):
            print(f"  {i}. \"{example[:70]}...\"")
    
    print("\n" + "="*60)
    print("🌐 ARTIGOS EXTERNOS ENCONTRADOS")
    print("="*60)
    
    for topic, articles in enriched_data.items():
        print(f"\n[{topic.upper()}]")
        
        if not articles:
            print("  ⚠️  Nenhum artigo encontrado")
            continue
        
        for i, article in enumerate(articles, 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     URL: {article['url']}")
            print(f"     Preview: {article['text'][:80]}...")
    
    print("\n" + "="*60)
    print("📈 ESTATÍSTICAS")
    print("="*60)
    
    total_topics = len(top_topics)
    total_occurrences = sum(count for _, count in top_topics)
    total_articles = sum(len(articles) for articles in enriched_data.values())
    
    print(f"\n  • Tópicos identificados: {total_topics}")
    print(f"  • Total de ocorrências: {total_occurrences}")
    print(f"  • Artigos externos encontrados: {total_articles}")
    print(f"  • Arquivos salvos: {len([a for a in enriched_data.values() if a])}")
    
    print("\n" + "="*60 + "\n")


def main():
    """
    Executa o fluxo completo de análise e enriquecimento
    """
    print("\n" + "="*60)
    print("🚀 EXERCÍCIO 8 - ENRIQUECIMENTO DE DADOS")
    print("="*60)
    print("\nFluxo:")
    print("  1. Analisar dados internos (conversations + feedbacks)")
    print("  2. Identificar tópicos mais frequentes")
    print("  3. Buscar artigos externos com Exa")
    print("  4. Salvar artigos como .txt")
    print("  5. Exibir resultados consolidados")
    print("\n" + "="*60 + "\n")
    
    input("Pressione ENTER para iniciar...")
    
    # Passo 1: Identificar tópicos frequentes
    print("\n" + "="*60)
    print("PASSO 1: Analisando dados internos...")
    print("="*60 + "\n")
    
    top_topics = get_top_topics(limit=5)
    
    print(f"✅ Identificados {len(top_topics)} tópicos frequentes\n")
    for i, (topic, count) in enumerate(top_topics, 1):
        print(f"  {i}. {topic}: {count} ocorrências")
    
    # Passo 2: Buscar artigos externos
    print("\n" + "="*60)
    print("PASSO 2: Buscando artigos externos...")
    print("="*60 + "\n")
    
    topics_list = [topic for topic, count in top_topics]
    enriched_data = enrich_topics_with_external_articles(topics_list, articles_per_topic=2)
    
    total_articles = sum(len(articles) for articles in enriched_data.values())
    print(f"\n✅ Encontrados {total_articles} artigos externos")
    
    # Passo 3: Salvar artigos
    print("\n" + "="*60)
    print("PASSO 3: Salvando artigos...")
    print("="*60 + "\n")
    
    save_articles_to_files(enriched_data)
    
    # Passo 4: Exibir resultados
    print("\n" + "="*60)
    print("PASSO 4: Exibindo resultados...")
    print("="*60)
    
    display_results(top_topics, enriched_data)
    
    print("✅ Processo concluído com sucesso!")
    print("\nArquivos salvos em: exemplos_exercicios/agentes/exe8/arquivos/")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        print("\nVerifique se:")
        print("  • O banco de dados está rodando")
        print("  • A chave EXA_API_KEY está configurada no .env")
        print("  • As bibliotecas necessárias estão instaladas")
