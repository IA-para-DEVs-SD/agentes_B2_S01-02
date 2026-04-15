import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sklearn.feature_extraction.text import HashingVectorizer

POSTGRES_CONFIG = {
    "host": "localhost",
    "database": "suporte_ai",
    "user": "admin",
    "password": "admin123",
    "port": 5433,
}

COLLECTION_NAME = "kb_chunks"
VECTOR_SIZE = 256  # pode aumentar para 384 ou 512 depois
qdrant = QdrantClient(host="localhost", port=6333, check_compatibility=False)

vectorizer = HashingVectorizer( #tranforma texto em números
    n_features=VECTOR_SIZE, #tamanho do verto final
    alternate_sign=False, # se valores podem ser negativos
    norm="l2"
)

def embed(text: str):
    vec = vectorizer.transform([text])
    return vec.toarray()[0].astype(float).tolist()

def search(query: str):
    query_vector = embed(query)
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=5,
    ).points

    print(f"\n🔎 Busca: {query}")
    for r in results:
        print(
            f"- [{r.payload['kb_name']}] {r.payload['title']} "
            f"(chunk {r.payload['chunk_order']}) | "
            f"{r.payload['content']} | score={r.score:.3f}"
        )

if __name__ == "__main__":
    #search("problema de pagamento")
    search("login")
    #search("política de reembolso")