import os
from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    get_ticket_conversation,
    classify_category,
    detect_followup,
    save_agent_run
)

load_dotenv()


class SupportTicketAgentBasic:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def summarize(self, conversation: str) -> str:
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
            Gere um resumo curto da conversa abaixo.

            Conversa:
            {conversation}

            Responda apenas com o resumo.
            """
        )

        return response.output_text

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