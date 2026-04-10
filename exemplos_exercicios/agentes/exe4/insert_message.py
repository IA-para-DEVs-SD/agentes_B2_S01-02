import psycopg2


# 1. CONEXÃO

def get_connection():
    return psycopg2.connect(
    dbname="suporte_ai",
    user="admin",
    password="admin123",
    host="localhost",
    port="5432"
    )

# INSERIR MENSAGEM (WRITE)

def insert_message(conn, msg):
    query = """
    INSERT INTO conversations (
    ticket_id, conversation_id, user_id,
    speaker, message, timestamp, ticket_status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, (
            msg["ticket_id"],
            msg["conversation_id"],
            msg["user_id"],
            msg["speaker"],
            msg["message"],
            msg["timestamp"],
            msg["ticket_status"]
            ))
            conn.commit()
            print("✅ Mensagem inserida com sucesso")
    except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao inserir: {e}")




if __name__ == "__main__":
    conn = get_connection()
    # nova mensagem chegando
    new_message = {
        "ticket_id": 1001,
        "conversation_id": 1,
        "user_id": 101,
        "speaker": "client",
        "message": "Agora apareceu que minha conta está bloqueada",
        "timestamp": "2026-04-01 09:07:00",
        "ticket_status": "open"
    }

    print("\n🚀 Inserindo nova mensagem...")
    insert_message(conn, new_message)


    conn.close()

