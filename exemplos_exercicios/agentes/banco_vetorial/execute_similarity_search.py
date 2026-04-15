import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
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
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 gera vetores de 384 dimensões

qdrant = QdrantClient(
    host="localhost",
    port=6333,
    check_compatibility=False,
)

model = SentenceTransformer(MODEL_NAME)


def embed(text: str) -> list[float]:
    return model.encode(text).tolist()


def collection_exists(collection_name: str) -> bool:
    collections = qdrant.get_collections().collections
    return any(c.name == collection_name for c in collections)


def search(query: str, limit: int = 5, kb_name: str | None = None):
    if not collection_exists(COLLECTION_NAME):
        raise ValueError(
            f"Coleção '{COLLECTION_NAME}' não encontrada no Qdrant. "
            f"Recrie e reindexe os dados com embeddings de {VECTOR_SIZE} dimensões."
        )

    query_vector = embed(query)

    query_filter = None
    if kb_name:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="kb_name",
                    match=MatchValue(value=kb_name),
                )
            ]
        )

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
    ).points

    print(f"\n🔎 Busca: {query}")
    if kb_name:
        print(f"📚 Filtrando pela KB: {kb_name}")

    if not results:
        print("Nenhum resultado encontrado.")
        return

    for i, r in enumerate(results, start=1):
        payload = r.payload or {}

        result_kb = payload.get("kb_name", "sem_kb")
        title = payload.get("title", "sem_título")
        chunk_order = payload.get("chunk_order", "N/A")
        content = payload.get("content", "")
        metadata = payload.get("metadata", {}) or {}

        categoria = metadata.get("categoria", "N/A")
        tipo = metadata.get("tipo", "N/A")

        content_preview = content.replace("\n", " ").strip()

        print(
            f"{i}. [{result_kb}] {title} | "
            f"chunk={chunk_order} | categoria={categoria} | tipo={tipo} | "
            f"score={r.score:.3f}"
        )
        print(f"   {content_preview}")
        print()


if __name__ == "__main__":
    #search("login")
    #search("não consigo entrar na conta")
    search("cobraram duas vezes")
    # search("quero reembolso", kb_name="policy_kb")