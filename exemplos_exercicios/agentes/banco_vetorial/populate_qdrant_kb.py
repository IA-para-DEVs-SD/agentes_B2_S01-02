from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "support_kb"

# conecta no Qdrant local
qdrant_client = QdrantClient(host="localhost", port=6333)

# modelo de embedding local
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    return embedding_model.encode(text).tolist()


def create_collection():
    collections = qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME not in collection_names:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Coleção '{COLLECTION_NAME}' criada.")
    else:
        print(f"ℹ️ Coleção '{COLLECTION_NAME}' já existe.")


def get_kb_documents():
    return [
        {
            "id": 1,
            "title": "Conta bloqueada após tentativas de login",
            "text": (
                "Se a conta estiver bloqueada após tentativas de login e a redefinição "
                "de senha não resolver, orientar o procedimento de desbloqueio da conta "
                "ou escalar para suporte nível 2."
            ),
            "categoria": "acesso"
        },
        {
            "id": 2,
            "title": "Redefinição de senha",
            "text": (
                "Quando o cliente relata dificuldade de acesso, a primeira ação padrão "
                "é orientar a redefinição de senha e confirmar se o problema persiste."
            ),
            "categoria": "acesso"
        },
        {
            "id": 3,
            "title": "Pagamento recusado",
            "text": (
                "Se o pagamento falhar, orientar o cliente a verificar cartão, saldo, "
                "limite e dados de cobrança antes de nova tentativa."
            ),
            "categoria": "pagamento"
        },
        {
            "id": 4,
            "title": "Entrega atrasada",
            "text": (
                "Se a entrega atrasar, consultar a transportadora, verificar status "
                "logístico e informar previsão atualizada ao cliente."
            ),
            "categoria": "entrega"
        },
        {
            "id": 5,
            "title": "Cancelamento de serviço",
            "text": (
                "Se o cliente solicitar cancelamento, confirmar identidade, validar "
                "impactos do cancelamento e seguir o procedimento definido pela empresa."
            ),
            "categoria": "cancelamento"
        }
    ]


def populate_kb():
    docs = get_kb_documents()

    points = []
    for doc in docs:
        vector = embed_text(doc["text"])

        points.append(
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload=doc
            )
        )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"✅ {len(points)} documentos inseridos na coleção '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    print("\n🚀 Populando a base vetorial...\n")
    create_collection()
    populate_kb()
    print("\n🎉 KB pronta no Qdrant.\n")