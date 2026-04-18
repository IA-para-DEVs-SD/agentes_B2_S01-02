"""
Script de teste para verificar as tools individualmente
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Verifica se a chave do Gemini está configurada
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key or gemini_key == "your-gemini-api-key-here":
    print("❌ ERRO: Configure a chave GEMINI_API_KEY no arquivo .env")
    print("   Obtenha sua chave em: https://aistudio.google.com/app/apikey")
    exit(1)

# Import após verificação da chave
from tools import get_feedback  # noqa: E402

print("\n" + "="*60)
print("🧪 TESTE DAS TOOLS")
print("="*60 + "\n")

# Verifica se foi passado um feedback_id
if len(sys.argv) > 1:
    try:
        feedback_id = int(sys.argv[1])
    except ValueError:
        print("❌ ERRO: O ID do feedback deve ser um número")
        print("Uso: python test_tools.py <feedback_id>")
        exit(1)
else:
    feedback_id = 1  # ID padrão para teste

# Teste: Buscar um feedback específico
print(f"🔍 Testando get_feedback({feedback_id})...")
feedback = get_feedback(feedback_id)

if feedback['found']:
    print("   ✅ Feedback encontrado")
    print(f"   ID: {feedback['feedback_id']}")
    print(f"   Canal: {feedback['channel']}")
    print(f"   Data: {feedback['created_at']}")
    print(f"   Texto: {feedback['feedback_text'][:80]}...")
else:
    print(f"   ❌ Feedback {feedback_id} não encontrado")
    print("   Tente outro ID ou verifique os dados no banco")

print("\n" + "="*60)
print("✅ Teste básico concluído!")
print("="*60 + "\n")
print("Para testar o agente completo, execute:")
print(f"  python exemplos_exercicios/agentes/exe3/run_feedback_agent.py {feedback_id}")
print("\n")
