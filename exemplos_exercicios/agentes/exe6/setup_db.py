"""
Script para verificar e criar a tabela internal_notes se necessário
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"

def setup_database():
    engine = create_engine(DB_URL)
    
    print("\n" + "="*60)
    print("🔧 SETUP DO BANCO DE DADOS - Exercício 6")
    print("="*60 + "\n")
    
    # Verifica se a tabela existe
    check_query = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'internal_notes'
        );
    """)
    
    with engine.begin() as conn:
        exists = conn.execute(check_query).scalar()
    
    if exists:
        print("✅ Tabela 'internal_notes' já existe")
        
        # Mostra estrutura
        desc_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'internal_notes'
            ORDER BY ordinal_position;
        """)
        
        with engine.begin() as conn:
            columns = conn.execute(desc_query).fetchall()
        
        print("\n📋 Estrutura da tabela:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
    else:
        print("⚠️  Tabela 'internal_notes' não existe. Criando...")
        
        create_query = text("""
            CREATE TABLE internal_notes (
                id SERIAL PRIMARY KEY,
                ticket_id INT,
                note_text TEXT NOT NULL,
                note_status TEXT NOT NULL,
                blocked_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        with engine.begin() as conn:
            conn.execute(create_query)
        
        print("✅ Tabela 'internal_notes' criada com sucesso!")
    
    # Conta registros
    count_query = text("SELECT COUNT(*) FROM internal_notes;")
    
    with engine.begin() as conn:
        count = conn.execute(count_query).scalar()
    
    print(f"\n📊 Total de registros: {count}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    setup_database()
