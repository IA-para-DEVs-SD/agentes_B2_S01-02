import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import get_ticket_conversation

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify_category(conversation_text: str) -> dict:
    prompt = f"""
Você é um classificador de tickets de suporte.

Classifique a conversa em apenas uma das categorias abaixo:
- acesso
- pagamento
- entrega
- cancelamento
- conta
- outros

Regras:
- Escolha somente uma categoria.
- Considere o assunto principal da conversa.
- Se não estiver claro, use "outros".

Conversa:
{conversation_text}
"""

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
                        ],
                        "description": "Categoria principal do ticket"
                    }
                },
                "required": ["categoria"],
                "additionalProperties": False
            },
            temperature=0.1
        )
    )

    result = json.loads(response.text)

    return {
        "categoria": result["categoria"],
        "metodo": "llm_gemini"
    }


if __name__ == "__main__":
    ticket_id = 1001

    ticket = get_ticket_conversation(ticket_id)

    if not ticket:
        print("Ticket não encontrado")
        raise SystemExit(1)

    conversation_text = ticket["conversation_text"]

    print("\n=== CONVERSA ===")
    print(conversation_text)

    result = classify_category(conversation_text)

    print("\n=== CLASSIFICAÇÃO ===")
    print(result)