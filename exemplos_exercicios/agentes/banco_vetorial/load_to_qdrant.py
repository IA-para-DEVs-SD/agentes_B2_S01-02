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

vectorizer = HashingVectorizer(
    n_features=VECTOR_SIZE,
    alternate_sign=False,
    norm="l2"
)

def connect_postgres():
    return psycopg2.connect(**POSTGRES_CONFIG)

qdrant = QdrantClient(host="localhost", port=6333, check_compatibility=False)

def embed(text: str):
    vec = vectorizer.transform([text])
    return vec.toarray()[0].astype(float).tolist()

def ensure_collection():
    if qdrant.collection_exists(COLLECTION_NAME):
        return
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

def fetch_kb_chunks():
    conn = connect_postgres()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            c.id,
            kb.name,
            d.title,
            c.chunk_order,
            c.content
        FROM kb_chunks c
        JOIN kb_documents d
            ON c.document_id = d.id
        JOIN knowledge_bases kb
            ON d.kb_id = kb.id
        ORDER BY c.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def load_to_qdrant():
    rows = fetch_kb_chunks()
    points = []

    for chunk_id, kb_name, title, chunk_order, content in rows:
        vector = embed(content)
        points.append(
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload={
                    "kb_name": kb_name,
                    "title": title,
                    "chunk_order": chunk_order,
                    "content": content,
                },
            )
        )

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )
    print(f"✅ {len(points)} chunks enviados para o Qdrant.")

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
    ensure_collection()
    load_to_qdrant()
    search("problema de pagamento")
    search("não consigo entrar na conta")
    search("política de reembolso")