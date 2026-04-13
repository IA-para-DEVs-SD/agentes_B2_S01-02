import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import TOOL_MAP, analyzed_feedbacks

load_dotenv()


class FeedbackAnalysisAgent:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.tool_declarations = [
            types.FunctionDeclaration(
                name="get_all_feedbacks",
                description="Lê todos os feedbacks da tabela feedbacks no banco de dados",
                parameters={"type": "object", "properties": {}},
            ),
            types.FunctionDeclaration(
                name="classify_feedback",
                description=(
                    "Salva a classificação de um feedback individual. "
                    "O agente deve preencher categoria, sentimento e resumo."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "feedback_id": {"type": "integer", "description": "ID do feedback"},
                        "feedback_text": {"type": "string", "description": "Texto original do feedback"},
                        "categoria": {
                            "type": "string",
                            "description": "Categoria: bug, elogio, pagamento, performance, atendimento, outros",
                        },
                        "sentimento": {
                            "type": "string",
                            "description": "Sentimento: positivo, negativo, neutro",
                        },
                        "resumo": {"type": "string", "description": "Resumo curto do feedback"},
                    },
                    "required": ["feedback_id", "feedback_text", "categoria", "sentimento", "resumo"],
                },
            ),
            types.FunctionDeclaration(
                name="generate_report",
                description="Gera o relatório consolidado com contagens e principais pontos",
                parameters={
                    "type": "object",
                    "properties": {
                        "principais_pontos": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista com os principais achados da análise",
                        }
                    },
                    "required": ["principais_pontos"],
                },
            ),
            types.FunctionDeclaration(
                name="save_results_to_file",
                description="Salva o relatório e feedbacks analisados em arquivos JSON",
                parameters={
                    "type": "object",
                    "properties": {
                        "report_json": {"type": "string", "description": "JSON do relatório consolidado"},
                        "feedbacks_json": {"type": "string", "description": "JSON da lista de feedbacks analisados"},
                    },
                    "required": ["report_json", "feedbacks_json"],
                },
            ),
        ]

        self.config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.tool_declarations)],
            temperature=0.2,
        )

    def run(self) -> str:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=(
                        "Você é um agente de análise de feedbacks de usuários.\n\n"
                        "Siga estes passos obrigatoriamente:\n"
                        "1. Use get_all_feedbacks para ler todos os feedbacks do banco.\n"
                        "2. Para CADA feedback, use classify_feedback com:\n"
                        "   - categoria: bug, elogio, pagamento, performance, atendimento, outros\n"
                        "   - sentimento: positivo, negativo, neutro\n"
                        "   - resumo: uma frase curta descrevendo o feedback\n"
                        "3. Depois de classificar TODOS, use generate_report com os principais pontos.\n"
                        "4. Use save_results_to_file para salvar o relatório e os feedbacks.\n"
                        "5. Por fim, escreva um relatório em texto para a gerência.\n\n"
                        "Comece agora."
                    ))
                ],
            )
        ]

        max_iterations = 50

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

                print(f"  🔧 Tool: {fn_name}({json.dumps(arguments, ensure_ascii=False)[:120]})")

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
