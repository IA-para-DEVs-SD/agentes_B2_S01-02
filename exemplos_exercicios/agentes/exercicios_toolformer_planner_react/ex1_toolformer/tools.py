"""
Tools para o exercício 1 - Toolformer
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"


def get_engine():
    return create_engine(DB_URL)


def get_ticket_conversation(ticket_id: int) -> dict:
    """
    Busca a conversa completa de um ticket no banco de dados
    
    Args:
        ticket_id: ID do ticket
    
    Returns:
        dict com informações do ticket e suas mensagens
    """
    engine = get_engine()
    
    query = text("""
        SELECT 
            ticket_id,
            conversation_id,
            speaker,
            message,
            timestamp,
            ticket_status
        FROM conversations
        WHERE ticket_id = :ticket_id
        ORDER BY timestamp
    """)
    
    with engine.begin() as conn:
        rows = conn.execute(query, {"ticket_id": ticket_id}).mappings().all()
    
    if not rows:
        return {
            "ticket_id": ticket_id,
            "found": False,
            "messages": [],
            "status": None
        }
    
    messages = []
    status = None
    
    for row in rows:
        messages.append({
            "speaker": row["speaker"],
            "message": row["message"],
            "timestamp": str(row["timestamp"])
        })
        status = row["ticket_status"]
    
    # Monta texto da conversa
    conversation_text = "\n".join([
        f"{msg['speaker']}: {msg['message']}" 
        for msg in messages
    ])
    
    return {
        "ticket_id": ticket_id,
        "found": True,
        "status": status,
        "messages": messages,
        "conversation_text": conversation_text,
        "message_count": len(messages)
    }


# Mapa de tools disponíveis
TOOL_MAP = {
    "get_ticket_conversation": get_ticket_conversation
}


if __name__ == "__main__":
    # Teste da tool
    print("\n" + "="*60)
    print("🧪 TESTE DA TOOL")
    print("="*60 + "\n")
    
    # Testa com ticket existente
    result = get_ticket_conversation(1001)
    
    if result["found"]:
        print(f"✅ Ticket {result['ticket_id']} encontrado")
        print(f"   Status: {result['status']}")
        print(f"   Mensagens: {result['message_count']}")
        print(f"\n   Conversa:")
        for msg in result['messages'][:3]:
            print(f"   {msg['speaker']}: {msg['message'][:60]}...")
    else:
        print(f"❌ Ticket {result['ticket_id']} não encontrado")
    
    print("\n" + "="*60 + "\n")
