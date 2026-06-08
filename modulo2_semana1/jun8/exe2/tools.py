import os
from sqlalchemy import create_engine, text
import json
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"postgresql+psycopg2://postgres:postgres123@{DB_HOST}:5450/mydb"
engine = create_engine(DB_URL)


def get_ticket_conversation(ticket_id: int) -> dict:
    query = text("""
        SELECT speaker, message, timestamp, ticket_status
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
            "conversation_text": ""
        }

    conversation_text = "\n".join(
        f"{row['speaker']}: {row['message']}"
        for row in rows
    )

    return {
        "ticket_id": ticket_id,
        "found": True,
        "conversation_text": conversation_text
    }


def classify_category_prompt(conversation_text: str) -> dict:
    """Classifica a categoria usando OpenAI ao invés de Gemini"""
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
Você é um classificador de tickets de suporte.

Classifique a conversa em apenas uma das categorias abaixo:
- login
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com a chave "categoria".

Conversa:
{conversation_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "categoria": result["categoria"],
            "metodo": "llm_openai"
        }

    except Exception as e:
        print("Erro classify_category:", e)
        return {
            "categoria": "outros",
            "metodo": "fallback_erro"
        }


def detect_followup(conversation_text: str) -> dict:
    lines = [line.strip() for line in conversation_text.split("\n") if line.strip()]

    if not lines:
        return {
            "precisa_followup": False,
            "motivo": "sem mensagens",
            "ultima_mensagem_foi_do_atendente": False
        }

    last_line = lines[-1].lower()
    ultima_mensagem_foi_do_atendente = last_line.startswith("atendente:")

    return {
        "precisa_followup": ultima_mensagem_foi_do_atendente,
        "motivo": (
            "última mensagem foi do atendente"
            if ultima_mensagem_foi_do_atendente
            else "última mensagem foi do cliente"
        ),
        "ultima_mensagem_foi_do_atendente": ultima_mensagem_foi_do_atendente
    }


def save_agent_run(agent_name: str, ticket_id: int, input_text: str, output_text: dict) -> None:
    query = text("""
        INSERT INTO agent_runs (
            agent_name,
            ticket_id,
            input_text,
            output_text
        )
        VALUES (
            :agent_name,
            :ticket_id,
            :input_text,
            :output_text
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "agent_name": agent_name,
                "ticket_id": ticket_id,
                "input_text": input_text,
                "output_text": json.dumps(output_text, ensure_ascii=False)
            }
        )


TOOL_MAP = {
    "get_ticket_conversation": get_ticket_conversation,
    "classify_category_prompt": classify_category_prompt,
    "detect_followup": detect_followup,
}