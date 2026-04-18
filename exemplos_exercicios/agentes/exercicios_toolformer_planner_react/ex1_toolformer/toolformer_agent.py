"""
Exercício 1 - Agente Toolformer
Decide quando usar a tool get_ticket_conversation
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import TOOL_MAP

load_dotenv()


class ToolformerAgent:
    """
    Agente que decide inteligentemente quando usar tools
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Declaração da tool disponível
        self.tool_declarations = [
            types.FunctionDeclaration(
                name="get_ticket_conversation",
                description="Busca informações completas de um ticket específico, incluindo todas as mensagens da conversa e o status atual",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID numérico do ticket a ser consultado"
                        }
                    },
                    "required": ["ticket_id"]
                },
            )
        ]
        
        self.generate_config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.tool_declarations)],
            temperature=0.1,
        )
    
    def run(self, user_question: str) -> str:
        """
        Processa uma pergunta do usuário e decide se precisa usar tools
        
        Args:
            user_question: Pergunta do usuário
        
        Returns:
            Resposta do agente
        """
        print(f"\n{'='*60}")
        print(f"❓ Pergunta: {user_question}")
        print(f"{'='*60}\n")
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Você é um assistente de suporte técnico.\n\n"
                            "Você tem acesso a uma tool chamada 'get_ticket_conversation' "
                            "que busca informações de tickets específicos.\n\n"
                            "IMPORTANTE:\n"
                            "- Use a tool APENAS quando a pergunta mencionar um ticket_id específico\n"
                            "- Se a pergunta for genérica sobre tickets, responda sem usar a tool\n"
                            "- Se a pergunta não for sobre tickets, responda normalmente\n\n"
                            f"Pergunta do usuário: {user_question}"
                        )
                    )
                ],
            )
        ]
        
        iteration = 0
        max_iterations = 5
        used_tool = False
        
        while iteration < max_iterations:
            iteration += 1
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=self.generate_config,
            )
            
            candidate = response.candidates[0]
            parts = candidate.content.parts
            
            # Verifica se há chamadas de função
            function_calls = [
                part.function_call
                for part in parts
                if getattr(part, "function_call", None) is not None
            ]
            
            if not function_calls:
                # Sem mais chamadas de função, retorna resposta final
                final_text = (response.text or "").strip()
                
                if used_tool:
                    print("✅ Tool foi utilizada")
                else:
                    print("ℹ️  Respondeu sem usar tool")
                
                return final_text
            
            # Adiciona a resposta do modelo ao histórico
            contents.append(candidate.content)
            
            # Executa as funções chamadas
            function_response_parts = []
            
            for call in function_calls:
                function_name = call.name
                arguments = dict(call.args) if call.args else {}
                
                print(f"🔧 Usando tool: {function_name}")
                print(f"   Argumentos: {arguments}")
                used_tool = True
                
                # Executa a tool
                result = TOOL_MAP[function_name](**arguments)
                
                # Mostra resultado resumido
                if result.get("found"):
                    print(f"   ✅ Ticket encontrado - Status: {result.get('status')}")
                else:
                    print(f"   ❌ Ticket não encontrado")
                
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
    print("\n" + "="*60)
    print("🤖 AGENTE TOOLFORMER - Exercício 1")
    print("="*60)
    
    agent = ToolformerAgent()
    
    # Teste 1: Pergunta com ticket_id (deve usar tool)
    print("\n" + "="*60)
    print("TESTE 1: Pergunta com ticket_id específico")
    print("="*60)
    
    response1 = agent.run("O ticket 1001 está resolvido?")
    print(f"\n📝 Resposta:\n{response1}\n")
    
    # Teste 2: Pergunta genérica (NÃO deve usar tool)
    print("\n" + "="*60)
    print("TESTE 2: Pergunta genérica sobre tickets")
    print("="*60)
    
    response2 = agent.run("O que é um ticket?")
    print(f"\n📝 Resposta:\n{response2}\n")
    
    # Teste 3: Pergunta sobre outro ticket
    print("\n" + "="*60)
    print("TESTE 3: Pergunta sobre status de outro ticket")
    print("="*60)
    
    response3 = agent.run("Qual o status do ticket 1007?")
    print(f"\n📝 Resposta:\n{response3}\n")
    
    print("="*60)
    print("✅ Testes concluídos!")
    print("="*60 + "\n")
