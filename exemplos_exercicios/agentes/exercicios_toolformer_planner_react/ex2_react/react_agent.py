"""
Exercício 2 - Agente ReAct (Reasoning + Acting)

O agente ReAct combina raciocínio e ação:
1. Thought (Pensamento): O agente raciocina sobre o que fazer
2. Action (Ação): Executa uma tool
3. Observation (Observação): Analisa o resultado
4. Answer (Resposta): Fornece resposta estruturada

Neste exercício, o agente:
- Recebe um ticket_id
- Busca a conversa usando a tool
- Analisa os dados
- Retorna: status, última mensagem do cliente, próximo passo sugerido
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import TOOL_MAP

# Carrega variáveis de ambiente
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class ReActAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        
        # Declaração das tools para o Gemini
        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="get_ticket_conversation",
                        description="Busca a conversa completa de um ticket no banco de dados",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "ticket_id": types.Schema(
                                    type=types.Type.INTEGER,
                                    description="ID do ticket a ser buscado"
                                )
                            },
                            required=["ticket_id"]
                        )
                    )
                ]
            )
        ]
        
        # System prompt com instruções ReAct
        self.system_instruction = """Você é um agente de análise de tickets que usa o padrão ReAct.

Quando receber uma solicitação para analisar um ticket:

1. THOUGHT (Pensamento): Raciocine sobre o que precisa fazer
2. ACTION (Ação): Use a tool get_ticket_conversation para buscar os dados
3. OBSERVATION (Observação): Analise os dados retornados
4. ANSWER (Resposta): Forneça uma resposta estruturada com:
   - Status atual do ticket
   - Última mensagem do cliente
   - Próximo passo sugerido

Formato da resposta:

Status: [status do ticket]
Última mensagem do cliente: [última mensagem]
Próximo passo: [sugestão baseada no contexto]

Seja objetivo e analítico."""
        
        self.generate_config = types.GenerateContentConfig(
            tools=self.tools,
            temperature=0.1
        )
    
    def run(self, user_input: str) -> str:
        """
        Executa o agente ReAct
        
        Args:
            user_input: Pergunta do usuário
            
        Returns:
            Resposta estruturada do agente
        """
        print(f"\n{'='*60}")
        print(f"❓ Pergunta: {user_input}")
        print(f"{'='*60}\n")
        
        # Histórico de mensagens
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
        ]
        
        # Loop ReAct
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Gera resposta
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=self.generate_config,
            )
            
            # Verifica se há function calls
            if response.candidates[0].content.parts:
                first_part = response.candidates[0].content.parts[0]
                
                # Se há function call, executa
                if hasattr(first_part, 'function_call') and first_part.function_call:
                    function_call = first_part.function_call
                    function_name = function_call.name
                    arguments = dict(function_call.args)
                    
                    print(f"🔧 THOUGHT: Preciso buscar dados do ticket")
                    print(f"🔧 ACTION: Usando tool {function_name}")
                    print(f"   Argumentos: {arguments}\n")
                    
                    # Executa a tool
                    result = TOOL_MAP[function_name](**arguments)
                    
                    print(f"👁️  OBSERVATION: Dados recebidos")
                    if result["found"]:
                        print(f"   - Ticket encontrado")
                        print(f"   - Status: {result['status']}")
                        print(f"   - Mensagens: {result['message_count']}\n")
                    else:
                        print(f"   - Ticket não encontrado\n")
                    
                    # Adiciona a resposta da tool ao histórico
                    contents.append(response.candidates[0].content)
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_name,
                                        response={"result": result}
                                    )
                                )
                            ]
                        )
                    )
                    
                    continue
                
                # Se não há function call, retorna a resposta
                if hasattr(first_part, 'text') and first_part.text:
                    print(f"💡 ANSWER: Resposta estruturada gerada\n")
                    return first_part.text
            
            # Se chegou aqui sem retornar, algo deu errado
            break
        
        return "Não foi possível processar a solicitação"


if __name__ == "__main__":
    agent = ReActAgent()
    
    print("\n" + "="*60)
    print("🤖 AGENTE REACT - Exercício 2")
    print("="*60)
    
    # Teste 1: Ticket existente
    print("\n" + "="*60)
    print("TESTE 1: Análise de ticket existente")
    print("="*60)
    
    response1 = agent.run("Analise o ticket 1007")
    print(f"📝 Resposta:\n{response1}\n")
    
    # Teste 2: Outro ticket
    print("\n" + "="*60)
    print("TESTE 2: Análise de outro ticket")
    print("="*60)
    
    response2 = agent.run("Analise o ticket 1002")
    print(f"📝 Resposta:\n{response2}\n")
    
    # Teste 3: Ticket não existente
    print("\n" + "="*60)
    print("TESTE 3: Ticket não encontrado")
    print("="*60)
    
    response3 = agent.run("Analise o ticket 9999")
    print(f"📝 Resposta:\n{response3}\n")
    
    print("="*60)
    print("✅ Testes concluídos!")
    print("="*60 + "\n")
