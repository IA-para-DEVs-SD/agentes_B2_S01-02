import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOL_MAP, save_agent_run

load_dotenv()


class SupportTicketAgentToolCalling:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.tools = [
            {
                "type": "function",
                "name": "get_ticket_conversation",
                "description": "Busca a conversa completa de um ticket no banco de dados",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID do ticket"
                        }
                    },
                    "required": ["ticket_id"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "classify_category_prompt",
                "description": "Classifica a categoria principal do problema com base na conversa",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_text": {
                            "type": "string",
                            "description": "Texto da conversa consolidada"
                        }
                    },
                    "required": ["conversation_text"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "detect_followup",
                "description": "Detecta se o ticket precisa de follow-up com base na última mensagem",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_text": {
                            "type": "string",
                            "description": "Texto da conversa consolidada"
                        }
                    },
                    "required": ["conversation_text"],
                    "additionalProperties": False
                }
            }
        ]

    def run(self, ticket_id: int) -> str:
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            tools=self.tools,
            input=(
                "Você é um agente de suporte com acesso a tools.\n"
                "Analise o ticket informado.\n"
                "Use as tools quando necessário.\n"
                "No final, devolva um JSON válido com estas chaves:\n"
                "ticket_id, categoria, resumo, precisa_followup, motivo_followup, status_sugerido.\n\n"
                f"Analise o ticket {ticket_id}."
            )
        )

        conversation_for_log = ""

        while True:
            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                final_text = response.output_text

                save_agent_run(
                    agent_name="support_agent_toolcalling",
                    ticket_id=ticket_id,
                    input_text=conversation_for_log,
                    output_text={"response": final_text}
                )

                return final_text

            tool_outputs = []

            for call in function_calls:
                function_name = call.name
                arguments = json.loads(call.arguments)

                result = TOOL_MAP[function_name](**arguments)

                if function_name == "get_ticket_conversation":
                    conversation_for_log = result.get("conversation_text", "")

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result, ensure_ascii=False)
                    }
                )

            response = self.client.responses.create(
                model="gpt-4.1-mini",
                previous_response_id=response.id,
                input=tool_outputs
            )