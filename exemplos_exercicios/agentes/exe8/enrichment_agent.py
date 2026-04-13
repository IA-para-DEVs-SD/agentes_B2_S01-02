import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import TOOL_MAP

load_dotenv()


class TopicEnrichmentAgent:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.tool_declarations = [
            types.FunctionDeclaration(
                name="get_top_topics",
                description=(
                    "Analisa feedbacks e conversations do banco de dados "
                    "e retorna os tópicos mais frequentes com contagem."
                ),
                parameters={"type": "object", "properties": {}},
            ),
            types.FunctionDeclaration(
                name="search_external_articles",
                description=(
                    "Busca artigos externos sobre um tópico usando Exa AI. "
                    "Retorna título, URL e texto de cada artigo."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Tópico para buscar artigos externos",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Número de artigos (padrão: 3)",
                        },
                    },
                    "required": ["topic"],
                },
            ),
            types.FunctionDeclaration(
                name="save_articles_to_files",
                description=(
                    "Salva os artigos de um tópico como arquivos .txt "
                    "na pasta exe8/arquivos."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Nome do tópico",
                        },
                        "articles": {
                            "type": "array",
                            "description": "Lista de artigos para salvar",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "text": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["topic", "articles"],
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
                        "Você é um agente de enriquecimento de dados de suporte.\n\n"
                        "Siga estes passos obrigatoriamente:\n"
                        "1. Use get_top_topics para identificar os tópicos mais frequentes.\n"
                        "2. Para cada um dos TOP 3 tópicos, use search_external_articles "
                        "para buscar 3 artigos externos.\n"
                        "3. Para cada tópico, use save_articles_to_files para salvar "
                        "os artigos como .txt.\n"
                        "4. Ao final, apresente um relatório consolidado mostrando:\n"
                        "   - Os tópicos mais frequentes com contagem\n"
                        "   - Os artigos encontrados para cada tópico\n"
                        "   - Os arquivos salvos\n\n"
                        "Comece agora."
                    ))
                ],
            )
        ]

        max_iterations = 30

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

                print(f"  🔧 Tool: {fn_name}({json.dumps(arguments, ensure_ascii=False)[:150]})")

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
