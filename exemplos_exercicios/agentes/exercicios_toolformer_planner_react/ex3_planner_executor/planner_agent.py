"""
Exercício 3 - Agente Planner

O Planner é responsável por criar um plano de análise estruturado.
Ele NÃO executa as ações, apenas define o que deve ser feito.

Responsabilidades:
- Receber uma solicitação de análise
- Gerar um plano estruturado em JSON
- Definir etapas claras de análise
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega variáveis de ambiente
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class PlannerAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        
        # System prompt para o Planner
        self.system_instruction = """Você é um agente Planner especializado em análise de backlog Scrum.

Sua responsabilidade é criar planos de análise estruturados em JSON.

Quando receber uma solicitação como "Analise o backlog da sprint", você deve gerar um plano com etapas claras.

Formato do plano (JSON):
{
  "objetivo": "descrição do objetivo da análise",
  "steps": [
    "etapa 1: descrição clara",
    "etapa 2: descrição clara",
    "etapa 3: descrição clara",
    ...
  ]
}

Etapas típicas para análise de backlog:
1. Carregar dados do backlog
2. Verificar tarefas bloqueadas
3. Identificar atrasos (dias_em_aberto alto)
4. Analisar distribuição de bugs
5. Avaliar distribuição de trabalho entre responsáveis
6. Verificar story points vs status
7. Identificar riscos
8. Sugerir melhorias

IMPORTANTE:
- Retorne APENAS o JSON, sem texto adicional
- Seja específico nas etapas
- Foque em análise de dados, não em execução"""
        
        self.generate_config = types.GenerateContentConfig(
            temperature=0.1,
            system_instruction=self.system_instruction
        )
    
    def create_plan(self, user_request: str) -> dict:
        """
        Cria um plano de análise baseado na solicitação do usuário
        
        Args:
            user_request: Solicitação do usuário
            
        Returns:
            Plano estruturado em formato dict
        """
        print(f"\n{'='*60}")
        print(f"📋 PLANNER: Criando plano de análise")
        print(f"{'='*60}\n")
        print(f"Solicitação: {user_request}\n")
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_request,
            config=self.generate_config
        )
        
        # Extrai o texto da resposta
        response_text = response.text.strip()
        
        # Remove markdown code blocks se existirem
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            plan = json.loads(response_text)
            print("✅ Plano criado com sucesso\n")
            print(f"Objetivo: {plan.get('objetivo', 'N/A')}")
            print(f"Etapas: {len(plan.get('steps', []))}")
            for i, step in enumerate(plan.get('steps', []), 1):
                print(f"  {i}. {step}")
            print()
            return plan
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear JSON: {e}")
            print(f"Resposta recebida: {response_text}")
            return {
                "objetivo": "Análise do backlog",
                "steps": [
                    "Carregar dados do backlog",
                    "Verificar tarefas bloqueadas",
                    "Identificar atrasos",
                    "Analisar bugs",
                    "Avaliar distribuição de trabalho"
                ]
            }


if __name__ == "__main__":
    planner = PlannerAgent()
    
    print("\n" + "="*60)
    print("🤖 AGENTE PLANNER - Exercício 3")
    print("="*60)
    
    # Teste: Criar plano de análise
    plan = planner.create_plan("Analise o backlog da sprint")
    
    # Salva o plano em arquivo para o executor usar
    with open("plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print("="*60)
    print("✅ Plano salvo em plan.json")
    print("="*60 + "\n")
