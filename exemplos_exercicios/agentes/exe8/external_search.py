"""
Parte 2: Buscar artigos externos usando Exa
"""
import os
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()

EXA_API_KEY = os.getenv("EXA_API_KEY")


def get_exa_client():
    if not EXA_API_KEY or EXA_API_KEY == "your-exa-api-key-here":
        raise ValueError("EXA_API_KEY não configurada no arquivo .env")
    return Exa(EXA_API_KEY)


def search_external_articles(topic: str, num_results: int = 3) -> list[dict]:
    """
    Busca artigos externos relacionados a um tópico
    
    Args:
        topic: Tópico a ser pesquisado
        num_results: Número de resultados desejados
    
    Returns:
        Lista de dicionários com informações dos artigos
    """
    exa = get_exa_client()
    
    # Monta query otimizada para o tópico
    query_map = {
        "login": "login issues troubleshooting password reset authentication",
        "pagamento": "payment problems troubleshooting failed transactions",
        "lentidão": "slow performance optimization speed issues",
        "travamento": "app crashes freezing troubleshooting",
        "entrega": "delivery problems late shipping issues",
        "cancelamento": "cancellation refund process",
        "atendimento": "customer support best practices",
        "interface": "user interface design usability",
        "bug": "bug fixing software issues troubleshooting",
        "elogio": "customer satisfaction positive feedback"
    }
    
    query = query_map.get(topic, f"{topic} troubleshooting solutions")
    
    try:
        response = exa.search_and_contents(
            query,
            num_results=num_results,
            text=True
        )
        
        articles = []
        for item in response.results:
            articles.append({
                "topic": topic,
                "title": item.title,
                "url": item.url,
                "text": item.text[:500] if item.text else ""
            })
        
        return articles
    
    except Exception as e:
        print(f"Erro ao buscar artigos para '{topic}': {e}")
        return []


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 TESTE DE BUSCA EXTERNA")
    print("="*60 + "\n")
    
    test_topics = ["login", "pagamento", "lentidão"]
    
    for topic in test_topics:
        print(f"\n[{topic.upper()}]")
        print("-" * 60)
        
        articles = search_external_articles(topic, num_results=2)
        
        if articles:
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   URL: {article['url']}")
                print(f"   Preview: {article['text'][:100]}...")
        else:
            print("   Nenhum artigo encontrado")
    
    print("\n" + "="*60 + "\n")
