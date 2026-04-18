"""
Agente de análise de feedbacks usando Gemini com tool calling
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import TOOL_MAP

load_dotenv()


class FeedbackAnalysisAgent:
    
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        self.tool_declarations = [
            types.FunctionDeclaration(
                name="get_feedback",
                description="Busca um feedback específico do banco de dados pelo ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "feedback_id": {
                            "type": "integer",
                            "description": "ID do feedback"
                        }
                    },
                    "required": ["feedback_id"]
                },
            ),
            types.FunctionDeclaration(
                name="analyze_feedback_with_llm",
                description="Analisa um feedback individual e retorna categoria, sentimento e resumo",
                parameters={
                    "type": "object",
                    "properties": {
                        "feedback_text": {
                            "type": "string",
                            "description": "Texto do feedback a ser analisado"
                        }
                    },
                    "required": ["feedback_text"]
                },
            ),
            types.FunctionDeclaration(
                name="classify_feedback",
                description="Classifica o feedback adicionando prioridade e flag de ação necessária",
                parameters={
                    "type": "object",
                    "properties": {
                        "categoria": {
                            "type": "string",
                            "description": "Categoria do feedback"
                        },
                        "sentimento": {
                            "type": "string",
                            "description": "Sentimento do feedback"
                        }
                    },
                    "required": ["categoria", "sentimento"]
                },
            ),
            types.FunctionDeclaration(
                name="save_analysis_results",
                description="Salva o resultado da análise no banco de dados",
                parameters={
                    "type": "object",
                    "properties": {
                        "feedback_id": {
                            "type": "integer",
                            "description": "ID do feedback"
                        },
                        "analysis": {
                            "type": "object",
                            "description": "Objeto com os resultados da análise (categoria, sentimento, resumo, prioridade, requer_acao)"
                        }
                    },
                    "required": ["feedback_id", "analysis"]
                },
            ),
            types.FunctionDeclaration(
                name="generate_final_report",
                description="Gera um relatório consolidado com estatísticas de todos os feedbacks analisados",
                parameters={
                    "type": "object",
                    "properties": {}
                },
            ),
        ]
        
        self.generate_config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.tool_declarations)],
            temperature=0.2,
        )
    
    def run(self, feedback_id: int) -> str:
        """
        Executa o agente para analisar um feedback específico
        """
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Você é um agente de análise de feedbacks com acesso a tools.\n\n"
                            "Sua tarefa é:\n"
                            "1. Buscar o feedback especificado\n"
                            "2. Analisar o feedback com LLM para extrair categoria, sentimento e resumo\n"
                            "3. Classificar o feedback adicionando prioridade e flag de ação\n"
                            "4. Salvar os resultados estruturados no banco\n\n"
                            "Execute essas etapas usando as tools disponíveis.\n"
                            f"Analise o feedback {feedback_id}.\n\n"
                            "Ao final, retorne um resumo do que foi feito."
                        )
                    )
                ],
            )
        ]
        
        iteration = 0
        max_iterations = 50  # Limite de segurança
        
        while iteration < max_iterations:
            iteration += 1
            
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
                print(f"\n{'='*60}")
                print("✅ Análise concluída!")
                print(f"{'='*60}\n")
                return final_text
            
            # Adiciona a resposta do modelo ao histórico
            contents.append(candidate.content)
            
            function_response_parts = []
            
            for call in function_calls:
                function_name = call.name
                arguments = dict(call.args) if call.args else {}
                
                print(f"\n🔧 Executando tool: {function_name}")
                if arguments:
                    print(f"   Argumentos: {list(arguments.keys())}")
                
                result = TOOL_MAP[function_name](**arguments)
                
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response=result,
                    )
                )
            
            # Devolve os resultados das funções ao modelo
            contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )
        
        return "⚠️ Limite de iterações atingido"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\n❌ Erro: Informe o ID do feedback")
        print("Uso: python feedback_agent.py <feedback_id>")
        print("Exemplo: python feedback_agent.py 1\n")
        sys.exit(1)
    
    try:
        feedback_id = int(sys.argv[1])
    except ValueError:
        print("\n❌ Erro: O ID do feedback deve ser um número")
        print("Exemplo: python feedback_agent.py 1\n")
        sys.exit(1)
    
    print("\n" + "="*60)
    print(f"🤖 AGENTE DE ANÁLISE DE FEEDBACKS - ID {feedback_id}")
    print("="*60 + "\n")
    
    agent = FeedbackAnalysisAgent()
    result = agent.run(feedback_id)
    
    print("\n" + "="*60)
    print("📝 RESULTADO FINAL")
    print("="*60)
    print(result)
    print("\n")
