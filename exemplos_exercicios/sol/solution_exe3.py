import os
import json
from collections import Counter

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres123@localhost:5450/mydb"
)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"postgresql+psycopg2://postgres:postgres123@{DB_HOST}:5450/mydb"
engine = create_engine(DB_URL)

# -----------------------------
# Tool 1: ler feedbacks do banco
# -----------------------------
def get_feedbacks():
    engine = create_engine(DATABASE_URL)

    query = """
        SELECT
            feedback_id,
            feedback_text,
            created_at,
            channel
        FROM feedbacks
        ORDER BY feedback_id
    """

    df = pd.read_sql(query, engine)
    
    # Converter timestamps para string para serialização JSON
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].astype(str)
    
    return df.to_dict(orient="records")


# -----------------------------
# Tool 2: salvar resultado local
# -----------------------------
def save_feedback_analysis(results):
    with open("feedback_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "file": "feedback_analysis_results.json",
        "total_saved": len(results),
    }


# -----------------------------
# Tool 3: consolidar números
# -----------------------------
def summarize_feedback_results(results):
    categorias = Counter([r["categoria"] for r in results])
    sentimentos = Counter([r["sentimento"] for r in results])

    return {
        "total_feedbacks": len(results),
        "categorias": dict(categorias),
        "sentimentos": dict(sentimentos),
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_feedbacks",
            "description": "Lê todos os feedbacks da tabela feedbacks no banco Postgres.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_feedback_analysis",
            "description": "Salva localmente a análise estruturada dos feedbacks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "feedback_id": {"type": "integer"},
                                "categoria": {"type": "string"},
                                "sentimento": {"type": "string"},
                                "resumo": {"type": "string"},
                            },
                            "required": [
                                "feedback_id",
                                "categoria",
                                "sentimento",
                                "resumo",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["results"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_feedback_results",
            "description": "Gera números consolidados a partir das análises individuais.",
            "parameters": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "feedback_id": {"type": "integer"},
                                "categoria": {"type": "string"},
                                "sentimento": {"type": "string"},
                                "resumo": {"type": "string"},
                            },
                            "required": [
                                "feedback_id",
                                "categoria",
                                "sentimento",
                                "resumo",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["results"],
                "additionalProperties": False,
            },
        },
    },
]


available_tools = {
    "get_feedbacks": get_feedbacks,
    "save_feedback_analysis": save_feedback_analysis,
    "summarize_feedback_results": summarize_feedback_results,
}


def run_agent():
    messages = [
        {
            "role": "system",
            "content": """
Você é um agente de análise de feedbacks.

Seu trabalho:
1. Ler feedbacks usando a tool get_feedbacks.
2. Analisar cada feedback.
3. Classificar cada um com:
   - categoria: bug, elogio, pagamento, performance, atendimento ou outros
   - sentimento: positivo, negativo ou neutro
   - resumo curto
4. Salvar a análise usando save_feedback_analysis.
5. Consolidar os números usando summarize_feedback_results.
6. Gerar um relatório final para liderança.

Use tools quando precisar acessar dados, salvar resultados ou calcular consolidados.
Não invente feedbacks.
""",
        },
        {
            "role": "user",
            "content": "Analise todos os feedbacks do banco e gere um relatório final para a gerência.",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )

    while True:
        message = response.choices[0].message
        
        if not message.tool_calls:
            print(message.content)
            break

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"Chamando tool: {tool_name}")

            result = available_tools[tool_name](**tool_args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )


if __name__ == "__main__":
    run_agent()