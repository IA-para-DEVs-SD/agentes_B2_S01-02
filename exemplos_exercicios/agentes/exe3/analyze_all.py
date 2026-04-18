"""
Script para analisar todos os feedbacks do banco
Respeita o limite de 5 requisições por minuto do Gemini free tier
"""
import time
from feedback_agent import FeedbackAnalysisAgent

print("\n" + "="*60)
print("🤖 ANÁLISE EM LOTE DE TODOS OS FEEDBACKS")
print("="*60)
print("⚠️  Gemini free tier: 5 requisições/minuto")
print("   Aguardando 15 segundos entre cada análise...")
print("="*60 + "\n")

# IDs dos feedbacks (1 a 30)
feedback_ids = range(1, 31)

agent = FeedbackAnalysisAgent()
success_count = 0
error_count = 0

for i, feedback_id in enumerate(feedback_ids, 1):
    print(f"\n{'='*60}")
    print(f"📝 Analisando feedback {i}/30 (ID: {feedback_id})")
    print(f"{'='*60}\n")
    
    try:
        result = agent.run(feedback_id)
        print(f"\n✅ Feedback {feedback_id} analisado com sucesso")
        success_count += 1
        
        # Aguarda 15 segundos entre requisições (4 por minuto, seguro)
        if i < len(feedback_ids):
            print(f"\n⏳ Aguardando 15 segundos antes do próximo...")
            time.sleep(15)
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print(f"⚠️  Limite de requisições atingido no feedback {feedback_id}")
            print("   Aguardando 60 segundos...")
            time.sleep(60)
            # Tenta novamente
            try:
                result = agent.run(feedback_id)
                print(f"✅ Feedback {feedback_id} analisado com sucesso (retry)")
                success_count += 1
                if i < len(feedback_ids):
                    time.sleep(15)
            except Exception as e2:
                print(f"❌ Erro ao analisar feedback {feedback_id}: {e2}")
                error_count += 1
        else:
            print(f"❌ Erro ao analisar feedback {feedback_id}: {e}")
            error_count += 1

print("\n" + "="*60)
print("📊 RESUMO DA ANÁLISE EM LOTE")
print("="*60)
print(f"✅ Sucessos: {success_count}")
print(f"❌ Erros: {error_count}")
print(f"📝 Total: {len(feedback_ids)}")
print(f"📈 Taxa de sucesso: {(success_count/len(feedback_ids)*100):.1f}%")
print("="*60 + "\n")

if success_count > 0:
    print("Para ver o relatório consolidado, execute:")
    print("  python exemplos_exercicios/agentes/exe3/generate_report.py")
    print("\n")
