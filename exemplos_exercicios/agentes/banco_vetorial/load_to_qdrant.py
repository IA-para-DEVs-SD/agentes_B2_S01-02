import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

POSTGRES_CONFIG = {
    "host": "localhost",
    "database": "suporte_ai",
    "user": "admin",
    "password": "admin123",
    "port": 5433,
}

COLLECTION_NAME = "kb_chunks"
MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

qdrant = QdrantClient(
    host="localhost",
    port=6333,
    check_compatibility=False,
)

model = SentenceTransformer(MODEL_NAME)


def embed(text: str) -> list[float]:
    return model.encode(text).tolist()


def fetch_chunks():
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    query = """
    SELECT
        c.id AS chunk_id,
        kb.name AS kb_name,
        d.title,
        c.chunk_order,
        c.content,
        c.metadata
    FROM kb_chunks c
    JOIN kb_documents d
        ON c.document_id = d.id
    JOIN knowledge_bases kb
        ON d.kb_id = kb.id
    ORDER BY d.id, c.chunk_order;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def recreate_collection():
    existing = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION_NAME in existing:
        qdrant.delete_collection(collection_name=COLLECTION_NAME)

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(f"✅ Collection '{COLLECTION_NAME}' criada com vetor de {VECTOR_SIZE} dimensões.")


def build_points(rows):
    points = []

    for row in rows:
        chunk_id, kb_name, title, chunk_order, content, metadata = row

        vector = embed(content)

        payload = {
            "kb_name": kb_name,
            "title": title,
            "chunk_order": chunk_order,
            "content": content,
            "metadata": metadata if metadata else {},
        }

        points.append(
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload=payload,
            )
        )

    return points


def upload_points(points, batch_size: int = 100):
    total = len(points)

    for i in range(0, total, batch_size):
        batch = points[i:i + batch_size]
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )
        print(f"⬆️ Enviados {min(i + batch_size, total)}/{total} pontos")


def main():
    print("📥 Lendo chunks do Postgres...")
    rows = fetch_chunks()

    if not rows:
        print("⚠️ Nenhum chunk encontrado no Postgres.")
        return

    print(f"✅ {len(rows)} chunks encontrados.")

    print("🧱 Recriando collection no Qdrant...")
    recreate_collection()

    print("🧠 Gerando embeddings...")
    points = build_points(rows)

    print("🚀 Enviando pontos para o Qdrant...")
    upload_points(points)

    print("✅ Indexação concluída com sucesso.")


if __name__ == "__main__":
    main()