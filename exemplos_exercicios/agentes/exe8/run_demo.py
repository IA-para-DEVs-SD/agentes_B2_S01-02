"""
Script de demonstração não-interativo do exercício 8
"""
from topic_analyzer import get_top_topics, get_topic_examples
from external_search import search_external_articles
from topic_enrichment import enrich_topics_with_external_articles, save_articles_to_files


def main():
    print("\n" + "="*60)
    print("🚀 EXERCÍCIO 8 - ENRIQUECIMENTO DE DADOS")
    print("="*60 + "\n")
    
    # Passo 1: Identificar tópicos frequentes
    print("PASSO 1: Analisando dados internos...")
    print("-" * 60 + "\n")
    
    top_topics = get_top_topics(limit=5)
    
    print(f"✅ Identificados {len(top_topics)} tópicos frequentes:\n")
    for i, (topic, count) in enumerate(top_topics, 1):
        print(f"  {i}. {topic:15s} - {count} ocorrências")
    
    # Passo 2: Buscar artigos externos
    print("\n" + "="*60)
    print("PASSO 2: Buscando artigos externos...")
    print("-" * 60 + "\n")
    
    topics_list = [topic for topic, count in top_topics]
    enriched_data = enrich_topics_with_external_articles(topics_list, articles_per_topic=2)
    
    total_articles = sum(len(articles) for articles in enriched_data.values())
    print(f"\n✅ Encontrados {total_articles} artigos externos")
    
    # Passo 3: Salvar artigos
    print("\n" + "="*60)
    print("PASSO 3: Salvando artigos...")
    print("-" * 60 + "\n")
    
    save_articles_to_files(enriched_data)
    
    # Passo 4: Exibir resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS CONSOLIDADOS")
    print("="*60)
    
    print("\n📝 Exemplos de mensagens dos usuários:")
    for topic, count in top_topics[:3]:
        print(f"\n[{topic.upper()}]")
        examples = get_topic_examples(topic, limit=2)
        for i, example in enumerate(examples, 1):
            print(f"  {i}. \"{example[:60]}...\"")
    
    print("\n" + "="*60)
    print("🌐 Artigos externos encontrados:")
    print("="*60)
    
    for topic, articles in list(enriched_data.items())[:3]:
        print(f"\n[{topic.upper()}]")
        if articles:
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article['title'][:60]}...")
                print(f"     {article['url']}")
        else:
            print("  ⚠️  Nenhum artigo encontrado")
    
    print("\n" + "="*60)
    print("📈 ESTATÍSTICAS FINAIS")
    print("="*60)
    
    total_occurrences = sum(count for _, count in top_topics)
    
    print(f"\n  • Tópicos identificados: {len(top_topics)}")
    print(f"  • Total de ocorrências: {total_occurrences}")
    print(f"  • Artigos externos: {total_articles}")
    print(f"  • Arquivos salvos: {len([a for a in enriched_data.values() if a])}")
    
    print("\n" + "="*60)
    print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\nArquivos salvos em: exemplos_exercicios/agentes/exe8/arquivos/")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nVerifique se:")
        print("  • O banco de dados está rodando")
        print("  • A chave EXA_API_KEY está configurada")
        print("\n")
