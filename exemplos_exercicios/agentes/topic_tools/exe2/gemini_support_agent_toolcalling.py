import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from langfuse import observe

from tools import TOOL_MAP, save_agent_run

load_dotenv()


class SupportTicketAgentToolCalling:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.tool_declarations = [
            types.FunctionDeclaration(
                name="get_ticket_conversation",
                description="Busca a conversa completa de um ticket no banco de dados",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID do ticket"
                        }
                    },
                    "required": ["ticket_id"]
                },
            ),
            types.FunctionDeclaration(
                name="classify_category_prompt",
                description="Classifica a categoria principal do problema com base na conversa",
                parameters={
                    "type": "object",
                    "properties": {
                        "conversation_text": {
                            "type": "string",
                            "description": "Texto da conversa consolidada"
                        }
                    },
                    "required": ["conversation_text"]
                },
            ),
            types.FunctionDeclaration(
                name="detect_followup",
                description="Detecta se o ticket precisa de follow-up com base na última mensagem",
                parameters={
                    "type": "object",
                    "properties": {
                        "conversation_text": {
                            "type": "string",
                            "description": "Texto da conversa consolidada"
                        }
                    },
                    "required": ["conversation_text"]
                },
            ),
        ]

        self.generate_config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.tool_declarations)],
            temperature=0.2,
        )

    @observe()  # 🔥 aqui está a mágica do Langfuse
    def run(self, ticket_id: int) -> str:
        conversation_for_log = ""

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Você é um agente de suporte com acesso a tools.\n"
                            "Analise o ticket informado.\n"
                            "Use as tools quando necessário.\n"
                            "No final, devolva um JSON válido com estas chaves:\n"
                            "ticket_id, categoria, resumo, precisa_followup, "
                            "motivo_followup, status_sugerido.\n\n"
                            "A categoria deve ser EXATAMENTE uma destas opções:\n"
                            "login, pagamento, entrega, cancelamento, conta, outros.\n"
                            "Não reescreva a categoria.\n\n"
                            f"Analise o ticket {ticket_id}."
                        )
                    )
                ],
            )
        ]

        while True:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=self.generate_config,
            )

            candidate = response.candidates[0]
            parts = candidate.content.parts

            function_calls = [
                part.function_call
                for part in parts
                if getattr(part, "function_call", None) is not None
            ]

            if not function_calls:
                final_text = (response.text or "").strip()

                save_agent_run(
                    agent_name="support_agent_toolcalling",
                    ticket_id=ticket_id,
                    input_text=conversation_for_log,
                    output_text={"response": final_text},
                )

                return final_text

            contents.append(candidate.content)

            function_response_parts = []

            for call in function_calls:
                function_name = call.name
                arguments = dict(call.args) if call.args else {}

                result = TOOL_MAP[function_name](**arguments)

                if function_name == "get_ticket_conversation":
                    conversation_for_log = result.get("conversation_text", "")

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response=result,
                    )
                )

            contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )


if __name__ == "__main__":
    agent = SupportTicketAgentToolCalling()
    result = agent.run(1001)
    print(result)