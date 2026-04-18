"""
Demonstração da ferramenta Exa para busca externa
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔍 EXERCÍCIO 7 - Busca Externa com Exa AI")
print("="*60 + "\n")

# Verifica se a chave está configurada
exa_key = os.getenv("EXA_API_KEY")

if not exa_key or exa_key == "your-exa-api-key-here":
    print("❌ ERRO: Configure a chave EXA_API_KEY no arquivo .env")
    print("\n📝 Como obter a chave:")
    print("   1. Acesse: https://exa.ai/")
    print("   2. Crie uma conta gratuita")
    print("   3. Obtenha sua API key")
    print("   4. Adicione no arquivo .env:")
    print("      EXA_API_KEY='sua-chave-aqui'")
    print("\n" + "="*60)
    print("ℹ️  O QUE É O EXA?")
    print("="*60)
    print("\nExa é uma API de busca semântica que permite:")
    print("  • Buscar informações atualizadas na web")
    print("  • Complementar dados internos do banco")
    print("  • Responder perguntas que não estão no sistema")
    print("  • Usar busca semântica (não apenas keywords)")
    print("\n" + "="*60)
    print("📚 CASOS DE USO")
    print("="*60)
    print("\n1. Buscar soluções para problemas técnicos:")
    print("   'login issues password reset'")
    print("\n2. Pesquisar sobre problemas de pagamento:")
    print("   'problemas com pagamento online'")
    print("\n3. Encontrar guias e tutoriais:")
    print("   'how to troubleshoot app crashes'")
    print("\n" + "="*60 + "\n")
    exit(1)

# Se a chave está configurada, tenta executar
try:
    from tools_external import search_external, summarize_external_results
    
    print("✅ Chave EXA configurada!")
    print("\n" + "="*60)
    print("TESTE 1: Busca sobre problemas de login")
    print("="*60 + "\n")
    
    results = search_external("login issues password reset", num_results=3)
    
    print(f"📊 Resultados encontrados: {len(results)}\n")
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   Preview: {r['text'][:100]}...")
        print()
    
    print("="*60)
    print("TESTE 2: Busca sobre problemas de pagamento")
    print("="*60 + "\n")
    
    results2 = search_external("problemas com pagamento", num_results=3)
    
    print(f"📊 Resultados encontrados: {len(results2)}\n")
    
    for i, r in enumerate(results2, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   Preview: {r['text'][:100]}...")
        print()
    
    print("="*60)
    print("✅ Testes concluídos com sucesso!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Erro ao executar busca: {e}")
    print("\nVerifique se:")
    print("  1. A biblioteca exa-py está instalada: pip install exa-py")
    print("  2. A chave EXA_API_KEY está correta")
    print("  3. Você tem créditos disponíveis na conta Exa")
    print("\n")
