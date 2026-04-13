from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

# Inicializa cliente Claude
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5433/suporte_ai"
engine = create_engine(DB_URL)

# =========================================================
# TOOL 1: GET CONVERSATION (MEMÓRIA)
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
    prompt = f"""
Você é um classificador de tickets de suporte.

Classifique a conversa em apenas uma das categorias abaixo:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda APENAS com um JSON válido com a chave "categoria".

Conversa:
{conversation_text}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)

        return {
            "categoria": result["categoria"],
            "metodo": "llm_claude"
        }

    except Exception as e:
        print("Erro classify_category_prompt:", e)
        return {
            "categoria": "outros",
            "metodo": "fallback_erro"
        }


# =========================================================
# TOOL 3: ANALYZE WITH MEMORY
# =========================================================


def analyze_with_memory(ticket_id: int, new_message: str) -> dict:
    conversation = get_ticket_conversation(ticket_id)

    if not conversation["found"]:
        return {
            "ticket_id": ticket_id,
            "categoria": "outros",
            "resumo": "Nenhum histórico encontrado para o ticket.",
            "acao_recomendada": "Analisar a nova mensagem isoladamente ou verificar se o ticket existe.",
            "observacao": "Análise com memória solicitada, mas sem histórico disponível.",
            "metodo": "sem_historico_disponivel"
        }

    conversation_text = conversation["conversation_text"]

    prompt = f"""
Você é um analista de suporte ao cliente.

Analise a NOVA mensagem considerando o HISTÓRICO do ticket.

Sua tarefa é:
1. Identificar a categoria principal do caso
2. Resumir o problema atual considerando o histórico
3. Dizer o que já parece ter sido tentado ou informado antes
4. Sugerir a próxima ação recomendada
5. Explicitar que a análise foi feita com histórico

Categorias possíveis:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Responda APENAS com um JSON válido contendo:
- categoria
- resumo
- contexto_relevante
- acao_recomendada
- observacao

Histórico do ticket:
{conversation_text}

Nova mensagem:
{new_message}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()
        
        # Remove markdown code blocks se existirem
        if response_text.startswith("```"):
            # Remove ```json ou ``` do início
            response_text = response_text.split("\n", 1)[1] if "\n" in response_text else response_text[3:]
            # Remove ``` do final
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
        
        result = json.loads(response_text)

        return {
            "ticket_id": ticket_id,
            "categoria": result["categoria"],
            "resumo": result["resumo"],
            "contexto_relevante": result["contexto_relevante"],
            "acao_recomendada": result["acao_recomendada"],
            "observacao": result["observacao"],
            "metodo": "llm_claude_com_historico"
        }

    except json.JSONDecodeError as e:
        print(f"Erro ao fazer parse do JSON: {e}")
        print(f"Resposta completa: {response_text if 'response_text' in locals() else 'N/A'}")
        
        return {
            "ticket_id": ticket_id,
            "categoria": "outros",
            "resumo": "Não foi possível analisar a mensagem com histórico.",
            "contexto_relevante": "Histórico recuperado, mas houve erro no parse do JSON.",
            "acao_recomendada": "Reexecutar a análise ou revisar o prompt/modelo.",
            "observacao": "Análise com histórico, fallback por erro de JSON.",
            "metodo": "fallback_erro_json"
        }
    except Exception as e:
        print("Erro analyze_with_memory:", e)

        return {
            "ticket_id": ticket_id,
            "categoria": "outros",
            "resumo": "Não foi possível analisar a mensagem com histórico.",
            "contexto_relevante": "Histórico recuperado, mas houve erro na análise.",
            "acao_recomendada": "Reexecutar a análise ou revisar o prompt/modelo.",
            "observacao": "Análise com histórico, fallback por erro.",
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
    "analyze_with_memory": analyze_with_memory,
}

# =========================================================
# MAIN (EXEMPLO COM MEMÓRIA)
# =========================================================

if __name__ == "__main__":
    ticket_id = 1001
    new_message = "Agora apareceu que minha conta está bloqueada"

    print("\n==============================")
    print("ANÁLISE 2 - COM HISTÓRICO (CLAUDE)")
    print("==============================\n")

    result = analyze_with_memory(ticket_id, new_message)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # opcional: salvar execução
    save_agent_run(
        agent_name="analyze_with_memory_claude",
        ticket_id=ticket_id,
        input_text=new_message,
        output_text=result
    )

