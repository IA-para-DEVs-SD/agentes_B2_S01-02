"""
Exemplo de RAG (Retrieval-Augmented Generation) usando PostgreSQL com pgvector

Este script demonstra como:
1. Conectar ao PostgreSQL
2. Gerar embeddings usando OpenAI
3. Armazenar documentos com embeddings
4. Fazer busca por similaridade (RAG)
5. Usar o resultado com LLM
"""

import os
import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "password": "postgres123"
}

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Gera embedding para um texto usando OpenAI
    
    Args:
        text: Texto para gerar embedding
        model: Modelo de embedding (text-embedding-3-small gera vetores de 1536 dimensões)
    
    Returns:
        Lista de floats representando o vetor embedding
    """
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


def insert_document_with_embedding(conn, content: str, metadata: dict = None):
    """
    Insere um documento com seu embedding no banco de dados
    
    Args:
        conn: Conexão com o PostgreSQL
        content: Conteúdo textual do documento
        metadata: Metadados opcionais em formato dict
    """
    # Gerar embedding para o conteúdo
    embedding = get_embedding(content)
    
    # Inserir no banco
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents (content, metadata, embedding)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (content, metadata, embedding)
    )
    doc_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    
    print(f"✓ Documento inserido com ID: {doc_id}")
    return doc_id


def search_similar_documents(conn, query: str, limit: int = 3):
    """
    Busca documentos similares usando busca vetorial
    
    Args:
        conn: Conexão com o PostgreSQL
        query: Query de busca (será convertida em embedding)
        limit: Número máximo de resultados
    
    Returns:
        Lista de documentos similares com suas similaridades
    """
    # Gerar embedding para a query
    query_embedding = get_embedding(query)
    
    # Buscar documentos similares
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, content, metadata, similarity
        FROM match_documents(%s::vector, %s)
        """,
        (query_embedding, limit)
    )
    results = cursor.fetchall()
    cursor.close()
    
    return results


def rag_query(conn, user_query: str, model: str = "gpt-4o-mini"):
    """
    Executa uma query RAG completa:
    1. Busca documentos relevantes
    2. Usa como contexto para LLM
    3. Gera resposta baseada no contexto
    
    Args:
        conn: Conexão com o PostgreSQL
        user_query: Pergunta do usuário
        model: Modelo LLM da OpenAI
    
    Returns:
        Resposta do LLM baseada nos documentos encontrados
    """
    print(f"\n🔍 Buscando documentos relevantes para: '{user_query}'")
    
    # 1. Buscar documentos similares
    similar_docs = search_similar_documents(conn, user_query, limit=3)
    
    if not similar_docs:
        return "Nenhum documento relevante encontrado."
    
    # 2. Montar contexto a partir dos documentos
    context = "\n\n".join([
        f"Documento {i+1} (similaridade: {doc[3]:.2%}):\n{doc[1]}"
        for i, doc in enumerate(similar_docs)
    ])
    
    print(f"\n📚 Documentos encontrados: {len(similar_docs)}")
    for i, doc in enumerate(similar_docs):
        print(f"  {i+1}. Similaridade: {doc[3]:.2%}")
    
    # 3. Criar prompt para LLM
    system_prompt = """Você é um assistente que responde perguntas baseado APENAS nos documentos fornecidos.
Se a resposta não estiver nos documentos, diga que não sabe."""
    
    user_prompt = f"""Contexto dos documentos:
{context}

Pergunta do usuário: {user_query}

Responda a pergunta baseado nos documentos acima."""
    
    # 4. Chamar LLM
    print(f"\n🤖 Gerando resposta com {model}...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content


def main():
    """Exemplo de uso do RAG com PostgreSQL"""
    
    # Conectar ao banco
    print("🔌 Conectando ao PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("✓ Conectado!")
    
    # === OPÇÃO 1: Inserir novos documentos com embeddings ===
    print("\n📝 Inserindo documentos com embeddings...")
    
    documents = [
        {
            "content": "Docker é uma plataforma de containerização que permite empacotar aplicações com suas dependências.",
            "metadata": {"category": "devops", "source": "docs"}
        },
        {
            "content": "Kubernetes é um sistema de orquestração de containers que automatiza deployment e scaling.",
            "metadata": {"category": "devops", "source": "docs"}
        },
        {
            "content": "Machine Learning é um campo da IA que permite computadores aprenderem com dados.",
            "metadata": {"category": "ai", "source": "tutorial"}
        }
    ]
    
    # Comentar se você já inseriu os documentos antes
    # for doc in documents:
    #     insert_document_with_embedding(conn, doc["content"], doc["metadata"])
    
    # === OPÇÃO 2: Fazer busca por similaridade (RAG) ===
    print("\n" + "="*60)
    print("🤖 EXEMPLO DE RAG")
    print("="*60)
    
    # Exemplo de query
    user_query = "Como funciona containerização?"
    
    # Executar RAG
    answer = rag_query(conn, user_query)
    
    print(f"\n💬 Pergunta: {user_query}")
    print(f"\n✨ Resposta:\n{answer}")
    
    # Fechar conexão
    conn.close()
    print("\n✓ Conexão fechada!")


if __name__ == "__main__":
    main()
