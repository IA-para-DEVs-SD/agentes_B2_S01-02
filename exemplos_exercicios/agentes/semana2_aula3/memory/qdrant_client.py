# Cliente Qdrant compartilhado entre os agentes
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "requirements_kb"


def get_qdrant_client():
    """Retorna cliente Qdrant configurado"""
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def create_collection_if_not_exists():
    """Cria coleção se não existir"""
    client = get_qdrant_client()
    
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,  # all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        print(f"✅ Coleção '{COLLECTION_NAME}' criada.")
    else:
        print(f"ℹ️ Coleção '{COLLECTION_NAME}' já existe.")
