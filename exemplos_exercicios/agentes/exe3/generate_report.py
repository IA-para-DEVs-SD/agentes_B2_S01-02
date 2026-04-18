"""
Script para gerar relatório consolidado dos feedbacks analisados
"""
import json
from tools import generate_final_report

print("\n" + "="*60)
print("📊 RELATÓRIO CONSOLIDADO DE FEEDBACKS")
print("="*60 + "\n")

try:
    report = generate_final_report()
    
    if report.get('total_feedbacks', 0) == 0:
        print("⚠️  Nenhum feedback foi analisado ainda")
        print("\nPara analisar feedbacks, execute:")
        print("  python exemplos_exercicios/agentes/exe3/analyze_all.py")
        print("\nOu analise individualmente:")
        print("  python exemplos_exercicios/agentes/exe3/run_feedback_agent.py <id>")
    else:
        print(f"Total de feedbacks analisados: {report['total_feedbacks']}\n")
        
        print("📂 Distribuição por Categoria:")
        for categoria, count in report['categorias'].items():
            print(f"   {categoria:15s}: {count:2d}")
        
        print("\n😊 Distribuição por Sentimento:")
        for sentimento, count in report['sentimentos'].items():
            print(f"   {sentimento:15s}: {count:2d}")
        
        print("\n⚡ Distribuição por Prioridade:")
        for prioridade, count in report['prioridades'].items():
            print(f"   {prioridade:15s}: {count:2d}")
        
        print(f"\n🚨 Feedbacks que requerem ação: {report['feedbacks_requerem_acao']}")
        
        if report.get('principais_pontos'):
            print("\n💡 Principais Pontos:")
            for i, ponto in enumerate(report['principais_pontos'], 1):
                print(f"   {i}. {ponto}")
        
        print("\n" + "="*60)
        print("📄 Relatório JSON completo:")
        print("="*60)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")

except Exception as e:
    print(f"❌ Erro ao gerar relatório: {e}")
    print("\n")
