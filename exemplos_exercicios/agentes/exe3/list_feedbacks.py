"""
Script auxiliar para listar todos os feedbacks disponíveis no banco
"""
from sqlalchemy import create_engine, text

# Configuração do banco de dados
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"
engine = create_engine(DB_URL)

print("\n" + "="*60)
print("📋 FEEDBACKS DISPONÍVEIS NO BANCO")
print("="*60 + "\n")

query = text("""
    SELECT 
        feedback_id,
        LEFT(feedback_text, 60) as preview,
        channel,
        created_at
    FROM feedbacks
    ORDER BY feedback_id
""")

try:
    with engine.begin() as conn:
        rows = conn.execute(query).mappings().all()
    
    if not rows:
        print("⚠️  Nenhum feedback encontrado no banco")
    else:
        print(f"Total: {len(rows)} feedbacks\n")
        for row in rows:
            print(f"ID {row['feedback_id']:2d} | {row['channel']:8s} | {row['preview']}...")
        
        print("\n" + "="*60)
        print("Para analisar um feedback, execute:")
        print("  python run_feedback_agent.py <feedback_id>")
        print("\nExemplo:")
        print(f"  python run_feedback_agent.py {rows[0]['feedback_id']}")
        print("="*60 + "\n")

except Exception as e:
    print(f"❌ Erro ao conectar ao banco: {e}")
    print("Verifique se o Docker está rodando e o banco está acessível")
    print("\n")
