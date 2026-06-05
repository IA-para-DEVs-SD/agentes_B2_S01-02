-- Script de inicialização do PostgreSQL
-- Este script é executado automaticamente quando o container é criado pela primeira vez

-- ========================================
-- 1. ATIVAR EXTENSÃO PGVECTOR (para RAG)
-- ========================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================================
-- 2. TABELAS TRADICIONAIS (exemplos básicos)
-- ========================================

-- Criar uma tabela de exemplo
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir alguns dados de exemplo
INSERT INTO usuarios (nome, email) VALUES
    ('João Silva', 'joao@email.com'),
    ('Maria Santos', 'maria@email.com'),
    ('Pedro Oliveira', 'pedro@email.com');

-- Criar outra tabela de exemplo
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    estoque INTEGER DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir produtos de exemplo
INSERT INTO produtos (nome, descricao, preco, estoque) VALUES
    ('Notebook', 'Notebook Dell i5 8GB RAM', 3500.00, 10),
    ('Mouse', 'Mouse sem fio Logitech', 150.00, 50),
    ('Teclado', 'Teclado mecânico RGB', 450.00, 25);

-- ========================================
-- 3. TABELA PARA RAG (com pgvector)
-- ========================================

-- Tabela para armazenar documentos com embeddings
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),  -- OpenAI text-embedding-3-small gera vetores de 1536 dimensões
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para busca vetorial rápida
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Inserir alguns documentos de exemplo (sem embeddings por enquanto)
INSERT INTO documents (content, metadata) VALUES
    ('PostgreSQL é um sistema de gerenciamento de banco de dados relacional open-source.', 
     '{"category": "database", "source": "wikipedia"}'),
    ('RAG (Retrieval-Augmented Generation) combina busca semântica com modelos de linguagem.', 
     '{"category": "ai", "source": "paper"}'),
    ('Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.', 
     '{"category": "programming", "source": "docs"}');

-- ========================================
-- 4. FUNÇÃO PARA BUSCA POR SIMILARIDADE (RAG)
-- ========================================

-- Função que faz busca vetorial por similaridade
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id INT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE documents.metadata @> filter
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ========================================
-- 5. VISUALIZAÇÕES ÚTEIS
-- ========================================

-- View para ver documentos sem mostrar o vetor completo (muito longo)
CREATE OR REPLACE VIEW documents_summary AS
SELECT 
    id,
    content,
    metadata,
    CASE 
        WHEN embedding IS NOT NULL THEN '✓ Tem embedding'
        ELSE '✗ Sem embedding'
    END as has_embedding,
    created_at
FROM documents;

-- Mensagem de confirmação
SELECT 'Banco de dados inicializado com sucesso!' AS status;
SELECT 'Extensão pgvector ativada para RAG!' AS rag_status;
