import os
from dotenv import load_dotenv
from google import genai

from tools import (
    get_ticket_conversation,
    classify_category,
    detect_followup,
    save_agent_run
)

load_dotenv()


class SupportTicketAgentBasic:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def summarize(self, conversation: str) -> str:
        prompt = f"""
Gere um resumo curto da conversa abaixo.

Conversa:
{conversation}

Responda apenas com o resumo.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip() if response.text else ""

    def run(self, ticket_id: int) -> dict:
        conversation = get_ticket_conversation(ticket_id)

        if not conversation:
            return {
                "ticket_id": ticket_id,
                "erro": "ticket não encontrado"
            }

        category = classify_category(conversation)
        followup = detect_followup(conversation)
        summary = self.summarize(conversation)

        result = {
            "ticket_id": ticket_id,
            "categoria": category["categoria"],
            "resumo": summary,
            "precisa_followup": followup["precisa_followup"],
            "motivo_followup": followup["motivo"]
        }

        save_agent_run(
            agent_name="support_agent_basic",
            ticket_id=ticket_id,
            input_text=conversation,
            output_text=result
        )

        return result