import os
from sqlalchemy import create_engine, text
import json

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"postgresql+psycopg2://admin:admin123@{DB_HOST}:5432/suporte_ai"
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

'''
def classify_category(conversation_text: str) -> dict:
    text_lower = conversation_text.lower()

    if "login" in text_lower or "senha" in text_lower or "acessar" in text_lower:
        categoria = "login"
    elif "pagamento" in text_lower or "cartão" in text_lower:
        categoria = "pagamento"
    elif "entrega" in text_lower or "transportadora" in text_lower:
        categoria = "entrega"
    elif "cancelar" in text_lower or "cancelamento" in text_lower:
        categoria = "cancelamento"
    elif "conta" in text_lower:
        categoria = "conta"
    else:
        categoria = "outros"

    return {
        "categoria": categoria,
        "metodo": "regra_simples"
    }
'''

def classify_category_prompt(conversation_text: str) -> dict:
    prompt = f"""
Você é um classificador de tickets de suporte.

Classifique a conversa em apenas uma das categorias abaixo:
- acesso
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
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "categoria": {
                            "type": "string",
                            "enum": [
                                "acesso",
                                "pagamento",
                                "entrega",
                                "cancelamento",
                                "conta",
                                "outros"
                            ]
                        }
                    },
                    "required": ["categoria"]
                },
                temperature=0.1
            )
        )

        result = json.loads(response.text)

        return {
            "categoria": result["categoria"],
            "metodo": "llm_gemini"
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