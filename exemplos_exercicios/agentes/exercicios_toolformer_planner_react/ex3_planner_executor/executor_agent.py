"""
Exercício 3 - Agente Executor

O Executor é responsável por executar o plano criado pelo Planner.
Ele tem acesso às tools e executa as análises.

Responsabilidades:
- Receber um plano estruturado
- Executar cada etapa usando tools
- Gerar relatório com resultados, riscos e sugestões
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import TOOL_MAP

# Carrega variáveis de ambiente
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class ExecutorAgent:
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
                        name="load_backlog",
                        description="Carrega todas as tarefas do backlog da sprint com estatísticas",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={}
                        )
                    )
                ]
            )
        ]
        
        # System prompt para o Executor
        self.system_instruction = """Você é um agente Executor especializado em análise de backlog Scrum.

Você recebe um plano de análise e deve executá-lo usando a tool load_backlog.

Após carregar os dados, você deve analisar e gerar um relatório estruturado com:

1. TAREFAS BLOQUEADAS
   - Liste tarefas com status "Bloqueado"
   - Identifique impactos

2. ATRASOS
   - Identifique tarefas com muitos dias_em_aberto
   - Analise prioridades vs tempo

3. BUGS
   - Total de bugs relacionados
   - Tarefas com mais bugs

4. DISTRIBUIÇÃO DE TRABALHO
   - Carga por responsável
   - Balanceamento

5. RISCOS
   - Identifique riscos para a sprint
   - Priorize por impacto

6. SUGESTÕES
   - Ações práticas para melhorar
   - Priorize por urgência

Seja objetivo, analítico e prático."""
        
        self.generate_config = types.GenerateContentConfig(
            tools=self.tools,
            temperature=0.1
        )
    
    def execute_plan(self, plan: dict) -> str:
        """
        Executa o plano de análise
        
        Args:
            plan: Plano estruturado criado pelo Planner
            
        Returns:
            Relatório de análise
        """
        print(f"\n{'='*60}")
        print(f"⚙️  EXECUTOR: Executando plano de análise")
        print(f"{'='*60}\n")
        
        # Monta a mensagem inicial com o plano
        plan_text = f"""Execute o seguinte plano de análise:

Objetivo: {plan.get('objetivo', 'N/A')}

Etapas:
"""
        for i, step in enumerate(plan.get('steps', []), 1):
            plan_text += f"{i}. {step}\n"
        
        plan_text += "\nUse a tool load_backlog para obter os dados e execute a análise completa."
        
        # Histórico de mensagens
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=plan_text)]
            )
        ]
        
        # Loop de execução
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
                    
                    print(f"🔧 Executando tool: {function_name}\n")
                    
                    # Executa a tool
                    result = TOOL_MAP[function_name]()
                    
                    if result["found"]:
                        print(f"✅ Backlog carregado:")
                        print(f"   - Total de tarefas: {result['total']}")
                        print(f"   - Bloqueadas: {result['stats']['blocked']}")
                        print(f"   - Em progresso: {result['stats']['in_progress']}")
                        print(f"   - A fazer: {result['stats']['todo']}")
                        print(f"   - Concluídas: {result['stats']['done']}")
                        print(f"   - Total de bugs: {result['stats']['total_bugs']}")
                        print(f"   - Total de story points: {result['stats']['total_points']}\n")
                    
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
                    print(f"📊 Análise concluída\n")
                    return first_part.text
            
            # Se chegou aqui sem retornar, algo deu errado
            break
        
        return "Não foi possível executar o plano"


if __name__ == "__main__":
    executor = ExecutorAgent()
    
    print("\n" + "="*60)
    print("🤖 AGENTE EXECUTOR - Exercício 3")
    print("="*60)
    
    # Carrega o plano criado pelo Planner
    try:
        with open("plan.json", "r", encoding="utf-8") as f:
            plan = json.load(f)
        print("\n✅ Plano carregado de plan.json")
    except FileNotFoundError:
        print("\n⚠️  Arquivo plan.json não encontrado. Usando plano padrão.")
        plan = {
            "objetivo": "Análise do backlog da sprint",
            "steps": [
                "Carregar dados do backlog",
                "Verificar tarefas bloqueadas",
                "Identificar atrasos",
                "Analisar bugs relacionados",
                "Avaliar distribuição de trabalho",
                "Identificar riscos",
                "Sugerir melhorias"
            ]
        }
    
    # Executa o plano
    report = executor.execute_plan(plan)
    
    print("="*60)
    print("📋 RELATÓRIO DE ANÁLISE")
    print("="*60 + "\n")
    print(report)
    print("\n" + "="*60 + "\n")
