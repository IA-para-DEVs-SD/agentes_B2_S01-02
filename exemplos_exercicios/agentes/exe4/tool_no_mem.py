from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ⚠️ Ajuste senha se necessário

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"
engine = create_engine(DB_URL)

# Inicializa cliente Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =========================================================
# TOOL 1: GET CONVERSATION (MEMÓRIA - NÃO USADA NO EXEMPLO 1)
# =========================================================


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


# =========================================================
# TOOL 2: CLASSIFICAÇÃO (LLM)
# =========================================================


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


# =========================================================
# TOOL 3: ANALYZE WITHOUT HISTORY (🔥 PRINCIPAL AQUI)
# =========================================================


def analyze_without_history(message: str) -> dict:
    prompt = f"""
Você é um analista de suporte ao cliente.

Analise apenas a mensagem abaixo, SEM considerar histórico anterior.

Sua tarefa é:
1. Identificar a categoria do problema
2. Resumir o problema
3. Sugerir a primeira ação
4. Explicitar que não há histórico

Categorias possíveis:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com:
- categoria
- resumo
- acao_inicial
- observacao

Mensagem:
{message}
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
                        },
                        "resumo": {"type": "string"},
                        "acao_inicial": {"type": "string"},
                        "observacao": {"type": "string"}
                    },
                    "required": [
                        "categoria",
                        "resumo",
                        "acao_inicial",
                        "observacao"
                    ]
                },
                temperature=0.1
            )
        )

        result = json.loads(response.text)

        return {
            "categoria": result["categoria"],
            "resumo": result["resumo"],
            "acao_inicial": result["acao_inicial"],
            "observacao": result["observacao"],
            "metodo": "llm_sem_historico"
        }

    except Exception as e:
        print("Erro analyze_without_history:", e)

        return {
            "categoria": "outros",
            "resumo": "Não foi possível analisar a mensagem isoladamente.",
            "acao_inicial": "Solicitar mais informações ao cliente.",
            "observacao": "Análise sem histórico (fallback por erro).",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 4: FOLLOW-UP
# =========================================================


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


# =========================================================
# TOOL 5: LOG EXECUTION
# =========================================================


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


# =========================================================
# TOOL MAP
# =========================================================

TOOL_MAP = {
    "get_ticket_conversation": get_ticket_conversation,
    "classify_category_prompt": classify_category_prompt,
    "detect_followup": detect_followup,
    "analyze_without_history": analyze_without_history,
}

# =========================================================
# MAIN (EXEMPLO SEM HISTÓRICO)
# =========================================================

if __name__ == "__main__":
    message = "me ajuda? eu estou sem acesso à minha conta, tentei logar, nada funciona"

    print("\n==============================")
    print("ANÁLISE 1 - SEM HISTÓRICO")
    print("==============================\n")

    result = analyze_without_history(message)

    print(json.dumps(result, indent=2, ensure_ascii=False))
