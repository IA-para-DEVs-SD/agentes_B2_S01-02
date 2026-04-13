import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import TOOL_MAP

load_dotenv()


class GuardrailNoteAgent:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.tool_declarations = [
            types.FunctionDeclaration(
                name="validate_internal_note",
                description=(
                    "Valida uma internal note aplicando guardrails. "
                    "Detecta PII (email, telefone, CPF) e linguagem negativa sobre o usuário. "
                    "Retorna status: saved, sanitized_and_saved ou blocked."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "note_text": {
                            "type": "string",
                            "description": "Texto da internal note a ser validada",
                        }
                    },
                    "required": ["note_text"],
                },
            ),
            types.FunctionDeclaration(
                name="save_internal_note",
                description=(
                    "Salva a internal note no banco de dados. "
                    "Use o texto sanitizado se o status for sanitized_and_saved. "
                    "Não salve se o status for blocked."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "integer", "description": "ID do ticket"},
                        "note_text": {"type": "string", "description": "Texto da nota (original ou sanitizado)"},
                        "note_status": {
                            "type": "string",
                            "description": "Status: saved, sanitized_and_saved ou blocked",
                        },
                        "blocked_reason": {
                            "type": "string",
                            "description": "Motivo do bloqueio, se aplicável",
                        },
                    },
                    "required": ["ticket_id", "note_text", "note_status"],
                },
            ),
            types.FunctionDeclaration(
                name="list_internal_notes",
                description="Lista internal notes salvas no banco, opcionalmente por ticket_id",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID do ticket para filtrar (opcional)",
                        }
                    },
                },
            ),
        ]

        self.config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.tool_declarations)],
            temperature=0.1,
        )

    def run(self, ticket_id: int, note_text: str) -> str:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=(
                        "Você é um agente de guardrail para internal notes de suporte.\n\n"
                        "Regras obrigatórias:\n"
                        "1. SEMPRE use validate_internal_note primeiro para validar a nota.\n"
                        "2. Se o status for 'saved': salve a nota original com save_internal_note.\n"
                        "3. Se o status for 'sanitized_and_saved': salve o texto SANITIZADO (não o original).\n"
                        "4. Se o status for 'blocked': salve com status 'blocked' e o motivo, "
                        "mas registre no banco para auditoria.\n"
                        "5. Ao final, explique o que aconteceu e por quê.\n\n"
                        f"Ticket ID: {ticket_id}\n"
                        f"Nota: {note_text}"
                    ))
                ],
            )
        ]

        max_iterations = 10

        for _ in range(max_iterations):
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=self.config,
            )

            candidate = response.candidates[0]
            parts = candidate.content.parts

            function_calls = [
                part.function_call
                for part in parts
                if getattr(part, "function_call", None) is not None
            ]

            if not function_calls:
                return (response.text or "").strip()

            contents.append(candidate.content)

            function_response_parts = []

            for call in function_calls:
                fn_name = call.name
                arguments = dict(call.args) if call.args else {}

                print(f"  🔧 Tool: {fn_name}({json.dumps(arguments, ensure_ascii=False)[:200]})")

                result = TOOL_MAP[fn_name](**arguments)

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=fn_name,
                        response=result,
                    )
                )

            contents.append(
                types.Content(role="user", parts=function_response_parts)
            )

        return "Agente atingiu o limite de iterações."
