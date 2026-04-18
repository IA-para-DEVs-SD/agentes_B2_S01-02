"""Exibe todos os dados salvos no Qdrant"""
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333, check_compatibility=False)

# Lista coleções
collections = client.get_collections().collections
print("Coleções no Qdrant:")
for c in collections:
    print(f"  - {c.name}")

# Busca todos os pontos
print()
print("=" * 60)
print("DADOS EM multi_agent_memory")
print("=" * 60)

result = client.scroll(collection_name="multi_agent_memory", limit=20)
points = result[0]

print(f"Total de pontos: {len(points)}\n")
for i, p in enumerate(points):
    print(f"--- Ponto {i+1} ---")
    print(f"ID: {p.id}")
    agent = p.payload.get("agent", "?")
    print(f"Agent: {agent}")
    ts = p.payload.get("timestamp", "?")
    print(f"Timestamp: {ts}")
    content = p.payload.get("content", "")
    print(f"Content ({len(content)} chars):")
    print(content[:2000])
    if len(content) > 2000:
        print("... [truncado]")
    print()
