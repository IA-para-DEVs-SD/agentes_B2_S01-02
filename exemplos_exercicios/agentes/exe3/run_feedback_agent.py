"""
Script para executar o agente de análise de feedbacks
Uso: python run_feedback_agent.py <feedback_id>
"""
import sys
from feedback_agent import FeedbackAnalysisAgent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Erro: Informe o ID do feedback")
        print("Uso: python run_feedback_agent.py <feedback_id>")
        print("Exemplo: python run_feedback_agent.py 1\n")
        sys.exit(1)
    
    try:
        feedback_id = int(sys.argv[1])
    except ValueError:
        print("\n❌ Erro: O ID do feedback deve ser um número")
        print("Exemplo: python run_feedback_agent.py 1\n")
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
