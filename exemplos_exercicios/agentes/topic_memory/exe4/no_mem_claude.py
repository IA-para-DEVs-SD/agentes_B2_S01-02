from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"
engine = create_engine(DB_URL)

# Inicializa cliente Claude
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CLAUDE_MODEL = "claude-sonnet-4-6"
# Se quiser mais barato/rápido, pode trocar por:
# CLAUDE_MODEL = "claude-3-5-haiku-20241022"


def call_claude_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Faz chamada ao Claude pedindo saída estritamente em JSON.
    """
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        temperature=0.1,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    response_text = "\n".join(text_parts).strip()

    # Tenta interpretar direto como JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # fallback: tenta extrair JSON se vier cercado por texto
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            possible_json = response_text[start:end + 1]
            return json.loads(possible_json)

        raise ValueError(f"Resposta não veio em JSON válido: {response_text}")


# =========================================================
# TOOL 1: GET CONVERSATION
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
# TOOL 2: CLASSIFICAÇÃO
# =========================================================

def classify_category_prompt(conversation_text: str) -> dict:
    system_prompt = """
Você é um classificador de tickets de suporte.
Sua resposta deve ser apenas JSON válido, sem markdown, sem explicações extras.
"""

    user_prompt = f"""
Classifique a conversa em apenas uma das categorias abaixo:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda em JSON com a chave "categoria".

Exemplo de formato:
{{
  "categoria": "acesso"
}}

Conversa:
{conversation_text}
"""

    try:
        result = call_claude_json(system_prompt, user_prompt)

        categoria = result.get("categoria", "outros")
        if categoria not in ["acesso", "pagamento", "entrega", "cancelamento", "conta", "outros"]:
            categoria = "outros"

        return {
            "categoria": categoria,
            "metodo": "llm_claude"
        }

    except Exception as e:
        print("Erro classify_category:", e)
        return {
            "categoria": "outros",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 3: ANALYZE WITHOUT HISTORY
# =========================================================

def analyze_without_history(message: str) -> dict:
    system_prompt = """
Você é um analista de suporte ao cliente.
Sua resposta deve ser apenas JSON válido, sem markdown, sem explicações extras.
"""

    user_prompt = f"""
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

Exemplo de formato:
{{
  "categoria": "acesso",
  "resumo": "O cliente relata que não consegue acessar a conta.",
  "acao_inicial": "Orientar validação de credenciais e fluxo de recuperação de senha.",
  "observacao": "Análise feita sem histórico anterior."
}}

Mensagem:
{message}
"""

    try:
        result = call_claude_json(system_prompt, user_prompt)

        categoria = result.get("categoria", "outros")
        if categoria not in ["acesso", "pagamento", "entrega", "cancelamento", "conta", "outros"]:
            categoria = "outros"

        return {
            "categoria": categoria,
            "resumo": result.get("resumo", "Não foi possível resumir a mensagem."),
            "acao_inicial": result.get("acao_inicial", "Solicitar mais informações ao cliente."),
            "observacao": result.get("observacao", "Análise sem histórico."),
            "metodo": "llm_sem_historico_claude"
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
# MAIN
# =========================================================

if __name__ == "__main__":
    message = "me ajuda? eu estou sem acesso à minha conta, tentei logar, nada funciona"

    print("\n==============================")
    print("ANÁLISE 1 - SEM HISTÓRICO")
    print("==============================\n")

    result = analyze_without_history(message)

    print(json.dumps(result, indent=2, ensure_ascii=False))