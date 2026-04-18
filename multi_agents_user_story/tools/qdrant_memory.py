"""
Tool de memória persistente usando Qdrant (Long-term memory)
Salva e busca outputs dos agentes usando embeddings.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sklearn.feature_extraction.text import HashingVectorizer
import uuid
import time

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "multi_agent_memory"
VECTOR_SIZE = 256

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, check_compatibility=False)

vectorizer = HashingVectorizer(
    n_features=VECTOR_SIZE,
    alternate_sign=False,
    norm="l2"
)


def embed(text: str) -> list:
    """Gera embedding de um texto usando HashingVectorizer"""
    vec = vectorizer.transform([text])
    return vec.toarray()[0].astype(float).tolist()


def ensure_collection():
    """Cria a coleção no Qdrant se não existir"""
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"✅ Coleção '{COLLECTION_NAME}' criada no Qdrant.")
    return True


def save_to_qdrant(agent_name: str, content: str, metadata: dict = None) -> dict:
    """
    Salva output de um agente no Qdrant como memória de longo prazo.

    Args:
        agent_name: Nome do agente (ex: "scrum_master")
        content: Conteúdo textual a ser salvo
        metadata: Metadados adicionais

    Returns:
        dict com status da operação
    """
    ensure_collection()

    point_id = str(uuid.uuid4())
    vector = embed(content)

    payload = {
        "agent": agent_name,
        "content": content,
        "timestamp": time.time(),
    }
    if metadata:
        payload.update(metadata)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(id=point_id, vector=vector, payload=payload)
        ],
    )

    return {
        "status": "saved",
        "point_id": point_id,
        "agent": agent_name,
        "content_length": len(content)
    }


def search_qdrant(query: str, limit: int = 5) -> list:
    """
    Busca semântica no Qdrant por conteúdos similares.

    Args:
        query: Texto de busca
        limit: Número máximo de resultados

    Returns:
        Lista de resultados com score e payload
    """
    ensure_collection()

    query_vector = embed(query)

    try:
        results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
        ).points
    except Exception:
        return []

    return [
        {
            "agent": r.payload.get("agent", "unknown"),
            "content": r.payload.get("content", ""),
            "score": round(r.score, 3),
        }
        for r in results
    ]
